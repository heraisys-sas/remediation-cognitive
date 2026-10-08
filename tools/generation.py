"""Infrastructure I/O des générateurs ; aucun tirage ni règle de contenu."""
import argparse
import json
from pathlib import Path


def arguments_generation(description: str, argv=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--dry-run", action="store_true", help="afficher sans écrire")
    return parser.parse_args(argv)


def ecrire_json(chemin: Path, donnees, *, dry_run: bool = False) -> None:
    if not dry_run:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
