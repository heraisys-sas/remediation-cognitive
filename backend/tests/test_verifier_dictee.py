"""La détection vocale ne compte jamais comme une tentative de réponse."""
import pickle

import pytest


def _session(client, theme="evocation", palier=2):
    response = client.post(f"/api/entrainement/{theme}/sessions", json={"palier": palier})
    assert response.status_code == 201, response.text
    data = response.json()
    return data, f"/api/entrainement/{theme}/sessions/{data['session_id']}"


def _fichiers(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_detection_sans_mutation_puis_validation_normale(client, app, tmp_path, monkeypatch):
    from backend.app.domain import capacites
    monkeypatch.setattr(capacites, "proche", lambda *args: pytest.fail("Pas de similarité sémantique"))
    data, url = _session(client)
    manager = app.state.gestionnaire_entrainement
    session = manager._sessions[data["session_id"]]
    item = session.items_par_id[data["items"][0]["id"]]
    mot = item["reponse"]["valeur"]
    avant = pickle.dumps(session)
    fichiers = _fichiers(tmp_path / "data")
    for texte, acceptee in [
        ("", False), ("zzzzzzzz", False), (f"pas {mot}", False),
        (f"ce n’est pas une {mot}", False),
        (f"c'est un {mot}", True), (mot, True),
    ]:
        response = client.post(url + "/verifier-dictee", json={"item_id": item["id"], "transcription": texte})
        assert response.status_code == 200, response.text
        assert response.json() == {"acceptee": acceptee}
        assert pickle.dumps(session) == avant
        assert _fichiers(tmp_path / "data") == fichiers
    response = client.post(url + "/reponses", json={"item_id": item["id"], "reponse": mot, "temps_ms": 1500})
    assert response.status_code == 200
    assert response.json()["correcte"] is True
    assert session.essais[item["id"]] == 1
    assert session.reponses == {item["id"]: True}


def test_detection_session_item_et_limites(client):
    data, url = _session(client)
    corps = {"item_id": data["items"][0]["id"], "transcription": "gare"}
    assert client.post(url.replace("evocation", "memoire") + "/verifier-dictee", json=corps).status_code == 404
    assert client.post("/api/entrainement/evocation/sessions/inconnue/verifier-dictee", json=corps).status_code == 404
    assert client.post(url + "/verifier-dictee", json={**corps, "item_id": "absent"}).status_code == 404
    assert client.post(url + "/verifier-dictee", json={**corps, "transcription": "a" * 501}).status_code == 422
    client.post(url + "/fin")
    assert client.post(url + "/verifier-dictee", json=corps).status_code == 409


@pytest.mark.parametrize("theme,palier", [("evocation", 1), ("evocation", 7), ("calcul-mental", 5)])
def test_detection_reservee_au_rappel_lexical(client, theme, palier):
    data, url = _session(client, theme, palier)
    response = client.post(url + "/verifier-dictee", json={"item_id": data["items"][0]["id"], "transcription": "gare"})
    assert response.status_code == 422


def test_detection_variantes_articles_et_mots_entiers(client, app):
    data, url = _session(client, palier=2)
    session = app.state.gestionnaire_entrainement._sessions[data["session_id"]]
    item = session.items_par_id[data["items"][0]["id"]]
    item["reponse"] = {"valeur": "vélo", "variantes": ["bicyclette"]}
    variante = "bicyclette"
    response = client.post(url + "/verifier-dictee", json={"item_id": item["id"], "transcription": variante})
    assert response.json() == {"acceptee": True}
    # Cas stable indépendant du tirage de contenu : gare n'est pas garde.
    item["reponse"] = {"valeur": "gare"}
    for texte, acceptee in [("la gare", True), ("on attend devant la gare", True), ("garde", False), ("non gare", False)]:
        response = client.post(url + "/verifier-dictee", json={"item_id": item["id"], "transcription": texte})
        assert response.json() == {"acceptee": acceptee}
