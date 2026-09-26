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
"""

from __future__ import annotations

import re
import unicodedata
from numbers import Real

from . import capacites

# Tolérance de comparaison flottante (représentations décimales exactes).
TOLERANCE_NUMERIQUE = 1e-9


def _normaliser_texte(valeur) -> str:
    """Normalise une valeur en texte comparable : trim + espaces réduits."""
    if valeur is None:
        return ""
    return " ".join(str(valeur).split())


#: Nombres en lettres → chiffres (une réponse dictée arrive souvent en mots :
#: « six » pour 6, « quarante-deux » pour 42, « deux cent trente » pour 230).
_UNITES_MOTS = {
    "zero": 0, "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
    "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11,
    "douze": 12, "treize": 13, "quatorze": 14, "quinze": 15, "seize": 16,
}
_DIZAINES_MOTS = {
    "vingt": 20, "trente": 30, "quarante": 40, "cinquante": 50,
    "soixante": 60, "quatrevingt": 80, "quatrevingtdix": 90,
}


def _nombre_en_chiffres(texte) -> float | None:
    """Convertit un nombre écrit en lettres en valeur numérique.

    Gère les unités, les dizaines, les formes irrégulières (« soixante-dix »,
    « quatre-vingt-dix »), « cent » et « mille », avec traits d'union, espaces
    ou « et ». Retourne None si le texte n'est pas un nombre en lettres.
    """
    texte = _clef_texte(texte)
    if not texte:
        return None
    texte = texte.replace("-", " ")
    texte = texte.replace("quatre vingt dix", "quatrevingtdix")
    texte = texte.replace("quatre vingts", "quatrevingt").replace("quatre vingt", "quatrevingt")
    jetons = [j for j in texte.split() if j != "et"]
    if not jetons:
        return None
    total, courant, vu = 0.0, 0.0, False
    for jeton in jetons:
        if jeton in _UNITES_MOTS:
            courant += _UNITES_MOTS[jeton]
        elif jeton in _DIZAINES_MOTS:
            courant += _DIZAINES_MOTS[jeton]
        elif jeton == "cent":
            courant = (courant or 1) * 100
        elif jeton == "mille":
            total += (courant or 1) * 1000
            courant = 0.0
        else:
            return None
        vu = True
    return total + courant if vu else None


def _en_nombre(valeur) -> float | None:
    """Interprète une réponse comme un nombre (chiffres, ou lettres) — sinon None."""
    if isinstance(valeur, bool) or valeur is None:
        return None
    if isinstance(valeur, Real):
        return float(valeur)
    texte = str(valeur).strip()
    if not texte:
        return None
    texte = texte.strip(" .,!?;:")   # la dictée ajoute souvent un point final
    if not texte:
        return None
    try:
        return float(texte.replace(",", "."))
    except ValueError:
        return _nombre_en_chiffres(texte)


def _corriger_numerique(reponse, attendue) -> bool:
    """Compare numériquement : accepte un nombre, une chaîne numérique, ou des lettres.

    La virgule décimale française est tolérée (``"56,5"`` vaut 56.5) et une réponse
    dictée en toutes lettres est comprise (« six » vaut 6, « quarante-deux » vaut 42).
    Tout ce qui n'est pas interprétable numériquement est faux.
    """
    if attendue is None or isinstance(reponse, bool):
        return False
    valeur = _en_nombre(reponse)
    if valeur is None:
        return False
    cible = _en_nombre(attendue)
    if cible is None:
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

    Sert au thème ``evocation`` (mot retrouvé) : l'objectif est le rappel du mot,
    pas l'orthographe exacte ni la typographie — un mot juste écrit sans accent
    reste juste.
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


#: Façons d'écrire « heure » après un nombre (« 15 h », « 15 heures », « 15hrs »).
_MOTS_HEURE = r"(?:h\b|heures?\b|hrs?\b)"


def _normaliser_horaires(texte: str) -> str:
    """Ramène les façons françaises de dire l'heure à la forme « 15h » / « 15h30 ».

    « 15 h », « 15 heures », « quinze heures », « 15:30 », « 15 heures 30 »,
    « trois heures et demie », « 15 heures moins le quart », « midi », « 8 heures
    du soir » : tout cela désigne la même heure. L'exercice porte sur le raisonnement,
    pas sur la façon d'écrire l'heure.
    """
    texte = re.sub(r"\bmidi\b", "12h", texte)
    texte = re.sub(r"\bminuit\b", "0h", texte)

    def avec_periode(correspondance):
        heure = int(correspondance.group(1))
        minutes = correspondance.group(2) or ""
        periode = correspondance.group(3) or ""
        if heure < 12 and periode.startswith(("du soir", "de l'apres-midi")):
            heure += 12
        return f"{heure}h{minutes}"

    texte = re.sub(
        rf"(\d{{1,2}})\s*{_MOTS_HEURE}(?:\s*(\d{{1,2}}))?(?:\s*(du soir|de l'apres-midi|du matin))?",
        avec_periode, texte)
    texte = re.sub(r"(\d{1,2})h\s*et\s*quart\b", lambda m: f"{m.group(1)}h15", texte)
    texte = re.sub(r"(\d{1,2})h\s*et\s*demie?\b", lambda m: f"{m.group(1)}h30", texte)
    texte = re.sub(r"(\d{1,2})h\s*moins\s*le\s*quart\b",
                   lambda m: f"{int(m.group(1)) - 1}h45", texte)
    # Minutes sur un seul chiffre : « 15h5 » vaut « 15h05 ».
    texte = re.sub(r"h(\d)\b", lambda m: f"h0{m.group(1)}", texte)
    return texte


def _clef_reponse(valeur) -> str:
    """Clé d'une réponse texte : casse, accents, espaces, horaires et nombres.

    - « 15 h », « 15h », « 15:00 » et « 15 heures » sont équivalents ;
    - « 15 heures 30 » vaut « 15h30 », « trois heures et demie » vaut « 3h30 » ;
    - « deux » et « 2 » sont équivalents (nombre en toutes lettres → chiffres).
    """
    texte = _clef_texte(valeur)
    # Nombres en toutes lettres d'abord : « quinze heures » -> « 15 heures ».
    jetons = [_NUMERAUX_QUOTIDIEN.get(jeton, jeton) for jeton in texte.split()]
    texte = " ".join(jetons)
    texte = _normaliser_horaires(texte)
    # Séparateur d'heure restant (« 15:30 »), avec ou sans minutes.
    texte = re.sub(r"(\d{1,2})\s*[:h]\s*(\d*)", r"\1h\2", texte)
    # « 15h00 » vaut « 15h » (heure pleine).
    texte = re.sub(r"(\d)h00\b", r"\1h", texte)
    jetons = [_NUMERAUX_QUOTIDIEN.get(jeton, jeton) for jeton in texte.split()]
    return " ".join(jetons)


def _est_reponse_libre(attendue) -> bool:
    """La réponse attendue est-elle une **phrase** (et non une valeur courte) ?

    Pour une heure, un nombre ou un code, seule la comparaison normalisée compte :
    comparer le « sens » n'aurait pas de sens. Pour une phrase, la comparaison
    sémantique du poste (embeddings Apple, repli lexical) tolère une reformulation.
    """
    texte = str(attendue or "").strip()
    if len(texte.split()) < 3:
        return False
    return not re.fullmatch(r"[\d\s:h.,;/+-]+", texte)


def _distance(a: str, b: str) -> int:
    """Distance d'édition (Levenshtein) — tolérance aux fautes de frappe."""
    if a == b:
        return 0
    precedent = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        courant = [i]
        for j, cb in enumerate(b, 1):
            courant.append(min(precedent[j] + 1, courant[j - 1] + 1,
                               precedent[j - 1] + (1 if ca != cb else 0)))
        precedent = courant
    return precedent[-1]


def _corriger_mot(reponse, item: dict) -> bool:
    """Réponse d'un seul mot (accès lexical) : tolérance de saisie et petite faute.

    - accents, casse et ponctuation ignorés ;
    - variantes acceptées si l'item les déclare (``reponse.variantes`` : synonymes,
      autre écriture) ;
    - une faute de frappe mineure reste acceptée (distance 1, ou 2 pour un mot long) :
      l'exercice porte sur la mémoire, pas sur l'orthographe.
    """
    bloc = item.get("reponse") or {}
    cibles = [bloc.get("valeur"), *(bloc.get("variantes") or [])]
    donnees = _clef_reponse(reponse)
    for cible in cibles:
        clef = _clef_reponse(cible)
        if not clef:
            continue
        if donnees == clef:
            return True
        if " " not in clef and " " not in donnees:
            tolerance = 1 if len(clef) < 7 else 2
            if _distance(donnees, clef) <= tolerance:
                return True
    # Dernier recours : le poste sait-il comparer le SENS (synonymes) ?
    return capacites.proche(str(reponse or ""), [str(c) for c in cibles if c])


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
    nombre = _en_nombre(reponse)
    if nombre is None:
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
    if theme == "methodes":
        # PQRST, GMT, auto-instruction, plan à vérifier, repérage : proposition choisie.
        if _clef_reponse(reponse) == _clef_reponse(attendue):
            return True
        # Sur un choix multiple, le filet sémantique est écarté : les autres
        # propositions sont des leurres proches par construction.
        if (item.get("contenu") or {}).get("options"):
            return False
        # Réponse libre formulée autrement (formulée en phrase) : le poste sait
        # comparer le sens (« je consulte le docteur » pour « je vais chez le médecin »).
        if _est_reponse_libre(attendue):
            return capacites.proche(str(reponse or ""), [str(attendue)])
        return False
    if theme == "quotidien":
        if item.get("type") == "prise-message":
            if _clef_reponse(reponse) == _clef_reponse(attendue):
                return True
            # Formulation proche (« la cave » pour « la porte de la cave »).
            return capacites.proche(str(reponse or ""), [str(attendue)])
        if item.get("type") == "estimation-temps":
            return _corriger_estimation(item, reponse)
        # etape-suivante et les familles à choix : la proposition choisie, en clair.
        return _clef_reponse(reponse) == _clef_reponse(attendue)
    if theme == "rappel-series":
        return _corriger_rappel_libre(item, reponse)
    if theme == "evocation":
        # Accès lexical : mot retrouvé, avec variantes et petite tolérance de frappe.
        return _corriger_mot(reponse, item)
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
