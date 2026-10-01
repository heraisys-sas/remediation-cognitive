#!/usr/bin/env python3
"""Génère le programme d'entraînement de 8 semaines (`content/programmes/`).

Le programme décrit **ce qui est proposé** chaque jour, jamais ce qui est exigé :

- rythme : 5 jours de séance, 1 journée légère, 1 jour de repos ;
- rotation des thèmes : calcul mental, mémoire, concentration, accès au mot,
  puis vie sociale / rappel de séries en alternance — l'alternance des domaines
  (interleaving) est plus favorable que l'enchaînement d'un seul thème, et elle
  limite la fatigue sur un même réseau ;
- durée : elle augmente d'une minute toutes les deux semaines, plafonnée à
  10 minutes par séance ;
- **complexification** : chaque semaine porte un *plafond de palier* par thème.
  Ce plafond est une **borne**, pas un objectif : l'avancement réel reste piloté
  par la maîtrise (90 % × 3 séances) et par la tolérance à la fatigue, comme le
  prévoient les protocoles du dépôt. Le programme ne force jamais un palier.

Déterminisme : aucune part aléatoire — deux exécutions produisent le même fichier.

Usage :

    python3 tools/generer_programme.py            # écrit le programme
    python3 tools/generer_programme.py --dry-run  # affiche un résumé
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
DOSSIER_SORTIE = RACINE_DEPOT / "content" / "programmes"
NOM_FICHIER = "8-semaines.json"

#: Nombre de semaines générées (deux mois).
SEMAINES = 8

#: Thèmes principaux, dans l'ordre de rotation hebdomadaire.
THEMES = ["calcul-mental", "memoire", "reperer-essentiel", "evocation", "quotidien", "methodes", "deduction", "rappel-series", "series-entendues", "actualiser-consigne", "comparer-documents", "garder-cap"]

#: Thèmes d'appoint, proposés seulement en journée légère « au choix ».
THEMES_EXTRA = ["anglais", "python"]

#: Nombre de paliers disponibles par thème (bornes des plafonds hebdomadaires).
PALIERS_DISPONIBLES = {
    "calcul-mental": 12,
    "memoire": 12,
    "concentration": 9,
    "evocation": 7,
    "quotidien": 8,
    "methodes": 6,
    "deduction": 5,
    "series-entendues": 4,
    "actualiser-consigne": 3,
    "comparer-documents": 3,
    "reperer-essentiel": 3,
    "garder-cap": 3,
    "rappel-series": 4,
}

#: Durée d'une séance (minutes) par semaine : +1 minute toutes les 2 semaines.
DUREE_SEMAINE = [6, 6, 7, 7, 8, 8, 9, 9]

#: Plafond de palier visé par semaine (borne, jamais un objectif) — ramené au
#: nombre de paliers réellement disponibles pour chaque thème.
PLAFOND_SEMAINE = [2, 3, 4, 5, 6, 7, 8, 9]

REGLES = {
    "progression": (
        "Le passage d'un palier reste piloté par la maîtrise (90 % de réussite sur "
        "3 séances consécutives). Le plafond hebdomadaire de ce programme est une "
        "borne, jamais un objectif : un palier non maîtrisé se reprend."
    ),
    "fatigue": (
        "La proposition d'arrêt en fin de séance est respectée ; une séance peut être "
        "close à tout moment."
    ),
    "jours_manques": (
        "Une journée manquée ne se rattrape pas : le programme reprend simplement au "
        "jour suivant, sans cumul."
    ),
    "alternance": (
        "Les domaines alternent dans la semaine (calcul, mémoire, concentration, "
        "langage, vie quotidienne, méthodes, déduction) : l'alternance limite la fatigue "
        "sur un même réseau et favorise le transfert."
    ),
    "duree": (
        "Une séance dure de 6 à 9 minutes selon la semaine, jamais plus de 10 minutes ; "
        "la journée légère est volontairement plus courte."
    ),
    "recul": (
        "Si deux séances consécutives d'un thème passent sous 50 % de réussite, le "
        "palier courant se reprend avant toute nouvelle montée en complexité."
    ),
}


def _plafonds(semaine: int) -> dict[str, int]:
    """Plafond de palier par thème pour la semaine (borné au contenu disponible)."""
    cible = PLAFOND_SEMAINE[semaine - 1]
    return {
        theme: min(PALIERS_DISPONIBLES[theme], cible)
        for theme in THEMES
    }


def _jours(semaine: int) -> list[dict]:
    """Plan des 7 jours : 5 séances, 1 journée légère, 1 jour de repos.

    La rotation démarre sur un thème différent toutes les semaines, pour que la
    même famille ne revienne pas toujours le même jour.
    """
    decalage = (semaine - 1) % len(THEMES)
    rotation = THEMES[decalage:] + THEMES[:decalage]
    jours = []
    for index, jour in enumerate(range(1, 8)):
        if jour == 6:
            jours.append({
                "jour": jour,
                "type": "legere",
                "duree_min": max(4, DUREE_SEMAINE[semaine - 1] - 2),
                "themes": ["au-choix"],
                "themes_extra": THEMES_EXTRA,
            })
        elif jour == 7:
            jours.append({
                "jour": jour,
                "type": "repos",
                "duree_min": 0,
                "themes": [],
            })
        else:
            jours.append({
                "jour": jour,
                "type": "seance",
                "duree_min": DUREE_SEMAINE[semaine - 1],
                "themes": [rotation[index % len(rotation)]],
            })
    return jours


def construire_programme() -> dict:
    """Assemble le programme complet (8 semaines de 7 jours)."""
    semaines = [
        {
            "semaine": numero,
            "duree_min": DUREE_SEMAINE[numero - 1],
            "plafond_palier": _plafonds(numero),
            "jours": _jours(numero),
        }
        for numero in range(1, SEMAINES + 1)
    ]
    return {
        "titre": "Programme de 8 semaines",
        "duree_semaines": SEMAINES,
        "seances_par_jour": 1,
        "themes": THEMES,
        "themes_extra": THEMES_EXTRA,
        "paliers_disponibles": PALIERS_DISPONIBLES,
        "regles": REGLES,
        "semaines": semaines,
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le programme de 8 semaines.")
    parseur.add_argument("--dry-run", action="store_true", help="afficher un résumé sans écrire")
    options = parseur.parse_args()

    programme = construire_programme()
    chemin = DOSSIER_SORTIE / NOM_FICHIER
    if options.dry_run:
        for semaine in programme["semaines"]:
            plan = " ".join(
                f"J{jour['jour']}={jour['type']}" for jour in semaine["jours"]
            )
            print(f"Semaine {semaine['semaine']} ({semaine['duree_min']} min) : {plan}")
        print(f"[dry-run] {chemin.relative_to(RACINE_DEPOT)} — {len(programme['semaines'])} semaines")
        return 0

    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8") as flux:
        json.dump(programme, flux, ensure_ascii=False, indent=2)
        flux.write("\n")
    total_jours = sum(len(semaine["jours"]) for semaine in programme["semaines"])
    print(f"[écrit] {chemin.relative_to(RACINE_DEPOT)} — {len(programme['semaines'])} semaines, {total_jours} jours")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
