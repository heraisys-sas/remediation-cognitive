#!/usr/bin/env python3
"""Énumération brute des solutions des 13 grilles réparées (indépendant du solveur)."""
import itertools
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "tools"))
from deduction_commun import (  # noqa: E402
    TYPES_BINAIRES, TYPES_UNAIRES, _vrai_binaire, _vrai_unaire, informations_autonomes,
    propager, resoudre_par_deduction,
)


def solutions(enonces, n, figures, couleurs, max_solutions=2):
    jetons = [(figures[f], couleurs[c]) for f in range(n) for c in range(n)]
    phrases = [informations_autonomes(p) for p in enonces]
    trouvees = []
    for placement in itertools.permutations(range(n * n)):
        cases = {jetons[i]: placement[i] for i in range(len(jetons))}
        ok = True
        for infos in phrases:
            for a in infos:
                if a["type"] in TYPES_UNAIRES:
                    if not _vrai_unaire(a, cases[(a["figure"], a["couleur"])], n):
                        ok = False; break
                else:
                    if not _vrai_binaire(a, cases[(a["figure"], a["couleur"])],
                                         cases[(a["figure2"], a["couleur2"])], n):
                        ok = False; break
            if not ok:
                break
        if ok:
            trouvees.append(placement)
            if len(trouvees) >= max_solutions:
                break
    return trouvees


def grille_depuis_placement(placement, jetons):
    grille = [None] * len(placement)
    for i, case in enumerate(placement):
        grille[case] = jetons[i]
    return grille


items = json.loads((RACINE / "content/entrainement/deduction/paliers/palier-03.json").read_text())
ok_total = 0
for item in items:
    if not item["id"].startswith("dc-"):
        continue
    c = item["contenu"]
    n = len(c["figures"])
    figures, couleurs = c["figures"], c["couleurs"]
    jetons = [(figures[f], couleurs[c_]) for f in range(n) for c_ in range(n)]
    sols = solutions(c["enonces"], n, figures, couleurs, max_solutions=2)
    stockee = [tuple(x) for x in item["reponse"]["grille"]]
    unique_ok = len(sols) == 1 and grille_depuis_placement(sols[0], jetons) == stockee
    # Plancher : chaque phrase retirée seule casse-t-elle la détermination ?
    bloquantes = 0
    for rang in range(len(c["enonces"])):
        essai = c["enonces"][:rang] + c["enonces"][rang + 1:]
        det = resoudre_par_deduction(essai, n, figures, couleurs)
        if not det:
            bloquantes += 1
    print(f"{item['id']}: solutions={len(sols)} | unique==stockée={unique_ok} | "
          f"phrases indispensables={bloquantes}/{len(c['enonces'])}")
    ok_total += 1 if unique_ok else 0
print(f"--- {ok_total}/13 grilles vérifiées uniques et conformes ---")
