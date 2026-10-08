from __future__ import annotations


from backend.app.domain.correction import (  # noqa: E402
    _mots_sequence as mots_sequence,
)



from .common import (
    _normaliser_texte, est_entier,
)

def erreurs_sequence_pqrst(item: dict, prefixe: str, contenu: dict) -> list[str]:
    """Contrôle du palier « PQRST mis en œuvre » (ADR-015).

    Vérifie la structure des cinq étapes et surtout la **faisabilité** : chacun des cinq
    critères doit proposer des expressions reconnaissables dont au moins une figure dans
    le résumé modèle. Les contradictions sont explicites et ne peuvent pas être vides.
    """
    erreurs: list[str] = []
    etapes_liste = contenu.get("etapes")
    if not isinstance(etapes_liste, list):
        return [prefixe + "étapes attendues sous forme de liste"]
    etapes = {etape.get("etape"): etape for etape in etapes_liste if isinstance(etape, dict)}
    for numero in (1, 2, 3, 4, 5):
        if numero not in etapes:
            erreurs.append(prefixe + f"étape {numero} manquante")

    parcours = etapes.get(1) or {}
    if not isinstance(parcours.get("options"), list) or len(parcours["options"]) != 3:
        erreurs.append(prefixe + "étape 1 : trois propositions attendues")
    elif parcours.get("bonne") not in parcours["options"]:
        erreurs.append(prefixe + "étape 1 : la bonne réponse doit figurer parmi les propositions")

    question = etapes.get(2) or {}
    if not str(question.get("modele") or "").strip():
        erreurs.append(prefixe + "étape 2 : une question modèle est attendue")

    lecture = etapes.get(3) or {}
    if "options" in lecture or "questions" in lecture:
        erreurs.append(prefixe + "étape 3 (lecture) : rien ne doit être demandé")

    reformulation = etapes.get(4) or {}
    criteres = reformulation.get("criteres") or []
    if len(criteres) != 5:
        erreurs.append(prefixe + f"étape 4 : 5 critères attendus (reçu {len(criteres)})")
    seuil = (item.get("reponse") or {}).get("seuil")
    if seuil != 0.8:
        erreurs.append(prefixe + f"étape 4 : seuil attendu 0,8 — 4 idées sur 5 (reçu {seuil!r})")
    modele = str(reformulation.get("modele") or "")
    jetons = mots_sequence(modele)
    for rang, critere in enumerate(criteres, start=1):
        if not isinstance(critere, dict) or not str(critere.get("label") or "").strip():
            erreurs.append(prefixe + f"étape 4, critère {rang} : label manquant")
            continue
        expressions = critere.get("expressions") or []
        groupes = critere.get("groupes") or [expressions]
        contradictions = critere.get("contradictions")
        if not isinstance(expressions, list) or not expressions or not all(
            isinstance(expression, str) and expression.strip() for expression in expressions
        ):
            erreurs.append(prefixe + f"étape 4, critère {rang} : expressions non vides attendues")
        if not isinstance(groupes, list) or not groupes or any(
            not isinstance(groupe, list) or not groupe or not all(
                isinstance(expression, str) and expression.strip() for expression in groupe
            ) for groupe in groupes
        ):
            erreurs.append(prefixe + f"étape 4, critère {rang} : groupes d'expressions invalides")
        elif any(
            not any(set(mots_sequence(expression)) <= jetons for expression in groupe)
            for groupe in groupes
        ):
            erreurs.append(prefixe + f"étape 4, critère {rang} : un sous-fait manque au résumé modèle")
        if not isinstance(contradictions, list) or not all(
            isinstance(expression, str) and expression.strip() for expression in contradictions
        ):
            erreurs.append(prefixe + f"étape 4, critère {rang} : contradictions doit être une liste de textes")

    test = etapes.get(5) or {}
    questions = test.get("questions") or []
    if len(questions) != 2:
        erreurs.append(prefixe + f"étape 5 : 2 questions de mémoire attendues (reçu {len(questions)})")
    for rang, question_test in enumerate(questions, start=1):
        options = question_test.get("options") or []
        if len(options) != 3 or question_test.get("bonne") not in options:
            erreurs.append(prefixe + f"étape 5, question {rang} : trois propositions dont la bonne")

    fiche = contenu.get("fiche_methode") or []
    if len(fiche) != 5:
        erreurs.append(prefixe + f"fiche méthode : 5 lignes attendues (reçu {len(fiche)})")
    phrases = [phrase for phrase in str(contenu.get("texte") or "").split(".") if phrase.strip()]
    if len(phrases) != 4:
        erreurs.append(prefixe + f"texte : 4 phrases attendues (reçu {len(phrases)})")
    return erreurs

def erreurs_rappel_libre(item: dict, prefixe: str, contenu: dict, affichage: object) -> list[str]:
    """Vérifie un item de rappel libre (séries, portée, seuil, délai, cibles)."""
    erreurs: list[str] = []
    series = affichage.get("series") if isinstance(affichage, dict) else None
    if not isinstance(series, list) or not series:
        erreurs.append(prefixe + "rappel-libre : affichage.series doit lister au moins une série")
        return erreurs

    mots: list[str] = []
    for position, serie in enumerate(series, start=1):
        if not isinstance(serie, list) or len(serie) < 3:
            erreurs.append(prefixe + f"rappel-libre : série {position} - au moins 3 mots attendus")
            continue
        if not all(isinstance(mot, str) and mot.strip() for mot in serie):
            erreurs.append(prefixe + f"rappel-libre : série {position} - mots attendus comme chaînes non vides")
            continue
        mots.extend(_normaliser_texte(mot) for mot in serie)
    if len(set(mots)) != len(mots):
        erreurs.append(
            prefixe + "rappel-libre : un mot revient dans plusieurs séries - le comptage serait ambigu"
        )

    portee = contenu.get("portee")
    if portee not in {"toutes-series", "premiere-serie"}:
        erreurs.append(prefixe + f"rappel-libre : portee inconnue {portee!r}")
    delai = contenu.get("delai_s", 0)
    if not est_entier(delai) or not 0 <= delai <= 180:
        erreurs.append(prefixe + f"rappel-libre : delai_s doit être un entier 0..180 : {delai!r}")

    reponse = item.get("reponse") if isinstance(item.get("reponse"), dict) else {}
    cibles, seuil = reponse.get("valeur"), reponse.get("seuil")
    if not isinstance(cibles, list) or not cibles or not all(
        isinstance(mot, str) and mot.strip() for mot in cibles
    ):
        erreurs.append(prefixe + "rappel-libre : reponse.valeur doit lister les mots cibles")
        return erreurs
    if isinstance(seuil, bool) or not isinstance(seuil, (int, float)) or not 0.25 <= float(seuil) <= 1:
        erreurs.append(prefixe + f"rappel-libre : reponse.seuil hors 0.25..1 : {seuil!r}")

    attendu = (
        [_normaliser_texte(mot) for mot in series[0]]
        if portee == "premiere-serie"
        else list(mots)
    )
    if sorted(_normaliser_texte(mot) for mot in cibles) != sorted(attendu):
        erreurs.append(
            prefixe + "rappel-libre : les cibles déclarées ne correspondent pas aux séries affichées"
        )
    return erreurs
