"""Horaires : toutes les façons de dire l'heure sont acceptées.

Une réponse dictée ou écrite arrive volontiers en toutes lettres (« 15 heures »,
« quinze heures », « trois heures et demie ») alors que l'attendu est « 15 h ».
L'exercice porte sur le raisonnement ou la mémoire, pas sur l'écriture de l'heure.
"""

from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.correction import _clef_reponse, corriger

CONTENU = ChargeurContenu()

#: (réponse donnée, réponse attendue) — mêmes clés attendues.
EQUIVALENCES = [
    ("15 heures", "15 h"),
    ("quinze heures", "15 h"),
    ("15h", "15 h"),
    ("15:00", "15 h"),
    ("15 heures du matin", "15 h"),
    ("15 heures 30", "15 h 30"),
    ("15 h 05", "15h05"),
    ("3 heures et demie", "3 h 30"),
    ("midi", "12 h"),
    ("midi et demi", "12 h 30"),
    ("15 heures moins le quart", "14 h 45"),
    ("3 heures du soir", "15 h"),
    ("8 heures du soir", "20 h"),
    ("deux heures", "2 h"),
]

#: Réponses qui doivent rester différentes.
DIFFERENCES = [
    ("16 heures", "15 h"),
    ("15 heures", "16 h"),
    ("15 heures 30", "15 h"),
    ("3 heures du soir", "3 h"),
]


def test_horaires_equivalents():
    for reponse, attendue in EQUIVALENCES:
        assert _clef_reponse(reponse) == _clef_reponse(attendue), (reponse, attendue)


def test_horaires_differents_refuses():
    for reponse, attendue in DIFFERENCES:
        assert _clef_reponse(reponse) != _clef_reponse(attendue), (reponse, attendue)


def test_correction_methodes_accepte_l_heure_en_lettres():
    """Le cas signalé : « 15 heures » pour un item qui attend « 15 h »."""
    item = CONTENU.item("methodes", "mt-1-pqrst-01")
    assert item["reponse"]["valeur"] == "15 h"
    assert corriger("methodes", item, "15 h") is True
    assert corriger("methodes", item, "15 heures") is True
    assert corriger("methodes", item, "quinze heures") is True
    assert corriger("methodes", item, "16 heures") is False
    assert corriger("methodes", item, "12 h") is False


def test_choix_multiple_sans_tolerance_de_sens():
    """Sur un choix multiple, les leurres sont proches : pas de filet sémantique."""
    item = CONTENU.item("methodes", "mt-1-pqrst-02")
    assert (item["contenu"].get("options")), "cet item doit proposer des choix"
    attendue = item["reponse"]["valeur"]
    assert corriger("methodes", item, attendue) is True
    # Une reformulation n'est pas acceptée : la réponse se choisit parmi les propositions.
    assert corriger("methodes", item, f"{attendue} s'il vous plaît") is False
