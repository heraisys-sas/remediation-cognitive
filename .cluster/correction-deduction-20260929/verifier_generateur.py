#!/usr/bin/env python3
"""Le générateur produit-il un contenu conforme ? (essai borné, en mémoire)"""
import random
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "tools"))
import generer_deduction as g  # noqa: E402
from deduction_commun import (  # noqa: E402
    TYPES_BINAIRES, phrases_qui_fixent_seules, rang_premiere_certitude, resoudre_par_deduction,
)

NOMBRE = int(sys.argv[1]) if len(sys.argv) > 1 else 4
rng = random.Random(g.GRAINE)
deja_vus: set = set()
paliers = [g.generer_palier(p, rng, NOMBRE, deja_vus) for p in (1, 2, 3, 4)]
erreurs = []
total = 0
for numero, items in enumerate(paliers, start=1):
    for item in items:
        total += 1
        c = item["contenu"]
        n = len(c["figures"])
        enonces = c["enonces"]
        if len(enonces) < 4:
            erreurs.append((item["id"], "moins de 4 phrases"))
        if numero in (2, 3, 4):
            solos = phrases_qui_fixent_seules(enonces, n, c["figures"], c["couleurs"])
            if solos:
                erreurs.append((item["id"], "phrase solo %s" % solos))
            rang = rang_premiere_certitude(enonces, n, c["figures"], c["couleurs"])
            if rang == 1:
                erreurs.append((item["id"], "première certitude au rang 1"))
        if not resoudre_par_deduction(enonces, n, c["figures"], c["couleurs"]):
            erreurs.append((item["id"], "non déterminée"))
        for phrase in enonces:
            infos = 1 + len(phrase.get("et") or [])
            types = {a.get("type") for a in [phrase] + list(phrase.get("et") or [])}
            if infos < 2:
                erreurs.append((item["id"], "phrase à %d information(s)" % infos))
            if not (types & TYPES_BINAIRES):
                erreurs.append((item["id"], "phrase sans relation binaire"))
print("grilles générées :", total)
for e in erreurs[:12]:
    print("  ERREUR:", e)
print("total erreurs :", len(erreurs))
