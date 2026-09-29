#!/usr/bin/env python3
"""Harmonise l'aide des items avancés (paliers 2–4) avec AIDE_CROISEMENT.

47 items portaient encore l'ancien texte « dont la phrase donne la position ».
Le contenu pédagogique change (l'aide) : la règle du contenu versionné impose de
nouveaux identifiants — dérivés du contenu (identifiant_item). Énoncés, solutions,
indices et consigne sont strictement préservés ; l'aide, la méta et l'identifiant
changent, jamais autre chose.

Usage (depuis la racine du dépôt) :
    python3 .cluster/correction-deduction-20260929/harmoniser_aides.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "tools"))
from generer_deduction import AIDE_CROISEMENT, identifiant_item  # noqa: E402

PALIERS = RACINE / "content" / "entrainement" / "deduction" / "paliers"
ANCIEN = "dont la phrase donne la position"
DATE = "2026-09-29"
NOTE = "correction 2026-09-29 : aide harmonisée (croisement des phrases)"


def main() -> int:
    lots = {}
    ids_avant = set()
    for numero in (1, 2, 3, 4):
        chemin = PALIERS / ("palier-%02d.json" % numero)
        items = json.loads(chemin.read_text(encoding="utf-8"))
        lots[numero] = (chemin, items)
        ids_avant |= {item["id"] for item in items}

    remplacements = []
    for numero in (2, 3, 4):
        for item in lots[numero][1]:
            if ANCIEN not in item["contenu"].get("aide", ""):
                continue  # déjà harmonisé (dc-3-*) ou contenu non concerné
            copie = json.loads(json.dumps(item))  # instantané avant modification
            item["contenu"]["aide"] = AIDE_CROISEMENT
            item["meta"]["date_creation"] = DATE
            auteur = item["meta"].get("auteur", "")
            if "correction 2026-09-29" not in auteur:
                item["meta"]["auteur"] = (auteur + " ; " + NOTE).strip(" ;")
            ancien_id = item["id"]
            item["id"] = identifiant_item(item["palier"], item["contenu"], item["reponse"])
            # Strictement rien d'autre ne change.
            assert item["contenu"]["enonces"] == copie["contenu"]["enonces"]
            assert item["contenu"]["indices"] == copie["contenu"]["indices"]
            assert item["contenu"]["consigne"] == copie["contenu"]["consigne"]
            assert item["contenu"]["figures"] == copie["contenu"]["figures"]
            assert item["contenu"]["couleurs"] == copie["contenu"]["couleurs"]
            assert item["reponse"] == copie["reponse"]
            assert item["contenu"]["aide"] != copie["contenu"]["aide"]
            remplacements.append((numero, ancien_id, item["id"]))

    ids_apres = [item["id"] for num in (1, 2, 3, 4) for item in lots[num][1]]
    assert len(set(ids_apres)) == len(ids_apres), "collision d'identifiants"
    nouveaux = {nouveau for _, _, nouveau in remplacements}
    assert not (nouveaux & ids_avant), "un nouvel identifiant reprend un identifiant existant"

    for numero in (1, 2, 3, 4):
        chemin, items = lots[numero]
        chemin.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lignes = ["# Correspondance des identifiants — harmonisation des aides (2026-09-29)", ""]
    lignes += ["- %s → %s" % (ancien, nouveau) for _, ancien, nouveau in remplacements]
    (RACINE / ".cluster/correction-deduction-20260929"
     / "mapping_aides_anciens_nouveaux.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")

    for numero in (2, 3, 4):
        nb = sum(1 for n, _, _ in remplacements if n == numero)
        print("palier %d : %d aide(s) harmonisée(s)" % (numero, nb))
    print("total : %d items ; mapping écrit" % len(remplacements))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
