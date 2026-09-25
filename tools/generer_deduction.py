#!/usr/bin/env python3
"""Génère le thème « deduction » — grilles logiques 3×3 et 4×4, garanties déductibles.

Méthode (ce qui la rend fiable) :
1. l'univers des solutions est fini et connu (72 grilles 3×3, 6 912 en 4×4) ;
2. pour chaque solution encore libre, on ajoute des **phrases à deux informations**
   une par une — en privilégiant les figures encore peu citées — en rejouant à chaque
   fois le **solveur de déduction** (`deduction_commun`) ;
3. on s'arrête dès que le puzzle est résoluble **par propagation, sans hypothèse**, puis
   on complète jusqu'au plancher du palier ; au-delà du plafond, la solution est écartée ;
4. une même solution n'est jamais resservie deux fois dans le thème.

Ce qui fait qu'une phrase **provoque une déduction** :
- palier 1 : chaque phrase croise deux contraintes de la même figure (« sur la ligne du
  haut, mais pas dans la colonne de gauche ») — jamais de placement direct à recopier ;
- palier 2 : phrases reliant deux figures (« juste à gauche de », « quelque part à
  droite de », « pas sur la même ligne que ») ;
- palier 3 : négations globales et conditionnel (« si … alors ») ;
- palier 4 : grille 4×4.

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
    _vrai_binaire,
    _vrai_unaire,
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

#: Formes de phrases composées : deux contraintes croisées sur la même figure.
FORMES_COMPOSES = [
    ("ligne", "pas-colonne"),
    ("colonne", "pas-ligne"),
    ("ligne", "pas-coin"),
    ("colonne", "pas-coin"),
    ("ligne", "pas-bord"),
    ("colonne", "pas-bord"),
    ("ligne", "ni-ni"),
    ("colonne", "ni-ni"),
    ("pas-ligne", "pas-colonne"),
]

#: Types d'indices relationnels (deux figures par phrase), sans le conditionnel.
BINAIRES_FORTS = {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
                  "comparaison", "autre-ligne", "autre-colonne",
                  "a-droite-de", "a-gauche-de", "au-dessus-de", "en-dessous-de"}

#: Types d'indices autorisés par palier (difficulté croissante).
TYPES_PAR_PALIER = {
    1: {"compose"},
    2: {"compose"} | BINAIRES_FORTS,
    3: {"compose"} | BINAIRES_FORTS | {"si-alors"},
    4: {"compose", "ancre"} | BINAIRES_FORTS | {"si-alors"},
}
#: Nombre minimal de phrases composées (deux contraintes croisées sur une figure)
#: par palier : c'est la forme qui oblige à recouper, elle ne doit pas disparaître.
QUOTA_COMPOSE = {1: 99, 2: 2, 3: 3, 4: 2}

#: Plancher et plafond du nombre de phrases, par palier.
MIN_INDICES = {1: 6, 2: 6, 3: 7, 4: 10}
MAX_INDICES = {1: 9, 2: 11, 3: 14, 4: 18}
#: Nombre maximal de placements directs (ancres) — réservés à la grille 4×4 :
#: une grille 4×4 ne se referme pas par déduction pure sans point de départ.
MAX_ANCRAGES = {1: 0, 2: 0, 3: 0, 4: 3}

DESCRIPTIONS = [
    "Phrases à deux informations : croiser ligne et colonne pour placer",
    "Phrases reliant deux figures : voisinage, à droite de, pas sur la même ligne",
    "Négations et conditionnel : éliminer pour déduire",
    "Grille 4×4 : plus de figures colorées, phrases variées",
]

CONSIGNE_3 = ("Place les neuf figures colorées. Règles : chaque ligne contient chaque figure "
              "une seule fois et chaque couleur une seule fois ; chaque colonne aussi — donc "
              "chaque figure colorée (un carré bleu, un cercle rouge…) n'apparaît qu'une fois "
              "dans la grille. Méthode : chaque phrase donne deux informations ; retiens ce qui "
              "est certain, barre ce qui devient impossible, puis recoupe les phrases.")
CONSIGNE_4 = ("Place les seize figures colorées. Règles : chaque ligne contient chaque figure "
              "une seule fois et chaque couleur une seule fois ; chaque colonne aussi — donc "
              "chaque figure colorée n'apparaît qu'une fois dans la grille. Méthode : chaque "
              "phrase donne deux informations ; retiens ce qui est certain, barre ce qui "
              "devient impossible, puis recoupe les phrases.")


def _atome(type_atome: str, case: int, n: int) -> dict | None:
    """Contrainte élémentaire positive vraie pour la figure assise à cette case."""
    ligne, colonne = divmod(case, n)
    if type_atome == "ligne":
        return {"type": "ligne", "ligne": ligne}
    if type_atome == "colonne":
        return {"type": "colonne", "colonne": colonne}
    if type_atome in ("pas-coin", "pas-bord", "ni-ni"):
        return {"type": type_atome}
    return None


def _variantes_atome(type_atome: str, case: int, n: int) -> list[dict]:
    """Toutes les contraintes élémentaires de ce type **vraies** pour cette case.

    Une négation « pas sur la ligne X » n'a de sens que si X n'est PAS la vraie
    ligne de la figure — sinon la phrase serait fausse.
    """
    ligne, colonne = divmod(case, n)
    if type_atome == "pas-ligne":
        return [{"type": "pas-ligne", "ligne": x} for x in range(n) if x != ligne]
    if type_atome == "pas-colonne":
        return [{"type": "pas-colonne", "colonne": x} for x in range(n) if x != colonne]
    atome = _atome(type_atome, case, n)
    return [atome] if atome and _vrai_unaire(atome, case, n) else []


def _cases_atome(atome: dict, n: int) -> set[int]:
    return {i for i in range(n * n) if _vrai_unaire(atome, i, n)}


def _indice(type_indice: str, nom_f: str, nom_c: str, **extra) -> dict:
    return {"type": type_indice, "figure": nom_f, "couleur": nom_c, **extra}


def _pool(paire, n: int, noms_f: list[str], noms_c: list[str], types: set[str]) -> list[dict]:
    """Toutes les phrases vraies autorisées par le palier."""
    fig, coul = paire
    pool: list[dict] = []

    # Phrases composées : deux contraintes croisées sur la même figure.
    if "compose" in types:
        for f, nom_f in enumerate(noms_f):
            for c, nom_c in enumerate(noms_c):
                case = cellule(fig, coul, f, c)
                for t1, t2 in FORMES_COMPOSES:
                    a1 = _atome(t1, case, n)
                    if not a1 or not _vrai_unaire(a1, case, n):
                        continue
                    c1 = _cases_atome(a1, n)
                    for a2 in _variantes_atome(t2, case, n):
                        c2 = _cases_atome(a2, n)
                        commun = c1 & c2
                        # La seconde information doit réellement retirer des cases.
                        if not (len(commun) < len(c1) and len(commun) < len(c2)):
                            continue
                        second = {k: v for k, v in a2.items() if k != "type"} | {"type": a2["type"]}
                        pool.append(_indice(t1, nom_f, nom_c,
                                            **{k: v for k, v in a1.items() if k != "type"},
                                            et=second))

    # Ancres : placement direct d'une figure (palier 4 uniquement, en petit nombre).
    if "ancre" in types:
        for f, nom_f in enumerate(noms_f):
            for c, nom_c in enumerate(noms_c):
                pool.append(_indice("case", nom_f, nom_c, case=cellule(fig, coul, f, c)))

    # Phrases reliant deux figures.
    types_paires = types & TYPES_BINAIRES
    if types_paires:
        for f1, nom_f1 in enumerate(noms_f):
            for c1, nom_c1 in enumerate(noms_c):
                case1 = cellule(fig, coul, f1, c1)
                for f2, nom_f2 in enumerate(noms_f):
                    for c2, nom_c2 in enumerate(noms_c):
                        if (f1, c1) == (f2, c2):
                            continue
                        case2 = cellule(fig, coul, f2, c2)
                        base = dict(figure2=nom_f2, couleur2=nom_c2)
                        for t in types_paires:
                            if _vrai_binaire({"type": t}, case1, case2, n):
                                pool.append(_indice(t, nom_f1, nom_c1, **base))
    return pool


def _jeton_principal(indice: dict) -> tuple[str, str]:
    return (indice["figure"], indice["couleur"])


def _score_binaire(type_indice: str, n: int) -> float:
    """Fraction de l'espace des paires (i1, i2) que la contrainte laisse possible."""
    paires = n ** 4
    if type_indice in ("voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous"):
        return n * (n - 1) / paires
    if type_indice == "comparaison":
        return n * (n * (n - 1) // 2) / paires
    if type_indice in ("a-droite-de", "a-gauche-de", "au-dessus-de", "en-dessous-de"):
        return (n * (n - 1) // 2) * n * n / paires
    if type_indice in ("autre-ligne", "autre-colonne"):
        return n ** 3 * (n - 1) / paires
    if type_indice == "si-alors":
        return (paires - len(coins(n)) * (n * n - len(bords(n)))) / paires
    return 1.0


def _score(indice: dict, n: int) -> float:
    """Puissance d'une phrase : plus le score est petit, plus elle élimine."""
    if indice["type"] == "case":
        return 0.0
    if indice["type"] in TYPES_BINAIRES:
        return _score_binaire(indice["type"], n)
    atome1 = {k: v for k, v in indice.items() if k not in ("figure", "couleur", "et")}
    atome2 = indice["et"]
    commun = _cases_atome(atome1, n) & _cases_atome(atome2, n)
    return len(commun) / (n * n)


def _melange(liste: list[dict], n: int, rng: random.Random) -> list[dict]:
    """Du plus puissant au moins puissant (égalités départagées au hasard)."""
    return sorted(liste, key=lambda ind: (_score(ind, n), rng.random()))


def _selection(paire, n: int, noms_f: list[str], noms_c: list[str], palier: int,
               rng: random.Random) -> list[dict] | None:
    """Phrases suffisantes pour une résolution par déduction, avec le dosage du palier."""
    pool = _pool(paire, n, noms_f, noms_c, TYPES_PAR_PALIER[palier])
    if not pool:
        return None
    composes = _melange([ind for ind in pool if "et" in ind], n, rng)
    autres = _melange([ind for ind in pool if "et" not in ind], n, rng)
    # Quelques phrases composées d'abord : elles portent la part de recoupement.
    quota = min(QUOTA_COMPOSE[palier], len(composes))
    ordre = composes[:quota] + _melange(composes[quota:] + autres, n, rng)

    choisis: list[dict] = []
    ancrages = 0
    for indice in ordre:
        if len(choisis) >= MAX_INDICES[palier]:
            break
        if indice["type"] == "case":
            if ancrages >= MAX_ANCRAGES[palier]:
                continue
            ancrages += 1
        choisis.append(indice)
        if len(choisis) >= MIN_INDICES[palier] and resoudre_par_deduction(choisis, n, noms_f, noms_c):
            return choisis
    return choisis if resoudre_par_deduction(choisis, n, noms_f, noms_c) else None


def _secours(paire, n: int, noms_f: list[str], noms_c: list[str],
             rng: random.Random) -> list[dict]:
    """Trois phrases de secours directes (aide progressive de l'interface)."""
    fig, coul = paire
    jetons = [(f, c) for f in range(n) for c in range(n)]
    rng.shuffle(jetons)
    secours = []
    for f, c in jetons[:3]:
        case = cellule(fig, coul, f, c)
        forme = rng.choice(["case", "ligne", "colonne"])
        if forme == "case":
            secours.append(_indice("case", noms_f[f], noms_c[c], case=case))
        else:
            atome = _atome(forme, case, n)
            secours.append(_indice(forme, noms_f[f], noms_c[c],
                                   **{k: v for k, v in atome.items() if k != "type"}))
    return secours


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
        "cap_complexite": "une phrase = deux informations croisées, jamais de placement direct à recopier",
        "contenu": {
            "consigne": CONSIGNE_3 if n == 3 else CONSIGNE_4,
            "figures": figures,
            "couleurs": couleurs,
            "enonces": indices,
            "indices": secours,
            "aide": ("Chaque phrase donne deux informations. Marque ce qui est certain, "
                     "barre ce qui devient impossible, puis recoupe avec les autres phrases."),
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
        for _ in range(10):
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
    print("Phrases par grille : min %d, max %d, moyenne %.1f." %
          (min(indices), max(indices), sum(indices) / len(indices)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
