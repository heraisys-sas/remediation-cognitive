#!/usr/bin/env python3
"""Remet à zéro le compteur de séances de la fenêtre courante (outil d'essai).

Le dosage du produit — 3 séances par jour en entraînement, 1 par semaine en
évaluation — est un garde-fou clinique : il n'est pas modifié ici. Cet outil sert
uniquement à **rouvrir la fenêtre** (journée, ou semaine pour l'évaluation) pendant
les essais, sans toucher aux autres données (cartes de révision, courbes de maîtrise,
journal).

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

# Fenêtres de comptage : même source de vérité que le serveur (domaine).
sys.path.insert(0, str(RACINE_DEPOT))
from backend.app.domain.contenu import ChargeurContenu  # noqa: E402
from backend.app.domain.dosage import debut_fenetre, fenetre_sessions  # noqa: E402


def compteurs() -> list[Path]:
    """Tous les compteurs de séances présents dans les données locales."""
    return sorted(RACINE_DONNEES.glob("entrainement/*/compteur-seances.json"))


def main() -> int:
    parseur = argparse.ArgumentParser(description="Remet à zéro le compteur de séances de la fenêtre courante.")
    parseur.add_argument("theme", nargs="?", help="thème précis (par défaut : tous)")
    parseur.add_argument("--date", default=date.today().isoformat(),
                         help="date de référence des fenêtres (par défaut : aujourd'hui)")
    parseur.add_argument("--dry-run", action="store_true")
    options = parseur.parse_args()

    cibles = [c for c in compteurs() if options.theme is None or c.parent.name == options.theme]
    if not cibles:
        portee = "thème « %s »" % options.theme if options.theme else "les données locales"
        print("Aucun compteur de séances trouvé pour %s." % portee, file=sys.stderr)
        return 1

    contenu = ChargeurContenu()
    reference = date.fromisoformat(options.date)
    for chemin in cibles:
        theme = chemin.parent.name
        fenetre = fenetre_sessions(contenu.categorie(theme))
        debut = debut_fenetre(fenetre, reference)
        intitule = "journée" if fenetre == "jour" else "semaine"
        donnees = json.loads(chemin.read_text(encoding="utf-8")) or {}
        avant = donnees.get("nb_sessions", 0)
        if options.dry_run:
            print("[dry-run] %s : %s séance(s) -> 0 (%s du %s)" % (theme, avant, intitule, debut.isoformat()))
            continue
        chemin.write_text(
            json.dumps({"date": debut.isoformat(), "nb_sessions": 0}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
        print("%s : %s séance(s) -> 0 (%s du %s rouverte)" % (theme, avant, intitule, debut.isoformat()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
