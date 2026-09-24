#!/usr/bin/env python3
"""Génère le thème « deduction » — grilles logiques 3×3 et 4×4.

Méthode suivie (puzzles de logique classiques) :
- une grille N×N, N figures et N couleurs ; **chaque figure colorée** (carré bleu,
  cercle rouge…) apparaît **une seule fois** — c'est ce qui rend chaque phrase
  non ambiguë et ce qui autorise des indices à **deux informations** ;
- les indices couvrent la taxonomie classique : direct (`case`), de ligne/colonne,
  relationnel (`voisin`, `comparaison`, `autre-ligne`, `autre-colonne`), négatif
  (`pas-coin`, `pas-bord`, `ni-ni`) et conditionnel (`si-alors`) ;
- **aucun indice redondant ni trivial** : les indices servent tous à lever une
  ambiguïté (le générateur ne complète pas avec des phrases décoratives) ;
- la solution est **unique** (vérifiée); la règle générale est rappelée dans la
  consigne, pas répétée comme un indice.

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

#: Nombre minimal d'indices par palier (un puzzle trop court est trivial).
MIN_INDICES = {1: 4, 2: 4, 3: 5, 4: 6}
#: Plafond d'indices par palier (lisibilité).
MAX_INDICES = {1: 6, 2: 6, 3: 7, 4: 9}


def carres_latins(n: int) -> list[tuple[int, ...]]:
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


def _cellule(fig: tuple, coul: tuple, f: int, c: int) -> int:
    for i in range(len(fig)):
        if fig[i] == f and coul[i] == c:
            return i
    return -1


def _coins(n: int) -> set[int]:
    return {0, n - 1, n * (n - 1), n * n - 1}


def _bords(n: int) -> set[int]:
    return {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}


def _pred(indice: dict, paire, n: int, noms_f: list[str], noms_c: list[str]) -> bool:
    """Un indice (deux informations) est-il vrai pour cette grille ?"""
    fig, coul = paire
    t = indice["type"]
    if t == "regle":
        return True
    f = noms_f.index(indice["figure"])
    c = noms_c.index(indice["couleur"])
    case = _cellule(fig, coul, f, c)
    if case < 0:
        return False
    coins, bords = _coins(n), _bords(n)
    if t == "case":
        return case == indice["case"]
    if t == "ligne":
        return case // n == indice["ligne"]
    if t == "colonne":
        return case % n == indice["colonne"]
    if t == "pas-coin":
        return case not in coins
    if t == "pas-bord":
        return case not in bords
    if t == "ni-ni":
        return case not in coins and case not in bords

    f2 = noms_f.index(indice["figure2"])
    c2 = noms_c.index(indice["couleur2"])
    autre = _cellule(fig, coul, f2, c2)
    if autre < 0:
        return False
    if t == "voisin-gauche":
        # « Le X est juste à gauche du Y » : Y est la case à droite de X.
        return autre == case + 1 and case % n != n - 1
    if t == "voisin-droite":
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
        # Si la première figure colorée est dans un coin, la seconde est sur le bord.
        return case not in coins or autre in bords
    raise ValueError(t)


def _indice_fc(type_indice: str, nom_f: str, nom_c: str, **extra) -> dict:
    return {"type": type_indice, "figure": nom_f, "couleur": nom_c, **extra}


def _pool(paire, n: int, noms_f: list[str], noms_c: list[str], types: set[str]) -> list[dict]:
    """Indices vrais (deux informations) dont le type est autorisé pour ce palier."""
    fig, coul = paire
    pool: list[dict] = []
    for f, nom_f in enumerate(noms_f):
        for c, nom_c in enumerate(noms_c):
            case = _cellule(fig, coul, f, c)
            if "case" in types:
                pool.append(_indice_fc("case", nom_f, nom_c, case=case))
            if "ligne" in types:
                pool.append(_indice_fc("ligne", nom_f, nom_c, ligne=case // n))
            if "colonne" in types:
                pool.append(_indice_fc("colonne", nom_f, nom_c, colonne=case % n))
            if "pas-coin" in types and case not in _coins(n):
                pool.append(_indice_fc("pas-coin", nom_f, nom_c))
            if "pas-bord" in types and case not in _bords(n):
                pool.append(_indice_fc("pas-bord", nom_f, nom_c))
            if "ni-ni" in types and case not in _coins(n) and case not in _bords(n):
                pool.append(_indice_fc("ni-ni", nom_f, nom_c))
    # Indices à deux figures colorées.
    types_paires = {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
                    "autre-ligne", "autre-colonne", "comparaison", "si-alors"} & types
    if types_paires:
        for f1, nom_f1 in enumerate(noms_f):
            for c1, nom_c1 in enumerate(noms_c):
                case1 = _cellule(fig, coul, f1, c1)
                for f2, nom_f2 in enumerate(noms_f):
                    for c2, nom_c2 in enumerate(noms_c):
                        if (f1, c1) == (f2, c2):
                            continue
                        case2 = _cellule(fig, coul, f2, c2)
                        base = dict(figure2=nom_f2, couleur2=nom_c2)
                        r1, col1 = divmod(case1, n)
                        r2, col2 = divmod(case2, n)
                        if "voisin-gauche" in types and case2 == case1 + 1 and col1 != n - 1:
                            pool.append(_indice_fc("voisin-gauche", nom_f1, nom_c1, **base))
                        if "voisin-droite" in types and case2 == case1 - 1 and col1 != 0:
                            pool.append(_indice_fc("voisin-droite", nom_f1, nom_c1, **base))
                        if "voisin-dessous" in types and case2 == case1 + n:
                            pool.append(_indice_fc("voisin-dessous", nom_f1, nom_c1, **base))
                        if "voisin-dessus" in types and case2 == case1 - n:
                            pool.append(_indice_fc("voisin-dessus", nom_f1, nom_c1, **base))
                        if "autre-ligne" in types and r1 != r2:
                            pool.append(_indice_fc("autre-ligne", nom_f1, nom_c1, **base))
                        if "autre-colonne" in types and col1 != col2:
                            pool.append(_indice_fc("autre-colonne", nom_f1, nom_c1, **base))
                        if "comparaison" in types and r1 == r2 and case1 < case2:
                            pool.append(_indice_fc("comparaison", nom_f1, nom_c1, **base))
                        if "si-alors" in types and (case1 not in _coins(n) or case2 in _bords(n)):
                            pool.append(_indice_fc("si-alors", nom_f1, nom_c1, **base))
    return pool


def _selection(paire, n: int, noms_f: list[str], noms_c: list[str], palier: int,
               rng: random.Random) -> list[dict] | None:
    """Indices nécessaires et suffisants (aucun indice décoratif)."""
    valides = grilles_valides(n)
    types = {"case", "ligne", "colonne"}
    if palier >= 2:
        types |= {"comparaison", "autre-ligne", "autre-colonne",
                  "voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous"}
    if palier >= 3:
        types |= {"pas-coin", "pas-bord", "ni-ni", "si-alors"}
    pool = _pool(paire, n, noms_f, noms_c, types)

    def glouton(melange: list[dict]) -> list[dict]:
        actuel = valides[:]
        choisis: list[dict] = []
        for indice in melange:
            if len(choisis) >= MAX_INDICES[palier]:
                break
            filtres = [x for x in actuel if _pred(indice, x, n, noms_f, noms_c)]
            if len(filtres) < len(actuel):
                choisis.append(indice)
                actuel = filtres
                if len(actuel) == 1:
                    break
        return choisis if len(actuel) == 1 and actuel[0] == paire else []

    meilleur: list[dict] = []
    for _ in range(300):
        rng.shuffle(pool)
        choisis = glouton(pool)
        if not choisis:
            continue
        if len(choisis) >= MIN_INDICES[palier]:
            return choisis
        if len(choisis) > len(meilleur):
            meilleur = choisis
    return meilleur or None


def _secours(paire, n: int, noms_f: list[str], noms_c: list[str]) -> list[dict]:
    """Trois indices de secours vrais (deux informations), pour l'aide progressive."""
    types = {"case", "ligne", "colonne", "comparaison", "autre-ligne", "autre-colonne"}
    pool = _pool(paire, n, noms_f, noms_c, types)
    return pool[:3]


def _generer(palier: int, rng: random.Random) -> dict | None:
    n = 3 if palier <= 3 else 4
    figures, couleurs = FIGURES[:n], COULEURS[:n]
    valides = grilles_valides(n)
    paire = valides[rng.randrange(len(valides))]
    indices = _selection(paire, n, figures, couleurs, palier, rng)
    if not indices:
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
            "consigne": ("Place les figures colorées. Chaque figure colorée (un carré bleu, un cercle rouge…) "
                         "apparaît une seule fois dans la grille. Méthode : note d'abord ce qui est certain, "
                         "barre ce qui devient impossible, puis recoupe les indices qui relient deux figures."),
            "figures": figures,
            "couleurs": couleurs,
            "enonces": indices,
            "indices": _secours(paire, n, figures, couleurs),
            "aide": "Commence par les indices les plus précis (ceux qui nomment une case), puis déduis le reste.",
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
        if essais > 6000:
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
        "Indices relationnels : voisinage, à gauche de, pas sur la même ligne",
        "Indices négatifs et conditionnels : éliminer et enchaîner (« si… alors »)",
        "Grille 4×4 : plus de figures colorées, indices variés",
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
