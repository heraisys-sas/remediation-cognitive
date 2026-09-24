#!/usr/bin/env python3
"""Génère le thème « deduction » — grilles logiques 3×3 et 4×4 (figures × couleurs).

Exercice de raisonnement déductif : une grille N×N contient N figures et N
couleurs, chaque figure et chaque couleur apparaissant une fois par ligne et
par colonne (carré latin). Des indices, à **recouper**, guident le placement.

Garanties (le générateur échoue s'il ne peut pas les tenir) :
- chaque indice est vrai pour la solution ;
- les indices déterminent la solution de façon UNIQUE ;
- des **indices de secours** (``contenu.indices``) sont fournis pour l'interface
  « Un indice », en plus des indices principaux.

Les indices sont structurés (type + paramètres) : l'interface les formule en
français, le validateur les vérifie sans rien interpréter.

Dimensions et paliers :
- paliers 1 à 3 : grille 3×3 (3 figures × 3 couleurs), 6 indices ;
- palier 4 : grille 4×4 (4 figures × 4 couleurs), 12 indices.

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
NOMS_LIGNES_3 = ["du haut", "du milieu", "du bas"]
NOMS_COLONNES_3 = ["de gauche", "du centre", "de droite"]

NOMS_CASES_4 = [
    "en haut à gauche", "en haut, deuxième", "en haut, troisième", "en haut à droite",
    "deuxième ligne à gauche", "deuxième ligne, deuxième", "deuxième ligne, troisième", "deuxième ligne à droite",
    "troisième ligne à gauche", "troisième ligne, deuxième", "troisième ligne, troisième", "troisième ligne à droite",
    "en bas à gauche", "en bas, deuxième", "en bas, troisième", "en bas à droite",
]
NOMS_LIGNES_4 = ["du haut", "de la deuxième", "de la troisième", "du bas"]
NOMS_COLONNES_4 = ["de gauche", "de la deuxième", "de la troisième", "de droite"]


def carres_latins(n: int) -> list[tuple[int, ...]]:
    """Tous les carrés latins N×N, aplatis en N² indices (ordre de lecture)."""
    resultats = []
    for lignes in itertools.product(itertools.permutations(range(n)), repeat=n):
        if all(sorted(lignes[r][c] for r in range(n)) == list(range(n)) for c in range(n)):
            resultats.append(tuple(lignes[r][c] for r in range(n) for c in range(n)))
    return resultats


def coin(n: int) -> set[int]:
    return {0, n - 1, n * (n - 1), n * n - 1}


def bord(n: int) -> set[int]:
    return {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}


# --- Indices ---------------------------------------------------------------


def _pred(indice: dict, g: tuple, n: int, noms: list[str]) -> bool:
    """Un indice est-il vrai pour le carré latin g (aplati, indices 0..n-1) ?"""
    t = indice["type"]
    if t == "regle":
        return True
    valeur = noms.index(indice.get("figure") or indice.get("couleur"))
    if t.startswith("case-"):
        return g[indice["case"]] == valeur
    if t == "ligne":
        return valeur in (g[indice["ligne"] * n + c] for c in range(n))
    if t == "colonne":
        return valeur in (g[r * n + indice["colonne"]] for r in range(n))
    if t.startswith("coin-"):
        return any(g[i] == valeur for i in coin(n))
    if t.startswith("bord-"):
        return any(g[i] == valeur for i in bord(n))
    if t.startswith("pas-"):
        return g[indice["case"]] != valeur
    raise ValueError(t)


def _pool(g: tuple, n: int, noms: list[str], figure: bool, autoriser_faibles: bool) -> list[dict]:
    """Tous les indices vrais pour ce carré (dimension figure ou couleur)."""
    pool: list[dict] = []
    cle_nom = "figure" if figure else "couleur"
    base = "figure" if figure else "couleur"
    for case in range(n * n):
        pool.append({"type": f"case-{base}", "case": case, cle_nom: noms[g[case]]})
        if autoriser_faibles:
            for autre in noms:
                if autre != noms[g[case]]:
                    pool.append({"type": f"pas-{base}", "case": case, cle_nom: autre})
    for nom in noms:
        v = noms.index(nom)
        if figure:
            for ligne in range(n):
                if v in (g[ligne * n + c] for c in range(n)):
                    pool.append({"type": "ligne", "figure": nom, "ligne": ligne})
        else:
            for colonne in range(n):
                if v in (g[r * n + colonne] for r in range(n)):
                    pool.append({"type": "colonne", "couleur": nom, "colonne": colonne})
        if autoriser_faibles:
            if any(g[i] == v for i in coin(n)):
                pool.append({"type": f"coin-{base}", cle_nom: nom})
            if any(g[i] == v for i in bord(n)):
                pool.append({"type": f"bord-{base}", cle_nom: nom})
    return pool


def _indices_dimension(g: tuple, n: int, noms: list[str], figure: bool,
                       autoriser_faibles: bool, budget: int,
                       rng: random.Random) -> list[dict] | None:
    """Indices de cette dimension qui déterminent UNIQUEMENT g parmi les carrés latins."""
    carres = carres_latins(n)
    pool = _pool(g, n, noms, figure, autoriser_faibles)

    def glouton(pool_melange: list[dict]) -> list[dict] | None:
        actuel = carres[:]
        choisis: list[dict] = []
        for indice in pool_melange:
            if len(choisis) >= budget:
                break
            filtres = [x for x in actuel if _pred(indice, x, n, noms)]
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

    for _ in range(200):
        rng.shuffle(pool)
        resultat = glouton(pool)
        if resultat is not None:
            return resultat
    return None


def _secours(g: tuple, n: int, noms: list[str], figure: bool, exclus: list[dict]) -> list[dict]:
    """Trois indices de secours vrais, non présents dans les indices principaux."""
    pool = _pool(g, n, noms, figure, True)
    def cle(indice): return json.dumps(indice, sort_keys=True)
    exclues = {cle(i) for i in exclus}
    disponibles = [i for i in pool if cle(i) not in exclues]
    # On préfère des indices informatifs (case / ligne / colonne) pour le secours.
    informatifs = [i for i in disponibles if i["type"].startswith("case-") or i["type"] in ("ligne", "colonne")]
    autres = [i for i in disponibles if i not in informatifs]
    return (informatifs + autres)[:3]


def _unique(indices: list[dict], n: int, noms: list[str]) -> bool:
    """Ces indices déterminent-ils UNE seule solution parmi les carrés latins ?"""
    carres = carres_latins(n)
    restants = [x for x in carres if all(_pred(i, x, n, noms) for i in indices)]
    return len(restants) == 1


def _injecter(choisis: list[dict], g: tuple, n: int, noms: list[str],
              figure: bool, types_voulus: tuple[str, ...]) -> list[dict]:
    """Remplace un indice direct par un indice du type voulu, si l'unicité tient."""
    if any(i["type"] in types_voulus for i in choisis):
        return choisis
    pool = _pool(g, n, noms, figure, True)
    directs = [i for i in choisis if i["type"].startswith("case-")]
    for direct in directs:
        for candidat in pool:
            if candidat["type"] not in types_voulus or candidat in choisis:
                continue
            nouveau = [candidat if i is direct else i for i in choisis]
            if _unique(nouveau, n, noms):
                return nouveau
    return choisis


def _generer(palier: int, rng: random.Random) -> dict | None:
    """Une grille du palier (solution + indices principaux + indices de secours)."""
    n = 3 if palier <= 3 else 4
    figures = FIGURES[:n]
    couleurs = COULEURS[:n]
    autoriser_faibles = palier in (3, 4)
    budget = 3 if n == 3 else 6

    carres = carres_latins(n)
    fig = carres[rng.randrange(len(carres))]
    coul = carres[rng.randrange(len(carres))]

    indices_fig = _indices_dimension(fig, n, figures, True, autoriser_faibles, budget, rng)
    if indices_fig is None:
        return None
    indices_coul = _indices_dimension(coul, n, couleurs, False, autoriser_faibles, budget, rng)
    if indices_coul is None:
        return None

    # Saveur du palier : relationnel (ligne/colonne) au palier 2, position
    # (coin/bord) au palier 3 — injectée seulement si l'unicité est préservée.
    if palier == 2:
        indices_fig = _injecter(indices_fig, fig, n, figures, True, ("ligne",))
        indices_coul = _injecter(indices_coul, coul, n, couleurs, False, ("colonne",))
    if palier == 3:
        indices_fig = _injecter(indices_fig, fig, n, figures, True, ("coin-figure", "bord-figure"))
        indices_coul = _injecter(indices_coul, coul, n, couleurs, False, ("coin-couleur", "bord-couleur"))

    enonces = indices_fig + indices_coul
    secours = _secours(fig, n, figures, True, indices_fig) + _secours(coul, n, couleurs, False, indices_coul)

    grille = [[figures[fig[i]], couleurs[coul[i]]] for i in range(n * n)]
    valeur = ";".join(f"{c[0]}:{c[1]}" for c in grille)
    return {
        "id": f"de-{palier}-{0:02d}",  # renuméroté par l'appelant
        "type": "grille-deduction",
        "module": "entrainement",
        "theme": "deduction",
        "fonctions_ciblees": ["fonctions-executives", "memoire-travail"],
        "palier": palier,
        "prerequis": [] if palier == 1 else [f"de-palier-{palier - 1}"],
        "cap_complexite": None,
        "contenu": {
            "consigne": "Place les figures et les couleurs en recoupant les indices. Chaque figure et chaque couleur apparaît une fois par ligne et par colonne.",
            "figures": figures,
            "couleurs": couleurs,
            "enonces": enonces,
            "indices": secours,
            "aide": "Commence par les indices qui désignent une case précise, puis recoupe avec les autres.",
        },
        "reponse": {"valeur": valeur, "grille": grille},
        "meta": {
            "auteur": AUTEUR,
            "date_creation": DATE_CREATION,
            "relecture_ortho": {"statut": "a_revoir"},
        },
    }


def generer_palier(palier: int, rng: random.Random, nombre: int) -> list[dict]:
    items = []
    essais = 0
    while len(items) < nombre:
        essais += 1
        if essais > 3000:
            raise SystemExit(f"échec : palier {palier} introuvable dans le budget d'essais")
        candidat = _generer(palier, rng)
        if candidat is None:
            continue
        candidat["id"] = f"de-{palier}-{len(items) + 1:02d}"
        items.append(candidat)
    return items


def _manifest(paliers: list[list[dict]]) -> dict:
    return {
        "theme": "deduction",
        "paliers": [
            {
                "id": f"de-palier-{numero}",
                "description": [
                    "Indices directs, peu de recoupements",
                    "Indices de ligne et de colonne à recouper",
                    "Indices négatifs : éliminer pour déduire",
                    "Grille 4×4 : plus de figures, de couleurs et d'indices",
                ][numero - 1],
                "prerequis": [] if numero == 1 else [f"de-palier-{numero - 1}"],
                "fichier": f"paliers/palier-{numero:02d}.json",
                "nb_items": len(items),
            }
            for numero, items in enumerate(paliers, start=1)
        ],
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le thème « deduction ».")
    parseur.add_argument("--dry-run", action="store_true", help="vérifier sans écrire")
    options = parseur.parse_args()

    rng = random.Random(GRAINE)
    paliers = [
        generer_palier(1, rng, 4),
        generer_palier(2, rng, 4),
        generer_palier(3, rng, 4),
        generer_palier(4, rng, 4),
    ]

    cibles = {BASE_SORTIE / "paliers.json": _manifest(paliers)}
    for numero, items in enumerate(paliers, start=1):
        cibles[BASE_SORTIE / "paliers" / f"palier-{numero:02d}.json"] = items

    for chemin, donnees in cibles.items():
        nb = len(donnees["paliers"]) if isinstance(donnees, dict) else len(donnees)
        if options.dry_run:
            print(f"[dry-run] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
        else:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[écrit] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
    total = sum(len(p) for p in paliers)
    print(f"Total : {total} grilles, {len(paliers)} paliers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
