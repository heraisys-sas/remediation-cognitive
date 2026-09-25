"""L'interface doit être servie sans mise en cache.

Un script périmé gardé par le navigateur se mélangeait au contenu courant : des
phrases s'affichaient tronquées (« … et . »). Ces tests verrouillent les en-têtes.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import creer_app

RACINE_PROJET = Path(__file__).resolve().parents[2]


def _client_avec_interface(tmp_path):
    app = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=RACINE_PROJET / "frontend",
    )
    return TestClient(app)


def test_interface_servie_sans_cache(tmp_path):
    client = _client_avec_interface(tmp_path)
    for chemin in ("/ui/src/app.js", "/ui/src/styles.css", "/ui/"):
        reponse = client.get(chemin)
        assert reponse.status_code == 200, chemin
        cache = reponse.headers.get("cache-control", "")
        assert "no-store" in cache and "no-cache" in cache, (chemin, cache)


def test_interface_absente_toleree(tmp_path):
    """Sans dossier frontend, l'application fonctionne quand même (404 sur /ui)."""
    app = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "frontend-inexistant",
    )
    client = TestClient(app)
    assert client.get("/ui/src/app.js").status_code == 404
    assert client.get("/api/sante").status_code in (200, 404)
