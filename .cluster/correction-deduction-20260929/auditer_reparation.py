#!/usr/bin/env python3
"""Audit des grilles réparées : solo, détermination, redondances, unicité."""
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "tools"))
from deduction_commun import (  # noqa: E402
    phrases_qui_fixent_seules, propager, rang_premiere_certitude, resoudre_par_deduction,
)


def retirables(phrases, n, figures, couleurs):
    restantes, total = list(phrases), 0
    change = True
    while change:
        change = False
        for rang in range(len(restantes) - 1, -1, -1):
            essai = restantes[:rang] + restantes[rang + 1:]
            if len(essai) < 4:
                continue
            d = propager(essai, n, figures, couleurs)
            if d is not None and all(len(x) == 1 for x in d):
                restantes = essai
                total += 1
                change = True
                break
    return total


items = json.loads((RACINE / "content/entrainement/deduction/paliers/palier-03.json").read_text())
for item in items:
    if not item["id"].startswith("dc-"):
        continue
    c = item["contenu"]
    n = len(c["figures"])
    enonces = c["enonces"]
    solos = phrases_qui_fixent_seules(enonces, n, c["figures"], c["couleurs"])
    det = resoudre_par_deduction(enonces, n, c["figures"], c["couleurs"])
    rang = rang_premiere_certitude(enonces, n, c["figures"], c["couleurs"])
    re_ = retirables(enonces, n, c["figures"], c["couleurs"])
    print(f"{item['id']}: {len(enonces)} phrases | solo={len(solos)} | determine={det} | rang={rang} | retirables={re_}")
