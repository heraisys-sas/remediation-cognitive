"""Tests du thème « Retrouver le mot » (evocation) et des missions dans la vraie vie.

Couvre : correction tolérante (accents, casse, espaces), réponse choisie parmi
des propositions, indices progressifs, essai « assisté » (réponse affichée,
aucune erreur commise mais FSRS en échec), validation du champ
``indice_utilise``, et le carnet de missions hors écran (stockage séparé).
"""

import json
import unicodedata
from pathlib import Path

from backend.app.domain.contenu import ChargeurContenu

CONTENU = ChargeurContenu()


def _sans_accents(texte):
    """Retire les accents — pour vérifier la tolérance de saisie."""
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def _forcer_palier(tmp_path, theme, palier):
    """Écrit l'état de maîtrise pour démarrer une séance à un palier donné."""
    dossier = tmp_path / "data" / theme
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "maitrise.json").write_text(
        json.dumps({"palier_courant": palier, "historique": []}), encoding="utf-8"
    )


def _demarrer(client, theme):
    reponse = client.post(f"/api/entrainement/{theme}/sessions")
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def _repondre(client, theme, session_id, item_id, reponse, indice_utilise=None, temps_ms=900):
    corps = {"item_id": item_id, "reponse": reponse, "temps_ms": temps_ms}
    if indice_utilise is not None:
        corps["indice_utilise"] = indice_utilise
    return client.post(
        f"/api/entrainement/{theme}/sessions/{session_id}/reponses", json=corps
    )


def _attendue(theme, item_id):
    return CONTENU.item(theme, item_id)["reponse"]["valeur"]


# -- Thème evocation -----------------------------------------------------------


def test_evocation_reconnaissance_options_et_tolerance(client):
    """Palier 1 : propositions affichées, réponse tolérante aux accents."""
    payload = _demarrer(client, "evocation")
    item = payload["items"][0]
    assert item["type"] == "reconnaissance"
    assert "reponse" not in item
    options = item["contenu"]["options"]
    assert len(options) == 3 and len(set(options)) == 3
    attendue = _attendue("evocation", item["id"])
    assert attendue in options

    # Réponse juste écrite en majuscules et sans accent : acceptée.
    saisie = _sans_accents(attendue).upper()
    reponse = _repondre(client, "evocation", payload["session_id"], item["id"], saisie)
    assert reponse.status_code == 200
    assert reponse.json()["correcte"] is True

    # Une autre proposition (donc fausse) est refusée.
    autre = payload["items"][1]
    mauvaise = next(
        option
        for option in autre["contenu"]["options"]
        if option != _attendue("evocation", autre["id"])
    )
    reponse = _repondre(client, "evocation", payload["session_id"], autre["id"], mauvaise)
    assert reponse.json()["correcte"] is False


def test_evocation_indices_jamais_la_reponse_et_aide_enregistree(client, tmp_path):
    """Palier 2 : indices hiérarchisés, aide mesurée, essai assisté sans erreur."""
    _forcer_palier(tmp_path, "evocation", 2)
    payload = _demarrer(client, "evocation")
    items = payload["items"]
    assert items and all(item["type"] == "rappel-indice" for item in items)

    premier, deuxieme, troisieme = items[0], items[1], items[2]
    for item in (premier, deuxieme, troisieme):
        indices = item["contenu"]["indices"]
        assert len(indices) >= 2
        assert all({"type", "texte"} <= set(indice) for indice in indices)
        # Garde-fou : aucun indice ne doit contenir la réponse.
        attendue = _sans_accents(_attendue("evocation", item["id"])).casefold()
        assert all(
            attendue not in _sans_accents(indice["texte"]).casefold() for indice in indices
        )

    # 1) retrouvé sans aide ; 2) retrouvé après un indice ; 3) réponse affichée.
    reponse = _repondre(
        client, "evocation", payload["session_id"], premier["id"],
        _attendue("evocation", premier["id"]), indice_utilise=0,
    )
    assert reponse.json() == {
        "correcte": True,
        "assistee": False,
        "attendue": _attendue("evocation", premier["id"]),
        "feedback": reponse.json()["feedback"],
    }

    reponse = _repondre(
        client, "evocation", payload["session_id"], deuxieme["id"],
        _attendue("evocation", deuxieme["id"]), indice_utilise=1,
    )
    assert reponse.json()["correcte"] is True

    nb_indices = len(troisieme["contenu"]["indices"])
    reponse = _repondre(
        client, "evocation", payload["session_id"], troisieme["id"],
        _attendue("evocation", troisieme["id"]), indice_utilise=nb_indices + 1,
    )
    corps = reponse.json()
    assert corps["assistee"] is True and corps["correcte"] is False
    assert corps["attendue"] == _attendue("evocation", troisieme["id"])

    fin = client.post(
        f"/api/entrainement/evocation/sessions/{payload['session_id']}/fin"
    ).json()
    assert fin["resume"]["items"] == 3
    assert fin["resume"]["correctes"] == 2       # l'essai assisté ne compte pas réussi
    assert fin["resume"]["assistees"] == 1
    assert fin["resume"]["sans_aide"] == 1       # seul le premier a été retrouvé seul


def test_evocation_indice_utilise_hors_bornes(client, tmp_path):
    """Un nombre d'indices incohérent est refusé (422)."""
    _forcer_palier(tmp_path, "evocation", 2)
    payload = _demarrer(client, "evocation")
    item = payload["items"][0]
    reponse = _repondre(
        client, "evocation", payload["session_id"], item["id"],
        _attendue("evocation", item["id"]), indice_utilise=99,
    )
    assert reponse.status_code == 422
    assert reponse.json()["erreur"] == "reponse_invalide"





def test_missions_listees(client):
    reponse = client.get("/api/missions")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert len(corps["missions"]) == 8
    assert corps["ressentis"]
    for mission in corps["missions"]:
        assert {"id", "titre", "niveau", "etapes", "pourquoi", "repere"} <= set(mission)
        assert mission["etapes"]
    # Aucune réponse attendue : ce sont des missions réelles, pas des items notés.
    assert all("reponse" not in mission for mission in corps["missions"])


def test_journal_missions_cycle_complet(client, tmp_path):
    """Le carnet vit dans son propre stockage, séparé de l'entraînement."""
    assert client.get("/api/missions/journal").json() == {"entrees": []}

    creation = client.post(
        "/api/missions/journal",
        json={"mission_id": "ms-01", "texte": "J'ai dit bonjour au voisin.", "ressenti": "facile"},
    )
    assert creation.status_code == 201
    entree = creation.json()["entree"]
    assert entree["mission_id"] == "ms-01" and entree["texte"] and entree["date"]

    entrees = client.get("/api/missions/journal").json()["entrees"]
    assert len(entrees) == 1 and entrees[0]["id"] == entree["id"]

    # Stockage séparé : journal/ n'est PAS sous le dossier de l'entraînement.
    assert (tmp_path / "journal" / "journal.json").is_file()
    assert not (tmp_path / "data" / "journal").exists()

    # Mission inconnue → 404 ; note vide → 422.
    assert client.post(
        "/api/missions/journal", json={"mission_id": "inconnue", "texte": "note"}
    ).status_code == 404
    assert client.post(
        "/api/missions/journal", json={"mission_id": "ms-01", "texte": "   "}
    ).status_code == 422
