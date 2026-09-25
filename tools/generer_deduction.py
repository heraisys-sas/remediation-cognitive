#!/usr/bin/env python3
"""Génère le thème « deduction » — grilles logiques 3×3 et 4×4, garanties déductibles.

Méthode (ce qui la rend fiable) :
1. l'univers des solutions est fini et connu (72 grilles 3×3, 6 912 en 4×4) ;
2. pour chaque solution encore libre, on ajoute des indices **un par un**, les plus
   informatifs d'abord, en rejouant le **solveur de déduction** (`deduction_commun`) ;
3. on s'arrête dès que le puzzle est résoluble **par propagation, sans hypothèse**, puis on
   complète jusqu'au plancher du palier ; au-delà du plafond, la solution est écartée ;
4. une même solution n'est jamais resservie deux fois dans le thème.

Aucun puzzle n'est donc « à deviner » : le solveur est le juge, pas l'intuition.

Difficulté croissante : palier 1 = indices directs uniquement ; palier 2 = relationnels
(voisinage, comparaison, pas la même ligne/colonne) ; palier 3 = négatifs et conditionnels ;
palier 4 = grille 4×4.

Usage :

    python3 tools/generer_deduction.py                    # 20 grilles par palier
    python3 tools/generer_deduction.py --par-palier 18
    python3 tools/generer_deduction.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deduction_commun import (  # noqa: E402
    TYPES_BINAIRES,
    bords,
    cellule,
    coins,
    grilles_valides,
    resoudre_par_deduction,
)

RACINE_DEPOT = Path(__file__).resolve().parent.parent
BASE_SORTIE = RACINE_DEPOT / "content" / "entrainement" / "deduction"

GRAINE: int = 20260925
DATE_CREATION: str = "2026-09-25"
AUTEUR: str = "generation-automatique (tools/generer_deduction.py)"
PAR_PALIER_DEFAUT: int = 20

FIGURES = ["cercle", "carre", "triangle", "losange"]
COULEURS = ["rouge", "bleu", "vert", "jaune"]

DIRECTS = {"case", "ligne", "colonne"}
RELATIONNELS = {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
                "comparaison", "autre-ligne", "autre-colonne"}
NEGATIFS = {"pas-coin", "pas-bord", "ni-ni", "si-alors"}

#: Types d'indices autorisés par palier (difficulté croissante).
TYPES_PAR_PALIER = {
    1: DIRECTS,
    2: DIRECTS | RELATIONNELS,
    3: DIRECTS | RELATIONNELS | NEGATIFS,
    4: DIRECTS | RELATIONNELS | NEGATIFS,
}
#: Plancher et plafond du nombre d'indices, par palier.
MIN_INDICES = {1: 6, 2: 6, 3: 5, 4: 8}
MAX_INDICES = {1: 12, 2: 12, 3: 12, 4: 18}

#: Force relative des types d'indices (0 = le plus discriminant).
FORCE_TYPE = {
    "case": 0, "ligne": 1, "colonne": 1,
    "voisin-gauche": 2, "voisin-droite": 2, "voisin-dessus": 2, "voisin-dessous": 2,
    "comparaison": 3, "autre-ligne": 4, "autre-colonne": 4,
    "pas-coin": 5, "pas-bord": 5, "ni-ni": 6, "si-alors": 6,
}

DESCRIPTIONS = [
    "Indices de position : la grille se déduit case par case",
    "Indices relationnels (voisinage, à gauche de, pas sur la même ligne)",
    "Indices négatifs et conditionnels : éliminer pour déduire",
    "Grille 4×4 : plus de figures colorées, indices variés",
]


def _indice(type_indice: str, nom_f: str, nom_c: str, **extra) -> dict:
    return {"type": type_indice, "figure": nom_f, "couleur": nom_c, **extra}


def _pool(paire, n: int, noms_f: list[str], noms_c: list[str], types: set[str]) -> list[dict]:
    """Tous les indices vrais (chacun porteur de deux informations) dont le type est autorisé."""
    fig, coul = paire
    pool: list[dict] = []
    for f, nom_f in enumerate(noms_f):
        for c, nom_c in enumerate(noms_c):
            case = cellule(fig, coul, f, c)
            if "case" in types:
                pool.append(_indice("case", nom_f, nom_c, case=case))
            if "ligne" in types:
                pool.append(_indice("ligne", nom_f, nom_c, ligne=case // n))
            if "colonne" in types:
                pool.append(_indice("colonne", nom_f, nom_c, colonne=case % n))
            if "pas-coin" in types and case not in coins(n):
                pool.append(_indice("pas-coin", nom_f, nom_c))
            if "pas-bord" in types and case not in bords(n):
                pool.append(_indice("pas-bord", nom_f, nom_c))
            if "ni-ni" in types and case not in coins(n) and case not in bords(n):
                pool.append(_indice("ni-ni", nom_f, nom_c))
    types_paires = types & TYPES_BINAIRES
    if types_paires:
        for f1, nom_f1 in enumerate(noms_f):
            for c1, nom_c1 in enumerate(noms_c):
                case1 = cellule(fig, coul, f1, c1)
                r1, col1 = divmod(case1, n)
                for f2, nom_f2 in enumerate(noms_f):
                    for c2, nom_c2 in enumerate(noms_c):
                        if (f1, c1) == (f2, c2):
                            continue
                        case2 = cellule(fig, coul, f2, c2)
                        r2, col2 = divmod(case2, n)
                        base = dict(figure2=nom_f2, couleur2=nom_c2)
                        if "voisin-gauche" in types and case2 == case1 + 1 and col1 != n - 1:
                            pool.append(_indice("voisin-gauche", nom_f1, nom_c1, **base))
                        if "voisin-droite" in types and case2 == case1 - 1 and col1 != 0:
                            pool.append(_indice("voisin-droite", nom_f1, nom_c1, **base))
                        if "voisin-dessous" in types and case2 == case1 + n:
                            pool.append(_indice("voisin-dessous", nom_f1, nom_c1, **base))
                        if "voisin-dessus" in types and case2 == case1 - n:
                            pool.append(_indice("voisin-dessus", nom_f1, nom_c1, **base))
                        if "autre-ligne" in types and r1 != r2:
                            pool.append(_indice("autre-ligne", nom_f1, nom_c1, **base))
                        if "autre-colonne" in types and col1 != col2:
                            pool.append(_indice("autre-colonne", nom_f1, nom_c1, **base))
                        if "comparaison" in types and r1 == r2 and case1 < case2:
                            pool.append(_indice("comparaison", nom_f1, nom_c1, **base))
                        if "si-alors" in types and (case1 not in coins(n) or case2 in bords(n)):
                            pool.append(_indice("si-alors", nom_f1, nom_c1, **base))
    return pool


def _ordre(pool: list[dict], rng: random.Random) -> list[dict]:
    """Indices du plus discriminant au moins discriminant (aléa entre forces voisines)."""
    groupes: dict[int, list[dict]] = {}
    for indice in pool:
        groupes.setdefault(FORCE_TYPE.get(indice["type"], 9), []).append(indice)
    ordre: list[dict] = []
    for rang in sorted(groupes):
        rng.shuffle(groupes[rang])
        ordre.extend(groupes[rang])
    return ordre


def _selection(paire, n: int, noms_f: list[str], noms_c: list[str], palier: int,
               rng: random.Random) -> list[dict] | None:
    """Indices suffisants pour une résolution par déduction, avec le dosage du palier."""
    pool = _pool(paire, n, noms_f, noms_c, TYPES_PAR_PALIER[palier])
    if not pool:
        return None
    choisis: list[dict] = []
    for indice in _ordre(pool, rng):
        if len(choisis) >= MAX_INDICES[palier]:
            return None
        choisis.append(indice)
        if len(choisis) >= MIN_INDICES[palier] and resoudre_par_deduction(choisis, n, noms_f, noms_c):
            return choisis
    return choisis if resoudre_par_deduction(choisis, n, noms_f, noms_c) else None


def _secours(paire, n: int, noms_f: list[str], noms_c: list[str],
             rng: random.Random) -> list[dict]:
    """Trois indices de secours vrais (aide progressive de l'interface)."""
    pool = _pool(paire, n, noms_f, noms_c, DIRECTS | RELATIONNELS)
    rng.shuffle(pool)
    return pool[:3]


def _item(palier: int, rang: int, paire, indices: list[dict], secours: list[dict],
          n: int, figures: list[str], couleurs: list[str]) -> dict:
    fig, coul = paire
    grille = [[figures[fig[i]], couleurs[coul[i]]] for i in range(n * n)]
    return {
        "id": "de-%d-%02d" % (palier, rang),
        "type": "grille-deduction",
        "module": "entrainement",
        "theme": "deduction",
        "fonctions_ciblees": ["fonctions-executives", "memoire-travail"],
        "palier": palier,
        "prerequis": [] if palier == 1 else ["de-palier-%d" % (palier - 1)],
        "cap_complexite": None,
        "contenu": {
            "consigne": ("Place les figures colorées. Chaque figure colorée (un carré bleu, un cercle rouge…) "
                         "apparaît une seule fois dans la grille. Méthode : note d'abord ce qui est certain, "
                         "barre ce qui devient impossible, puis recoupe les indices qui relient deux figures."),
            "figures": figures,
            "couleurs": couleurs,
            "enonces": indices,
            "indices": secours,
            "aide": ("Les indices suffisent : en les recoupant, chaque case se déduit. "
                     "Commence par ceux qui désignent une case précise."),
        },
        "reponse": {
            "valeur": ";".join("%s:%s" % (c[0], c[1]) for c in grille),
            "grille": grille,
        },
        "meta": {
            "auteur": AUTEUR,
            "date_creation": DATE_CREATION,
            "relecture_ortho": {"statut": "a_revoir"},
        },
    }


def generer_palier(palier: int, rng: random.Random, nombre: int,
                   deja_vus: set) -> list[dict]:
    """Grilles d'un palier : solutions distinctes dans tout le thème, chacune déductible."""
    n = 3 if palier <= 3 else 4
    figures, couleurs = FIGURES[:n], COULEURS[:n]
    univers = grilles_valides(n)
    ordre = list(range(len(univers)))
    rng.shuffle(ordre)

    items: list[dict] = []
    for rang_grille in ordre:
        if len(items) >= nombre:
            break
        paire = univers[rang_grille]
        if paire in deja_vus:
            continue
        for _ in range(8):
            indices = _selection(paire, n, figures, couleurs, palier, rng)
            if indices:
                deja_vus.add(paire)
                items.append(_item(palier, len(items) + 1, paire, indices,
                                   _secours(paire, n, figures, couleurs, rng),
                                   n, figures, couleurs))
                break
    if len(items) < nombre:
        raise SystemExit("palier %d : %d grilles seulement (univers épuisé)" % (palier, len(items)))
    return items


def _manifest(paliers: list[list[dict]]) -> dict:
    return {
        "theme": "deduction",
        "paliers": [
            {
                "id": "de-palier-%d" % numero,
                "description": DESCRIPTIONS[numero - 1],
                "prerequis": [] if numero == 1 else ["de-palier-%d" % (numero - 1)],
                "fichier": "paliers/palier-%02d.json" % numero,
                "nb_items": len(items),
            }
            for numero, items in enumerate(paliers, start=1)
        ],
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le thème « deduction ».")
    parseur.add_argument("--par-palier", type=int, default=PAR_PALIER_DEFAUT)
    parseur.add_argument("--dry-run", action="store_true")
    options = parseur.parse_args()

    rng = random.Random(GRAINE)
    deja_vus: set = set()
    paliers = [generer_palier(p, rng, options.par_palier, deja_vus) for p in (1, 2, 3, 4)]

    cibles = {BASE_SORTIE / "paliers.json": _manifest(paliers)}
    for numero, items in enumerate(paliers, start=1):
        cibles[BASE_SORTIE / "paliers" / ("palier-%02d.json" % numero)] = items

    for chemin, donnees in cibles.items():
        nb = len(donnees["paliers"]) if isinstance(donnees, dict) else len(donnees)
        if options.dry_run:
            print("[dry-run] %s (%s entrées)" % (chemin.relative_to(RACINE_DEPOT), nb))
        else:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("[écrit] %s (%s entrées)" % (chemin.relative_to(RACINE_DEPOT), nb))

    total = sum(len(p) for p in paliers)
    indices = [len(i["contenu"]["enonces"]) for p in paliers for i in p]
    print("Total : %d grilles, %d paliers, solutions distinctes : %d." % (total, len(paliers), len(deja_vus)))
    print("Indices par grille : min %d, max %d, moyenne %.1f." %
          (min(indices), max(indices), sum(indices) / len(indices)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
