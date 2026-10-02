"""Tests de l'empan de mots et du rappel libre de séries.

Couvre : ordre significatif pour l'empan de mots (tolérance sur la saisie,
pas sur l'ordre), seuil de réussite du rappel libre, affichage multi-séries,
rappel différé, et non-divulgation de la réponse avant soumission.
"""

import json
import unicodedata

from backend.app.domain.contenu import ChargeurContenu

CONTENU = ChargeurContenu()


def _sans_accents(texte):
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


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


# -- Empan de mots ---------------------------------------------------------------


def test_empan_mots_ordre_et_tolerance(client, tmp_path):
    """L'ordre compte ; les accents et la casse ne comptent pas."""
    _forcer_palier(tmp_path, "memoire", 9)
    payload = _demarrer(client, "memoire")
    item = payload["items"][0]
    assert item["type"] == "empan-mots"
    assert "reponse" not in item
    elements = item["contenu"]["affichage"]["elements"]
    assert len(elements) >= 3
    assert len(set(elements)) == len(elements)      # pas de mot répété
    assert item["contenu"]["affichage"]["duree_par_item_ms"] == 2000
    assert item["contenu"]["affichage"]["pause_item_ms"] == 2000

    # Bon ordre, saisie sans accents et en majuscules : accepté.
    bonne = " ".join(_sans_accents(mot) for mot in elements).upper()
    reponse = _repondre(client, "memoire", payload["session_id"], item["id"], bonne)
    assert reponse.status_code == 200 and reponse.json()["correcte"] is True

    # Même série dans le désordre : refusée (ce n'est pas la même tâche).
    deuxieme = payload["items"][1]
    elements2 = deuxieme["contenu"]["affichage"]["elements"]
    desordre = " ".join(reversed(elements2))
    reponse = _repondre(client, "memoire", payload["session_id"], deuxieme["id"], desordre)
    assert reponse.json()["correcte"] is False


def test_toutes_les_sequences_memoire_suivent_la_cadence_deux_plus_deux():
    """Chiffres, mots et lettres partagent 2 s d'affichage puis 2 s de blanc."""
    items = CONTENU.items("memoire")
    sequences = [
        (item["id"], item["contenu"]["affichage"])
        for item in items
        if item["contenu"].get("affichage", {}).get("mode") == "sequence"
    ]

    assert sequences
    assert {item["type"] for item in items
            if item["contenu"].get("affichage", {}).get("mode") == "sequence"} == {
                "empan", "empan-mots", "n-back",
            }
    for identifiant, affichage in sequences:
        assert affichage["duree_par_item_ms"] == 2000, identifiant
        assert affichage["pause_item_ms"] == 2000, identifiant


def test_empan_mots_reponse_attendue_masquee(client, tmp_path):
    """Le payload de séance ne doit jamais porter la réponse attendue."""
    _forcer_palier(tmp_path, "memoire", 10)
    payload = _demarrer(client, "memoire")

    def contient_cle(objet, cle):
        if isinstance(objet, dict):
            return cle in objet or any(contient_cle(valeur, cle) for valeur in objet.values())
        if isinstance(objet, list):
            return any(contient_cle(valeur, cle) for valeur in objet)
        return False

    assert not contient_cle(payload, "reponse")
    assert all(item["type"] == "empan-mots" for item in payload["items"])


# -- Rappel libre de séries ------------------------------------------------------


def test_rappel_libre_seuil_et_series(client, tmp_path):
    """Le rappel libre est réussi au seuil déclaré — ni tout ou rien, ni fuite."""
    _forcer_palier(tmp_path, "rappel-series", 1)
    payload = _demarrer(client, "rappel-series")
    item = payload["items"][0]
    assert item["type"] == "rappel-libre"
    assert item["contenu"]["affichage"]["mode"] == "series"
    series = item["contenu"]["affichage"]["series"]
    assert series and all(len(serie) >= 3 for serie in series)
    assert item["contenu"]["portee"] == "toutes-series"
    # Un seul mot ne suffit pas au seuil (0,75 pour une série de 4 mots).
    reponse = _repondre(
        client, "rappel-series", payload["session_id"], item["id"], series[0][0]
    )
    assert reponse.json()["correcte"] is False
    assert isinstance(reponse.json()["attendue"], list)

    # Tous les mots sans accents : réussite complète.
    tous = " ".join(_sans_accents(mot) for serie in series for mot in serie)
    reponse = _repondre(
        client, "rappel-series", payload["session_id"], item["id"], tous
    )
    assert reponse.json()["correcte"] is True
    assert len(reponse.json()["detail_rappel"]["retrouves"]) == len(series[0])


def test_rappel_libre_credite_les_cibles_mais_signale_une_intrusion(client, tmp_path):
    """Un mot inventé ne doit plus produire une maîtrise complète malgré les cibles retrouvées."""
    _forcer_palier(tmp_path, "rappel-series", 1)
    payload = _demarrer(client, "rappel-series")
    item = payload["items"][0]
    cibles = " ".join(item["contenu"]["affichage"]["series"][0])
    resultat = _repondre(
        client, "rappel-series", payload["session_id"], item["id"], f"{cibles} ardoise"
    ).json()
    assert resultat["correcte"] is False
    assert len(resultat["detail_rappel"]["retrouves"]) == len(
        item["contenu"]["affichage"]["series"][0]
    )
    assert resultat["detail_rappel"]["intrusions"] == ["ardoise"]


def test_rappel_premiere_serie_distingue_une_confusion_de_serie(client, tmp_path):
    """Un mot présenté hors de la série demandée est une confusion, pas une intrusion."""
    _forcer_palier(tmp_path, "rappel-series", 4)
    payload = _demarrer(client, "rappel-series")
    item = next(i for i in payload["items"] if i["contenu"]["portee"] == "premiere-serie")
    series = item["contenu"]["affichage"]["series"]
    reponse = " ".join([*series[0], series[1][0]])
    resultat = _repondre(
        client, "rappel-series", payload["session_id"], item["id"], reponse
    ).json()
    assert resultat["correcte"] is False
    assert resultat["detail_rappel"]["confusions_series"] == [series[1][0]]
    assert resultat["detail_rappel"]["intrusions"] == []


def test_rappel_differe_declare_et_premiere_serie(client, tmp_path):
    """Le palier différé annonce l'attente et cible la première série."""
    _forcer_palier(tmp_path, "rappel-series", 4)
    payload = _demarrer(client, "rappel-series")
    items = payload["items"]
    assert all(item["contenu"]["delai_s"] == 20 for item in items)
    assert all("20 secondes" in item["contenu"]["consigne"] for item in items)

    premiere = next(item for item in items if item["contenu"]["portee"] == "premiere-serie")
    assert len(premiere["contenu"]["affichage"]["series"]) >= 2
    cibles = _attendue("rappel-series", premiere["id"])
    attendues_affichage = premiere["contenu"]["affichage"]["series"][0]
    assert cibles == attendues_affichage      # la première série, et rien d'autre
    assert "PREMIÈRE série" in premiere["contenu"]["enonce"]
