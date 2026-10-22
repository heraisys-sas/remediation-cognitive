"""Serveur Playwright dédié : stockage éphémère, aucune donnée personnelle."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import uvicorn

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))


def main():
    from backend.app.main import creer_app

    with TemporaryDirectory(prefix='orthogone-ui-') as dossier:
        app = creer_app(
            racine_donnees=Path(dossier) / 'entrainement',
            dossier_frontend=RACINE / 'frontend',
        )
        uvicorn.run(app, host='127.0.0.1', port=18091, log_level='warning')


if __name__ == '__main__':
    main()
