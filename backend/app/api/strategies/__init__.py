"""API des stratégies appliquées, journal atomique séparé des anciens QCM."""
import json
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictBool

from .protocoles import BANQUES, INITIAL, ORIGINAUX, VERSION, advance, public, result

router = APIRouter(prefix='/api/strategies', tags=['stratégies appliquées'])


class Creation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    parcours: Literal['plan', 'rappel', 'message', 'temps']
    condition: Literal['avec-note', 'sans-note'] | None = None
    sans_limite_sessions: StrictBool = False


class Etape(BaseModel):
    model_config = ConfigDict(extra='forbid')
    etape_id: UUID
    action: str
    donnees: dict = Field(default_factory=dict)


def now():
    return datetime.now(timezone.utc).isoformat()


@router.post('/sessions', status_code=201)
def create(body: Creation, request: Request):
    if body.condition is not None and body.parcours != 'message':
        raise HTTPException(422, 'La condition de note concerne la prise de message')
    storage = request.app.state.blocs_strategies
    session = {'session_id': str(uuid4()), 'parcours': body.parcours, 'version': VERSION, 'condition': (body.condition or 'avec-note') if body.parcours == 'message' else 'standard', 'phase': INITIAL[body.parcours], 'donnees': {}, 'aides': [], 'pauses': 0, 'pause': None, 'pause_secondes': 0, 'temps_fiable': True, 'cree': now(), 'terminee': False, 'etapes': {}, 'evenements': [], 'sans_limite_sessions': body.sans_limite_sessions}
    with storage.lock:
        root = storage.path(session['session_id']).parent
        archives = [json.loads(path.read_text()) for path in root.glob('*.json')]
        count = sum(item.get('cree', '')[:10] == session['cree'][:10] for item in archives)
        prior = sorted((item for item in archives if item['parcours'] == body.parcours), key=lambda item: item['cree'])
        last = prior[-1].get('scenario_id', ORIGINAUX[body.parcours]['id']) if prior else None
        bank = BANQUES[body.parcours]
        session['scenario_id'] = bank[(bank.index(last) + 1) % len(bank)] if last in bank else bank[0]
        if count >= 3 and not body.sans_limite_sessions:
            raise HTTPException(429, 'Trois séances ont déjà été ouvertes aujourd’hui')
        storage.save(session)
    return public(session)


@router.post('/sessions/{identifier}/etapes')
def step(identifier: str, body: Etape, request: Request):
    storage = request.app.state.blocs_strategies
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
            raise HTTPException(409, 'Séance terminée')
        # Notes personnelles et champs superflus ne sont jamais persistés.
        allowed = {'plan_initial': {'ordre'}, 'reviser': {'ordre'}, 'executer': {'action_id'}, 'configurer': {'piece_id', 'rappel'}, 'intercaler': {'action_id'}, 'joindre': {'piece_id'}, 'masquer': {'note_presente'}, 'restituer': {'quoi', 'quand', 'absence'}, 'agir': {'action_id', 'heure'}, 'estimer': {'secondes'}, 'classer': {'document_id', 'categorie'}, 'comparer': {'duree_active_secondes', 'duree_ecoulee_secondes', 'pauses_secondes', 'attente_interface_secondes'}, 'marge': {'secondes'}}
        if set(body.donnees) - allowed.get(body.action, set()):
            raise HTTPException(422, 'Données inattendues')
        try:
            advance(session, body.action, body.donnees)
        except (ValueError, TypeError) as error:
            raise HTTPException(409, str(error)) from None
        response = public(session)
        session['etapes'][key] = {'requete': payload, 'reponse': response}
        session['evenements'].append({'action': body.action, 'phase': session['phase'], 'date': now()})
        storage.save(session)
        return response


@router.post('/sessions/{identifier}/fin')
def finish(identifier: str, request: Request):
    storage = request.app.state.blocs_strategies
    with storage.lock:
        session = storage.read(identifier)
        if not session['terminee']:
            session.update(terminee=True, fin=now())
            storage.save(session)
        return result(session)
