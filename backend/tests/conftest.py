"""Fixtures des tests backend : application isolée (données dans tmp_path).

Chaque test reçoit une app construite avec une racine de données
temporaire — jamais backend/data/ réel — et un dossier frontend
temporaire (montage statique testé séparément).
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import creer_app


@pytest.fixture()
def app(tmp_path):
    """App avec stockage isolé (tmp_path) et dossier frontend inexistant."""
    return creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "frontend-inexistant",
    )


@pytest.fixture()
def client(app):
    """Client HTTP de test branché sur l'application isolée."""
    return TestClient(app)
