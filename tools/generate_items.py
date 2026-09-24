#!/usr/bin/env python3
"""Générateur d'items de calcul mental — paliers Kumon-like (tables ×2 à ×9).

Génère, avec la seule bibliothèque standard, le contenu de départ du thème
« calcul-mental » du module Entraînement :

- ``content/entrainement/calcul-mental/paliers/palier-01.json`` …
  ``palier-09.json`` : un tableau d'items par palier ;
- ``content/entrainement/calcul-mental/paliers.json`` : manifest ordonné
  des paliers (id, table, prerequis, fichier, nb_items).

Ordre imposé des paliers : ×2, ×5, ×10, ×3, ×4, ×6, ×7, ×8, ×9. Chaque palier
couvre **toute** la table dans les deux sens (``a × b`` et ``b × a``), avec
déduplication du carré (``n × n`` une seule fois), soit 19 items uniques par
palier. Les facteurs croisés vont de 1 à 10.

Format de sortie : conforme à ``content/schema-item.json`` — module
« entrainement », type « production », fonction cible « automatisation »,
énoncé ``a × b``, réponse numérique attendue.

Usage :

    python3 tools/generate_items.py [--dry-run] [--date AAAA-MM-JJ]

La date de création est fixée par défaut (régénération déterministe, contenu
versionné) ; ``--date`` permet de la changer. Contenu généré procéduralement :
100 % original,
TEA-Ch).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# --- Paramètres de génération -------------------------------------------------

#: Table couverte par chaque palier, dans l'ordre Kumon-like imposé (palier 1 → 9).
TABLES_PAR_PALIER: list[int] = [2, 5, 10, 3, 4, 6, 7, 8, 9]

#: Bornes des facteurs croisés : chaque table est croisée avec 1..FACTEUR_MAX.
FACTEUR_MIN: int = 1
FACTEUR_MAX: int = 10

#: Métadonnées traçables posées sur chaque item généré.
AUTEUR: str = "generation-automatique (tools/generate_items.py)"
DATE_CREATION_DEFAUT: str = "2026-09-03"

#: Racine du dépôt (parent du dossier tools/) et dossier de sortie du contenu.
RACINE_DEPOT = Path(__file__).resolve().parent.parent
DOSSIER_SORTIE = RACINE_DEPOT / "content" / "entrainement" / "calcul-mental"


# --- Construction des items ---------------------------------------------------


def construire_item(
    table: int, a: int, b: int, numero_palier: int, prerequis: list[str], date_creation: str
) -> dict:
    """Construit un item de production conforme à content/schema-item.json.

    Args:
        table: table du palier (sert d'espace de nommage dans l'identifiant).
        a: premier facteur de l'énoncé ``a × b``.
        b: second facteur de l'énoncé.
        numero_palier: numéro du palier (1-based).
        prerequis: identifiants de concepts/items prérequis (graphe de connaissances).
        date_creation: date ISO 8601 posée dans ``meta.date_creation``.

    Returns:
        Item complet, prêt à être sérialisé en JSON.
    """
    return {
        "id": f"cm-{table}-{a}x{b}",
        "type": "production",
        "module": "entrainement",
        "theme": "calcul-mental",
        "fonctions_ciblees": ["automatisation"],
        "palier": numero_palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": {"enonce": f"{a} × {b}", "aide": None},
        "reponse": {"valeur": a * b},
        "meta": {
            "auteur": AUTEUR,
            "date_creation": date_creation,
            "relecture_ortho": {"statut": "a_revoir"},
        },
    }


def construire_palier(table: int, numero_palier: int, date_creation: str) -> list[dict]:
    """Construit les items d'un palier : toute la table, deux sens, dédupliquée.

    Pour chaque facteur croisé ``b`` (1..10), on produit ``table × b`` puis
    ``b × table`` ; le carré ``table × table`` n'apparaît qu'une seule fois,
    soit 19 items uniques par palier. Le prérequis d'un palier est le palier
    précédent (identifiant de concept ``cm-palier-N`` défini dans le manifest).

    Args:
        table: table de multiplication couverte par le palier.
        numero_palier: numéro du palier (1-based).
        date_creation: date ISO 8601 posée dans les métadonnées.

    Returns:
        Liste ordonnée d'items uniques.
    """
    prerequis = [] if numero_palier == 1 else [f"cm-palier-{numero_palier - 1}"]
    items: list[dict] = []
    for b in range(FACTEUR_MIN, FACTEUR_MAX + 1):
        # Deux sens (a×b et b×a) sauf pour le carré, produit une seule fois.
        couples = [(table, b)] if b == table else [(table, b), (b, table)]
        for a, c in couples:
            items.append(construire_item(table, a, c, numero_palier, prerequis, date_creation))
    return items


def construire_manifest(paliers: list[list[dict]]) -> dict:
    """Construit le manifest ordonné des paliers.

    Args:
        paliers: listes d'items, indexées par numéro de palier (0-based ici).

    Returns:
        Manifest : thème, puis paliers avec id, table, prerequis, fichier et
        nombre d'items. Le prerequis d'un palier est le palier précédent.
    """
    entrees = []
    for numero, items in enumerate(paliers, start=1):
        entrees.append(
            {
                "id": f"cm-palier-{numero}",
                "table": TABLES_PAR_PALIER[numero - 1],
                "prerequis": [] if numero == 1 else [f"cm-palier-{numero - 1}"],
                "fichier": f"paliers/palier-{numero:02d}.json",
                "nb_items": len(items),
            }
        )
    return {"theme": "calcul-mental", "paliers": entrees}


# --- Écriture -----------------------------------------------------------------


def ecrire_json(chemin: Path, donnees: dict | list) -> None:
    """Écrit ``donnees`` en JSON UTF-8 lisible (indentation 2, accents conservés).

    Args:
        chemin: fichier cible (les parents sont créés si besoin).
        donnees: objet ou tableau à sérialiser.
    """
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8") as flux:
        json.dump(donnees, flux, ensure_ascii=False, indent=2)
        flux.write("\n")


def main() -> int:
    """Point d'entrée : construit les 9 paliers + le manifest, puis les écrit.

    Returns:
        Code de sortie (0 en cas de succès).
    """
    parseur = argparse.ArgumentParser(
        description="Génère les items de calcul mental (paliers Kumon-like, conforme au schéma)."
    )
    parseur.add_argument(
        "--dry-run", action="store_true", help="affiche le plan de génération sans écrire de fichier"
    )
    parseur.add_argument(
        "--date",
        default=DATE_CREATION_DEFAUT,
        help="date_creation (meta) à poser, AAAA-MM-JJ (défaut : %(default)s)",
    )
    options = parseur.parse_args()

    paliers = [
        construire_palier(table, numero, options.date)
        for numero, table in enumerate(TABLES_PAR_PALIER, start=1)
    ]

    cibles: dict[Path, dict | list] = {}
    for numero, items in enumerate(paliers, start=1):
        cibles[DOSSIER_SORTIE / "paliers" / f"palier-{numero:02d}.json"] = items
    cibles[DOSSIER_SORTIE / "paliers.json"] = construire_manifest(paliers)

    for chemin in sorted(cibles):
        donnees = cibles[chemin]
        taille = len(donnees) if isinstance(donnees, list) else len(donnees["paliers"])
        relatif = chemin.relative_to(RACINE_DEPOT)
        if options.dry_run:
            print(f"[simulation] {relatif} ({taille} entrées)")
        else:
            ecrire_json(chemin, donnees)
            print(f"[écrit] {relatif} ({taille} entrées)")

    total = sum(len(items) for items in paliers)
    print(f"Total : {len(paliers)} paliers, {total} items.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
