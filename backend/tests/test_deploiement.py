import logging

from fastapi.testclient import TestClient

from backend.app.main import creer_app


def test_demarrage_signale_absence_authentification_sans_bloquer(tmp_path, caplog):
    application = creer_app(racine_donnees=tmp_path / 'entrainement')
    with caplog.at_level(logging.WARNING, logger='backend.app.main'):
        with TestClient(application) as client:
            assert client.get('/health').json() == {'status': 'ok'}
    assert 'sans authentification' in caplog.text
    assert 'mono-utilisateur' in caplog.text
    assert 'contrôle d’accès' in caplog.text.replace("'", '’')
    assert 'isolation des données par instance' in caplog.text
