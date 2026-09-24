"""Correction côté serveur des réponses du module entraînement.

Garde-fou central : la réponse attendue d'un item ne quitte JAMAIS le
serveur avant la soumission de l'utilisateur. La comparaison se fait ici
(``corriger``), puis le résultat (correcte + réponse attendue révélée
après coup pour le feedback guidé) est renvoyé par l'API.

Règles par thème (docs/30-technique/api-contract.md) :
- ``calcul-mental``  : comparaison numérique — accepte ``56`` ou ``"56"`` ;
- ``anglais``        : texte insensible à la casse, espaces trimmés ;
- ``python``         : chaîne exacte trimmée — production comme
  ``prediction-sortie`` ;
- ``memoire``        : texte insensible à la casse, TOUS les espaces ignorés
  (les empans tapés avec espaces restent valides) — sauf ``empan-mots``, où
  l'ORDRE des mots est significatif (comparaison mot à mot, sans accents) ;
- ``concentration``  : comparaison numérique (chaînes, cascades, double tâche,
  séries — réponses entières) ;
- ``rappel-series``  : rappel libre — réussite si la part de mots retrouvés
  atteint le seuil déclaré par l'item (``reponse.seuil``) ;
- ``evocation``      : texte tolérant — casse, accents, espaces et guillemets
  ignorés (un mot retrouvé se juge sur le mot, pas sur son accent) ;
- ``social``         : texte tolérant — la réponse est la proposition choisie.
"""

from __future__ import annotations

import re
import unicodedata
from numbers import Real

# Tolérance de comparaison flottante (représentations décimales exactes).
TOLERANCE_NUMERIQUE = 1e-9


def _normaliser_texte(valeur) -> str:
    """Normalise une valeur en texte comparable : trim + espaces réduits."""
    if valeur is None:
        return ""
    return " ".join(str(valeur).split())


def _corriger_numerique(reponse, attendue) -> bool:
    """Compare numériquement : accepte un nombre ou une chaîne numérique.

    La virgule décimale française est tolérée dans les chaînes
    (``"56,5"`` vaut 56.5). Tout ce qui n'est pas interprétable
    numériquement est faux.
    """
    if attendue is None or isinstance(reponse, bool):
        return False
    if isinstance(reponse, Real):
        valeur = float(reponse)
    else:
        try:
            valeur = float(str(reponse).strip().replace(",", "."))
        except ValueError:
            return False
    try:
        cible = float(attendue)
    except (TypeError, ValueError):
        return False
    return abs(valeur - cible) <= TOLERANCE_NUMERIQUE


def _corriger_sans_espaces(reponse, attendue) -> bool:
    """Compare deux textes en ignorant TOUT espace et la casse (thème memoire).

    Les empans tapés avec des espaces (``"5 8 2 9 4"``) restent équivalents
    à la séquence collée (``"58294"``) ; la casse est ignorée pour le n-back.
    """
    nettoyer = lambda valeur: "".join(str(valeur or "").split()).lower()
    return nettoyer(reponse) == nettoyer(attendue)


def _clef_texte(valeur) -> str:
    """Clé de comparaison souple : casse, accents, espaces et guillemets ignorés.

    Sert aux thèmes ``evocation`` (mot retrouvé) et ``social`` (proposition
    choisie) : l'objectif est le rappel du mot ou du sens, pas l'orthographe
    exacte ni la typographie — un mot juste écrit sans accent reste juste.
    """
    texte = unicodedata.normalize("NFD", str(valeur or "").casefold())
    sans_accents = "".join(c for c in texte if not unicodedata.combining(c))
    return " ".join(sans_accents.replace("«", " ").replace("»", " ").split())


#: Nombres écrits en lettres → chiffres (tolérance de saisie des réponses de la
#: vie quotidienne : « deux » vaut « 2 », « dix » vaut « 10 »…).
_NUMERAUX_QUOTIDIEN = {
    "zero": "0", "un": "1", "une": "1", "deux": "2", "trois": "3",
    "quatre": "4", "cinq": "5", "six": "6", "sept": "7", "huit": "8",
    "neuf": "9", "dix": "10", "onze": "11", "douze": "12", "treize": "13",
    "quatorze": "14", "quinze": "15", "seize": "16", "vingt": "20",
    "trente": "30", "quarante": "40", "cinquante": "50", "soixante": "60",
    "cent": "100", "mille": "1000",
}


def _clef_quotidien(valeur) -> str:
    """Clé des réponses de la vie quotidienne : nombres et heures normalisés.

    - « 14 h 30 », « 14h30 » et « 14:30 » sont équivalents ;
    - « deux » et « 2 » sont équivalents (nombre en toutes lettres → chiffres).
    """
    texte = _clef_texte(valeur)
    # Normalise le séparateur d'heure entre deux chiffres (h ou :), avec ou sans espaces.
    texte = re.sub(r"(\d)\s*[:h]\s*(\d)", r"\1 h \2", texte)
    jetons = [_NUMERAUX_QUOTIDIEN.get(jeton, jeton) for jeton in texte.split()]
    return " ".join(jetons)


def _mots(texte) -> list[str]:
    """Découpe un texte en mots normalisés (accents, casse et ponctuation ignorés)."""
    return [
        _clef_texte(mot)
        for mot in re.split(r"[^0-9A-Za-z\u00C0-\u024F']+", str(texte or ""))
        if mot.strip()
    ]


def _corriger_mots_ordonnes(reponse, attendue) -> bool:
    """Empan de mots : la SÉQUENCE compte (mots dans l'ordre attendu).

    La tolérance porte sur la saisie (accents, casse, ponctuation), pas sur
    l'ordre : retrouver les mots dans le désordre n'est pas la même tâche.
    """
    return _mots(reponse) == _mots(attendue)


def _corriger_rappel_libre(item: dict, reponse) -> bool:
    """Rappel libre : réussi si la part de mots retrouvés atteint le seuil.

    Aucun ordre n'est exigé — le rappel libre mesure ce qui revient, pas la
    restitution d'une liste. Comparaison sans accents ni casse ; le pluriel
    simple (mot + « s ») est toléré.
    """
    reponse_item = item.get("reponse") or {}
    cibles = reponse_item.get("valeur") or []
    if not isinstance(cibles, list) or not cibles:
        return False
    seuil = float(reponse_item.get("seuil") or 1.0)
    jetons = set(_mots(reponse))
    trouves = sum(
        1
        for mot in cibles
        if _clef_texte(mot) in jetons or f"{_clef_texte(mot)}s" in jetons
    )
    return (trouves / len(cibles)) >= seuil


def _corriger_estimation(item: dict, reponse) -> bool:
    """Estimation de durée : acceptée dans la fourchette déclarée par l'item.

    Une estimation n'est pas une mesure exacte : la réponse est correcte si elle
    tombe dans ``reponse.intervalle`` (bornes incluses).
    """
    reponse_item = item.get("reponse") or {}
    intervalle = reponse_item.get("intervalle")
    if isinstance(reponse, bool):
        return False
    if isinstance(reponse, Real):
        nombre = float(reponse)
    else:
        try:
            nombre = float(str(reponse).strip().replace(",", "."))
        except ValueError:
            return False
    if isinstance(intervalle, list) and len(intervalle) == 2:
        return float(intervalle[0]) <= nombre <= float(intervalle[1])
    return _corriger_numerique(reponse, reponse_item.get("valeur"))


def _corriger_grille(item: dict, reponse) -> bool:
    """Grille de déduction : la grille soumise doit être exacte (9 cases).

    La réponse est une chaîne « figure:couleur;… » (ordre de lecture) ; la
    comparaison est insensible à la casse, le découpage sur « ; ».
    """
    attendue = str((item.get("reponse") or {}).get("valeur") or "")
    cellules_attendues = [c.strip().lower() for c in attendue.split(";") if c.strip()]
    cellules_donnees = [c.strip().lower() for c in str(reponse or "").split(";") if c.strip()]
    return cellules_donnees == cellules_attendues


def corriger(theme: str, item: dict, reponse) -> bool:
    """Retourne True si la réponse soumise correspond à la réponse attendue.

    - ``theme`` : identifiant API du thème (calcul-mental, anglais, python,
      memoire, concentration) ;
    - ``item`` : item complet côté serveur (avec ``reponse.valeur``) ;
    - ``reponse`` : réponse utilisateur (str ou nombre, corps du contrat).

    Fonction interne serveur : ne jamais l'exposer avant soumission.
    """
    attendue = (item.get("reponse") or {}).get("valeur")
    if theme in ("calcul-mental", "concentration"):
        return _corriger_numerique(reponse, attendue)
    if theme == "deduction":
        return _corriger_grille(item, reponse)
    if theme == "quotidien":
        if item.get("type") == "prise-message":
            return _clef_quotidien(reponse) == _clef_quotidien(attendue)
        if item.get("type") == "estimation-temps":
            return _corriger_estimation(item, reponse)
        # etape-suivante et les familles à choix : la proposition choisie, en clair.
        return _clef_texte(reponse) == _clef_texte(attendue)
    if theme == "rappel-series":
        return _corriger_rappel_libre(item, reponse)
    if theme in ("evocation", "social"):
        return _clef_texte(reponse) == _clef_texte(attendue)
    if theme in ("anglais", "memoire"):
        if theme == "memoire":
            if item.get("type") == "empan-mots":
                return _corriger_mots_ordonnes(reponse, attendue)
            return _corriger_sans_espaces(reponse, attendue)
        return (
            _normaliser_texte(reponse).lower()
            == _normaliser_texte(attendue).lower()
        )
    # python — production et prediction-sortie : chaîne exacte trimmée
    # (cas sensitive ; la valeur attendue peut être str ou nombre).
    reponse_texte = "" if reponse is None else str(reponse)
    attendue_texte = "" if attendue is None else str(attendue)
    return reponse_texte.strip() == attendue_texte.strip()
