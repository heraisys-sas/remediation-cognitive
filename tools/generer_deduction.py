#!/usr/bin/env python3
"""Génère le thème « deduction » — logigrammes 3×3 et 4×4.

**Une seule règle, évidente** : chaque figure colorée se pose une fois, dans une case,
et une case ne contient qu'une figure. Tout le reste vient des **phrases**.

Une phrase est une **chaîne** : une ancre de départ, puis des relations d'une figure à
la suivante. Elle peut donc porter trois informations ou plus, ce qui raccourcit
l'exercice — surtout au début :

    « Le triangle vert est dans le coin en bas à droite, juste au-dessus du carré bleu,
      qui est juste à gauche du cercle rouge. »

Méthode :

1. on tire un placement (chaque figure colorée une fois) ;
2. on construit le vivier de chaînes vraies (ancre + relations enchaînées) ;
3. on ajoute les chaînes les plus fortes jusqu'à ce que le **solveur de déduction**
   (`deduction_commun.resoudre_par_deduction`) détermine toutes les cases — sans
   hypothèse, avec les seules phrases.

Les paliers resserrent ensuite les phrases : chaînes longues et ancres précises au
début, relations plus lâches (voisinage, comparaison, négations, conditionnel) ensuite.

Usage :

    python3 tools/generer_deduction.py                 # 20 grilles par palier
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
    arrangement,
    bords,
    cellule,
    coins,
    jetons,
    propager,
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

#: Relations utilisées pour les chaînes, par palier (une information, deux figures).
RELATIONS_PAR_PALIER = {
    1: {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous"},
    2: {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
        "voisin-diagonale", "comparaison", "a-droite-de", "a-gauche-de",
        "au-dessus-de", "en-dessous-de"},
    3: {"voisin-diagonale", "comparaison", "a-droite-de", "a-gauche-de",
        "au-dessus-de", "en-dessous-de", "autre-ligne", "autre-colonne"},
    4: {"voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
        "voisin-diagonale", "oppose", "comparaison", "a-droite-de", "a-gauche-de",
        "au-dessus-de", "en-dessous-de", "autre-ligne", "autre-colonne"},
}
#: Repères autorisés pour l'ancre d'une chaîne, par palier.
#: Les paliers 3 et 4 n'acceptent que des repères **négatifs** : il faut éliminer.
ANCRES_PAR_PALIER = {
    1: {"ligne", "colonne", "coin"},
    2: {"ligne", "colonne", "coin", "diagonale", "diagonale-inverse"},
    3: {"pas-ligne", "pas-colonne", "pas-coin", "pas-bord", "ni-ni",
        "pas-diagonale", "pas-diagonale-inverse"},
    4: {"ligne", "colonne", "coin", "diagonale", "diagonale-inverse",
        "pas-ligne", "pas-colonne", "pas-coin", "pas-bord", "ni-ni",
        "pas-diagonale", "pas-diagonale-inverse"},
}
#: Longueur maximale d'une chaîne (nombre de relations après l'ancre).
LONGUEUR_CHAINE = {1: 2, 2: 1, 3: 1, 4: 1}
#: Longueur minimale d'une chaîne : au début, on veut des phrases denses.
LONGUEUR_MIN = {1: 2, 2: 1, 3: 1, 4: 1}
#: Plancher et plafond du nombre de phrases, par palier.
MIN_PHRASES = {1: 4, 2: 5, 3: 6, 4: 8}
MAX_PHRASES = {1: 9, 2: 12, 3: 14, 4: 20}
#: Nombre maximal d'ancres par grille (une ancre = un point de départ).
MAX_ANCRES = {1: 3, 2: 4, 3: 5, 4: 8}
#: Vocabulaire à faire apparaître dans chaque palier : au moins une phrase qui
#: l'utilise (le choix libre sacrifiait le vocabulaire rare au profit de chaînes
#: plus longues). Ces phrases-là sont protégées du nettoyage des redondances.
VOCABULAIRE_REQUIS = {
    1: {"coin"},
    2: {"diagonale", "diagonale-inverse", "voisin-diagonale"},
    3: {"pas-diagonale", "pas-diagonale-inverse", "voisin-diagonale"},
    4: {"oppose", "coin", "diagonale"},
}

#: Largeur de faisceau : on ne garde que les meilleures chaînes partielles.
FAISCEAU = 60
#: Nombre de phrases conservées dans le vivier.
TAILLE_VIVIER = 400

DESCRIPTIONS = [
    "Chaînes longues : un repère, puis deux relations en suivant les figures",
    "Repères sûrs et relations variées : voisinage, à droite de, plus haut que",
    "Repères négatifs et relations lâches : éliminer pour déduire",
    "Grille 4×4 : plus de figures colorées",
]


def _atomes_position(case: int, n: int) -> list[dict]:
    """Informations de position vraies pour une figure assise à cette case."""
    ligne, colonne = divmod(case, n)
    atomes = [{"type": "ligne", "ligne": ligne}, {"type": "colonne", "colonne": colonne}]
    for x in range(n):
        if x != ligne:
            atomes.append({"type": "pas-ligne", "ligne": x})
        if x != colonne:
            atomes.append({"type": "pas-colonne", "colonne": x})
    if case in coins(n):
        atomes.append({"type": "coin"})
    else:
        atomes.append({"type": "pas-coin"})
    if case not in bords(n):
        atomes.append({"type": "pas-bord"})
    if case not in coins(n) and case not in bords(n):
        atomes.append({"type": "ni-ni"})
    atomes.append({"type": "diagonale" if ligne == colonne else "pas-diagonale"})
    atomes.append({"type": "diagonale-inverse" if ligne + colonne == n - 1
                   else "pas-diagonale-inverse"})
    return atomes


def _cases(atome: dict, n: int) -> set[int]:
    return {i for i in range(n * n) if _vrai_unaire(atome, i, n)}


def _force_binaire(type_indice: str, n: int) -> float:
    """Part de l'espace des paires que la relation laisse possible (petit = fort)."""
    paires = n ** 4
    if type_indice in ("voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous"):
        return n * (n - 1) / paires
    if type_indice == "voisin-diagonale":
        return 4 * (n - 1) ** 2 / paires
    if type_indice == "oppose":
        return n * n / paires
    if type_indice == "comparaison":
        return n * (n * (n - 1) // 2) / paires
    if type_indice in ("a-droite-de", "a-gauche-de", "au-dessus-de", "en-dessous-de"):
        return (n * (n - 1) // 2) * n * n / paires
    if type_indice in ("autre-ligne", "autre-colonne"):
        return n ** 3 * (n - 1) / paires
    if type_indice == "si-alors":
        return (paires - len(coins(n)) * (n * n - len(bords(n)))) / paires
    return 1.0


def _profondeur(atome: dict, n: int) -> int:
    """Nombre de cases qu'une information de position laisse ouvertes."""
    return len(_cases(atome, n))


def _vivier(paire, n: int, noms_f: list[str], noms_c: list[str], palier: int,
            rng: random.Random) -> list[tuple[float, dict]]:
    """Chaînes vraies : (force, phrase). Plus la force est petite, plus la chaîne serre."""
    fig, coul = paire
    cases = {(f, c): cellule(fig, coul, f, c) for f in range(n) for c in range(n)}
    relations = RELATIONS_PAR_PALIER[palier]

    # Relations vraies, les plus fortes d'abord, pour chaque couple de figures.
    liens: dict[tuple, list[tuple[float, str]]] = {}
    for a in cases:
        for b in cases:
            if a == b:
                continue
            for type_indice in relations:
                if _vrai_binaire({"type": type_indice}, cases[a], cases[b], n):
                    liens.setdefault((a, b), []).append((_force_binaire(type_indice, n), type_indice))
    for cle in liens:
        liens[cle].sort()

    # Départs : une figure et un repère de position vrai.
    autorisees = ANCRES_PAR_PALIER[palier]
    depart = []
    for a in cases:
        for atome in _atomes_position(cases[a], n):
            if atome["type"] not in autorisees:
                continue
            profondeur = _profondeur(atome, n)
            depart.append(((a,), [atome], profondeur / (n * n), {a}))
    depart.sort(key=lambda item: item[2])

    # Chaînes : on prolonge par la relation la plus forte vers une figure non citée.
    longueur = LONGUEUR_CHAINE[palier]
    minimum = LONGUEUR_MIN[palier]
    complet: list[tuple[float, dict]] = []
    front = depart[:FAISCEAU]
    for niveau in range(longueur):
        suivants = []
        for chemin, atomes, force, vus in front:
            for cle, candidats in liens.items():
                if cle[0] != chemin[-1] or cle[1] in vus:
                    continue
                force_lien, type_indice = candidats[0]
                atome = {"type": type_indice, "figure2": noms_f[cle[1][0]], "couleur2": noms_c[cle[1][1]]}
                suivants.append((chemin + (cle[1],), atomes + [atome], force * force_lien, vus | {cle[1]}))
        if niveau + 1 >= minimum:
            complet.extend(suivants)
        suivants.sort(key=lambda item: item[2])
        front = suivants[:FAISCEAU]

    # Chaînes : conversion en phrases (la première information fait l'ancre).
    phrases: list[tuple[float, dict]] = []
    for chemin, atomes, force, _ in complet:
        entete = dict(atomes[0])
        entete["figure"] = noms_f[chemin[0][0]]
        entete["couleur"] = noms_c[chemin[0][1]]
        suite = []
        for rang, atome in enumerate(atomes[1:], start=1):
            precedent = chemin[rang - 1]
            suite.append({"figure": noms_f[precedent[0]], "couleur": noms_c[precedent[1]], **atome})
        if suite:
            entete["et"] = suite
        phrases.append((force, entete))

    # Phrases d'ancrage : une seule information de position (le repère absolu).
    for a in cases:
        for atome in _atomes_position(cases[a], n):
            if atome["type"] not in autorisees:
                continue
            phrases.append((_profondeur(atome, n) / (n * n),
                            {"figure": noms_f[a[0]], "couleur": noms_c[a[1]], **atome}))

    phrases.sort(key=lambda item: (item[0], rng.random()))
    return phrases[:TAILLE_VIVIER]


def _cellules_ouvertes(phrases: list[dict], n: int, noms_f: list[str], noms_c: list[str]) -> int | None:
    """Nombre de cases encore ouvertes après propagation ; None si contradiction."""
    domaines = propager(phrases, n, noms_f, noms_c)
    if domaines is None:
        return None
    return sum(len(domaine) for domaine in domaines)


def _sujets_phrase(phrase: dict) -> set[tuple[str, str]]:
    """Figures colorées citées par une phrase."""
    sujets = set()
    nom_f, nom_c = phrase.get("figure"), phrase.get("couleur")
    for atome in [phrase] + list(phrase.get("et") or []):
        f = atome.get("figure", nom_f)
        c = atome.get("couleur", nom_c)
        if f and c:
            sujets.add((f, c))
    return sujets


def _nombre_ancres(phrases: list[dict]) -> int:
    return sum(1 for p in phrases if p.get("type") not in TYPES_BINAIRES)


def _minimaliser(phrases: list[dict], n: int, noms_f: list[str], noms_c: list[str],
                 plancher: int = 3, preserver: frozenset = frozenset()) -> list[dict]:
    """Retire les phrases devenues inutiles : aucune indication redondante.

    Une phrase est redondante quand la grille reste entièrement déterminée sans elle
    — la figure est déjà située par les autres phrases. Les phrases ``preserver``
    (vocabulaire demandé) ne sont jamais retirées.
    """
    resultat = list(phrases)
    change = True
    while change and len(resultat) > plancher:
        change = False
        for rang in range(len(resultat) - 1, -1, -1):
            if id(resultat[rang]) in preserver:
                continue
            essai = resultat[:rang] + resultat[rang + 1:]
            if len(essai) >= plancher and resoudre_par_deduction(essai, n, noms_f, noms_c):
                resultat = essai
                change = True
                break
    return resultat


def _types_de(phrase: dict) -> set[str]:
    return {atome.get("type") for atome in [phrase] + list(phrase.get("et") or [])}


def _presenter(phrases: list[dict], rng: random.Random) -> list[dict]:
    """Ordre de présentation des phrases, tiré au sort pour chaque grille.

    Les phrases du vocabulaire obligatoire sont choisies **en premier** ; si on les
    laissait à cette place, **toutes** les grilles commenceraient par le même type de
    phrase (« coin », puis « diagonale »…) — une régularité visible qui met sur la
    piste sans raison. L'ordre ne porte aucune information : on le mélange.
    """
    melangees = list(phrases)
    rng.shuffle(melangees)
    return melangees


def _selection(paire, n: int, noms_f: list[str], noms_c: list[str], palier: int,
               rng: random.Random) -> list[dict] | None:
    """Phrases suffisantes pour une résolution par déduction, avec le dosage du palier.

    Choix glouton piloté par le solveur : à chaque étape, on retient la phrase qui
    **détermine le plus de cases** (le moins de cases encore ouvertes). C'est ce qui
    donne le plus court ensemble de phrases qui suffit à reconstruire la grille.
    """
    vivier = _vivier(paire, n, noms_f, noms_c, palier, rng)
    if not vivier:
        return None
    phrases = [phrase for _, phrase in vivier]
    # Vocabulaire demandé : on retient d'abord une phrase par type requis.
    obligatoires: list[dict] = []
    for type_requis in sorted(VOCABULAIRE_REQUIS[palier]):
        for phrase in phrases:
            if type_requis in _types_de(phrase) and phrase not in obligatoires:
                obligatoires.append(phrase)
                break
    protegees = frozenset(id(phrase) for phrase in obligatoires)
    restants = [rang for rang, phrase in enumerate(phrases) if phrase not in obligatoires]
    choisis: list[dict] = list(obligatoires)
    while restants and len(choisis) < MAX_PHRASES[palier]:
        gagnant, meilleur = None, None
        for rang in restants:
            essai = choisis + [phrases[rang]]
            ouvertes = _cellules_ouvertes(essai, n, noms_f, noms_c)
            if ouvertes is None:
                continue
            if meilleur is None or ouvertes < meilleur:
                gagnant, meilleur = rang, ouvertes
        if gagnant is None:
            return None
        choisis.append(phrases[gagnant])
        restants.remove(gagnant)
        if meilleur == n * n and len(choisis) >= MIN_PHRASES[palier]:
            return _presenter(_minimaliser(choisis, n, noms_f, noms_c, preserver=protegees), rng)
    if len(choisis) >= MIN_PHRASES[palier] and resoudre_par_deduction(choisis, n, noms_f, noms_c):
        return _presenter(_minimaliser(choisis, n, noms_f, noms_c, preserver=protegees), rng)
    return None


def _secours(paire, n: int, noms_f: list[str], noms_c: list[str],
             rng: random.Random) -> list[dict]:
    """Trois phrases de secours directes (aide progressive de l'interface)."""
    fig, coul = paire
    melange = jetons(n)
    rng.shuffle(melange)
    secours = []
    for f, c in melange[:3]:
        case = cellule(fig, coul, f, c)
        if rng.random() < 0.4:
            secours.append({"type": "case", "figure": noms_f[f], "couleur": noms_c[c], "case": case})
        else:
            forme = rng.choice(["ligne", "colonne"])
            valeur = case // n if forme == "ligne" else case % n
            secours.append({"type": forme, "figure": noms_f[f], "couleur": noms_c[c], forme: valeur})
    return secours


def _item(palier: int, rang: int, paire, phrases: list[dict], secours: list[dict],
          n: int, figures: list[str], couleurs: list[str]) -> dict:
    fig, coul = paire
    grille = [[figures[fig[i]], couleurs[coul[i]]] for i in range(n * n)]
    nombre = "neuf" if n == 3 else "seize"
    return {
        "id": "de-%d-%02d" % (palier, rang),
        "type": "grille-deduction",
        "module": "entrainement",
        "theme": "deduction",
        "fonctions_ciblees": ["fonctions-executives", "memoire-travail"],
        "palier": palier,
        "prerequis": [] if palier == 1 else ["de-palier-%d" % (palier - 1)],
        "cap_complexite": "les phrases suffisent : aucune règle cachée, suivre les chaînes",
        "contenu": {
            "consigne": (
                f"Place les {nombre} figures colorées. Deux évidences seulement : chaque figure "
                "colorée (un carré bleu, un cercle rouge…) se pose une fois, et une case ne "
                "contient qu'une figure. Tout le reste est dans les phrases : suis les chaînes "
                "d'une figure à l'autre, note ce qui est certain, barre ce qui devient impossible."),
            "figures": figures,
            "couleurs": couleurs,
            "enonces": phrases,
            "indices": secours,
            "aide": ("Chaque phrase enchaîne plusieurs informations : commence par la figure "
                     "dont la phrase donne la position, puis suis les relations."),
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


def generer_palier(palier: int, rng: random.Random, nombre: int, deja_vus: set) -> list[dict]:
    """Grilles d'un palier : placements distincts, chacune déductible des seules phrases."""
    n = 3 if palier <= 3 else 4
    figures, couleurs = FIGURES[:n], COULEURS[:n]
    items: list[dict] = []
    essais = 0
    while len(items) < nombre:
        essais += 1
        if essais > 40000:
            raise SystemExit("palier %d : %d grilles seulement (abandon)" % (palier, len(items)))
        paire = arrangement(rng, n)
        if paire in deja_vus:
            continue
        for _ in range(6):
            phrases = _selection(paire, n, figures, couleurs, palier, rng)
            if phrases:
                deja_vus.add(paire)
                items.append(_item(palier, len(items) + 1, paire, phrases,
                                   _secours(paire, n, figures, couleurs, rng),
                                   n, figures, couleurs))
                break
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
    nombres = [len(i["contenu"]["enonces"]) for p in paliers for i in p]
    infos = [sum(1 + len(p.get("et") or []) for p in i["contenu"]["enonces"]) for p in paliers for i in p]
    figures_citees = [len({s for ph in i["contenu"]["enonces"] for s in _sujets_phrase(ph)})
                      for lot in paliers for i in lot]
    print("Total : %d grilles, %d paliers, placements distincts : %d." % (total, len(paliers), len(deja_vus)))
    print("Phrases par grille : min %d, max %d, moyenne %.1f." % (min(nombres), max(nombres), sum(nombres) / len(nombres)))
    print("Informations par grille : min %d, max %d, moyenne %.1f." % (min(infos), max(infos), sum(infos) / len(infos)))
    print("Figures citées par grille : min %d, max %d (sur %d)." % (min(figures_citees), max(figures_citees), 9))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
