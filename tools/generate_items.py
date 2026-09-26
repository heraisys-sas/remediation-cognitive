#!/usr/bin/env python3
"""Générateur d'items de calcul mental — automatismes utiles et numératie du quotidien.

Génère, avec la seule bibliothèque standard, le contenu du thème « calcul-mental » :

- ``content/entrainement/calcul-mental/paliers/palier-01.json`` … ``palier-09.json`` ;
- ``content/entrainement/calcul-mental/paliers.json`` : manifest ordonné.

**Pourquoi cette progression et pas les tables dans l'ordre scolaire.** Un adulte
n'a rien à automatiser sur la table de 1 ni sur celle de 10 : ce ne sont pas des
faits à retrouver mais des **règles** (« × 1 ne change rien », « × 10 ajoute un
zéro »). Les driller prend du temps sans rien construire. La progression retenue
suit ce dont un adulte se sert réellement :

1. **faits de base** (compléments dans 10, doubles, additions et soustractions
   dans 20) — la récupération automatique libère de la mémoire de travail ;
2. **repères étendus** (compléments à 100, multiplications utiles ×2 à ×5) ;
3. **mémoire de travail** (deux opérations enchaînées) ;
4. **numératie du quotidien** (argent, quantités, durées) — le transfert dans la
   vie réelle, qui est le but du module.

Les énoncés sont des questions courtes et naturelles, jamais « 2 × 1 » : on
s'adresse à un adulte, pas à un enfant qui apprend ses tables.

Usage :

    python3 tools/generate_items.py [--dry-run] [--date AAAA-MM-JJ]
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

# --- Paramètres de génération -------------------------------------------------

#: Graine fixe : la régénération est déterministe, le contenu est versionné.
GRAINE: int = 20260926

#: Nombre d'items par palier.
ITEMS_PAR_PALIER: int = 18

#: Métadonnées traçables posées sur chaque item généré.
AUTEUR: str = "generation-automatique (tools/generate_items.py)"
DATE_CREATION_DEFAUT: str = "2026-09-26"

RACINE_DEPOT = Path(__file__).resolve().parent.parent
DOSSIER_SORTIE = RACINE_DEPOT / "content" / "entrainement" / "calcul-mental"

#: Description de chaque palier (manifest) : ce qui est travaillé, en clair.
DESCRIPTIONS: list[str] = [
    "Compléments et retraits dans 10 : les faits de base",
    "Doubles et presque-doubles : une stratégie avant le calcul",
    "Additions dans 20 : récupération automatique",
    "Soustractions dans 20 : récupération automatique",
    "Compléments à 100 : les repères d'argent et de quantités",
    "Multiplications utiles (× 2 à × 5) : doubler, tripler, partager",
    "Deux opérations enchaînées : mémoire de travail",
    "Au quotidien : l'argent (total, rendu de monnaie)",
    "Au quotidien : quantités et durées (proportions, totaux)",
]

#: Fonctions ciblées par palier (au-delà de l'automatisation de base).
FONCTIONS_PAR_PALIER: list[list[str]] = [
    ["automatisation"],
    ["automatisation", "flexibilite"],
    ["automatisation"],
    ["automatisation"],
    ["automatisation", "memoire-travail"],
    ["automatisation"],
    ["memoire-travail", "fonctions-executives"],
    ["automatisation", "memoire-travail"],
    ["memoire-travail", "fonctions-executives"],
]

#: Aide (repliée) et consigne (une fois par séance) par palier, quand elles servent.
CONSIGNES: dict[int, str] = {
    7: "Calcule par étapes, sans rien écrire : d'abord la première opération, puis la seconde.",
}
AIDES: dict[int, str] = {
    2: "Un presque-double, c'est le double plus un : 7 + 8 = 7 + 7 + 1.",
    5: "Pour aller à 100, complète d'abord à la dizaine suivante.",
    6: "Doubler, c'est × 2 ; partager en deux, c'est ÷ 2.",
    7: "Garde le premier résultat en tête, puis enchaîne la seconde opération.",
    8: "Rends la monnaie : ce qu'on te donne moins ce que ça coûte.",
    9: "Pour le double de personnes, il faut le double de quantité.",
}
CAPS: dict[int, str] = {
    7: "deux opérations au maximum (charge de mémoire de travail bornée)",
    9: "une seule transformation (double ou total), sans pourcentage",
}


def _item(numero_palier: int, rang: int, enonce: str, valeur: int,
          date_creation: str, aide: str | None = None) -> dict:
    """Construit un item de production conforme à content/schema-item.json.

    Les identifiants portent un suffixe de génération (``cm2-``) : le contenu a été
    entièrement revu, il ne doit donc pas hériter des états de révision de l'ancien
    (règle de versionnage du contenu).
    """
    contenu: dict = {"enonce": enonce, "aide": aide}
    if numero_palier in CONSIGNES:
        contenu["consigne"] = CONSIGNES[numero_palier]
    return {
        "id": f"cm2-{numero_palier}-{rang:02d}",
        "type": "production",
        "module": "entrainement",
        "theme": "calcul-mental",
        "fonctions_ciblees": FONCTIONS_PAR_PALIER[numero_palier - 1],
        "palier": numero_palier,
        "prerequis": [] if numero_palier == 1 else [f"cm-palier-{numero_palier - 1}"],
        "cap_complexite": CAPS.get(numero_palier),
        "contenu": contenu,
        "reponse": {"valeur": valeur},
        "meta": {
            "auteur": AUTEUR,
            "date_creation": date_creation,
            "relecture_ortho": {"statut": "a_revoir"},
        },
    }


def _complements_dans_10(rng: random.Random) -> list[tuple[str, int]]:
    """Faits de base : ce qui manque pour faire 10, puis les retraits dans 10."""
    couples = []
    for n in range(1, 10):
        couples.append((f"Combien manque-t-il à {n} pour faire 10 ?", 10 - n))
    for n in range(2, 11):
        couples.append((f"Combien font 10 − {n} ?", 10 - n))
    rng.shuffle(couples)
    return couples


def _doubles(rng: random.Random) -> list[tuple[str, int]]:
    """Doubles puis presque-doubles : la stratégie précède l'automatisme."""
    couples = [(f"Combien font {n} + {n} ?", 2 * n) for n in range(3, 10)]
    couples += [(f"Combien font {n} + {n + 1} ?", 2 * n + 1) for n in range(3, 10)]
    rng.shuffle(couples)
    return couples


def _additions_dans_20(rng: random.Random) -> list[tuple[str, int]]:
    couples = []
    for a in range(2, 10):
        for b in range(3, 10):
            if 8 <= a + b <= 19 and a <= b:
                couples.append((f"Combien font {a} + {b} ?", a + b))
    rng.shuffle(couples)
    return couples


def _soustractions_dans_20(rng: random.Random) -> list[tuple[str, int]]:
    couples = []
    for total in range(11, 20):
        for partie in range(3, total - 2):
            couples.append((f"Combien font {total} − {partie} ?", total - partie))
    rng.shuffle(couples)
    return couples


def _complements_a_100(rng: random.Random) -> list[tuple[str, int]]:
    couples = []
    for dizaine in range(10, 100, 10):
        couples.append((f"Combien manque-t-il à {dizaine} pour faire 100 ?", 100 - dizaine))
    for depart in (15, 25, 35, 45, 55, 65, 75, 85, 95):
        couples.append((f"Combien manque-t-il à {depart} pour faire 100 ?", 100 - depart))
    rng.shuffle(couples)
    return couples


def _multiplications_utiles(rng: random.Random) -> list[tuple[str, int]]:
    """× 2 à × 5 seulement : ni × 1 (règle), ni × 10 (règle), ni grosses tables."""
    couples = []
    for table in (2, 3, 4, 5):
        for facteur in range(3, 10):
            couples.append((f"Combien font {table} × {facteur} ?", table * facteur))
    rng.shuffle(couples)
    return couples


def _deux_etapes(rng: random.Random) -> list[tuple[str, int]]:
    """Deux opérations enchaînées : la mémoire de travail entre en jeu."""
    couples = []
    for a in range(4, 10):
        for b in range(3, 10):
            if a + b > 17:
                continue
            retrait = (a + b) % 5 + 2
            # Écarter les cas où le retrait annule un des termes (« 8 + 3 − 3 »).
            if retrait in (a, b) or a + b - retrait < 2:
                continue
            couples.append((f"Combien font {a} + {b} − {retrait} ?", a + b - retrait))
    for table in (2, 3, 4):
        for facteur in range(3, 8):
            ajout = table + 1
            couples.append((f"Combien font {table} × {facteur} + {ajout} ?",
                            table * facteur + ajout))
    rng.shuffle(couples)
    return couples


def _argent(rng: random.Random) -> list[tuple[str, int]]:
    """Argent : totaux et rendus de monnaie, à résultat entier."""
    couples = []
    # Totaux d'articles (prix entiers, petits nombres).
    for prix in (2, 3, 4, 5, 6, 7):
        for nombre in (2, 3):
            couples.append((f"{nombre} articles à {prix} € — combien en tout ?", prix * nombre))
    # Rendu de monnaie : le rendu n'a de sens que si l'article coûte moins que la coupure.
    for prix in (2, 3, 4, 6, 7, 8):
        couples.append((f"Un article à {prix} €, payé avec 10 € — combien te rend-on ?", 10 - prix))
    for prix in (12, 14, 15, 16, 18, 19):
        couples.append((f"Un article à {prix} €, payé avec 20 € — combien te rend-on ?", 20 - prix))
    # Prix décimal dont le double reste entier (utilisé dans la vie courante).
    for prix in ("2,50", "4,50", "12,50", "1,50"):
        couples.append((f"Deux articles à {prix} € — combien en tout ?", int(float(prix.replace(",", ".")) * 2)))
    rng.shuffle(couples)
    return couples


def _quantites(rng: random.Random) -> list[tuple[str, int]]:
    """Quantités et durées : proportions et totaux, à résultat entier."""
    couples = [
        ("Pour 4 personnes, il faut 250 g de farine. Pour 8 personnes ?", 500),
        ("Pour 4 personnes, il faut 150 g de riz. Pour 8 personnes ?", 300),
        ("Une recette pour 2 personnes demande 3 œufs. Pour 6 personnes ?", 9),
        ("Une recette pour 4 personnes demande 200 g de sucre. Pour 12 personnes ?", 600),
        ("Un pot de peinture couvre 5 m². Pour 20 m², combien de pots ?", 4),
        ("Une séance dure 20 minutes. Trois séances ?", 60),
        ("Une séance dure 25 minutes. Deux séances ?", 50),
        ("Un trajet dure 15 minutes. Quatre trajets ?", 60),
        ("Un film de 90 minutes, plus 15 minutes de pause ?", 105),
        ("Trois rendez-vous d'une heure trente ? (en minutes)", 270),
        ("Un paquet contient 12 biscuits. Deux paquets ?", 24),
        ("Un paquet contient 10 serviettes. Il en reste 4 : combien ont été prises ?", 6),
        ("20 tablettes de chocolat partagées en 4 sachets — combien par sachet ?", 5),
        ("Quinze cartons rangés par piles de 5 : combien de piles ?", 3),
        ("Un exercice prend 8 minutes. Cinq exercices ?", 40),
        ("Quatre séries de 7 répétitions ?", 28),
        ("Une boîte de 30 comprimés, 3 par jour pendant 5 jours : combien en reste-t-il ?", 15),
        ("Deux litres et demi d'eau, plus trois litres et demi ?", 6),
    ]
    rng.shuffle(couples)
    return couples


#: Une famille d'items par palier : (génératrice, nombre d'items).
FAMILLES: list[tuple] = [
    (_complements_dans_10, 18),
    (_doubles, 14),
    (_additions_dans_20, 18),
    (_soustractions_dans_20, 18),
    (_complements_a_100, 17),
    (_multiplications_utiles, 18),
    (_deux_etapes, 18),
    (_argent, 18),
    (_quantites, 18),
]


def construire_palier(numero_palier: int, rng: random.Random, date_creation: str) -> list[dict]:
    """Construit les items d'un palier en piochant dans sa famille, sans doublon."""
    generatrice, nombre = FAMILLES[numero_palier - 1]
    couples = list(dict.fromkeys(generatrice(rng)))
    items = []
    for rang, (enonce, valeur) in enumerate(couples[:nombre], start=1):
        items.append(_item(numero_palier, rang, enonce, valeur, date_creation,
                           AIDES.get(numero_palier)))
    if len(items) < nombre:
        raise SystemExit(f"palier {numero_palier} : {len(items)} item(s) seulement")
    return items


def construire_manifest(paliers: list[list[dict]]) -> dict:
    """Manifest ordonné : id, description, prérequis, fichier et nombre d'items."""
    return {
        "theme": "calcul-mental",
        "paliers": [
            {
                "id": f"cm-palier-{numero}",
                "description": DESCRIPTIONS[numero - 1],
                "prerequis": [] if numero == 1 else [f"cm-palier-{numero - 1}"],
                "fichier": f"paliers/palier-{numero:02d}.json",
                "nb_items": len(items),
            }
            for numero, items in enumerate(paliers, start=1)
        ],
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le thème « calcul-mental ».")
    parseur.add_argument("--dry-run", action="store_true")
    parseur.add_argument("--date", default=DATE_CREATION_DEFAUT,
                         help="date de création posée dans les métadonnées")
    options = parseur.parse_args()

    rng = random.Random(GRAINE)
    paliers = [construire_palier(numero, rng, options.date)
               for numero in range(1, len(FAMILLES) + 1)]

    cibles = {DOSSIER_SORTIE / "paliers.json": construire_manifest(paliers)}
    for numero, items in enumerate(paliers, start=1):
        cibles[DOSSIER_SORTIE / "paliers" / f"palier-{numero:02d}.json"] = items

    for chemin, donnees in cibles.items():
        nb = len(donnees["paliers"]) if isinstance(donnees, dict) else len(donnees)
        if options.dry_run:
            print(f"[dry-run] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
        else:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
            print(f"[écrit] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
    print(f"Total : {sum(len(p) for p in paliers)} items, {len(paliers)} paliers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
