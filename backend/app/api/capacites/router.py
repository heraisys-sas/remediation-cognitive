"""Routes des capacités du poste (similarité, synthèse vocale).

- `GET  /api/capacites`            → ce que ce poste sait faire, et par quel moyen ;
- `POST /api/capacites/similarite` → proximité de deux textes (0 à 1) ;
- `POST /api/capacites/synthese`   → synthèse vocale par la voix du système (WAV).

Tout est **local** : la reconnaissance vocale, elle, est assurée côté client
(navigateur ou OS de la tablette) — le serveur ne capte pas le micro.
"""

from __future__ import annotations

import base64
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, constr

from ...domain import capacites as cap
from ...domain import voix_locales
from ...domain import accompagnement_local

router = APIRouter(prefix="/api/capacites", tags=["capacites"])


class DemandeSimilarite(BaseModel):
    """Corps de POST /api/capacites/similarite."""

    texte: str
    cibles: list[str]


class DemandeSynthese(BaseModel):
    """Corps de POST /api/capacites/synthese."""

    texte: str
    voix: str | None = None


class DemandeAccompagnement(BaseModel):
    """Seulement le texte présenté et la tentative, jamais un corrigé."""

    texte: constr(strip_whitespace=True, min_length=1, max_length=6000)
    reformulation: constr(strip_whitespace=True, min_length=1, max_length=2000)
    categories_deja_vues: list[Literal["objectif", "contrainte", "verification"]] = Field(default_factory=list, max_length=2)


@router.get("/accompagnement")
def etat_accompagnement() -> dict:
    return accompagnement_local.etat()


@router.post("/accompagnement")
async def accompagner(corps: DemandeAccompagnement) -> dict:
    return await accompagnement_local.accompagner(corps.texte, corps.reformulation, corps.categories_deja_vues)


@router.get("/voix")
def liste_voix() -> dict:
    return {"voix": voix_locales.voix_disponibles()}


@router.get("")
def etat() -> dict:
    """GET /api/capacites — capacités disponibles sur ce poste."""
    return cap.capacites()


@router.post("/similarite")
def similarite(corps: DemandeSimilarite) -> dict:
    """Proximité du texte avec chaque cible (fournisseur courant)."""
    scores = [
        {"cible": cible, "score": cap.similarite(corps.texte, cible)}
        for cible in corps.cibles
    ]
    meilleur = max(scores, key=lambda s: s["score"]) if scores else None
    return {
        "fournisseur": cap.fournisseur_similarite(),
        "scores": scores,
        "proche": bool(meilleur and meilleur["score"] >= cap.SEUIL_SIMILARITE),
    }


@router.post("/synthese")
def synthese(corps: DemandeSynthese):
    """Synthèse du texte par la voix du système → WAV en base64."""
    resultat = (voix_locales.synthetiser(corps.texte, corps.voix)
                if corps.voix else cap.synthese(corps.texte))
    if resultat is None:
        return JSONResponse(
            status_code=503,
            content={"erreur": "synthese_indisponible",
                     "message": "La voix du système n'est pas disponible sur ce poste."},
        )
    audio, mime = resultat
    return {"mime": mime, "audio_base64": base64.b64encode(audio).decode("ascii")}
