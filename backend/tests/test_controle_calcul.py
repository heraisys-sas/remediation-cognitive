"""Le contrôle indépendant du calcul mental doit couvrir chaque famille d'énoncé.

Régression constatée : un point d'interrogation non échappé dans un motif faisait qu'une
famille entière d'énoncés n'était plus recalculée — **silencieusement**. Un contrôle qui ne
contrôle rien est plus dangereux que pas de contrôle : chaque forme d'énoncé est donc
testée ici, et un énoncé non calculable doit le dire (``None``), jamais inventer une valeur.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from validate_items import _reponse_calculee  # noqa: E402

#: (énoncé tel qu'il est lu, réponse que le contrôle indépendant doit retrouver)
FORMES = [
    # Opérations et enchaînements
    ("Combien font 8 + 5 ?", 13),
    ("Combien font 13 − 5 ?", 8),
    ("Combien font 4 × 7 ?", 28),
    ("Combien font 8 + 7 − 2 ?", 13),
    ("Combien font 2 × 3 + 3 ?", 9),
    # Repères
    ("Combien manque-t-il à 7 pour faire 10 ?", 3),
    ("Combien manque-t-il à 70 pour faire 100 ?", 30),
    # Argent
    ("2 articles à 7 € — combien en tout ?", 14),
    ("2 articles à 12,50 € — combien en tout ?", 25),
    ("Un article à 7 €, payé avec 10 € — combien te rend-on ?", 3),
    # Sens du nombre (dyscalculie)
    ("Quel nombre est le plus grand : 63 ou 59 ?", 63),
    ("Combien de dizaines dans 47 ?", 4),
    ("43 = 40 + ?", 3),
    ("Quel nombre vient juste après 69 ?", 70),
    ("À mi-chemin entre 40 et 50 ?", 45),
    ("Quel est le double de 35 ?", 70),
    # Suites et erreurs
    ("Continue la suite : 40, 50, 60, 70, ?", 80),
    ("Compte à rebours : 24, 20, 16, 12, ?", 8),
    ("4, 8, 18, 16, 20 — quel nombre est faux ?", 18),
    # Faits à l'envers
    ("81 = 9 × ?", 9),
    ("63 = ? × 9", 7),
    # Séries de calcul (attention soutenue)
    ("75 − 9 − 9 − 9 − 9 − 9", 30),
    ("8 + 4 − 3", 9),
]

#: Énoncés que le contrôle ne peut pas recalculer (famille « vie quotidienne »).
NON_CALCULABLES = [
    "Pour 4 personnes, il faut 250 g de farine. Pour 8 personnes ?",
    "Un film de 90 minutes, plus 15 minutes de pause ?",
    "Trois rendez-vous d'une heure trente ? (en minutes)",
]


def test_chaque_famille_est_recalculee():
    for enonce, attendu in FORMES:
        assert _reponse_calculee(enonce) == attendu, enonce


def test_enonces_non_calculables_reconnus_comme_tels():
    for enonce in NON_CALCULABLES:
        assert _reponse_calculee(enonce) is None, enonce
