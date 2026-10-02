#!/usr/bin/env python3
"""Générateur du thème « memoire » — sprint 2.

Génère, avec la seule bibliothèque standard et une graine fixe (déterminisme :
deux exécutions produisent des fichiers identiques), le contenu du thème mémoire :

- ``content/entrainement/memoire/paliers/palier-01.json`` … ``palier-12.json`` :
  empans de chiffres (endroit/envers), paires associatives mot–nombre, sondes
  n-back (rappel temporel), puis **empans de mots** (paliers 9 à 12, matériel
  verbal) — 18 items par palier ;
Le thème est accompagné d'un manifest ``paliers.json`` (ordre, description,
prerequis, fichier, nb_items). Format des items : strictement conforme à
``content/schema-item.json`` (module « entrainement », meta traçable,
relecture orthophoniste à faire).

Les familles s'appuient sur des techniques classiques d'entraînement cognitif
(empan, n-back et apprentissage par paires)
implémentées en 100 % original : la logique est assimilée, jamais le matériel
des tests protégés (PASAT, d2, MMSE, ECPA/Pearson).

Usage :

    python3 tools/generer_memo_concentration.py [--dry-run] [--date AAAA-MM-JJ]
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

# --- Paramètres généraux ------------------------------------------------------

#: Graine du générateur aléatoire (déterminisme du contenu versionné).
GRAINE: int = 20260904

#: Métadonnées traçables posées sur chaque item généré.
AUTEUR: str = "generation-automatique (tools/generer_memo_concentration.py)"
DATE_CREATION_DEFAUT: str = "2026-09-10"

#: Racine du dépôt (parent du dossier tools/) et base du contenu.
RACINE_DEPOT = Path(__file__).resolve().parent.parent
BASE_SORTIE = RACINE_DEPOT / "content" / "entrainement"

#: Lettres autorisées pour les séquences n-back (sans ambiguïté orthoacoustique).
LETTRES_NBACK = "BKLMPRT"

#: Pool de mots pour les paires associatives (majuscules, concrets).
MOTS_PAIRES = [
    "LUNE", "PONT", "ARBRE", "ROUE", "FLEUR", "TRAIN",
    "PORTE", "NUAGE", "PIERRE", "LIVRE", "PLUIE", "TABLE",
]

#: Pool de mots pour l'empan de mots et le rappel de séries : concrets, courts
#: (1–2 syllabes), et choisis pour limiter les confusions phonologiques entre eux.
MOTS_EMPAN = [
    "chat", "lune", "porte", "stylo", "table", "rivière", "pomme", "jardin",
    "montre", "nuage", "panier", "bougie", "fromage", "manteau", "chemin",
    "fenêtre", "sable", "crayon", "chapeau", "cuisine", "voiture", "orange",
    "marteau", "plage", "tapis", "guitare", "bureau", "soleil", "poisson",
    "chemise", "montagne", "bouteille", "chaussure", "journal", "musique",
    "neige", "bateau", "colline", "horloge", "feuille", "chocolat", "drapeau",
    "camion", "radis", "vélo", "ballon", "cahier", "jardinier",
]

#: Rythme commun des séquences à mémoriser : deux secondes de présentation,
#: puis deux secondes de blanc. Cette cadence vaut pour les chiffres, les mots
#: et les lettres afin que le rythme ne dépende pas du palier ou de la famille.
DUREE_ITEM_MS: int = 2000
DUREE_ITEM_MOTS_MS: int = 2000
BLANC_INTER_ITEM_MS: int = 2000

#: Caps de complexité explicites (dosage anti sur-sollicitation).
CAP_NBACK_8 = "séquences de 8 éléments maximum"


# --- Socle commun -------------------------------------------------------------


def _item(
    identifiant: str,
    type_item: str,
    theme: str,
    fonctions: list[str],
    palier: int,
    prerequis: list[str],
    cap: str | None,
    contenu: dict,
    reponse: dict,
    date_creation: str,
) -> dict:
    """Construit un item complet conforme à content/schema-item.json."""
    return {
        "id": identifiant,
        "type": type_item,
        "module": "entrainement",
        "theme": theme,
        "fonctions_ciblees": fonctions,
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": cap,
        "contenu": contenu,
        "reponse": reponse,
        "meta": {
            "auteur": AUTEUR,
            "date_creation": date_creation,
            "relecture_ortho": {"statut": "a_revoir"},
        },
    }


def _rng_perimetre(perimetre: str) -> random.Random:
    """Générateur aléatoire isolé par périmètre (« thème:famille »).

    Un générateur PARTAGÉ rend le contenu instable : ajouter une famille ou un
    palier décale le tirage de tout ce qui suit, et du contenu déjà livré est
    réécrit silencieusement (mêmes identifiants, exercices différents) — c'est
    arrivé au sprint 4. Chaque périmètre tire
    donc de sa propre séquence, dérivée de la graine et de son nom : deux
    exécutions restent identiques, et une extension ne touche que la famille
    qu'elle ajoute.
    """
    return random.Random(f"{GRAINE}:{perimetre}")


def _chiffres_sans_doublon_adjacent(rng: random.Random, longueur: int) -> list[str]:
    """Chiffres 0..9 en chaînes, sans deux chiffres identiques consécutifs."""
    chiffres = [str(rng.randrange(10))]
    while len(chiffres) < longueur:
        candidat = str(rng.randrange(10))
        if candidat != chiffres[-1]:
            chiffres.append(candidat)
    return chiffres


def _lettres_sans_doublon_adjacent(rng: random.Random, longueur: int) -> list[str]:
    """Lettres majuscules sans deux identiques consécutifs (lisibilité)."""
    lettres = [rng.choice(LETTRES_NBACK)]
    while len(lettres) < longueur:
        candidat = rng.choice(LETTRES_NBACK)
        if candidat != lettres[-1]:
            lettres.append(candidat)
    return lettres


# --- Thème « memoire » ----------------------------------------------------------


def _empan(rng, palier, longueur, envers, nn, prerequis, date_creation):
    """Empan de chiffres : séquence montrée une à une, rappel endroit ou envers."""
    elements = _chiffres_sans_doublon_adjacent(rng, longueur)
    if envers:
        attendue = "".join(reversed(elements))
        enonce = "Tape la séquence à l'envers (de mémoire)."
    else:
        attendue = "".join(elements)
        enonce = "Tape la séquence de mémoire, dans l'ordre."
    contenu = {
        "consigne": "Mémorise la séquence de chiffres.",
        "affichage": {
            "mode": "sequence",
            "duree_par_item_ms": DUREE_ITEM_MS,
            "pause_item_ms": BLANC_INTER_ITEM_MS,
            "elements": elements,
        },
        "enonce": enonce,
        "aide": None,
    }
    return _item(
        f"me-{palier}-empan-{nn:02d}", "empan", "memoire", ["memoire-travail"],
        palier, prerequis, None, contenu, {"valeur": attendue}, date_creation,
    )


def _empan_mots(rng, palier, longueur, envers, nn, prerequis, date_creation):
    """Empan de mots : même logique que l'empan de chiffres, matériel verbal.

    Le rappel verbal est plus sensible à la similarité phonologique : les mots
    sont donc sans doublon dans la séquence et tirés d'un ensemble concret.
    """
    elements = rng.sample(MOTS_EMPAN, longueur)
    if envers:
        attendue = " ".join(reversed(elements))
        enonce = "Tape les mots à l'envers (le dernier d'abord)."
    else:
        attendue = " ".join(elements)
        enonce = "Tape les mots dans l'ordre, en les séparant par des espaces."
    contenu = {
        "consigne": "Mémorise les mots affichés.",
        "affichage": {
            "mode": "sequence",
            "duree_par_item_ms": DUREE_ITEM_MOTS_MS,
            "pause_item_ms": BLANC_INTER_ITEM_MS,
            "elements": elements,
        },
        "enonce": enonce,
        "aide": None,
    }
    return _item(
        f"me-{palier}-mots-{nn:02d}", "empan-mots", "memoire", ["memoire-travail"],
        palier, prerequis, None, contenu, {"valeur": attendue}, date_creation,
    )


def _nback(rng, palier, pas, nn, prerequis, date_creation):
    """Sonde n-back : rappel de l'élément N positions avant la fin de la séquence."""
    longueur = pas + 4
    elements = _lettres_sans_doublon_adjacent(rng, longueur)
    sonde = elements[longueur - 1 - pas]
    contenu = {
        "consigne": "Mémorise la séquence d'éléments.",
        "affichage": {
            "mode": "sequence",
            "duree_par_item_ms": DUREE_ITEM_MS,
            "pause_item_ms": BLANC_INTER_ITEM_MS,
            "elements": elements,
        },
        "enonce": f"Quel élément était {pas} positions avant la fin ? Tape-le.",
        "aide": None,
    }
    cap = CAP_NBACK_8 if palier >= 8 else None
    return _item(
        f"me-{palier}-nback-{nn:02d}", "n-back", "memoire",
        ["memoire-travail", "attention-soutenue"], palier, prerequis, cap,
        contenu, {"valeur": sonde}, date_creation,
    )


def _paires(rng, palier, nb_paires, nn, prerequis, date_creation):
    """Paires associatives mot–nombre : mémorisation puis rappel sondé."""
    mots = rng.sample(MOTS_PAIRES, nb_paires)
    nombres = rng.sample(range(10, 100), nb_paires)
    elements = [[mot, str(nombre)] for mot, nombre in zip(mots, nombres)]
    sondage = rng.randrange(nb_paires)
    contenu = {
        "consigne": "Mémorise chaque paire mot–nombre.",
        "affichage": {
            "mode": "liste",
            "duree_totale_ms": nb_paires * 4000,
            "elements": elements,
        },
        "enonce": f"Nombre associé à « {mots[sondage]} » ?",
        "aide": None,
    }
    return _item(
        f"me-{palier}-paires-{nn:02d}", "paires-associatives", "memoire",
        ["memoire-travail", "memorisation-longue"], palier, prerequis, None,
        contenu, {"valeur": str(nombres[sondage])}, date_creation,
    )


# --- Composition des paliers ------------------------------------------------------


def _paliers_memoire(date_creation):
    """Construit les 12 paliers du thème « memoire » (18 items chacun).

    Chaque famille (empan, empan de mots, paires, n-back) tire ses items d'un
    générateur isolé — voir ``_rng_perimetre``.
    """
    paliers = []
    compositions = [
        # (nb, type, paramètres) — voir spec .cluster/enrichissement/spec.md
        [("empan", {"longueur": 3, "envers": False})] * 18,
        [("empan", {"longueur": 4, "envers": False})] * 18,
        [("empan", {"longueur": 5, "envers": False})] * 10
        + [("paires", {"nb_paires": 2})] * 8,
        [("empan", {"longueur": 3, "envers": True})] * 9
        + [("empan", {"longueur": 6, "envers": False})] * 9,
        [("empan", {"longueur": 4, "envers": True})] * 10
        + [("nback", {"pas": 2})] * 8,
        [("empan", {"longueur": 5, "envers": True})] * 9
        + [("paires", {"nb_paires": 3})] * 9,
        [("empan", {"longueur": 6, "envers": True})] * 8
        + [("nback", {"pas": 3})] * 10,
        [("paires", {"nb_paires": 4})] * 8 + [("nback", {"pas": 4})] * 10,
        # Paliers 9 à 12 — empan de mots (matériel verbal, même logique que les chiffres).
        [("mots", {"longueur": 3, "envers": False})] * 18,
        [("mots", {"longueur": 4, "envers": False})] * 18,
        [("mots", {"longueur": 5, "envers": False})] * 18,
        [("mots", {"longueur": 3, "envers": True})] * 9
        + [("mots", {"longueur": 4, "envers": True})] * 9,
    ]
    compteurs: dict[str, int] = {}
    rngs: dict[str, random.Random] = {}
    for numero, composition in enumerate(compositions, start=1):
        prerequis = [] if numero == 1 else [f"me-palier-{numero - 1}"]
        items = []
        for famille, parametres in composition:
            rng = rngs.setdefault(famille, _rng_perimetre(f"memoire:{famille}"))
            compteurs[famille] = compteurs.get(famille, 0) + 1
            nn = compteurs[famille]
            if famille == "empan":
                items.append(_empan(rng, numero, parametres["longueur"],
                                    parametres["envers"], nn, prerequis, date_creation))
            elif famille == "mots":
                items.append(_empan_mots(rng, numero, parametres["longueur"],
                                         parametres["envers"], nn, prerequis, date_creation))
            elif famille == "paires":
                items.append(_paires(rng, numero, parametres["nb_paires"],
                                     nn, prerequis, date_creation))
            else:
                items.append(_nback(rng, numero, parametres["pas"],
                                    nn, prerequis, date_creation))
        paliers.append(items)
    return paliers


# --- Manifests et écriture ---------------------------------------------------------


def _manifest(theme: str, prefixe: str, descriptions: list[str],
              paliers: list[list[dict]]) -> dict:
    """Manifest ordonné d'un thème (id, description, prerequis, fichier, nb_items)."""
    entrees = []
    for numero, items in enumerate(paliers, start=1):
        entrees.append({
            "id": f"{prefixe}-palier-{numero}",
            "description": descriptions[numero - 1],
            "prerequis": [] if numero == 1 else [f"{prefixe}-palier-{numero - 1}"],
            "fichier": f"paliers/palier-{numero:02d}.json",
            "nb_items": len(items),
        })
    return {"theme": theme, "paliers": entrees}


DESCRIPTIONS_MEMOIRE = [
    "Empan 3 chiffres, endroit",
    "Empan 4 chiffres, endroit",
    "Empan 5 + premières paires mot–nombre",
    "Empan envers 3, endroit 6",
    "Envers 4 + sonde rappel d’une position (pas 2)",
    "Envers 5 + paires 3",
    "Envers 6 + sonde rappel d’une position (pas 3)",
    "Paires 4 + sonde rappel d’une position (pas 4)",
    "Empan de mots 3, endroit",
    "Empan de mots 4, endroit",
    "Empan de mots 5, endroit",
    "Empan de mots envers 3 et 4",
]

def _ecrire_json(chemin: Path, donnees) -> None:
    """Écriture JSON UTF-8 lisible (parents créés si besoin)."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8") as flux:
        json.dump(donnees, flux, ensure_ascii=False, indent=2)
        flux.write("\n")


def main() -> int:
    """Point d'entrée : génère les paliers et le manifest du thème mémoire."""
    parseur = argparse.ArgumentParser(
        description="Génère les items du thème « memoire »."
    )
    parseur.add_argument("--dry-run", action="store_true",
                         help="affiche le plan sans écrire de fichier")
    parseur.add_argument("--date", default=DATE_CREATION_DEFAUT,
                         help="date_creation (meta), AAAA-MM-JJ (défaut : %(default)s)")
    options = parseur.parse_args()

    memoire = _paliers_memoire(options.date)

    cibles: dict[Path, object] = {}
    for numero, items in enumerate(memoire, start=1):
        cibles[BASE_SORTIE / "memoire" / "paliers" / f"palier-{numero:02d}.json"] = items
    cibles[BASE_SORTIE / "memoire" / "paliers.json"] = _manifest(
        "memoire", "me", DESCRIPTIONS_MEMOIRE, memoire
    )
    for chemin in sorted(cibles):
        donnees = cibles[chemin]
        taille = len(donnees) if isinstance(donnees, list) else len(donnees["paliers"])
        relatif = chemin.relative_to(RACINE_DEPOT)
        if options.dry_run:
            print(f"[simulation] {relatif} ({taille} entrées)")
        else:
            _ecrire_json(chemin, donnees)
            print(f"[écrit] {relatif} ({taille} entrées)")

    total = sum(len(items) for items in memoire)
    print(f"Total : {len(memoire)} paliers mémoire, {total} items.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
