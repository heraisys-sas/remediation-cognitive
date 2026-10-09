"""Pratique guidée isolée : correction serveur et fichiers atomiques par bloc."""
import json
import os
import random
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictBool

from .protocoles import VERSION, correction, observations, parameters, stimulus

router = APIRouter(prefix="/api/memoires-immediates", tags=["mémoires immédiates"])


class Creation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    parcours: str
    parametres: dict = Field(default_factory=dict)
    sans_limite_sessions: StrictBool = False


class Reponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    essai_id: str
    reponse: str | list | dict | None
    observations: dict = Field(default_factory=dict)
    assistee: StrictBool = False


class Interruption(BaseModel):
    model_config = ConfigDict(extra="forbid")
    essai_id: str
    phase: str
    assistee: StrictBool = False
    observations: dict = Field(default_factory=dict)


class Aide(BaseModel):
    model_config = ConfigDict(extra="forbid")
    essai_id: str


def now():
    return datetime.now(timezone.utc).isoformat()


class Blocs:
    def __init__(self, root):
        self.root = Path(root)
        self.lock = threading.Lock()

    def path(self, identifier):
        try:
            canonical = str(UUID(identifier))
        except (ValueError, AttributeError):
            raise HTTPException(404, "Bloc inconnu") from None
        return self.root / f"{canonical}.json"

    def read(self, identifier):
        try:
            return json.loads(self.path(identifier).read_text())
        except FileNotFoundError:
            raise HTTPException(404, "Bloc inconnu") from None

    def save(self, session):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.path(session["session_id"])
        temp = path.with_suffix(f".{uuid4()}.tmp")
        try:
            with temp.open("w", encoding="utf-8") as stream:
                json.dump(session, stream, ensure_ascii=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            temp.unlink(missing_ok=True)

    def trial(self, session, index, linked=None):
        identifier = str(uuid4())
        trial = {"id": identifier, "index": index, "stimulus": stimulus(session["parcours"], session["parametres"], identifier, session["changements"][index - 1]), "cree": now(), "premiere": None, "aide": None, "interruption": None}
        if linked:
            trial["remplace"] = linked
        session["essais"].append(trial)
        return trial

    def public(self, trial):
        return {key: trial[key] for key in ("id", "index", "stimulus")}

    def active(self, session, identifier, allow_answered=False):
        if session["terminee"]:
            raise HTTPException(409, "Bloc terminé")
        trial = next((e for e in session["essais"] if e["id"] == identifier), None)
        if not trial or trial["interruption"] or (trial["premiere"] and not allow_answered):
            raise HTTPException(409, "Essai indisponible")
        if not allow_answered and trial is not session["essais"][-1]:
            raise HTTPException(409, "Essai indisponible")
        return trial

    def results(self, session):
        rows = [{"essai_id": e["id"], "index": e["index"], "premiere": e["premiere"], "aide": e["aide"], "interruption": e["interruption"], "remplace": e.get("remplace")} for e in session["essais"]]
        return {"session_id": session["session_id"], "parcours": session["parcours"], "version": VERSION, "parametres": session["parametres"], "terminee": session["terminee"], "observations": rows}


def store(request):
    return request.app.state.blocs_memoires


@router.post("/sessions", status_code=201)
def create(body: Creation, request: Request):
    try:
        params = parameters(body.parcours, body.parametres)
    except ValueError as error:
        raise HTTPException(422, str(error)) from None
    storage = store(request)
    changed = [True, True, False, False]
    random.SystemRandom().shuffle(changed)
    session = {"session_id": str(uuid4()), "parcours": body.parcours, "version": VERSION, "parametres": params, "changements": changed, "cree": now(), "terminee": False, "essais": []}
    trial = storage.trial(session, 1)
    with storage.lock:
        today = now()[:10]
        count = sum(json.loads(path.read_text()).get("cree", "")[:10] == today for path in storage.root.glob("*.json"))
        if count >= 3 and not body.sans_limite_sessions:
            raise HTTPException(429, "Trois blocs ont déjà été ouverts aujourd’hui")
        session["sans_limite_sessions"] = body.sans_limite_sessions
        storage.save(session)
    return {"session_id": session["session_id"], "parcours": body.parcours, "version": VERSION, "parametres": params, "essai": storage.public(trial)}


@router.post("/sessions/{identifier}/reponses")
def answer(identifier: str, body: Reponse, request: Request):
    storage = store(request)
    with storage.lock:
        session = storage.read(identifier)
        trial = storage.active(session, body.essai_id, True)
        existing = trial["aide"] if body.assistee else trial["premiere"]
        if existing and "reponse" in existing:
            if existing["reponse"] != body.reponse or existing["observations"] != body.observations:
                raise HTTPException(409, "Réponse déjà verrouillée")
            following = next((e for e in session["essais"] if e["index"] == trial["index"] + 1 and not e["interruption"]), None)
            return {"correction": existing["correction"], "essai_suivant": storage.public(following) if following else None, "terminee": following is None}
        if not body.assistee and trial is not session["essais"][-1]:
            raise HTTPException(409, "Essai indisponible")
        if body.assistee and (not trial["premiere"] or not trial["aide"] or trial["aide"].get("reponse_validee") or trial["aide"].get("interruption")):
            raise HTTPException(409, "Aide non ouverte")
        try:
            facts = observations(body.observations)
            result = correction(session["parcours"], trial["stimulus"], body.reponse)
        except (ValueError, TypeError) as error:
            raise HTTPException(422, str(error)) from None
        record = {"reponse": body.reponse, "correction": result, "observations": facts, "validee": now()}
        if body.assistee:
            trial["aide"].update(record, reponse_validee=True)
            following = next((e for e in reversed(session["essais"]) if not e["premiere"] and not e["interruption"]), None)
        else:
            trial["premiere"] = record
            following = storage.trial(session, trial["index"] + 1) if trial["index"] < 4 else None
        storage.save(session)
        return {"correction": result, "essai_suivant": storage.public(following) if following else None, "terminee": following is None}


@router.post("/sessions/{identifier}/aide")
def help_trial(identifier: str, body: Aide, request: Request):
    storage = store(request)
    with storage.lock:
        session = storage.read(identifier)
        trial = storage.active(session, body.essai_id, True)
        if not trial["premiere"]:
            raise HTTPException(409, "Aide indisponible")
        if not trial["aide"]:
            trial["aide"] = {"ouverte": now(), "apres_correction": True}
        storage.save(session)
        return {"essai": storage.public(trial), "assistee": True}


@router.post("/sessions/{identifier}/interruption")
def interrupt(identifier: str, body: Interruption, request: Request):
    storage = store(request)
    with storage.lock:
        session = storage.read(identifier)
        if body.assistee:
            trial = storage.active(session, body.essai_id, True)
            if not trial["aide"] or trial["aide"].get("reponse_validee"):
                raise HTTPException(409, "Aide indisponible")
            if body.phase not in ("pret", "exposition", "masque", "reponse"):
                raise HTTPException(422, "Phase inconnue")
            try:
                facts = observations(body.observations)
            except ValueError as error:
                raise HTTPException(422, str(error)) from None
            if not trial["aide"].get("interruption"):
                trial["aide"]["interruption"] = {"phase": body.phase, "observations": facts, "date": now()}
                storage.save(session)
            following = next((e for e in reversed(session["essais"]) if not e["premiere"] and not e["interruption"]), None)
            return {"essai": storage.public(following) if following else None, "assistee_interrompue": True}
        existing = next((e for e in session["essais"] if e.get("remplace") == body.essai_id), None)
        if existing:
            return {"essai": storage.public(existing)}
        trial = storage.active(session, body.essai_id)
        if body.phase not in ("pret", "exposition", "masque", "reponse"):
            raise HTTPException(422, "Phase inconnue")
        try:
            facts = observations(body.observations)
        except ValueError as error:
            raise HTTPException(422, str(error)) from None
        trial["interruption"] = {"phase": body.phase, "observations": facts, "date": now()}
        following = storage.trial(session, trial["index"], trial["id"])
        storage.save(session)
        return {"essai": storage.public(following)}


@router.post("/sessions/{identifier}/fin")
def finish(identifier: str, request: Request):
    storage = store(request)
    with storage.lock:
        session = storage.read(identifier)
        if not session["terminee"]:
            session.update(terminee=True, fin=now())
            storage.save(session)
        return storage.results(session)
