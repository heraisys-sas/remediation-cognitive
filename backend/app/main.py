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
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


class InterfaceStatique(StaticFiles):
    """Sert l'interface **sans mise en cache**.

    Sans ces en-têtes, le navigateur gardait une version périmée du script et la
    mélangeait au contenu courant : des phrases s'affichaient tronquées. En local,
    recharger à chaque fois ne coûte rien.
    """

    async def get_response(self, path, scope):
        reponse = await super().get_response(path, scope)
        if path.startswith("audio/series/") and path.endswith(".m4a") and reponse.status_code < 400:
            # Corpus audio immuable, chemins versionnés et mutualisés entre listes.
            reponse.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        else:
            reponse.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            reponse.headers["Pragma"] = "no-cache"
            reponse.headers["Expires"] = "0"
        return reponse

from .api.entrainement import router as router_entrainement
from .api.entrainement.service import GestionnaireSessions
from .api.memoires_immediates import Blocs, router as router_memoires
from .api.strategies import router as router_strategies
from .api.nback import router as router_nback
from .api.capacites import router as router_capacites
from .api.programme import router as router_programme
from .api.missions import router as router_missions
from .domain.contenu import RACINE_PROJET
from .storage.journal import StockageJournal
from .storage.programme import StockageProgramme
from .storage.store import StockageJSON


@asynccontextmanager
async def avertir_deploiement(application):
    logging.getLogger(__name__).warning(
        "Orthogone sans authentification : instance mono-utilisateur, "
        "à écouter sur 127.0.0.1 ou ::1. Une exposition réseau exige "
        "un contrôle d'accès externe et une isolation des données par instance. "
        "Voir docs/30-technique/deploiement-local.md."
    )
    yield


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
        lifespan=avertir_deploiement,
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
    racine_memoires = Path(racine_donnees).parent / "memoires-immediates" if racine_donnees else RACINE_PROJET / "backend" / "data" / "memoires-immediates"
    application.state.blocs_memoires = Blocs(racine_memoires)
    application.include_router(router_memoires)
    racine_strategies = Path(racine_donnees).parent / "strategies" if racine_donnees else RACINE_PROJET / "backend" / "data" / "strategies"
    application.state.blocs_strategies = Blocs(racine_strategies)
    application.include_router(router_strategies)
    racine_nback = Path(racine_donnees).parent / "nback" if racine_donnees else RACINE_PROJET / "backend" / "data" / "nback"
    application.state.blocs_nback = Blocs(racine_nback)
    application.include_router(router_nback)

    # Carnet des missions hors écran (thème social) : stockage SÉPARÉ des
    # données d'entraînement (il contient des éléments personnels) — même
    # horloge que les séances, pour dater les notes de façon cohérente.
    racine_journal = Path(racine_donnees).parent / "journal" if racine_donnees else None
    application.state.stockage_journal = StockageJournal(racine=racine_journal)
    application.state.horloge = application.state.gestionnaire_entrainement.horloge
    application.include_router(router_missions)

    # Programme d'entraînement : état local minimal (date de début), périmètre
    # entraînement — aucune donnée de santé, aucun suivi de performance.
    racine_programme = Path(racine_donnees).parent / "programme" if racine_donnees else None
    application.state.stockage_programme = StockageProgramme(racine=racine_programme)
    application.include_router(router_programme)

    # Capacités du poste (similarité de textes, synthèse vocale) — tout reste local.
    application.include_router(router_capacites)

    # Interface statique : montage tolérant — le dossier frontend/ peut
    # ne pas exister encore (livré en parallèle) ; /ui rend alors 404.
    frontend = Path(dossier_frontend) if dossier_frontend else RACINE_PROJET / "frontend"
    if frontend.is_dir():
        application.mount(
            "/ui", InterfaceStatique(directory=frontend, html=True), name="interface"
        )
    return application


app = creer_app()
