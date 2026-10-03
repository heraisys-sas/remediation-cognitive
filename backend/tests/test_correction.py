"""Tests unitaires : correction serveur (domain.correction) et sélection
des items (domain.selection)."""

from datetime import datetime, timedelta, timezone

from backend.app.domain.correction import corriger
from backend.app.domain.selection import selectionner_items

T0 = datetime(2026, 9, 3, 12, 0, 0, tzinfo=timezone.utc)
T0_MINUS_1H = datetime(2026, 9, 3, 11, 0, 0, tzinfo=timezone.utc)
T0_MINUS_3J = datetime(2026, 8, 31, 12, 0, 0, tzinfo=timezone.utc)


def _item(theme: str, type_item: str, valeur, palier: int = 1, item_id: str = "x") -> dict:
    """Fabrique un item minimal conforme au schéma pour les tests."""
    return {
        "id": item_id,
        "type": type_item,
        "theme": theme,
        "palier": palier,
        "contenu": {"enonce": "?", "aide": None},
        "reponse": {"valeur": valeur},
    }


# -- correction : calcul mental (numérique) ------------------------------------


def test_calcul_mental_accepte_nombre_ou_chaine():
    item = _item("calcul-mental", "production", 56)
    assert corriger("calcul-mental", item, 56) is True
    assert corriger("calcul-mental", item, "56") is True
    assert corriger("calcul-mental", item, " 56 ") is True


def test_calcul_mental_rejette_mauvaise_valeur_et_non_numerique():
    item = _item("calcul-mental", "production", 56)
    assert corriger("calcul-mental", item, 57) is False
    assert corriger("calcul-mental", item, "abc") is False
    assert corriger("calcul-mental", item, None) is False


def test_calcul_mental_decimal_virgule_francaise():
    item = _item("calcul-mental", "production", 56.5)
    assert corriger("calcul-mental", item, "56,5") is True


# -- correction : anglais (texte insensible à la casse, trimmé) ----------------


def test_anglais_insensible_casse_et_espaces():
    item = _item("anglais", "production", "went")
    assert corriger("anglais", item, "WENT") is True
    assert corriger("anglais", item, "  went  ") is True
    assert corriger("anglais", item, "Went") is True


def test_anglais_rejette_mauvais_verbe():
    item = _item("anglais", "production", "went")
    assert corriger("anglais", item, "gone") is False


# -- correction : python (chaîne exacte trimmée, production et prédiction) -----


def test_python_production_exacte_trimmee():
    item = _item("python", "production", "len")
    assert corriger("python", item, " len ") is True
    assert corriger("python", item, "len") is True
    assert corriger("python", item, "LEN") is False
    assert corriger("python", item, "lenn") is False


def test_python_prediction_sortie_chaine_exacte():
    item = _item("python", "prediction-sortie", 10, palier=2)
    assert corriger("python", item, "10") is True
    assert corriger("python", item, 10) is True
    # Exact : "10.0" n'est pas la chaîne attendue.
    assert corriger("python", item, "10.0") is False
    item_zero = _item("python", "prediction-sortie", 0, palier=2)
    assert corriger("python", item_zero, "0") is True
    item_texte = _item("python", "prediction-sortie", "abc", palier=2)
    assert corriger("python", item_texte, " abc ") is True
    assert corriger("python", item_texte, "ABC") is False


# -- sélection des items --------------------------------------------------------


def _items_paliers() -> list[dict]:
    return [
        _item("calcul-mental", "production", 4, palier=1, item_id=f"p1-{n}") for n in range(14)
    ] + [
        _item("calcul-mental", "production", 25, palier=2, item_id="p2-0")
    ]


def test_selection_nouveaux_dabord_quotas_et_palier():
    items = _items_paliers()
    selection = selectionner_items(items, {}, palier_courant=1, maintenant=T0, max_items=12)
    assert [it["id"] for it in selection] == [f"p1-{n}" for n in range(12)]
    # Aucun item du palier 2 ne fuit dans la sélection.
    assert all(it["palier"] == 1 for it in selection)


def test_selection_items_dus_en_premier():
    from engine.srs.fsrs import CarteFSRS, planifier

    items = _items_paliers()
    # Une seule carte, revue à l'instant T0 → échéance future → non due.
    revue, _ = planifier(CarteFSRS("p1-3"), 3, T0)
    cartes = {"p1-3": revue}
    selection = selectionner_items(items, cartes, palier_courant=1, maintenant=T0, max_items=12)
    # La carte non due est écartée ; les nouveaux remplissent le quota.
    assert "p1-3" not in [it["id"] for it in selection]
    assert len(selection) == 12


def test_selection_items_dus_puis_nouveaux():
    from engine.srs.fsrs import CarteFSRS, planifier

    items = _items_paliers()
    # Carte revue il y a trois jours avec échec : échéance dépassée → servie en premier.
    pas_due_recemment, _ = planifier(CarteFSRS("p1-7"), 1, T0_MINUS_3J)
    cartes = {"p1-7": pas_due_recemment}
    selection = selectionner_items(items, cartes, palier_courant=1, maintenant=T0, max_items=12)
    assert selection[0]["id"] == "p1-7"
    assert len(selection) == 12


def test_selection_aucun_item_disponible():
    from engine.srs.fsrs import CarteFSRS, planifier

    items = _items_paliers()
    cartes = {}
    for item in items:
        if item["palier"] == 1:
            cartes[item["id"]], _ = planifier(CarteFSRS(item["id"]), 3, T0)
    selection = selectionner_items(items, cartes, palier_courant=1, maintenant=T0, max_items=12)
    assert selection == []


def test_selection_pratique_anticipee_prend_les_echeances_les_plus_proches():
    from engine.srs.fsrs import CarteFSRS, planifier

    items = _items_paliers()
    cartes = {}
    for rang, item in enumerate(items):
        if item["palier"] == 1:
            # Horaires de revue inversés : les six dernières cartes ont
            # l'échéance la plus proche, sans toucher à l'état interne FSRS.
            revue = T0 + timedelta(minutes=13 - rang)
            cartes[item["id"]], _ = planifier(CarteFSRS(item["id"]), 3, revue)
    selection = selectionner_items(
        items, cartes, palier_courant=1, maintenant=T0, max_items=6,
        inclure_non_dus=True,
    )
    assert [item["id"] for item in selection] == [f"p1-{n}" for n in range(13, 7, -1)]
