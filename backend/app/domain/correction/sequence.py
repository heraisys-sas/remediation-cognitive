from __future__ import annotations
import re
from .normalization import (
    _clef_texte,
)
from .text import (
    _clef_reponse,
)

ETAPES_JUGEES_SEQUENCE = (1, 4, 5)

def _mots_sequence(valeur) -> set[str]:
    """Jetons d'une réponse libre, découpés sur tout ce qui n'est pas alphanumérique.

    L'apostrophe et le trait d'union séparent : « d'identité » donne `identite`, sinon une
    idée-clé écrite sans apostrophe ne serait jamais retrouvée (dictée, réponse tapée vite).
    """
    return {jeton for jeton in re.split(r"[^0-9a-z]+", _clef_texte(valeur)) if jeton}

def _liste_mots_sequence(valeur) -> list[str]:
    return [jeton for jeton in re.split(r"[^0-9a-z]+", _clef_texte(valeur)) if jeton]

def _positions_expression(expression: str, jetons: list[str]) -> list[int]:
    attendus = _liste_mots_sequence(expression)
    if not attendus:
        return []
    largeur = len(attendus)
    return [
        debut for debut in range(len(jetons) - largeur + 1)
        if jetons[debut:debut + largeur] == attendus
    ]

def _evaluer_critere_sequence(critere: dict, jetons: list[str]) -> str:
    """Classe une idée de reformulation : retrouvée, contredite ou non reconnue.

    Les expressions et contradictions sont déclarées par item. Une négation située
    juste avant une expression reconnue (``pas au bureau``, ``sans identité``) prime
    également sur la simple présence du mot-clé. Le correcteur reste volontairement
    borné : il ne prétend pas comprendre toute phrase libre.
    """
    for contradiction in critere.get("contradictions") or []:
        if _positions_expression(str(contradiction), jetons):
            return "contredite"

    groupes = critere.get("groupes") or [critere.get("expressions") or []]
    groupes_retrouves = 0
    for groupe in groupes:
        groupe_retrouve = False
        for expression in groupe:
            for debut in _positions_expression(str(expression), jetons):
                contexte = jetons[max(0, debut - 4):debut]
                if any(mot in contexte for mot in ("pas", "sans", "jamais", "aucun", "aucune")):
                    return "contredite"
                groupe_retrouve = True
                break
            if groupe_retrouve:
                break
        groupes_retrouves += int(groupe_retrouve)
    return "retrouvee" if groupes and groupes_retrouves == len(groupes) else "non_reconnue"

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

    # 4 — Reformulation : critères sémantiques bornés, avec contradictions explicites.
    reformulation = etapes.get(4) or {}
    criteres = reformulation.get("criteres") or []
    seuil = float((item.get("reponse") or {}).get("seuil") or reformulation.get("seuil") or 1.0)
    jetons = _liste_mots_sequence(fournie(4))
    evaluations = [(_evaluer_critere_sequence(critere, jetons), critere) for critere in criteres]
    trouvees = [critere["label"] for etat, critere in evaluations if etat == "retrouvee"]
    contredites = [critere["label"] for etat, critere in evaluations if etat == "contredite"]
    manquantes = [critere["label"] for etat, critere in evaluations if etat == "non_reconnue"]
    reussi_4 = (
        bool(criteres)
        and not contredites
        and (len(trouvees) / len(criteres)) >= seuil
    )
    detail["4"] = {
        "correcte": reussi_4,
        "trouvees": trouvees,
        "contredites": contredites,
        "manquantes": manquantes,
        "seuil": seuil,
        "modele": reformulation.get("modele"),
        "correction_bornee": True,
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
