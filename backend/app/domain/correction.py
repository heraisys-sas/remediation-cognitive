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


#: Étapes **jugées** d'une séquence « PQRST mis en œuvre » (la lecture ne se juge pas).
ETAPES_JUGEES_SEQUENCE = (1, 4, 5)


def _mots_sequence(valeur) -> set[str]:
    """Jetons d'une réponse libre, découpés sur tout ce qui n'est pas alphanumérique.

    L'apostrophe et le trait d'union séparent : « d'identité » donne `identite`, sinon une
    idée-clé écrite sans apostrophe ne serait jamais retrouvée (dictée, réponse tapée vite).
    """
    return {jeton for jeton in re.split(r"[^0-9a-z]+", _clef_texte(valeur)) if jeton}


def _idee_retrouvee(idee: str, jetons: set[str], minimum: int = 4) -> bool:
    """Une idée-clé est retrouvée si un jeton la porte — égal ou préfixe.

    Le préfixe évite d'exiger la forme exacte : « remboursement » doit valoir l'idée
    « rembourse », « identité » valoir « identite ».
    """
    clef = _clef_texte(idee)
    if not clef:
        return False
    if clef in jetons or f"{clef}s" in jetons:
        return True
    if len(clef) < minimum:
        return False
    return any(jeton.startswith(clef) for jeton in jetons)


def corriger_sequence(item: dict, reponse) -> tuple[bool, dict]:
    """Juge une séquence « PQRST mis en œuvre » (ADR-015) : (réussi, détail par étape).

    - **étape 1 — Parcours** : le sujet du texte (choix) ;
    - **étape 2 — Question** : **non notée** ; on vérifie seulement qu'une question a été
      écrite, et le **modèle** est renvoyé — c'est la production qui travaille, pas sa note ;
    - **étape 4 — Reformulation** : idées-clés retrouvées, seuil déclaré par l'item
      (4 sur 5) ; les idées manquées sont renvoyées pour le retour ;
    - **étape 5 — Test** : les deux questions de mémoire, réussies ensemble.

    La lecture (étape 3) ne se juge pas : elle est guidée par la question écrite.
    """
    contenu = item.get("contenu") or {}
    etapes = {etape.get("etape"): etape for etape in contenu.get("etapes") or []}
    donnees = reponse if isinstance(reponse, dict) else {}

    def fournie(numero: int):
        return donnees.get(str(numero), donnees.get(numero))

    detail: dict[str, dict] = {}
    verdicts: list[bool] = []

    # 1 — Parcours
    parcours = etapes.get(1) or {}
    reussi_1 = _clef_reponse(fournie(1)) == _clef_reponse(parcours.get("bonne"))
    detail["1"] = {"correcte": reussi_1, "attendue": parcours.get("bonne")}
    verdicts.append(reussi_1)

    # 2 — Question écrite (non notée : une production vide est simplement signalée)
    question = etapes.get(2) or {}
    texte_question = str(fournie(2) or "").strip()
    detail["2"] = {
        "correcte": bool(texte_question),
        "modele": question.get("modele"),
        "non_notee": True,
    }

    # 4 — Reformulation : part d'idées-clés retrouvées, seuil de l'item
    reformulation = etapes.get(4) or {}
    idees = [str(idee) for idee in reformulation.get("idees_cles") or []]
    seuil = float((item.get("reponse") or {}).get("seuil") or reformulation.get("seuil") or 1.0)
    jetons = _mots_sequence(fournie(4))
    trouvees = [idee for idee in idees if _idee_retrouvee(idee, jetons)]
    manquantes = [idee for idee in idees if idee not in trouvees]
    reussi_4 = bool(idees) and (len(trouvees) / len(idees)) >= seuil
    detail["4"] = {
        "correcte": reussi_4,
        "trouvees": trouvees,
        "manquantes": manquantes,
        "seuil": seuil,
        "modele": reformulation.get("modele"),
    }
    verdicts.append(reussi_4)

    # 5 — Test : les deux questions de mémoire
    test = etapes.get(5) or {}
    questions = test.get("questions") or []
    reponses_test = fournie(5)
    if not isinstance(reponses_test, list):
        reponses_test = [reponses_test]
    verdicts_questions = []
    for rang, question_test in enumerate(questions):
        donnee = reponses_test[rang] if rang < len(reponses_test) else None
        verdicts_questions.append(
            _clef_reponse(donnee) == _clef_reponse(question_test.get("bonne"))
        )
    reussi_5 = bool(verdicts_questions) and all(verdicts_questions)
    detail["5"] = {
        "correcte": reussi_5,
        "questions": [q.get("bonne") for q in questions],
        "reussies": verdicts_questions,
    }
    verdicts.append(reussi_5)

    return all(verdicts), detail


def _corriger_sans_espaces(reponse, attendue) -> bool:
    """Séquence ou valeur courte (empans, n-back, paires) : la saisie est normalisée.

    - espaces, casse, accents et ponctuation ignorés ;
    - **nombres en toutes lettres convertis** : une réponse dictée arrive souvent en mots
      (« zéro sept un » pour « 071 », « soixante-treize » pour « 73 ») ;
    - l'ORDRE reste strict : c'est la tâche.
    """
    def clef(valeur) -> str:
        jetons = []
        for jeton in _clef_texte(valeur).split():
            nombre = _en_nombre(jeton)
            if nombre is not None and float(nombre).is_integer():
                jetons.append(str(int(nombre)))
            else:
                jetons.append(jeton)
        return "".join(jetons)

    return clef(reponse) == clef(attendue)


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


#: Unités qu'une dictée écrit en chiffres ou en lettres (« cent quatre-vingts euros »).
#: Les heures ne sont pas ici : elles ont leur propre normalisation.
_UNITES_QUANTITE = ("euros", "euro", "centimes", "centime", "litres", "litre", "kilos",
                    "kilo", "grammes", "gramme", "metres", "metre", "kilometres",
                    "kilometre", "minutes", "minute", "jours", "jour", "mois", "ans",
                    "personnes", "fois")

#: Mots qui peuvent former un nombre en toutes lettres (« cent quatre-vingt-dix »).
_MOTIF_NOMBRE_LETTRES = "|".join(sorted(
    {*_UNITES_MOTS, *_DIZAINES_MOTS, "cent", "mille", "quatre", "vingt", "et",
     "quatrevingt", "quatrevingtdix"}, key=len, reverse=True))


def _normaliser_quantites(texte: str) -> str:
    """Montants et quantités : « 180 € », « 180 eur » et « cent quatre-vingts euros ».

    Une réponse dictée arrive souvent écrite autrement que la réponse attendue : le
    symbole au lieu du mot, ou le montant en toutes lettres. L'exercice porte sur le
    raisonnement (ou la mémoire), pas sur la façon d'écrire un montant.
    """
    texte = re.sub(r"(?<=\d)\s*€", " euros", texte)          # « 180 € » -> « 180 euros »
    texte = re.sub(r"€\s*(?=\d)", "", texte)                 # « € 180 » -> « 180 euros »
    texte = re.sub(r"\b(?:euros?|eur\.?)\b", "euros", texte)  # « 180 eur » -> « 180 euros »

    def en_chiffres(correspondance):
        valeur = _nombre_en_chiffres(correspondance.group(1))
        if valeur is None:
            return correspondance.group(0)
        entier = int(valeur) if float(valeur).is_integer() else valeur
        return f"{entier} {correspondance.group(2)}"

    motif = (rf"((?:{_MOTIF_NOMBRE_LETTRES})s?(?:[\s-]+(?:{_MOTIF_NOMBRE_LETTRES})s?)*)"
             rf"\s+({'|'.join(_UNITES_QUANTITE)}s?)")
    return re.sub(motif, en_chiffres, texte)


#: Déterminants de tête, retirés avant comparaison : « un verre » doit valoir « verre ».
_DETERMINANTS = {"un", "une", "1", "le", "la", "les", "des", "du", "de", "mon", "ma",
                 "mes", "ton", "ta", "tes", "son", "sa", "ses", "ce", "cet", "cette",
                 "ces", "l", "d"}


def _sans_determinant(texte: str) -> str:
    """Retire un déterminant de tête, s'il en reste quelque chose.

    « un verre » vaut « verre », « la carte de mutuelle » vaut « carte de mutuelle ». Le
    mot doit exister sans son déterminant : on ne vide pas une réponse qui serait
    seulement « un ».
    """
    jetons = texte.split()
    if len(jetons) > 1 and jetons[0] in _DETERMINANTS:
        return " ".join(jetons[1:])
    return texte


def _meme_mot(clef_a: str, clef_b: str) -> bool:
    """Deux clés désignent-elles le même mot ? Le **pluriel simple** est toléré.

    « des gares » vaut « gare » : le pluriel est une forme légitime, pas une autre réponse.
    La tolérance ne s'applique qu'à des mots d'au moins trois lettres, et jamais à une
    différence interne (« gare » / « garde » restent deux mots distincts).
    """
    if clef_a == clef_b:
        return True
    if not clef_a or not clef_b:
        return False
    if clef_a.rstrip("s") == clef_b.rstrip("s"):
        return min(len(clef_a), len(clef_b)) >= 3
    return False


def _contient_reponse(reponse, attendue) -> bool:
    """La réponse attendue (courte) est-elle **écrite dans** la réponse donnée ?

    « on attend devant la gare » vaut « la gare », « un verre d'eau » vaut « verre ».
    Bornes, parce qu'accepter trop large est plus grave que refuser :

    - la réponse attendue reste **courte** (trois mots au plus) ;
    - aucun **jalon de sens** ne doit différer (jour, moment, nombre) : « vendredi soir »
      ne vaut pas « jeudi soir », « 280 € » ne vaut pas « 180 euros » ;
    - la correspondance se fait sur des **mots entiers** (pas au milieu d'un mot).
    """
    clef = _clef_reponse(attendue)
    donnees = _clef_reponse(reponse)
    if not clef or not donnees or len(clef.split()) > 3:
        return False
    if _jetons_critiques(reponse) != _jetons_critiques(attendue):
        return False
    if clef == donnees:
        return True
    for variante in (clef, f"{clef}s" if not clef.endswith("s") else clef[:-1]):
        if re.search(rf"(?<![0-9a-z]){re.escape(variante)}(?![0-9a-z])", donnees):
            return True
    return False


def _clef_reponse(valeur) -> str:
    """Clé d'une réponse texte : casse, accents, espaces, horaires et nombres.

    - « 15 h », « 15h », « 15:00 » et « 15 heures » sont équivalents ;
    - « 15 heures 30 » vaut « 15h30 », « trois heures et demie » vaut « 3h30 » ;
    - « deux » et « 2 » sont équivalents (nombre en toutes lettres → chiffres).
    """
    texte = _clef_texte(valeur)
    # Déterminant de tête retiré **avant** tout le reste : « un verre » doit devenir
    # « verre », pas « 1 verre » (la conversion des nombres en lettres passe après).
    texte = _sans_determinant(texte)
    # 1. Montants et quantités en toutes lettres : « cent quatre-vingts euros » -> « 180 euros »
    #    (avant la conversion mot à mot, qui casserait les nombres composés).
    texte = _normaliser_quantites(texte)
    # 2. Nombres en toutes lettres isolés : « quinze heures » -> « 15 heures ».
    jetons = [_NUMERAUX_QUOTIDIEN.get(jeton, jeton) for jeton in texte.split()]
    texte = " ".join(jetons)
    # 3. Heures : « 15 h », « 15 heures », « 3 heures et demie », « midi »…
    texte = _normaliser_horaires(texte)
    # Séparateur d'heure restant (« 15:30 »), avec ou sans minutes.
    texte = re.sub(r"(\d{1,2})\s*[:h]\s*(\d*)", r"\1h\2", texte)
    # « 15h00 » vaut « 15h » (heure pleine).
    texte = re.sub(r"(\d)h00\b", r"\1h", texte)
    jetons = [_NUMERAUX_QUOTIDIEN.get(jeton, jeton) for jeton in texte.split()]
    jetons = _sans_determinant(" ".join(jetons)).split()
    return " ".join(jetons)


#: Jalons qui changent le sens d'une réponse : un jour, un moment ou un nombre n'est
#: jamais « à peu près » le même. Le filet sémantique ne doit jamais les traverser.
_JOURS = {"lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"}
_MOIS = {"janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout",
         "septembre", "octobre", "novembre", "decembre"}
_MOMENTS = {"matin", "midi", "apres-midi", "soir", "minuit", "nuit"}
#: Nombres en toutes lettres — sauf « un » et « une », qui sont le plus souvent des
#: articles (« une cave » n'est pas un jalon, « deux jours » en est un).
_MOTS_NOMBRES = (set(_UNITES_MOTS) | set(_DIZAINES_MOTS) | {"cent", "mille"}) - {"un", "une"}


def _jetons_critiques(texte) -> frozenset[str]:
    """Jalons de sens d'une réponse : jours, mois, moments, nombres (chiffres ou lettres).

    Le découpage se fait sur tout caractère non alphanumérique : sans cela, « jeudi soir,
    comme prévu » ne contenait pas le jalon « soir » (le jeton était « soir, »), et la
    comparaison des jalons refusait à tort une réponse correcte.
    """
    jalons = set()
    for jeton in re.split(r"[^0-9a-z]+", _clef_texte(texte)):
        if (jeton in _JOURS or jeton in _MOIS or jeton in _MOMENTS
                or (jeton in _MOTS_NOMBRES and len(jeton) > 2)
                or any(caractere.isdigit() for caractere in jeton)):
            jalons.add(jeton)
    return frozenset(jalons)


def _sens_proche(reponse, attendues) -> bool:
    """Le poste reconnaît-il la réponse comme le même **sens** (dernier recours) ?

    Encadré : on ne traverse jamais un jalon de sens. Mesuré sur ce poste — « vendredi
    soir » ≈ « jeudi soir » 0,85, « jeudi matin » ≈ « jeudi soir » 0,81, « 14 h 30 » ≈
    « 15 h 30 » 0,999. Ces écarts-là sont des erreurs, pas des façons de dire : dès que
    les jalons diffèrent, la proximité de sens ne s'applique pas. Les variantes
    acceptables (réponse plus courte, synonyme) se déclarent dans l'item.
    """
    jalons = _jetons_critiques(reponse)
    for cible in attendues:
        if not cible:
            continue
        if _jetons_critiques(cible) != jalons:
            continue
        if capacites.proche(str(reponse or ""), [str(cible)]):
            return True
    return False


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
        # Pluriel simple : « des gares » vaut « gare » (même mot, autre forme).
        if _meme_mot(donnees, clef):
            return True
        if " " not in clef and " " not in donnees:
            # Faute de frappe tolérée seulement sur les mots assez longs : sur un mot court,
            # une lettre change crée un AUTRE mot (« gare » / « garde »). Accepter une réponse
            # fausse est plus grave que refuser une faute de frappe (ADR-008).
            tolerance = 2 if len(clef) >= 10 else 1 if len(clef) >= 7 else 0
            if tolerance and _distance(donnees, clef) <= tolerance:
                return True
        # Le mot attendu peut avoir été écrit dans une phrase (« un verre d'eau »).
        if _contient_reponse(reponse, cible):
            return True
    # Dernier recours : le poste sait-il comparer le SENS (synonymes) ?
    return _sens_proche(reponse, [cible for cible in cibles if cible])


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
        # comparer le sens (« je consulte le docteur » pour « je vais chez le médecin »),
        # et une réponse courte peut être écrite dans une phrase (ADR-008).
        if _est_reponse_libre(attendue):
            return _sens_proche(reponse, [attendue])
        return _contient_reponse(reponse, attendue)
    if theme == "quotidien":
        if item.get("type") == "prise-message":
            if _clef_reponse(reponse) == _clef_reponse(attendue):
                return True
            # Formulation proche (« la cave » pour « la porte de la cave ») — mais
            # jamais à travers un jour, un moment ou un nombre (voir _sens_proche).
            return _sens_proche(reponse, [attendue]) or _contient_reponse(reponse, attendue)
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
