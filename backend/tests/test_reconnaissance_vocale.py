"""Reconnaissance des réponses dictées : du sens partout, sans excès de tolérance.

Audit de **tous** les champs à réponse libre — ceux où la dictée est proposée. Pour chacun,
la forme dictée doit passer, et une réponse *fausse* doit rester refusée. Le second point
compte le plus : accepter une mauvaise réponse est plus grave que refuser une bonne réponse
écrite autrement (ADR-008).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from backend.app.domain.contenu import ChargeurContenu  # noqa: E402
from backend.app.domain.correction import corriger  # noqa: E402

CONTENU = ChargeurContenu()


def _corrige(theme, item_id, reponse):
    item = CONTENU.item(theme, item_id)
    assert item is not None, f"item {item_id} absent du contenu"
    return corriger(theme, item, reponse)


# --- Formes dictées acceptées (la forme change, pas le contenu) ---------------

ACCEPTEES = [
    # Valeurs numériques : chiffres, mots, symboles d'unité.
    ("calcul-mental", "cm3-1-01", "3"),                 # attendu 3
    ("calcul-mental", "cm3-1-01", "trois"),
    ("concentration", "co-1-chaine-01", "quarante-six"),  # attendu 46
    ("concentration", "co-1-chaine-01", "46"),
    # Séquences de chiffres : espacées, collées, ou dictées en mots.
    ("memoire", "me-1-empan-01", "549"),
    ("memoire", "me-1-empan-01", "5 4 9"),
    ("memoire", "me-1-empan-01", "cinq quatre neuf"),
    # Nombre associé, dicté en mots.
    ("memoire", "me-3-paires-01", "soixante-treize"),   # attendu 73
    # Accès lexical : sans accent, en variante déclarée.
    ("evocation", "ev-2-rappel-02", "cle"),             # attendu « clé »
    ("evocation", "ev-6-analyse-01", "marteau"),
    # Prise de message : heure écrite en toutes lettres, jour tel quel.
    ("quotidien", "qo-1-message-01", "14 heures 30"),   # attendu « 14 h 30 »
    ("quotidien", "qo-1-message-08", "jeudi soir"),
    # Rappel libre : liste dans le désordre partiel, accents/casse ignorés.
    ("rappel-series", "rs2-1-libre-01", "Radis, cahier, plage, pomme"),
]


# --- Réponses fausses, qui doivent rester refusées ---------------------------

REFUSEES = [
    # Un chiffre, un montant, un jour, un moment, un ordre ne s'accepte pas « à peu près ».
    ("calcul-mental", "cm3-1-01", "quatre"),
    ("concentration", "co-1-chaine-01", "47"),
    ("memoire", "me-1-empan-01", "cinq quatre huit"),
    ("memoire", "me-1-empan-01", "neuf quatre cinq"),   # ordre inversé
    ("memoire", "me-1-empan-01", "554"),
    ("memoire", "me-3-paires-01", "septante-deux"),     # 72 au lieu de 73
    ("quotidien", "qo-1-message-08", "vendredi soir"),
    ("quotidien", "qo-1-message-08", "jeudi matin"),
    ("quotidien", "qo-1-message-01", "15 h 30"),
    ("quotidien", "qo-1-message-01", "14 h 45"),
    ("evocation", "ev-2-rappel-02", "serrure"),
]


@pytest.mark.parametrize("theme,item_id,reponse", ACCEPTEES)
def test_formes_dictees_acceptees(theme, item_id, reponse):
    assert _corrige(theme, item_id, reponse) is True, f"{theme}/{item_id} : {reponse!r}"


@pytest.mark.parametrize("theme,item_id,reponse", REFUSEES)
def test_reponses_fausses_refusees(theme, item_id, reponse):
    assert _corrige(theme, item_id, reponse) is False, f"{theme}/{item_id} : {reponse!r}"


def test_empan_dicté_en_mots_et_en_chiffres_donnent_la_meme_cle():
    """Le cas qui manquait : une séquence dictée en mots doit valoir la séquence chiffrée."""
    for forme in ("549", "5 4 9", "cinq quatre neuf", "cinq 4 neuf"):
        assert _corrige("memoire", "me-1-empan-01", forme) is True, forme
    # …mais l'ordre et les chiffres restent stricts.
    for fausse in ("594", "549 1", "cinq quatre huit"):
        assert _corrige("memoire", "me-1-empan-01", fausse) is False, fausse


def test_le_code_ne_se_dicte_pas():
    """La dictée est retirée des thèmes dont la réponse est du code (indentation, symboles)."""
    source = (Path(__file__).resolve().parents[2] / "frontend" / "src" / "app.js").read_text()
    assert "THEMES_SANS_DICTEE" in source and "python" in source


# --- Articles et réponses courtes écrites dans une phrase ---------------------

def test_article_devant_le_mot_accepte():
    """« un verre » doit valoir « verre » : l'article n'est pas la réponse."""
    item = CONTENU.item("evocation", "ev-7-analyse-03")   # attendu « gare »
    assert item["reponse"]["valeur"] == "gare"
    for forme in ("gare", "la gare", "une gare", "des gares"):
        assert corriger("evocation", item, forme) is True, forme
    for fausse in ("villa", "garde", "arrêt"):
        assert corriger("evocation", item, fausse) is False, fausse


def test_mot_ecrit_dans_une_phrase_accepte():
    """« on attend devant la gare » vaut « gare » : le mot est bien produit."""
    item = CONTENU.item("evocation", "ev-7-analyse-03")
    assert corriger("evocation", item, "on attend devant la gare") is True
    assert corriger("evocation", item, "devant la gare") is True


def test_la_contenance_ne_traverse_pas_un_jalon():
    """La tolérance est bornée : un jour, un moment ou un nombre ne s'accepte pas « autour »."""
    quotidien = CONTENU.item("quotidien", "qo-1-message-08")   # attendu « jeudi soir »
    assert corriger("quotidien", quotidien, "jeudi soir, comme prévu") is True
    assert corriger("quotidien", quotidien, "vendredi soir, comme prévu") is False


def test_le_mot_dans_une_petite_phrase_seulement():
    """Le mot attendu est accepté dans une **petite** phrase, pas dans un texte entier.

    Demande d'usage : « le mot dans une petite phrase qui reprend l'élément de réponse ».
    Au-delà d'une douzaine de mots, ce n'est plus une réponse — et le mot pourrait s'y
    trouver par hasard.
    """
    item = CONTENU.item("evocation", "ev-7-analyse-03")   # attendu « gare »
    for petite in ("on attend devant la gare", "rendez-vous à la gare", "je vais à la gare"):
        assert corriger("evocation", item, petite) is True, petite
    longue = ("Hier, en revenant du marché où j'avais acheté des légumes pour la semaine, "
              "je suis passée devant la gare avec ma sœur et nous avons parlé du voyage")
    assert corriger("evocation", item, longue) is False, "une phrase trop longue n'est pas une réponse"
