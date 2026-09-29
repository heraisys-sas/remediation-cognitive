#!/usr/bin/env python3
"""Indicateurs STRUCTURELS des grilles, sans calibration clinique.

`rang_lecture` : première certitude par propagation dans l'ordre affiché ; ce
n'est PAS le nombre minimal d'indices à croiser. `support_propage` : taille du
plus petit sous-ensemble trouvé par propagation parmi les lots de 1 à 3 phrases,
indépendamment de l'ordre ; borne supérieure, jamais une preuve de minimum exact.
`solo` : raccourcis prouvés par énumération exhaustive d'une phrase.
Les informations retirables sont testées individuellement, ancres comprises ;
leur total ne signifie pas qu'on puisse toutes les supprimer simultanément.
"""

from __future__ import annotations

import argparse
import csv
import json
from itertools import combinations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deduction_commun import propager, informations_autonomes, phrases_qui_fixent_seules  # noqa: E402

RACINE = Path(__file__).resolve().parent.parent
PALIERS = RACINE / "content" / "entrainement" / "deduction" / "paliers"


def _atomes(phrase: dict) -> list[dict]:
    return [phrase] + list(phrase.get("et") or [])


def _determine_une_position(phrases: list[dict], n: int, figures: list[str],
                            couleurs: list[str]) -> bool:
    """La propagation de CE LOT laisse-t-il au moins une case avec un seul jeton ?"""
    domaines = propager(phrases, n, figures, couleurs)
    if domaines is None:
        raise ValueError("Grille contradictoire : mesure impossible")
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
    return len(phrases_qui_fixent_seules(phrases, n, figures, couleurs))


def _support_propage(phrases, n, figures, couleurs):
    for taille in range(1, min(3, len(phrases)) + 1):
        if any(_determine_une_position(list(lot), n, figures, couleurs)
               for lot in combinations(phrases, taille)):
            return taille
    return None  # aucun support trouvé jusqu'à 3, pas « minimum > 3 »


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
    """Redondance interne : informations qu'on peut retirer une à une sans casser.

    Chaque atome est réellement retiré (l'ancre comprise) : la phrase est remplacée
    par ses atomes restants, devenus des phrases autonomes — aucune copie ne garde
    un champ ``et`` caché. Une phrase à un seul atome compte si la grille tient sans
    elle. On mesure le nombre total d'informations retirables.
    """
    total = 0
    for rang, phrase in enumerate(phrases):
        informations = informations_autonomes(phrase)
        for pos in range(len(informations)):
            restes = [a for i, a in enumerate(informations) if i != pos]
            # Atomes indépendants : aucune copie ne conserve un champ `et` caché.
            essai = phrases[:rang] + restes + phrases[rang + 1:]
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
        "rang_lecture": _k_premier_placement(phrases, n, contenu["figures"], contenu["couleurs"]),
        "support_propage": _support_propage(phrases, n, contenu["figures"], contenu["couleurs"]),
        "solo": _effet_solo(phrases, n, contenu["figures"], contenu["couleurs"]),
        "retirables": _retirables_entre_phrases(phrases, n, contenu["figures"], contenu["couleurs"]),
        "retirables_internes": _retirables_internes(phrases, n, contenu["figures"], contenu["couleurs"]),
    }


def _tableau(mesures: list[dict]) -> str:
    lignes = ["| grille | palier | taille | phrases | informations | rang de lecture (propagation) | support trouvé (borne ≤) | effet solo | retirables | informations retirables |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for m in mesures:
        lignes.append(
            "| {id} | {palier} | {taille}x{taille} | {phrases} | {informations} | {rang_lecture} | {support_propage} | {solo} | {retirables} | {retirables_internes} |".format(**m)
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

    print("Rang de lecture ≠ minimum logique. Support propagé ≤ 3 : borne supérieure, vide si non trouvé.\n")
    print(f"# Indicateurs structurels — {len(mesures)} grilles\n")
    print(_tableau(mesures))

    # Synthèse par palier : ce sont ces colonnes qui portent le jugement.
    print("\n## Synthèse par palier\n")
    print("| palier | grilles | phrases (moy) | rang lecture min | rang lecture max | effet solo (total) | retirables (total) | infos internes retirables |")
    print("|---|---|---|---|---|---|---|---|")
    for palier in sorted({m["palier"] for m in mesures}):
        lot = [m for m in mesures if m["palier"] == palier]
        ks = [m["rang_lecture"] for m in lot if m["rang_lecture"] is not None]
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
