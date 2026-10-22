#!/usr/bin/env python3
"""Génère le thème « rappel-series » — rappel libre de séries de mots.

Paradigme visé :
plusieurs courtes séries de mots sont présentées l'une après l'autre, puis
l'utilisateur doit **rappeler librement** ce dont il se souvient — tous mots
confondus, ou seulement ceux de la première série. Deux variantes s'y ajoutent :

- **rappel immédiat** : la question suit directement l'affichage ;
- **rappel différé** : un intermède (`delai_s`) sépare l'affichage de la
  question — c'est ce délai, et non la répétition, qui rend l'exercice
  difficile (l'information doit être retrouvée sans indice contextuel).

La réussite n'est pas « tout ou rien » : un **seuil** de mots retrouvés est
déclaré dans l'item (`reponse.seuil`). Le comptage est fait côté serveur ;
l'interface affiche ensuite les mots retrouvés et manqués — sans note, sans
norme, sans comparaison entre personnes.

Le contenu est déterministe (graine fixe) : deux exécutions produisent des
fichiers identiques.

Usage :

    python3 tools/generer_rappel_series.py            # écrit le contenu
    python3 tools/generer_rappel_series.py --dry-run  # affiche sans écrire
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
BASE_SORTIE = RACINE_DEPOT / "content" / "entrainement" / "rappel-series"

#: Graine du générateur (déterminisme du contenu versionné).
#: Ce thème n'a qu'une seule famille (« rappel-libre ») : son tirage est donc
#: déjà isolé par construction — pas de flux partagé à découpler ici
#: (règle du dépôt : docs/30-technique/contenu-versionne.md).
GRAINE: int = 20260922
DATE_CREATION: str = "2026-10-01"
AUTEUR: str = "redaction-assistee (tools/generer_rappel_series.py)"

#: Pool de mots : concrets, courts, choisis pour limiter les confusions
#: phonologiques entre eux (le rappel verbal est sensible à la similarité).
MOTS = [
    "chat", "lune", "porte", "stylo", "table", "rivière", "pomme", "jardin",
    "montre", "nuage", "panier", "bougie", "fromage", "manteau", "chemin",
    "fenêtre", "sable", "crayon", "chapeau", "cuisine", "voiture", "orange",
    "marteau", "plage", "tapis", "guitare", "bureau", "soleil", "poisson",
    "chemise", "montagne", "bouteille", "chaussure", "journal", "musique",
    "neige", "bateau", "colline", "horloge", "feuille", "chocolat", "drapeau",
    "camion", "radis", "vélo", "ballon", "cahier", "fourchette",
]

#: Garde : un mot dupliqué dans le pool rendrait le comptage des rappels ambigu
#: (un même mot retrouvé vaudrait double) — le validateur de contenu le refuse,
#: mais l'erreur doit être signalée ici, à la génération.
if len(set(MOTS)) != len(MOTS):
    doublons = sorted({mot for mot in MOTS if MOTS.count(mot) > 1})
    raise SystemExit(f"Pool de mots invalide — doublons : {doublons}")

#: Rythme de départ du POC, à ajuster avec la personne (pas une norme clinique).
DUREE_MOT_MS: int = 2000
PAUSE_SERIE_MS: int = 3000


def _meta() -> dict:
    """Métadonnées d'item (relecture orthophoniste à tracer)."""
    return {
        "auteur": AUTEUR,
        "date_creation": DATE_CREATION,
        "relecture_ortho": {"statut": "a_revoir"},
    }


def _series_sans_doublon(rng: random.Random, tailles: list[int]) -> list[list[str]]:
    """Tire les mots de chaque série : distincts dans la série ET entre séries.

    Un mot ne peut pas apparaître deux fois : le comptage des rappels serait
    ambigu (un même mot retrouvé vaudrait double).
    """
    tirage = rng.sample(MOTS, sum(tailles))
    series, curseur = [], 0
    for taille in tailles:
        series.append(tirage[curseur:curseur + taille])
        curseur += taille
    return series


def _item_rappel(
    rng: random.Random,
    palier: int,
    numero: int,
    tailles: list[int],
    portee: str,
    seuil: float,
    delai_s: int,
    prerequis: list[str],
) -> dict:
    """Construit un item de rappel libre (immédiat ou différé)."""
    series = _series_sans_doublon(rng, tailles)
    cibles = series[0] if portee == "premiere-serie" else [mot for serie in series for mot in serie]
    multiple = len(series) > 1

    if portee == "premiere-serie":
        enonce = "Quels étaient les mots de la PREMIÈRE série ? Sépare-les par des espaces."
    elif multiple:
        enonce = "Écris tous les mots dont tu te souviens, toutes séries confondues, séparés par des espaces."
    else:
        enonce = "Écris tous les mots dont tu te souviens, séparés par des espaces."

    consigne = (
        "Mémorise chaque série de mots, l'une après l'autre."
        if multiple
        else "Mémorise les mots affichés."
    )
    if delai_s > 0:
        consigne += f" La question viendra après un temps d'attente de {delai_s} secondes."

    contenu = {
        "consigne": consigne,
        "affichage": {
            "mode": "series",
            "series": series,
            "duree_par_item_ms": DUREE_MOT_MS,
            "pause_item_ms": 2000,
            "modalite": "visuelle",
            "pause_serie_ms": PAUSE_SERIE_MS,
        },
        "delai_s": delai_s,
        "portee": portee,
        "enonce": enonce,
        "aide": "Note d'abord les mots qui viennent sans effort, puis cherche les autres.",
    }
    return {
        "id": f"rs2-{palier}-libre-{numero:02d}",
        "type": "rappel-libre",
        "module": "entrainement",
        "theme": "rappel-series",
        "fonctions_ciblees": ["memorisation-longue", "recuperation"],
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": contenu,
        "reponse": {"valeur": cibles, "seuil": seuil},
        "meta": _meta(),
    }


#: Composition des paliers : (tailles des séries, portée, seuil, délai, nombre).
COMPOSITIONS: list[list[tuple[list[int], str, float, int, int]]] = [
    # Palier 1 — une seule série de 4 mots, rappel immédiat.
    [([4], "toutes-series", 0.75, 0, 8)],
    # Palier 2 — deux séries de 3 mots, rappel de l'ensemble.
    [([3, 3], "toutes-series", 0.6, 0, 8)],
    # Palier 3 — trois séries de 3 mots, rappel de l'ensemble.
    [([3, 3, 3], "toutes-series", 0.5, 0, 8)],
    # Palier 4 — rappel différé : toutes séries après 20 s, et première série seule.
    [([3, 3], "toutes-series", 0.5, 20, 4), ([3, 4], "premiere-serie", 0.6, 20, 4)],
]

DESCRIPTIONS = [
    "Une série de 4 mots, rappel libre immédiat",
    "Deux séries de 3 mots, rappel de l'ensemble",
    "Trois séries de 3 mots, rappel de l'ensemble",
    "Rappel différé (20 s) : toutes les séries, puis la première seulement",
]


def construire_paliers(rng: random.Random, *, enrichissement: bool = True) -> list[list[dict]]:
    """Assemble les paliers et leur complément éditorial versionné."""
    paliers = []
    for numero, composition in enumerate(COMPOSITIONS, start=1):
        prerequis = [] if numero == 1 else [f"rs-palier-{numero - 1}"]
        items = []
        compteur = 0
        for tailles, portee, seuil, delai, nombre in composition:
            for _ in range(nombre):
                compteur += 1
                items.append(
                    _item_rappel(rng, numero, compteur, tailles, portee, seuil, delai, prerequis)
                )
        if numero == 4:
            # Une séance courte doit rencontrer les deux portées de rappel.
            items = [item for paire in zip(items[:4], items[4:]) for item in paire]
            for rang, item in enumerate(items, 1):
                item['id'] = f"rs2-{numero}-libre-{rang:02d}"
        paliers.append(items)
    if enrichissement:
        source = Path(__file__).parent / "content_sources/rappel-series_04_2026-10-10.json"
        paliers[3].extend(json.loads(source.read_text(encoding="utf-8")))
    return paliers


def _manifest(paliers: list[list[dict]]) -> dict:
    """Manifest ordonné du thème (id, description, prerequis, fichier, nb_items)."""
    return {
        "theme": "rappel-series",
        "paliers": [
            {
                "id": f"rs-palier-{numero}",
                "description": DESCRIPTIONS[numero - 1],
                "prerequis": [] if numero == 1 else [f"rs-palier-{numero - 1}"],
                "fichier": f"paliers/palier-{numero:02d}.json",
                "nb_items": len(items),
            }
            for numero, items in enumerate(paliers, start=1)
        ],
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le thème « rappel-series ».")
    parseur.add_argument("--dry-run", action="store_true", help="afficher sans écrire")
    options = parseur.parse_args()

    rng = random.Random(GRAINE)
    paliers = construire_paliers(rng)

    cibles: dict[Path, object] = {}
    for numero, items in enumerate(paliers, start=1):
        cibles[BASE_SORTIE / "paliers" / f"palier-{numero:02d}.json"] = items
    cibles[BASE_SORTIE / "paliers.json"] = _manifest(paliers)

    total = 0
    for chemin, donnees in cibles.items():
        nb = len(donnees["paliers"]) if isinstance(donnees, dict) else len(donnees)
        total += nb if isinstance(donnees, list) else 0
        if options.dry_run:
            print(f"[dry-run] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
        else:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            with chemin.open("w", encoding="utf-8") as flux:
                json.dump(donnees, flux, ensure_ascii=False, indent=2)
                flux.write("\n")
            print(f"[écrit] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
    print(f"Total : {total} items, {len(paliers)} paliers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
