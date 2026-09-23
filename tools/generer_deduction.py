#!/usr/bin/env python3
"""Génère le thème « deduction » — grille 3×3 (3 figures × 3 couleurs).

Exercice de raisonnement déductif : une grille 3×3 doit contenir les trois
figures (cercle, carré, triangle) et les trois couleurs (rouge, bleu, vert),
chaque figure et chaque couleur apparaissant une fois par ligne et par colonne
(carré latin). Six indices, à **recouper** pour reconstruire la solution, guident
le placement.

Garanties (vérifiées par le solveur intégré, sinon la génération échoue) :
- chaque indice est VRAI pour la solution ;
- les six indices déterminent la solution de façon UNIQUE (aucune ambiguïté).

Les indices sont des données structurées (type + paramètres) : l'interface les
formule en français, le validateur les vérifie sans rien interpréter.

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

FIGURES = ["cercle", "carre", "triangle"]
COULEURS = ["rouge", "bleu", "vert"]
NOMS_CASES = [
    "en haut à gauche", "en haut au centre", "en haut à droite",
    "au milieu à gauche", "au centre", "au milieu à droite",
    "en bas à gauche", "en bas au centre", "en bas à droite",
]
NOMS_LIGNES = ["du haut", "du milieu", "du bas"]
NOMS_COLONNES = ["de gauche", "du centre", "de droite"]


def carres_latins() -> list[tuple[int, ...]]:
    """Les 12 carrés latins 3×3, APLATIS en 9 indices (ordre de lecture)."""
    resultats = []
    for lignes in itertools.product(itertools.permutations([0, 1, 2]), repeat=3):
        if all(sorted(lignes[r][c] for r in range(3)) == [0, 1, 2] for c in range(3)):
            resultats.append(tuple(lignes[r][c] for r in range(3) for c in range(3)))
    return resultats


# --- Indices structurés -------------------------------------------------------


def _predicat(indice, fig: tuple, coul: tuple) -> bool:
    """Un indice est-il vrai pour la grille (fig, coul) ? (fig/coul : 9 indices)."""
    t = indice["type"]
    if t == "case-couleur":
        return coul[indice["case"]] == COULEURS.index(indice["couleur"])
    if t == "case-figure":
        return fig[indice["case"]] == FIGURES.index(indice["figure"])
    if t == "ligne":
        return FIGURES.index(indice["figure"]) in (fig[indice["ligne"] * 3 + c] for c in range(3))
    if t == "colonne":
        return COULEURS.index(indice["couleur"]) in (coul[r * 3 + indice["colonne"]] for r in range(3))
    if t == "meme-ligne":
        i_f = fig.index(FIGURES.index(indice["figure"]))
        i_c = coul.index(COULEURS.index(indice["couleur"]))
        return i_f // 3 == i_c // 3
    if t == "meme-colonne":
        i_f = fig.index(FIGURES.index(indice["figure"]))
        i_c = coul.index(COULEURS.index(indice["couleur"]))
        return i_f % 3 == i_c % 3
    if t == "pas-couleur":
        return coul[indice["case"]] != COULEURS.index(indice["couleur"])
    if t == "pas-figure":
        return fig[indice["case"]] != FIGURES.index(indice["figure"])
    if t == "regle":
        return True
    raise ValueError(t)


def _indice_case_figure(case, figure):
    return {"type": "case-figure", "case": case, "figure": figure}


def _indice_case_couleur(case, couleur):
    return {"type": "case-couleur", "case": case, "couleur": couleur}


def _indice_meme_ligne(figure, couleur):
    return {"type": "meme-ligne", "figure": figure, "couleur": couleur}


def _indice_meme_colonne(figure, couleur):
    return {"type": "meme-colonne", "figure": figure, "couleur": couleur}


def _indice_ligne(figure, ligne):
    return {"type": "ligne", "figure": figure, "ligne": ligne}


def _indice_colonne(couleur, colonne):
    return {"type": "colonne", "couleur": couleur, "colonne": colonne}


def _indice_pas_couleur(case, couleur):
    return {"type": "pas-couleur", "case": case, "couleur": couleur}


def _indice_pas_figure(case, figure):
    return {"type": "pas-figure", "case": case, "figure": figure}


def _indice_regle(variante):
    return {"type": "regle", "variante": variante}


def construire_pool(fig: tuple, coul: tuple, autoriser_negatifs: bool) -> list[dict]:
    """Tous les indices vrais (et les négatifs autorisés) pour la solution."""
    pool: list[dict] = []
    for case in range(9):
        pool.append(_indice_case_figure(case, FIGURES[fig[case]]))
        pool.append(_indice_case_couleur(case, COULEURS[coul[case]]))
        if autoriser_negatifs:
            for autre in COULEURS:
                if autre != COULEURS[coul[case]]:
                    pool.append(_indice_pas_couleur(case, autre))
            for autre in FIGURES:
                if autre != FIGURES[fig[case]]:
                    pool.append(_indice_pas_figure(case, autre))
    for figure in FIGURES:
        for ligne in range(3):
            probe = {"type": "ligne", "figure": figure, "ligne": ligne}
            if _predicat(probe, fig, coul):
                pool.append(probe)
    for couleur in COULEURS:
        for colonne in range(3):
            probe = {"type": "colonne", "couleur": couleur, "colonne": colonne}
            if _predicat(probe, fig, coul):
                pool.append(probe)
    return pool


def _pool_par_palier(fig: tuple, coul: tuple, palier: int) -> list[dict]:
    """Pool d'indices autorisés selon le palier (progression de difficulté)."""
    pool = construire_pool(fig, coul, palier >= 3)
    if palier == 1:
        return [i for i in pool if i["type"] in ("case-figure", "case-couleur", "regle")]
    if palier == 2:
        return [i for i in pool if not i["type"].startswith("pas-")]
    return pool


def _survivants(indices: list[dict], toutes) -> list | None:
    """Solutions restantes pour ces indices ; None si elles ne sont pas uniques."""
    restants = [(f, c) for (f, c) in toutes if all(_predicat(i, f, c) for i in indices)]
    return restants if len(restants) == 1 else None


def _injecter(choisis: list[dict], pool: list[dict], types: tuple[str, ...], toutes) -> list[dict]:
    """Remplace un indice direct par un indice de « saveur », si l'unicité tient."""
    if any(i["type"] in types for i in choisis):
        return choisis
    directs = [i for i in choisis if i["type"] in ("case-figure", "case-couleur")]
    for direct in directs:
        for candidat in pool:
            if candidat["type"] not in types or candidat in choisis:
                continue
            nouveau = [candidat if i is direct else i for i in choisis]
            if _survivants(nouveau, toutes) is not None:
                return nouveau
    return choisis


def select_indices(fig: tuple, coul: tuple, palier: int,
                   rng: random.Random) -> list[dict] | None:
    """Six indices qui déterminent UNIQUEMENT la solution, avec la saveur du palier."""
    carres = carres_latins()
    toutes = [(f, c) for f in carres for c in carres]
    pool = _pool_par_palier(fig, coul, palier)

    def glouton(pool_melange: list[dict]) -> list[dict] | None:
        actuel = toutes[:]
        choisis: list[dict] = []
        for indice in pool_melange:
            if len(choisis) >= 6:
                break
            filtres = [(f, c) for (f, c) in actuel if _predicat(indice, f, c)]
            if len(filtres) < len(actuel):
                choisis.append(indice)
                actuel = filtres
                if len(actuel) == 1:
                    break
        if len(actuel) != 1:
            return None
        while len(choisis) < 6:
            choisis.append(_indice_regle(len(choisis) % 2))
        return choisis

    for _ in range(400):
        rng.shuffle(pool)
        resultat = glouton(pool)
        if resultat is None:
            continue
        if palier == 2:
            resultat = _injecter(resultat, pool, ("ligne", "colonne"), toutes)
        if palier == 3:
            resultat = _injecter(resultat, pool, ("pas-couleur", "pas-figure"), toutes)
        return resultat
    return None


def generer_palier(palier: int, rng: random.Random) -> list[dict]:
    """4 grilles du palier (chaque grille : solution + 6 indices uniques)."""
    carres = carres_latins()
    items = []
    essais = 0
    while len(items) < 4:
        essais += 1
        if essais > 1500:
            raise SystemExit("échec : aucune grille unique trouvée dans le budget d'essais")
        fig = carres[rng.randrange(len(carres))]
        coul = carres[rng.randrange(len(carres))]
        indices = select_indices(fig, coul, palier, rng)
        if indices is None:
            continue
        grille = [
            [FIGURES[fig[i]], COULEURS[coul[i]]] for i in range(9)
        ]
        valeur = ";".join(f"{g[0]}:{g[1]}" for g in grille)
        items.append({
            "id": f"de-{palier}-{len(items) + 1:02d}",
            "type": "grille-deduction",
            "module": "entrainement",
            "theme": "deduction",
            "fonctions_ciblees": ["fonctions-executives", "memoire-travail"],
            "palier": palier,
            "prerequis": [] if palier == 1 else [f"de-palier-{palier - 1}"],
            "cap_complexite": None,
            "contenu": {
                "consigne": "Place les trois figures et les trois couleurs en recoupant les indices. Chaque figure et chaque couleur apparaît une fois par ligne et par colonne.",
                "figures": FIGURES,
                "couleurs": COULEURS,
                "enonces": indices,
                "aide": "Commence par les indices qui désignent une case précise, puis recoupe avec les autres.",
            },
            "reponse": {"valeur": valeur, "grille": grille},
            "meta": {
                "auteur": AUTEUR,
                "date_creation": DATE_CREATION,
                "relecture_ortho": {"statut": "a_revoir"},
            },
        })
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
                    "Indices négatifs : il faut éliminer pour déduire",
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
    paliers = [generer_palier(p, rng) for p in (1, 2, 3)]

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
