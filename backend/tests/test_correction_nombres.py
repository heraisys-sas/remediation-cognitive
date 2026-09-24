"""Réponses numériques : la forme dictée est acceptée comme les chiffres.

Une réponse donnée à voix haute arrive en toutes lettres (« six ») ; l'exercice
porte sur le calcul, pas sur la transcription. On vérifie donc l'équivalence
lettres ↔ chiffres, et le refus de tout ce qui n'est pas un nombre.
"""

from backend.app.domain.correction import _corriger_numerique, _nombre_en_chiffres


def test_nombres_en_lettres_equivalents_aux_chiffres():
    assert _corriger_numerique("six", 6) is True
    assert _corriger_numerique("six.", 6) is True          # la dictée ajoute un point
    assert _corriger_numerique("six !", 6) is True
    assert _corriger_numerique(6, "six") is True
    assert _corriger_numerique("42", "quarante-deux") is True
    assert _corriger_numerique("vingt-et-un", 21) is True
    assert _corriger_numerique("soixante-dix", 70) is True
    assert _corriger_numerique("quatre-vingts", 80) is True
    assert _corriger_numerique("quatre-vingt-dix-sept", 97) is True
    assert _corriger_numerique("deux cent trente", 230) is True
    assert _corriger_numerique("mille", 1000) is True


def test_nombres_refuses():
    assert _corriger_numerique("sept", 8) is False         # un autre nombre
    assert _corriger_numerique("banane", 6) is False       # pas un nombre
    assert _corriger_numerique("", 6) is False
    assert _corriger_numerique("6,5", 6.5) is True         # virgule française


def test_conversion_des_nombres_en_lettres():
    assert _nombre_en_chiffres("zéro") == 0
    assert _nombre_en_chiffres("onze") == 11
    assert _nombre_en_chiffres("quatre-vingt-onze") == 91
    assert _nombre_en_chiffres("cent") == 100
    assert _nombre_en_chiffres("une pomme") is None        # texte, pas un nombre
