"""Routes HTTP du module entraînement — mapping pur du contrat d'API.

Source de vérité : docs/30-technique/api-contract.md. Toute la logique
vit dans service.py ; les libellés visibles viennent du vocabulaire
centralisé (domain.messages) — aucune chaîne utilisateur construite ici,
seuls les codes machine du contrat (``erreur``) sont fixés par celui-ci.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...domain import messages
from .service import (
    GestionnaireSessions,
    ItemHorsSeance,
    LimiteSessionsAtteinte,
    PalierInconnu,
    ParcoursInconnu,
    ReponseInvalide,
    SessionDejaTerminee,
    SessionInconnue,
    ThemeInconnu,
)

router = APIRouter(prefix="/api/entrainement", tags=["entrainement"])


class DemarrageOptionnel(BaseModel):
    """Corps facultatif de POST …/sessions.

    - ``palier`` : essai sur un palier précis (la progression ne peut pas reculer) ;
    - ``sans_limite_sessions`` : dérogation explicite au plafond de séances,
      demandée depuis l'accueil — accordée par le serveur pour tous les thèmes
      (fenêtre du jour ou de la semaine selon la catégorie — ADR-021).
    """

    palier: int | None = Field(default=None, ge=1)
    parcours: str | None = Field(default=None, pattern=r"^[a-z0-9-]+$")
    sans_limite_sessions: bool = False


class ReponseUtilisateur(BaseModel):
    """Corps de POST …/reponses (contrat : reponse str|number|objet, temps_ms int).

    Un **objet** est attendu pour les séquences guidées (« PQRST mis en œuvre ») : ses clés
    sont les numéros d'étape.

    ``indice_utilise`` (optionnel) : nombre d'indices consultés ; la valeur
    ``nb_indices + 1`` signale un essai clos par affichage de la réponse.
    """

    item_id: str
    reponse: str | int | float | dict
    temps_ms: int
    indice_utilise: int | None = None


class TranscriptionAVerifier(BaseModel):
    """Aperçu de dictée : aucune réponse n'est encore enregistrée."""

    item_id: str
    transcription: str = Field(max_length=500)


def _gestionnaire(request: Request) -> GestionnaireSessions:
    """Récupère le gestionnaire métier attaché à l'application."""
    return request.app.state.gestionnaire_entrainement


def _erreur(statut: int, code: str) -> JSONResponse:
    """Réponse d'erreur : code machine du contrat + message du vocabulaire."""
    return JSONResponse(
        status_code=statut,
        content={
            "erreur": code,
            "message": messages.texte("entrainement", f"erreur_{code}"),
        },
    )


@router.get("/themes")
def lister_themes(request: Request) -> dict:
    """GET /api/entrainement/themes — thèmes disponibles."""
    return {"themes": _gestionnaire(request).contenu.themes()}


@router.post("/{theme}/sessions", status_code=201)
def demarrer_session(theme: str, request: Request, corps: DemarrageOptionnel | None = None):
    """POST /api/entrainement/{theme}/sessions — 201 (items sans réponse) ou 429.

    Corps facultatif ``{"palier": N, "sans_limite_sessions": bool}`` : essai sur un
    palier précis, sans effet sur la progression (elle ne peut pas reculer) ; et
    dérogation explicite au plafond de la fenêtre du thème — tous les thèmes (ADR-021).
    """
    try:
        return _gestionnaire(request).demarrer(
            theme,
            palier_force=corps.palier if corps else None,
            sans_limite_sessions=corps.sans_limite_sessions if corps else False,
            parcours=corps.parcours if corps else None,
        )
    except PalierInconnu:
        return _erreur(422, "palier_inconnu")
    except ParcoursInconnu:
        return _erreur(422, "parcours_inconnu")
    except ThemeInconnu:
        return _erreur(404, "theme_inconnu")
    except ReponseInvalide:
        return _erreur(422, "reponse_invalide")
    except LimiteSessionsAtteinte:
        # Corps exact du contrat : refus du plafond de la fenêtre — une dérogation
        # explicite (« sans_limite_sessions », ADR-021) peut le lever côté service.
        return JSONResponse(
            status_code=429,
            content={
                "erreur": "limite_sessions_atteinte",
                "sessions_restantes_aujourdhui": 0,
            },
        )


@router.post("/{theme}/sessions/{session_id}/reponses")
def envoyer_reponse(theme: str, session_id: str, corps: ReponseUtilisateur, request: Request):
    """POST …/reponses — correction serveur immédiate (feedback guidé)."""
    try:
        return _gestionnaire(request).repondre(
            theme,
            session_id,
            corps.item_id,
            corps.reponse,
            corps.temps_ms,
            corps.indice_utilise,
        )
    except SessionInconnue:
        return _erreur(404, "session_inconnue")
    except SessionDejaTerminee:
        return _erreur(409, "session_terminee")
    except ItemHorsSeance:
        return _erreur(404, "item_hors_seance")
    except ReponseInvalide:
        return _erreur(422, "reponse_invalide")


@router.post("/{theme}/sessions/{session_id}/verifier-dictee")
def verifier_dictee(theme: str, session_id: str, corps: TranscriptionAVerifier,
                    request: Request):
    """Détecte un mot attendu sans comptabiliser les transcriptions partielles."""
    try:
        return _gestionnaire(request).verifier_dictee(
            theme, session_id, corps.item_id, corps.transcription,
        )
    except SessionInconnue:
        return _erreur(404, "session_inconnue")
    except SessionDejaTerminee:
        return _erreur(409, "session_terminee")
    except ItemHorsSeance:
        return _erreur(404, "item_hors_seance")
    except ReponseInvalide:
        return _erreur(422, "reponse_invalide")


@router.post("/{theme}/sessions/{session_id}/fin")
def terminer_session(theme: str, session_id: str, request: Request):
    """POST …/fin — résumé, proposition d'arrêt éventuelle, persistance."""
    try:
        return _gestionnaire(request).terminer(theme, session_id)
    except SessionInconnue:
        return _erreur(404, "session_inconnue")
    except SessionDejaTerminee:
        return _erreur(409, "session_terminee")
