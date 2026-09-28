#!/usr/bin/env python3
"""Mesure la difficulté clinique des grilles « déduction » — sans solveur-compteur.

Le nombre de tours du solveur ne dit **rien** de la difficulté ressentie : il mesure
la machine, pas le raisonnement humain. Les mesures qui comptent sont :

- **phrases** : combien d'énoncés la grille présente ;
- **k** : combien de phrases (dans l'ordre présenté) il faut lire avant le premier
  placement certain — la « mise en route » du raisonnement ;
- **phrases à effet solo** : combien de phrases, prises **seules**, déterminent déjà
  une position (domaine réduit à un singleton par propagation de cette phrase seule) ;
  attendu 0 aux paliers avancés — sinon la grille se résout par placement au lieu de
  recoupements ;
- **phrases retirables** : redondance **entre phrases** — combien peuvent être
  retirées sans perdre la déductibilité ; attendu 0 : chaque phrase doit compter ;
- **informations retirables** : redondance **interne** — combien d'informations
  (atomes) peuvent être retirées d'une phrase sans casser la déductibilité ; mesurée
  (elle n'est pas interdite : une ancre peut porter un repère non strictement
  nécessaire, mais elle doit rester rare).

Usage :

    python3 tools/mesurer_difficulte.py                    # mesure le stock actuel
    python3 tools/mesurer_difficulte.py --csv sortie.csv   # + CSV

La sortie est un tableau markdown ; avec ``--csv`` un fichier CSV est écrit en plus.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deduction_commun import propager  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
PALIERS = RACINE / "content" / "entrainement" / "deduction" / "paliers"


def _atomes(phrase: dict) -> list[dict]:
    return [phrase] + list(phrase.get("et") or [])


def _est_figure_debut(atome: dict) -> bool:
    """Un atome de figure (pas de figure2) : sa suppression retire une contrainte."""
    return "figure2" not in atome


def _determine_une_position(phrases: list[dict], n: int, figures: list[str],
                            couleurs: list[str]) -> bool:
    """La propagation de CE LOT laisse-t-il au moins une case avec un seul jeton ?"""
    domaines = propager(phrases, n, figures, couleurs)
    if domaines is None:
        return True  # contradiction = sur-contrainte, traitée comme déterminée
    return any(len(domaine) == 1 for domaine in domaines)


def _k_premier_placement(phrases: list[dict], n: int, figures: list[str],
                         couleurs: list[str]) -> int | None:
    """Nombre de phrases (ordre présenté) avant la première position certaine."""
    for coupe in range(1, len(phrases) + 1):
        if _determine_une_position(phrases[:coupe], n, figures, couleurs):
            return coupe
    return None  # jamais déterminée (grille non résoluble, d'ailleurs)


def _effet_solo(phrases: list[dict], n: int, figures: list[str],
                couleurs: list[str]) -> int:
    """Phrases qui, SEULES, fixent déjà une position (domaine singleton)."""
    total = 0
    for phrase in phrases:
        if _determine_une_position([phrase], n, figures, couleurs):
            total += 1
    return total


def _retirables_entre_phrases(phrases: list[dict], n: int, figures: list[str],
                              couleurs: list[str]) -> int:
    """Redondance entre phrases : combien peuvent disparaître sans casser la déduction.

    Glouton : on retire une phrase, on rejoue le solveur ; si la grille reste
    entièrement déterminée, la phrase était redondante et ne revient pas.
    """
    restantes = list(phrases)
    retirables = 0
    change = True
    while change:
        change = False
        for rang in range(len(restantes) - 1, -1, -1):
            essai = restantes[:rang] + restantes[rang + 1:]
            if not essai:
                continue
            domaines = propager(essai, n, figures, couleurs)
            if domaines is not None and all(len(d) == 1 for d in domaines):
                restantes = essai
                retirables += 1
                change = True
                break
    return retirables


def _retirables_internes(phrases: list[dict], n: int, figures: list[str],
                        couleurs: list[str]) -> int:
    """Redondance interne : informations d'une phrase qu'on peut vider sans casser.

    Une information est « vidée » quand on la retire du champ ``et`` (ou qu'on vide le
    contenu d'une phrase devenue un seul atome binaire → phrase retirée si la grille
    tient sans elle). On mesure le nombre total d'informations retirables.
    """
    total = 0
    for rang, phrase in enumerate(phrases):
        atomes = _atomes(phrase)
        if len(atomes) < 2:
            continue
        for pos in range(1, len(atomes)):  # on ne vide jamais l'ancre de tête
            restes = [a for i, a in enumerate(atomes) if i != pos]
            essai = phrases[:rang] + phrases[rang + 1:] + [restes[0]] if len(restes) == 1 else None
            if essai is None:
                reduite = dict(restes[0])
                reduite["et"] = restes[1:]
                essai = phrases[:rang] + [reduite] + phrases[rang + 1:]
            domaines = propager(essai, n, figures, couleurs)
            if domaines is not None and all(len(d) == 1 for d in domaines):
                total += 1
    return total


def _mesurer_item(item: dict) -> dict:
    contenu = item["contenu"]
    n = len(contenu["figures"])
    phrases = contenu["enonces"]
    infos = sum(len(_atomes(p)) for p in phrases)
    return {
        "id": item["id"],
        "palier": item["palier"],
        "taille": n,
        "phrases": len(phrases),
        "informations": infos,
        "k": _k_premier_placement(phrases, n, contenu["figures"], contenu["couleurs"]),
        "solo": _effet_solo(phrases, n, contenu["figures"], contenu["couleurs"]),
        "retirables": _retirables_entre_phrases(phrases, n, contenu["figures"], contenu["couleurs"]),
        "retirables_internes": _retirables_internes(phrases, n, contenu["figures"], contenu["couleurs"]),
    }


def _tableau(mesures: list[dict]) -> str:
    lignes = ["| grille | palier | taille | phrases | informations | k (premier placement) | effet solo | retirables | informations retirables |",
              "|---|---|---|---|---|---|---|---|---|"]
    for m in mesures:
        lignes.append(
            "| {id} | {palier} | {taille}x{taille} | {phrases} | {informations} | {k} | {solo} | {retirables} | {retirables_internes} |".format(**m)
        )
    return "\n".join(lignes)


def main() -> int:
    parseur = argparse.ArgumentParser(description="Mesure la difficulté des grilles déduction.")
    parseur.add_argument("--csv", type=Path, default=None,
                         help="Écrit aussi un CSV à ce chemin.")
    options = parseur.parse_args()

    mesures: list[dict] = []
    for fichier in sorted(PALIERS.glob("palier-*.json")):
        for item in json.loads(fichier.read_text(encoding="utf-8")):
            mesures.append(_mesurer_item(item))

    print(f"# Mesure de difficulté — {len(mesures)} grilles\n")
    print(_tableau(mesures))

    # Synthèse par palier : ce sont ces colonnes qui portent le jugement.
    print("\n## Synthèse par palier\n")
    print("| palier | grilles | phrases (moy) | k min | k max | effet solo (total) | retirables (total) | infos internes retirables |")
    print("|---|---|---|---|---|---|---|---|")
    for palier in sorted({m["palier"] for m in mesures}):
        lot = [m for m in mesures if m["palier"] == palier]
        ks = [m["k"] for m in lot if m["k"] is not None]
        print(f"| {palier} | {len(lot)} | {sum(m['phrases'] for m in lot) / len(lot):.1f} "
              f"| {min(ks)} | {max(ks)} "
              f"| {sum(m['solo'] for m in lot)} "
              f"| {sum(m['retirables'] for m in lot)} "
              f"| {sum(m['retirables_internes'] for m in lot)} |")

    if options.csv:
        options.csv.parent.mkdir(parents=True, exist_ok=True)
        with options.csv.open("w", encoding="utf-8", newline="") as flux:
            ecrivain = csv.DictWriter(flux, fieldnames=list(mesures[0].keys()))
            ecrivain.writeheader()
            ecrivain.writerows(mesures)
        print(f"\nCSV écrit : {options.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
