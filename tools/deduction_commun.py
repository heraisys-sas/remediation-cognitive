#!/usr/bin/env python3
"""Cœur commun du thème « déduction » : univers des grilles et solveur de déduction.

Règles du puzzle (celles annoncées dans la consigne) :
- une grille N×N contient N figures et N couleurs ;
- chaque figure apparaît une fois par ligne et par colonne (carré latin) ;
- chaque couleur aussi (donc **chaque figure colorée** apparaît une seule fois).

Le module fournit :

- ``grilles_valides(n)`` — l'univers des grilles respectant les règles ;
- ``pred_indice(...)`` — vérité d'un indice pour une grille ;
- ``resoudre_par_deduction(indices, n, ...)`` — **le contrôle qui compte** : le puzzle
  est-il entièrement résoluble par propagation de contraintes (aucune hypothèse) ?

Le solveur est *sound* mais volontairement incomplet : il ne retire un jeton que
lorsqu'aucun placement ne peut le justifier. S'il termine avec toutes les cases
déterminées, le puzzle est **déductible** ; sinon, on ajoute des indices jusqu'à ce
qu'il le soit — on ne livre jamais un puzzle « à deviner ».
"""

from __future__ import annotations

import itertools

#: Types d'indices portant sur la position d'un seul jeton (contraintes unaires).
TYPES_UNAIRES = {"case", "ligne", "colonne", "pas-coin", "pas-bord", "ni-ni"}
#: Types d'indices reliant deux jetons (contraintes binaires).
TYPES_BINAIRES = {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
                  "autre-ligne", "autre-colonne", "comparaison", "si-alors"}


def carres_latins(n: int) -> list[tuple[int, ...]]:
    """Tous les carrés latins N×N, aplatis en N² indices (ordre de lecture)."""
    resultats = []
    for lignes in itertools.product(itertools.permutations(range(n)), repeat=n):
        if all(sorted(lignes[r][c] for r in range(n)) == list(range(n)) for c in range(n)):
            resultats.append(tuple(lignes[r][c] for r in range(n) for c in range(n)))
    return resultats


def grilles_valides(n: int) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Couples (figures, couleurs) où chaque figure colorée est unique."""
    carres = carres_latins(n)
    return [(f, c) for f in carres for c in carres
            if len({(f[i], c[i]) for i in range(n * n)}) == n * n]


def coins(n: int) -> set[int]:
    return {0, n - 1, n * (n - 1), n * n - 1}


def bords(n: int) -> set[int]:
    return {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}


def cellule(fig: tuple, coul: tuple, f: int, c: int) -> int:
    """Case de la figure colorée (f, c) — unique par construction."""
    for i in range(len(fig)):
        if fig[i] == f and coul[i] == c:
            return i
    return -1


def pred_indice(indice: dict, paire, n: int, noms_f: list[str], noms_c: list[str]) -> bool:
    """Un indice est-il vrai pour cette grille ?"""
    fig, coul = paire
    t = indice["type"]
    if t == "regle":
        return True
    if indice.get("figure") not in noms_f or indice.get("couleur") not in noms_c:
        return False
    case = cellule(fig, coul, noms_f.index(indice["figure"]), noms_c.index(indice["couleur"]))
    if case < 0:
        return False
    if t == "case":
        return case == indice["case"]
    if t == "ligne":
        return case // n == indice["ligne"]
    if t == "colonne":
        return case % n == indice["colonne"]
    if t == "pas-coin":
        return case not in coins(n)
    if t == "pas-bord":
        return case not in bords(n)
    if t == "ni-ni":
        return case not in coins(n) and case not in bords(n)
    if indice.get("figure2") not in noms_f or indice.get("couleur2") not in noms_c:
        return False
    autre = cellule(fig, coul, noms_f.index(indice["figure2"]), noms_c.index(indice["couleur2"]))
    if autre < 0:
        return False
    if t == "voisin-droite":
        return autre == case + 1 and case % n != n - 1
    if t == "voisin-gauche":
        return autre == case - 1 and case % n != 0
    if t == "voisin-dessous":
        return autre == case + n
    if t == "voisin-dessus":
        return autre == case - n
    if t == "autre-ligne":
        return case // n != autre // n
    if t == "autre-colonne":
        return case % n != autre % n
    if t == "comparaison":
        return case // n == autre // n and case < autre
    if t == "si-alors":
        return case not in coins(n) or autre in bords(n)
    return False


def _position_possible(indice: dict, case: int, n: int) -> bool:
    """Pour une contrainte unaire : le jeton peut-il occuper cette case ?"""
    t = indice["type"]
    if t == "case":
        return case == indice["case"]
    if t == "ligne":
        return case // n == indice["ligne"]
    if t == "colonne":
        return case % n == indice["colonne"]
    if t == "pas-coin":
        return case not in coins(n)
    if t == "pas-bord":
        return case not in bords(n)
    if t == "ni-ni":
        return case not in coins(n) and case not in bords(n)
    return True


def _contrainte_binaire(indice: dict, i1: int, i2: int, n: int) -> bool:
    """Pour une contrainte binaire : les deux jetons peuvent-ils occuper i1 et i2 ?"""
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
    if t == "si-alors":
        return i1 not in coins(n) or i2 in bords(n)
    return True


def resoudre_par_deduction(indices: list[dict], n: int,
                           noms_f: list[str], noms_c: list[str],
                           limite_tours: int = 60) -> bool:
    """Le puzzle est-il entièrement résoluble par propagation, sans hypothèse ?

    Retourne True seulement si toutes les cases finissent déterminées par les
    règles et les indices. Un False ne veut pas dire « insuffisant » au sens
    strict (le solveur est incomplet), mais il invite à ajouter des indices —
    c'est la garantie prudente qu'on veut.
    """
    jetons = [(f, c) for f in range(n) for c in range(n)]
    domaines: list[set[tuple[int, int]]] = [set(jetons) for _ in range(n * n)]

    def retirer(case: int, jeton: tuple[int, int]) -> bool:
        if jeton in domaines[case]:
            domaines[case].discard(jeton)
            return True
        return False

    unaires, binaires = [], []
    for indice in indices:
        if indice["type"] == "regle":
            continue
        if indice["type"] in TYPES_UNAIRES:
            unaires.append((indice, (noms_f.index(indice["figure"]), noms_c.index(indice["couleur"]))))
        elif indice["type"] in TYPES_BINAIRES:
            binaires.append((
                indice,
                (noms_f.index(indice["figure"]), noms_c.index(indice["couleur"])),
                (noms_f.index(indice["figure2"]), noms_c.index(indice["couleur2"])),
            ))

    change, tours = True, 0
    while change and tours < limite_tours:
        change, tours = False, tours + 1

        # 1. Contraintes unaires (position d'un jeton).
        for indice, jeton in unaires:
            for case in range(n * n):
                if jeton in domaines[case] and not _position_possible(indice, case, n):
                    change |= retirer(case, jeton)

        # 2. « Toutes différentes » : figures et couleurs, par ligne et par colonne.
        for ligne in range(n):
            for valeur in range(n):
                for indice_valeur in (0, 1):
                    cases = [ligne * n + c for c in range(n)
                             if any(j[indice_valeur] == valeur for j in domaines[ligne * n + c])]
                    if not cases:
                        return False
                    if len(cases) == 1:
                        case = cases[0]
                        for jeton in list(domaines[case]):
                            if jeton[indice_valeur] != valeur:
                                change |= retirer(case, jeton)
        for colonne in range(n):
            for valeur in range(n):
                for indice_valeur in (0, 1):
                    cases = [r * n + colonne for r in range(n)
                             if any(j[indice_valeur] == valeur for j in domaines[r * n + colonne])]
                    if not cases:
                        return False
                    if len(cases) == 1:
                        case = cases[0]
                        for jeton in list(domaines[case]):
                            if jeton[indice_valeur] != valeur:
                                change |= retirer(case, jeton)

        # 3. Chaque figure colorée est unique dans toute la grille.
        for case in range(n * n):
            if len(domaines[case]) == 1:
                (jeton,) = tuple(domaines[case])
                for autre in range(n * n):
                    if autre != case:
                        change |= retirer(autre, jeton)

        # 4. Contraintes binaires : un jeton n'est gardé que si l'autre a une place possible.
        for indice, jeton1, jeton2 in binaires:
            places2 = {c for c in range(n * n) if jeton2 in domaines[c]}
            for case in range(n * n):
                if jeton1 in domaines[case] and not any(
                    _contrainte_binaire(indice, case, autre, n) for autre in places2
                ):
                    change |= retirer(case, jeton1)

    return all(len(domaines[case]) == 1 for case in range(n * n))
