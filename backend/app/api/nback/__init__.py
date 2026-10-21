"""Journal indépendant du n-back, sans entraînement adaptatif ni FSRS."""
import json
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictBool, ValidationError

from .protocoles import DECISIONS, VERSION, advance, canonical, public, sequence

router = APIRouter(prefix='/api/nback', tags=['n-back visuel'])


class Creation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    n: int = Field(default=1, strict=True, ge=1, le=3)
    sans_limite_sessions: StrictBool = False


class Decision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    decision: Literal['identique', 'different', 'absence']
    exposition_secondes: float | None = Field(default=None, strict=True, ge=0, le=86400, allow_inf_nan=False)


class Interruption(BaseModel):
    model_config = ConfigDict(extra='forbid')
    raison: Literal['pause', 'masquage', 'fatigue', 'sortie']


class Etape(BaseModel):
    model_config = ConfigDict(extra='forbid')
    etape_id: UUID
    action: Literal['commencer', 'suivant', 'repondre', 'interrompre']
    donnees: dict = Field(default_factory=dict)


def now():
    return datetime.now(timezone.utc).isoformat()


@router.post('/sessions', status_code=201)
def create(body: Creation, request: Request):
    storage = request.app.state.blocs_nback
    session = dict(session_id=str(uuid4()), version=VERSION, condition='observation-sans-feedback', n=body.n, total=body.n + DECISIONS, position=0, phase='ready', terminee=False, decisions=[], etapes={}, cree=now())
    with storage.lock:
        archives = [json.loads(path.read_text()) for path in storage.path(session['session_id']).parent.glob('*.json')]
        if sum(item.get('cree', '')[:10] == session['cree'][:10] for item in archives) >= 3 and not body.sans_limite_sessions:
            raise HTTPException(429, 'Trois séances ont déjà été ouvertes aujourd’hui')
        used = {canonical(item['sequence']) for item in archives if item.get('n') == body.n and item.get('condition') == session['condition']}
        for _ in range(1000):
            values = sequence(n=body.n)
            if canonical(values) not in used:
                session['sequence'] = values
                break
        else:
            raise HTTPException(503, 'Une nouvelle série ne peut pas être préparée. Réessaie plus tard.')
        storage.save(session)
    return public(session)


@router.post('/sessions/{identifier}/etapes')
def step(identifier: str, body: Etape, request: Request):
    storage = request.app.state.blocs_nback
    with storage.lock:
        session = storage.read(identifier)
        key = str(body.etape_id)
        payload = {'action': body.action, 'donnees': body.donnees}
        if key in session['etapes']:
            old = session['etapes'][key]
            if old['requete'] != payload:
                raise HTTPException(409, 'Étape déjà enregistrée avec une autre réponse')
            return old['reponse']
        if session['terminee']:
            raise HTTPException(409, 'Bloc terminé')
        try:
            if body.action == 'repondre':
                data = Decision.model_validate(body.donnees).model_dump(exclude_none=True)
            elif body.action == 'interrompre':
                data = Interruption.model_validate(body.donnees).model_dump()
            elif body.donnees:
                raise HTTPException(422, 'Données inattendues')
            else:
                data = {}
        except ValidationError:
            raise HTTPException(422, 'Réponse non valide') from None
        try:
            advance(session, body.action, data)
        except ValueError as error:
            raise HTTPException(409, str(error)) from None
        if session['terminee']:
            session['fin'] = now()
        response = public(session)
        session['etapes'][key] = {'requete': payload, 'reponse': response}
        storage.save(session)
        return response


@router.post('/sessions/{identifier}/fin')
def finish(identifier: str, request: Request):
    storage = request.app.state.blocs_nback
    with storage.lock:
        session = storage.read(identifier)
        if not session['terminee']:
            advance(session, 'interrompre', {'raison': 'sortie'})
            session['fin'] = now()
            storage.save(session)
        return public(session)
