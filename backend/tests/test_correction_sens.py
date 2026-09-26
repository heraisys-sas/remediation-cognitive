"""Le filet sémantique ne doit jamais traverser un jalon de sens.

Régression constatée en usage réel : « vendredi soir » accepté pour « jeudi soir ».
La proximité de sens est utile pour une reformulation (« la cave » pour « la porte de
la cave »), jamais pour changer un jour, un moment ou un nombre — mesuré sur ce poste,
« 14 h 30 » ≈ « 15 h 30 » vaut 0,999.
"""

import pytest

from backend.app.domain import capacites
from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.correction import _jetons_critiques, _sens_proche, corriger

CONTENU = ChargeurContenu()

#: Paires que la proximité de sens acceptait à tort (mesures du 2026-09-26).
JALONS_DIFFERENTS = [
    ("vendredi soir", "jeudi soir"),
    ("jeudi matin", "jeudi soir"),
    ("14 h 30", "15 h 30"),
    ("mercredi", "mardi"),
    ("jeudi", "jeudi soir"),
    ("dans trois jours", "dans deux jours"),
]


def test_jalons_de_sens_jamais_traverses():
    for reponse, attendue in JALONS_DIFFERENTS:
        assert _sens_proche(reponse, [attendue]) is False, (reponse, attendue)


def test_jalons_detectes():
    assert _jetons_critiques("jeudi soir") == frozenset({"jeudi", "soir"})
    assert _jetons_critiques("14 h 30") == frozenset({"14", "30"})
    assert _jetons_critiques("la porte de la cave") == frozenset()


def test_reformulation_sans_jalon_reste_possible():
    """« la cave » pour « la porte de la cave » : aucun jalon, le sens décide."""
    assert _jetons_critiques("la cave") == _jetons_critiques("la porte de la cave")
    if capacites.fournisseur_similarite() == "lexical":
        pytest.skip("sans empreintes système, seule la comparaison lexicale est disponible")
    assert _sens_proche("la cave", ["la porte de la cave"]) is True


def test_prise_message_au_quotidien():
    """Le cas signalé : un jour ne s'accepte pas « à peu près »."""
    item = CONTENU.item("quotidien", "qo-1-message-08")
    assert item["reponse"]["valeur"] == "jeudi soir"
    assert corriger("quotidien", item, "jeudi soir") is True
    assert corriger("quotidien", item, "vendredi soir") is False
    assert corriger("quotidien", item, "jeudi matin") is False
    assert corriger("quotidien", item, "jeudi") is False


def test_heures_du_quotidien_toujours_distinctes():
    """« 14 h 30 » et « 15 h 30 » restent deux réponses différentes."""
    item = CONTENU.item("quotidien", "qo-1-message-01")
    assert item["reponse"]["valeur"] == "14 h 30"
    assert corriger("quotidien", item, "14 h 30") is True
    assert corriger("quotidien", item, "14 heures 30") is True
    assert corriger("quotidien", item, "15 h 30") is False
