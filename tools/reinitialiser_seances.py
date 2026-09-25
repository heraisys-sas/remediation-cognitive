#!/usr/bin/env python3
"""Remet à zéro le compteur de séances du jour (outil d'essai).

Le dosage du produit — 3 séances par jour en entraînement, 1 en évaluation — est un
garde-fou clinique : il n'est pas modifié ici. Cet outil sert uniquement à **rouvrir
la journée** pendant les essais, sans toucher aux autres données (cartes de révision,
courbes de maîtrise, journal).

Usage :

    python3 tools/reinitialiser_seances.py                  # tous les thèmes
    python3 tools/reinitialiser_seances.py deduction        # un seul thème
    python3 tools/reinitialiser_seances.py --date 2026-09-25
    python3 tools/reinitialiser_seances.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
RACINE_DONNEES = RACINE_DEPOT / "backend" / "data"


def compteurs() -> list[Path]:
    """Tous les compteurs de séances présents dans les données locales."""
    return sorted(RACINE_DONNEES.glob("entrainement/*/compteur-seances.json"))


def main() -> int:
    parseur = argparse.ArgumentParser(description="Remet à zéro le compteur de séances du jour.")
    parseur.add_argument("theme", nargs="?", help="thème précis (par défaut : tous)")
    parseur.add_argument("--date", default=date.today().isoformat(),
                         help="date à créditer (par défaut : aujourd'hui)")
    parseur.add_argument("--dry-run", action="store_true")
    options = parseur.parse_args()

    cibles = [c for c in compteurs() if options.theme is None or c.parent.name == options.theme]
    if not cibles:
        portee = "thème « %s »" % options.theme if options.theme else "les données locales"
        print("Aucun compteur de séances trouvé pour %s." % portee, file=sys.stderr)
        return 1

    for chemin in cibles:
        donnees = json.loads(chemin.read_text(encoding="utf-8")) or {}
        avant = donnees.get("nb_sessions", 0)
        if options.dry_run:
            print("[dry-run] %s : %s séance(s) -> 0" % (chemin.parent.name, avant))
            continue
        chemin.write_text(
            json.dumps({"date": options.date, "nb_sessions": 0}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
        print("%s : %s séance(s) -> 0 (journée du %s rouverte)" % (chemin.parent.name, avant, options.date))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
