"""Point d'entrée FastAPI.

Trois périmètres d'API strictement isolés (voir docs/30-technique/adr/ADR-002) :
- /api/entrainement : hors périmètre médical, diffusable librement ;
- /api/reeducation  : usage strictement familial — aucune route au sprint 1 ;
- /api/bilan        : données de santé — AUCUN endpoint au sprint 1
  (garde-fou : aucune donnée de bilan ne transite par ce service).

L'interface statique (frontend/) est montée sur /ui quand le dossier
existe — il est créé en parallèle par l'agent interface-web ; le chemin
est résolu depuis l'emplacement de ce fichier, indépendamment du CWD.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.entrainement import router as router_entrainement
from .api.entrainement.service import GestionnaireSessions
from .domain.contenu import RACINE_PROJET
from .storage.store import StockageJSON


def creer_app(
    racine_donnees: Path | None = None,
    dossier_frontend: Path | None = None,
    horloge=None,
) -> FastAPI:
    """Construit l'application FastAPI.

    ``racine_donnees``, ``dossier_frontend`` et ``horloge`` sont
    injectables pour les tests ; par défaut : backend/data/entrainement
    (persistance JSON), <racine du dépôt>/frontend (interface statique)
    et l'horloge UTC réelle.
    """
    application = FastAPI(
        title="Entraînement cognitif — API (Phase 1)",
        version="0.1.0",
        description=(
            "Module Entraînement (hors MDR) : séances adaptatives, correction "
            "serveur, garde-fous de dosage. Périmètres rééducation et bilan : "
            "phases ultérieures, usage familial."
        ),
    )

    @application.get("/health")
    def health() -> dict:
        """Sonde de vie (contrat : {"status": "ok"})."""
        return {"status": "ok"}

    application.state.gestionnaire_entrainement = GestionnaireSessions(
        stockage=StockageJSON(racine=racine_donnees),
        horloge=horloge,
    )
    application.include_router(router_entrainement)

    # Interface statique : montage tolérant — le dossier frontend/ peut
    # ne pas exister encore (livré en parallèle) ; /ui rend alors 404.
    frontend = Path(dossier_frontend) if dossier_frontend else RACINE_PROJET / "frontend"
    if frontend.is_dir():
        application.mount(
            "/ui", StaticFiles(directory=frontend, html=True), name="interface"
        )
    return application


app = creer_app()
