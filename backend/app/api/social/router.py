"""Routes du carnet de missions hors écran (périmètre social).

Contrat : voir docs/30-technique/api-contract.md et l'ADR-004.
- GET  /api/social/missions          → missions proposées (préparation) ;
- GET  /api/social/journal           → notes déjà écrites ;
- POST /api/social/journal           → ajoute une note (201).

Une mission n'a PAS de réponse attendue : l'application propose une
préparation (étapes, repère de réussite), l'utilisateur réalise l'interaction
dans la vie réelle, puis note ce qui s'est passé. Aucune note n'est comparée,
notée ou interprétée — et le journal reste dans son propre stockage.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ...domain import messages

router = APIRouter(prefix="/api/social", tags=["social"])

#: Longueur maximale d'une note (garde-fou de saisie, pas de jugement de contenu).
LONGUEUR_MAX_NOTE = 2000

#: Ressentis proposés (facultatifs) — vocabulaire neutre, non clinique.
RESSENTIS = ["facile", "moyen", "difficile", "inattendu"]


class NoteMission(BaseModel):
    """Corps de POST /api/social/journal."""

    mission_id: str
    texte: str
    ressenti: str | None = None


def _contenu(request: Request):
    """Chargeur de contenu partagé avec le module entraînement."""
    return request.app.state.gestionnaire_entrainement.contenu


def _journal(request: Request):
    """Stockage du journal (périmètre séparé, injecté au démarrage)."""
    return request.app.state.stockage_journal


@router.get("/missions")
def lister_missions(request: Request) -> dict:
    """GET /api/social/missions — missions de préparation disponibles."""
    return {"missions": _contenu(request).missions(), "ressentis": RESSENTIS}


@router.get("/journal")
def lire_journal(request: Request) -> dict:
    """GET /api/social/journal — notes écrites (les plus récentes en dernier)."""
    return {"entrees": _journal(request).lire_entrees()}


@router.post("/journal", status_code=201)
def ajouter_note(corps: NoteMission, request: Request):
    """POST /api/social/journal — ajoute une note de mission (201)."""
    missions = {mission["id"] for mission in _contenu(request).missions()}
    if corps.mission_id not in missions:
        return JSONResponse(
            status_code=404,
            content={"erreur": "mission_inconnue", "message": messages.texte("social", "mission_inconnue")},
        )
    texte = (corps.texte or "").strip()
    if not texte or len(texte) > LONGUEUR_MAX_NOTE:
        return JSONResponse(
            status_code=422,
            content={
                "erreur": "note_invalide",
                "message": messages.texte("social", "journal_entree_invalide"),
            },
        )
    entree = _journal(request).ajouter(
        corps.mission_id, texte, corps.ressenti, request.app.state.horloge()
    )
    return {"entree": entree}
