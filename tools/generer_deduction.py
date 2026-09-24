#!/usr/bin/env python3
"""Génère le thème « deduction » — grilles logiques 3×3 et 4×4.

Règles du puzzle (ce qui le rend déductible) :
- une grille N×N contient N figures et N couleurs ;
- **chaque figure colorée** (une figure dans une couleur donnée, ex. « carré bleu »)
  apparaît **une seule fois** dans la grille ;
- les indices sont à **deux informations** : ils nomment une figure colorée et
  indiquent soit sa position, soit sa relation à une autre figure colorée
  (« le carré bleu est juste à gauche du rond rouge »). Comme chaque figure
  colorée est unique, ces phrases sont **non ambiguës**.

Garanties (le générateur échoue sinon) :
- la solution est un couple de carrés latins **orthogonaux** (chaque combinaison
  figure × couleur exactement une fois) ;
- chaque indice est vrai pour la solution ;
- les indices déterminent la solution de façon **unique** parmi toutes les grilles
  valides.

Usage :

    python3 tools/generer_deduction.py            # écrit le contenu
    python3 tools/generer_deduction.py --dry-run  # vérifie sans écrire
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
BASE_SORTIE = RACINE_DEPOT / "content" / "entrainement" / "deduction"

GRAINE: int = 20260924
DATE_CREATION: str = "2026-09-24"
AUTEUR: str = "generation-automatique (tools/generer_deduction.py)"

FIGURES = ["cercle", "carre", "triangle", "losange"]
COULEURS = ["rouge", "bleu", "vert", "jaune"]

NOMS_CASES_3 = [
    "en haut à gauche", "en haut au centre", "en haut à droite",
    "au milieu à gauche", "au centre", "au milieu à droite",
    "en bas à gauche", "en bas au centre", "en bas à droite",
]
NOMS_CASES_4 = [
    "en haut à gauche", "en haut, deuxième", "en haut, troisième", "en haut à droite",
    "deuxième ligne à gauche", "deuxième ligne, deuxième", "deuxième ligne, troisième", "deuxième ligne à droite",
    "troisième ligne à gauche", "troisième ligne, deuxième", "troisième ligne, troisième", "troisième ligne à droite",
    "en bas à gauche", "en bas, deuxième", "en bas, troisième", "en bas à droite",
]


def carres_latins(n: int) -> list[tuple[int, ...]]:
    """Tous les carrés latins N×N, aplatis en N² indices (ordre de lecture)."""
    resultats = []
    for lignes in itertools.product(itertools.permutations(range(n)), repeat=n):
        if all(sorted(lignes[r][c] for r in range(n)) == list(range(n)) for c in range(n)):
            resultats.append(tuple(lignes[r][c] for r in range(n) for c in range(n)))
    return resultats


def grilles_valides(n: int) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Couples (figures, couleurs) où chaque figure colorée est unique (orthogonaux)."""
    carres = carres_latins(n)
    valides = []
    for fig in carres:
        for coul in carres:
            if len({(fig[i], coul[i]) for i in range(n * n)}) == n * n:
                valides.append((fig, coul))
    return valides


def _cellule(fig: tuple, coul: tuple, f: int, c: int) -> int:
    """Case de la figure colorée (f, c) — unique par construction."""
    for i in range(len(fig)):
        if fig[i] == f and coul[i] == c:
            return i
    return -1


def _coins(n: int) -> set[int]:
    return {0, n - 1, n * (n - 1), n * n - 1}


def _bords(n: int) -> set[int]:
    return {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}


def _pred(indice: dict, paire, n: int, noms_f: list[str], noms_c: list[str]) -> bool:
    """Un indice est-il vrai pour cette grille ?"""
    fig, coul = paire
    t = indice["type"]
    if t == "regle":
        return True
    f = noms_f.index(indice["figure"])
    c = noms_c.index(indice["couleur"])
    case = _cellule(fig, coul, f, c)
    if case < 0:
        return False
    if t == "case":
        return case == indice["case"]
    if t == "ligne":
        return case // n == indice["ligne"]
    if t == "colonne":
        return case % n == indice["colonne"]
    if t == "pas-coin":
        return case not in _coins(n)
    if t == "pas-bord":
        return case not in _bords(n)
    if t.startswith("voisin-"):
        f2 = noms_f.index(indice["figure2"])
        c2 = noms_c.index(indice["couleur2"])
        autre = _cellule(fig, coul, f2, c2)
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
    raise ValueError(t)


def _pool(paire, n: int, noms_f: list[str], noms_c: list[str],
          autoriser_faibles: bool, autoriser_voisins: bool) -> list[dict]:
    """Indices vrais (deux informations chacun) pour cette grille."""
    fig, coul = paire
    pool: list[dict] = []
    for f, nom_f in enumerate(noms_f):
        for c, nom_c in enumerate(noms_c):
            case = _cellule(fig, coul, f, c)
            pool.append({"type": "case", "figure": nom_f, "couleur": nom_c, "case": case})
            if autoriser_faibles:
                if case not in _coins(n):
                    pool.append({"type": "pas-coin", "figure": nom_f, "couleur": nom_c})
                if case not in _bords(n):
                    pool.append({"type": "pas-bord", "figure": nom_f, "couleur": nom_c})
            if case // n < n:
                pool.append({"type": "ligne", "figure": nom_f, "couleur": nom_c, "ligne": case // n})
                pool.append({"type": "colonne", "figure": nom_f, "couleur": nom_c, "colonne": case % n})
            if autoriser_voisins:
                r, col = divmod(case, n)
                if col + 1 < n:
                    f2, c2 = fig[case + 1], coul[case + 1]
                    pool.append({"type": "voisin-gauche", "figure": noms_f[f2], "couleur": noms_c[c2],
                                 "figure2": nom_f, "couleur2": nom_c})
                if col > 0:
                    f2, c2 = fig[case - 1], coul[case - 1]
                    pool.append({"type": "voisin-droite", "figure": noms_f[f2], "couleur": noms_c[c2],
                                 "figure2": nom_f, "couleur2": nom_c})
                if r + 1 < n:
                    f2, c2 = fig[case + n], coul[case + n]
                    pool.append({"type": "voisin-dessus", "figure": noms_f[f2], "couleur": noms_c[c2],
                                 "figure2": nom_f, "couleur2": nom_c})
                if r > 0:
                    f2, c2 = fig[case - n], coul[case - n]
                    pool.append({"type": "voisin-dessous", "figure": noms_f[f2], "couleur": noms_c[c2],
                                 "figure2": nom_f, "couleur2": nom_c})
    return pool


def _selection(paire, n: int, noms_f: list[str], noms_c: list[str], palier: int,
               rng: random.Random) -> list[dict] | None:
    """Indices déterminant UNIQUEMENT cette grille, avec la saveur du palier."""
    valides = grilles_valides(n)
    faibles = palier >= 3
    voisins = palier >= 2
    budget = 6 if n == 3 else 8
    types_autorises = {"case", "ligne", "colonne", "regle"}
    if voisins:
        types_autorises |= {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous"}
    if faibles:
        types_autorises |= {"pas-coin", "pas-bord"}

    pool = [i for i in _pool(paire, n, noms_f, noms_c, faibles, voisins)
            if i["type"] in types_autorises]

    def glouton(melange: list[dict]) -> list[dict] | None:
        actuel = valides[:]
        choisis: list[dict] = []
        for indice in melange:
            if len(choisis) >= budget:
                break
            filtres = [x for x in actuel if _pred(indice, x, n, noms_f, noms_c)]
            if len(filtres) < len(actuel):
                choisis.append(indice)
                actuel = filtres
                if len(actuel) == 1:
                    break
        if len(actuel) != 1:
            return None
        while len(choisis) < budget:
            choisis.append({"type": "regle", "variante": len(choisis) % 2})
        return choisis

    for _ in range(300):
        rng.shuffle(pool)
        resultat = glouton(pool)
        if resultat is not None:
            return resultat
    return None


def _secours(paire, n: int, noms_f: list[str], noms_c: list[str]) -> list[dict]:
    """Trois indices de secours vrais (deux informations), hors indices principaux."""
    pool = _pool(paire, n, noms_f, noms_c, True, True)
    return pool[:3] if len(pool) >= 3 else pool


def _generer(palier: int, rng: random.Random) -> dict | None:
    """Une grille du palier (solution + indices à deux informations + secours)."""
    n = 3 if palier <= 3 else 4
    figures, couleurs = FIGURES[:n], COULEURS[:n]
    valides = grilles_valides(n)
    paire = valides[rng.randrange(len(valides))]
    indices = _selection(paire, n, figures, couleurs, palier, rng)
    if indices is None:
        return None
    fig, coul = paire
    grille = [[figures[fig[i]], couleurs[coul[i]]] for i in range(n * n)]
    return {
        "id": "de-%d-00" % palier,
        "type": "grille-deduction",
        "module": "entrainement",
        "theme": "deduction",
        "fonctions_ciblees": ["fonctions-executives", "memoire-travail"],
        "palier": palier,
        "prerequis": [] if palier == 1 else ["de-palier-%d" % (palier - 1)],
        "cap_complexite": None,
        "contenu": {
            "consigne": ("Place les figures colorées en recoupant les indices. Chaque figure colorée "
                         "(un carré bleu, un rond rouge…) apparaît une seule fois dans la grille."),
            "figures": figures,
            "couleurs": couleurs,
            "enonces": indices,
            "indices": _secours(paire, n, figures, couleurs),
            "aide": "Chaque indice donne deux informations : la figure colorée et sa place. Commence par celles qui désignent une case.",
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


def generer_palier(palier: int, rng: random.Random, nombre: int) -> list[dict]:
    items, essais = [], 0
    while len(items) < nombre:
        essais += 1
        if essais > 4000:
            raise SystemExit("échec : palier %d introuvable" % palier)
        candidat = _generer(palier, rng)
        if candidat is None:
            continue
        candidat["id"] = "de-%d-%02d" % (palier, len(items) + 1)
        items.append(candidat)
    return items


def _manifest(paliers: list[list[dict]]) -> dict:
    descriptions = [
        "Indices de position (chaque phrase donne la figure colorée et sa case)",
        "Indices de ligne et de colonne à recouper",
        "Indices de voisinage : deux figures colorées reliées entre elles",
        "Grille 4×4 : plus de figures colorées et d'indices",
    ]
    return {
        "theme": "deduction",
        "paliers": [
            {
                "id": "de-palier-%d" % numero,
                "description": descriptions[numero - 1],
                "prerequis": [] if numero == 1 else ["de-palier-%d" % (numero - 1)],
                "fichier": "paliers/palier-%02d.json" % numero,
                "nb_items": len(items),
            }
            for numero, items in enumerate(paliers, start=1)
        ],
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le thème « deduction ».")
    parseur.add_argument("--dry-run", action="store_true")
    options = parseur.parse_args()

    rng = random.Random(GRAINE)
    paliers = [generer_palier(p, rng, 4) for p in (1, 2, 3, 4)]

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
    print("Total : %d grilles, %d paliers." % (sum(len(p) for p in paliers), len(paliers)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
