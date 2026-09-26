"""Montants et quantités : la dictée écrit autrement que la réponse attendue.

Cas signalé : « 180 € » refusé pour un item attendant « 180 euros » (thème méthodes),
et la dictée peut aussi rendre « cent quatre-vingts euros ». Un montant se vérifie par
une **équivalence déterministe** (symbole, abréviation, nombre en toutes lettres) —
pas par un moteur statistique, qui n'aurait ici aucune raison d'être.
"""

from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.correction import _clef_reponse, corriger

CONTENU = ChargeurContenu()

EQUIVALENCES = [
    ("180 €", "180 euros"),
    ("180€", "180 euros"),
    ("180 eur", "180 euros"),
    ("cent quatre-vingts euros", "180 euros"),
    ("quatre-vingt-dix euros", "90 euros"),
    ("quatre-vingt-un euros", "81 euros"),
    ("12,50 €", "12,50 euros"),
    ("deux litres", "2 litres"),
    ("deux jours", "2 jours"),
]

DIFFERENCES = [
    ("280 €", "180 euros"),
    ("180 €", "1800 euros"),
    ("trois jours", "2 jours"),
]


def test_montants_equivalents():
    for reponse, attendue in EQUIVALENCES:
        assert _clef_reponse(reponse) == _clef_reponse(attendue), (reponse, attendue)


def test_montants_differents_refuses():
    for reponse, attendue in DIFFERENCES:
        assert _clef_reponse(reponse) != _clef_reponse(attendue), (reponse, attendue)


def test_les_heures_ne_sont_pas_perturbees():
    """Les montants et les heures cohabitent : la normalisation des unes ne casse pas l'autre."""
    assert _clef_reponse("quinze heures") == _clef_reponse("15 h")
    assert _clef_reponse("3 heures et demie") == _clef_reponse("3 h 30")


def test_devise_au_methodes():
    """Le cas signalé : le montant du devis, écrit avec le symbole."""
    item = CONTENU.item("methodes", "mt-1-pqrst-06")
    assert item["reponse"]["valeur"] == "180 euros"
    assert corriger("methodes", item, "180 euros") is True
    assert corriger("methodes", item, "180 €") is True
    assert corriger("methodes", item, "cent quatre-vingts euros") is True
    assert corriger("methodes", item, "280 euros") is False
    assert corriger("methodes", item, "80 €") is False
