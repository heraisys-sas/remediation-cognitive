#!/usr/bin/env python3
"""Cœur commun du thème « déduction » : arrangements, vérité des phrases, solveur.

**Une seule règle, évidente** : chaque figure colorée (« carré bleu ») est posée une
fois, dans une case, et une case ne contient qu'une figure. Tout le reste doit venir
des **phrases** : rien n'est supposé en plus, aucune règle cachée.

Une phrase peut porter **plusieurs informations** (champ ``et``, liste) — au début de
l'apprentissage, deux ou trois informations par phrase raccourcissent l'exercice ; plus
tard, des phrases à deux informations obligent à recouper davantage.

    {"type": "ligne", "figure": "carre", "couleur": "bleu", "ligne": 0,
     "et": [{"type": "colonne", "colonne": 2},
            {"type": "pas-colonne", "colonne": 0}]}

Chaque information supplémentaire peut porter son propre sujet (``figure``/``couleur``),
ce qui permet de parler de deux figures dans la même phrase.

Le solveur ``resoudre_par_deduction`` est le juge : il n'utilise que la règle ci-dessus
et les phrases, et n'accepte une grille que si elle est entièrement déterminée par
propagation, sans hypothèse.
"""

from __future__ import annotations

import random

#: Types d'indices portant sur la position d'un seul jeton (contraintes unaires).
TYPES_UNAIRES = {"case", "ligne", "colonne", "pas-ligne", "pas-colonne",
                 "pas-coin", "pas-bord", "ni-ni"}
#: Types d'indices reliant deux jetons (contraintes binaires).
TYPES_BINAIRES = {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
                  "autre-ligne", "autre-colonne", "comparaison",
                  "a-droite-de", "a-gauche-de", "au-dessus-de", "en-dessous-de",
                  "si-alors"}


def jetons(n: int) -> list[tuple[int, int]]:
    """Les n² figures colorées (indice de figure, indice de couleur)."""
    return [(f, c) for f in range(n) for c in range(n)]


def coins(n: int) -> set[int]:
    return {0, n - 1, n * (n - 1), n * n - 1}


def bords(n: int) -> set[int]:
    return {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}


def arrangement(rng: random.Random, n: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Un placement : (figures, couleurs) par case — chaque figure colorée une fois."""
    melange = jetons(n)
    rng.shuffle(melange)
    return tuple(t[0] for t in melange), tuple(t[1] for t in melange)


def cellule(fig: tuple, coul: tuple, f: int, c: int) -> int:
    """Case de la figure colorée (f, c) ; -1 si absente."""
    for i in range(len(fig)):
        if fig[i] == f and coul[i] == c:
            return i
    return -1


def atomes(indice: dict) -> list[dict]:
    """Les informations d'une phrase : la principale, puis celles du champ ``et``."""
    supplementaires = indice.get("et") or []
    if isinstance(supplementaires, dict):       # tolérance : ancien format à un seul « et »
        supplementaires = [supplementaires]
    return [indice] + [a for a in supplementaires if isinstance(a, dict)]


def sujet(indice: dict, atome: dict) -> tuple[str, str]:
    """Figure colorée dont parle une information (héritée si non précisée)."""
    return (atome.get("figure", indice.get("figure")), atome.get("couleur", indice.get("couleur")))


def _vrai_unaire(atome: dict, case: int, n: int) -> bool:
    """Cette information de position est-elle compatible avec cette case ?"""
    t = atome.get("type")
    if t == "case":
        return case == atome["case"]
    if t == "ligne":
        return case // n == atome["ligne"]
    if t == "colonne":
        return case % n == atome["colonne"]
    if t == "pas-ligne":
        return case // n != atome["ligne"]
    if t == "pas-colonne":
        return case % n != atome["colonne"]
    if t == "pas-coin":
        return case not in coins(n)
    if t == "pas-bord":
        return case not in bords(n)
    if t == "ni-ni":
        return case not in coins(n) and case not in bords(n)
    return True


def _vrai_binaire(indice: dict, i1: int, i2: int, n: int) -> bool:
    """Cette relation entre deux figures colorées est-elle compatible avec ces cases ?"""
    t = indice["type"]
    if t == "voisin-droite":
        return i2 == i1 + 1 and i1 % n != n - 1
    if t == "voisin-gauche":
        return i2 == i1 - 1 and i1 % n != 0
    if t == "voisin-dessous":
        return i2 == i1 + n
    if t == "voisin-dessus":
        return i2 == i1 - n
    if t == "autre-ligne":
        return i1 // n != i2 // n
    if t == "autre-colonne":
        return i1 % n != i2 % n
    if t == "comparaison":
        return i1 // n == i2 // n and i1 < i2
    if t == "a-droite-de":
        return i1 % n > i2 % n
    if t == "a-gauche-de":
        return i1 % n < i2 % n
    if t == "au-dessus-de":
        return i1 // n < i2 // n
    if t == "en-dessous-de":
        return i1 // n > i2 // n
    if t == "si-alors":
        return i1 not in coins(n) or i2 in bords(n)
    return True


def pred_indice(indice: dict, paire, n: int, noms_f: list[str], noms_c: list[str]) -> bool:
    """La phrase est-elle vraie pour cet arrangement ? (toutes ses informations)"""
    fig, coul = paire
    for atome in atomes(indice):
        nom_f, nom_c = sujet(indice, atome)
        if nom_f not in noms_f or nom_c not in noms_c:
            return False
        case = cellule(fig, coul, noms_f.index(nom_f), noms_c.index(nom_c))
        if case < 0:
            return False
        if atome.get("type") in TYPES_UNAIRES and not _vrai_unaire(atome, case, n):
            return False
        if atome.get("type") in TYPES_BINAIRES:
            if atome.get("figure2") not in noms_f or atome.get("couleur2") not in noms_c:
                return False
            autre = cellule(fig, coul, noms_f.index(atome["figure2"]), noms_c.index(atome["couleur2"]))
            if autre < 0 or not _vrai_binaire(atome, case, autre, n):
                return False
    return True


def propager(indices: list[dict], n: int, noms_f: list[str], noms_c: list[str],
             limite_tours: int = 80) -> list[set[tuple[int, int]]] | None:
    """Domaines possibles de chaque case après propagation ; None si contradiction.

    Règles utilisées, et elles seules : une case ne contient qu'une figure colorée,
    et chaque figure colorée est posée une fois. Le reste vient des phrases.
    """
    tous = jetons(n)
    domaines: list[set[tuple[int, int]]] = [set(tous) for _ in range(n * n)]

    def retirer(case: int, jeton: tuple[int, int]) -> bool:
        if jeton in domaines[case]:
            domaines[case].discard(jeton)
            return True
        return False

    def placer(case: int, jeton: tuple[int, int]) -> bool:
        """Fixer un jeton à une case : il quitte les autres cases, la case est pleine."""
        change = False
        for autre in range(n * n):
            if autre != case:
                change |= retirer(autre, jeton)
        for voisin in list(domaines[case]):
            if voisin != jeton:
                change |= retirer(case, voisin)
        return change

    unaires: list[tuple[dict, tuple[int, int]]] = []
    binaires: list[tuple[dict, tuple[int, int], tuple[int, int]]] = []
    for indice in indices:
        for atome in atomes(indice):
            jeton = (noms_f.index(sujet(indice, atome)[0]), noms_c.index(sujet(indice, atome)[1]))
            if atome.get("type") in TYPES_BINAIRES:
                autre = (noms_f.index(atome["figure2"]), noms_c.index(atome["couleur2"]))
                binaires.append((atome, jeton, autre))
            else:
                unaires.append((atome, jeton))

    change, tours = True, 0
    while change and tours < limite_tours:
        change, tours = False, tours + 1

        # 1. Informations de position.
        for atome, jeton in unaires:
            for case in range(n * n):
                if jeton in domaines[case] and not _vrai_unaire(atome, case, n):
                    change |= retirer(case, jeton)

        # 2. Relations entre deux figures colorées (consistance d'arc).
        for atome, jeton1, jeton2 in binaires:
            places2 = {c for c in range(n * n) if jeton2 in domaines[c]}
            for case in range(n * n):
                if jeton1 in domaines[case] and not any(
                    _vrai_binaire(atome, case, autre, n) for autre in places2
                ):
                    change |= retirer(case, jeton1)

        # 3. Case déterminée -> le jeton est là.
        for case in range(n * n):
            if len(domaines[case]) == 1:
                change |= placer(case, next(iter(domaines[case])))

        # 4. Jeton qui n'a plus qu'une case possible -> il y est.
        for jeton in tous:
            places = [c for c in range(n * n) if jeton in domaines[c]]
            if not places:
                return None
            if len(places) == 1:
                change |= placer(places[0], jeton)

    if any(not domaine for domaine in domaines):
        return None
    return domaines


def resoudre_par_deduction(indices: list[dict], n: int,
                           noms_f: list[str], noms_c: list[str],
                           limite_tours: int = 80) -> bool:
    """La grille est-elle entièrement déterminée par les phrases ?

    Retourne True si toutes les cases finissent déterminées par propagation, sans
    hypothèse. Un False invite à ajouter ou à densifier des phrases.
    """
    domaines = propager(indices, n, noms_f, noms_c, limite_tours)
    return bool(domaines) and all(len(domaine) == 1 for domaine in domaines)
