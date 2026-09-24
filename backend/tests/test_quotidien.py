"""Tests du thème « Au quotidien » — remédiation fonctionnelle.

Vérifie que les exercices travaillent la fonction dans une situation de vie,
avec correction adaptée : rappel tolérant d'un fait d'un message, choix de la
prochaine étape, estimation de durée acceptée dans une fourchette.
"""

import json

from backend.app.domain.contenu import ChargeurContenu

CONTENU = ChargeurContenu()


def _forcer_palier(tmp_path, theme, palier):
    dossier = tmp_path / "data" / theme
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "maitrise.json").write_text(
        json.dumps({"palier_courant": palier, "historique": []}), encoding="utf-8"
    )


def _demarrer(client, theme):
    reponse = client.post(f"/api/entrainement/{theme}/sessions")
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def _repondre(client, theme, session_id, item_id, reponse, temps_ms=1200):
    return client.post(
        f"/api/entrainement/{theme}/sessions/{session_id}/reponses",
        json={"item_id": item_id, "reponse": reponse, "temps_ms": temps_ms},
    )


def _attendue(theme, item_id):
    return CONTENU.item(theme, item_id)["reponse"]["valeur"]


def test_prise_message_tolerances_formats(client):
    """Le fond compte, pas la forme : « deux » = « 2 », « 14 h 30 » = « 14h30 » = « 14:30 »."""
    payload = _demarrer(client, "quotidien")
    items = {item["id"]: item for item in payload["items"]}

    # « Combien de bouteilles ? » → « deux » : le chiffre 2 est accepté.
    deux = items["qo-1-message-02"]
    assert _repondre(client, "quotidien", payload["session_id"], deux["id"], "2").json()["correcte"] is True
    assert _repondre(client, "quotidien", payload["session_id"], deux["id"], "deux").json()["correcte"] is True

    # « À quelle heure ? » → « 14 h 30 » : variantes d'écriture acceptées.
    heure = items["qo-1-message-01"]
    for variante in ("14h30", "14:30", "14 h 30"):
        assert _repondre(client, "quotidien", payload["session_id"], heure["id"], variante).json()["correcte"] is True


def test_prise_message_memoire_de_travail(client):
    """Le message est affiché, le fait demandé en fait partie, et se rappelle."""
    payload = _demarrer(client, "quotidien")
    item = payload["items"][0]
    assert item["type"] == "prise-message"
    assert item["contenu"]["affichage"]["mode"] == "liste"
    assert "reponse" not in item                       # jamais de fuite
    attendue = _attendue("quotidien", item["id"])

    reponse = _repondre(client, "quotidien", payload["session_id"], item["id"], attendue)
    assert reponse.status_code == 200 and reponse.json()["correcte"] is True

    # Un fait erroné est refusé.
    autre = payload["items"][1]
    reponse = _repondre(
        client, "quotidien", payload["session_id"], autre["id"], "réponse absente du message"
    )
    assert reponse.json()["correcte"] is False


def test_etape_suivante_planification(client, tmp_path):
    """La prochaine étape est choisie parmi des propositions."""
    _forcer_palier(tmp_path, "quotidien", 2)
    payload = _demarrer(client, "quotidien")
    item = payload["items"][0]
    assert item["type"] == "etape-suivante"
    options = item["contenu"]["options"]
    assert len(options) == 3 and _attendue("quotidien", item["id"]) in options

    reponse = _repondre(
        client, "quotidien", payload["session_id"], item["id"], _attendue("quotidien", item["id"])
    )
    assert reponse.json()["correcte"] is True

    mauvaise = next(o for o in options if o != _attendue("quotidien", item["id"]))
    assert _repondre(
        client, "quotidien", payload["session_id"], item["id"], mauvaise
    ).json()["correcte"] is False


def test_familles_choix_initiation_intention_solution(client, tmp_path):
    """Paliers 4 à 6 : initiation, plan « si-alors », résolution de problème."""
    for palier, type_attendu in ((4, "par-ou-commencer"), (5, "si-alors"), (6, "meilleure-solution")):
        _forcer_palier(tmp_path, "quotidien", palier)
        payload = _demarrer(client, "quotidien")
        item = payload["items"][0]
        assert item["type"] == type_attendu
        assert len(item["contenu"]["options"]) == 3
        bonne = _attendue("quotidien", item["id"])
        assert bonne in item["contenu"]["options"]
        assert _repondre(
            client, "quotidien", payload["session_id"], item["id"], bonne
        ).json()["correcte"] is True


def test_estimation_temps_fourchette(client, tmp_path):
    """Une estimation est correcte dans sa fourchette, pas en dehors."""
    _forcer_palier(tmp_path, "quotidien", 3)
    payload = _demarrer(client, "quotidien")
    item = payload["items"][0]
    assert item["type"] == "estimation-temps"
    intervalle = CONTENU.item("quotidien", item["id"])["reponse"]["intervalle"]
    dedans = (intervalle[0] + intervalle[1]) / 2
    dehors = intervalle[1] + 100

    assert _repondre(
        client, "quotidien", payload["session_id"], item["id"], dedans
    ).json()["correcte"] is True
    assert _repondre(
        client, "quotidien", payload["session_id"], item["id"], dehors
    ).json()["correcte"] is False
