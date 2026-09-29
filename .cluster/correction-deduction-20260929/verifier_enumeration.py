#!/usr/bin/env python3
"""Vérification indépendante : nombre de solutions par énumération brute (9!)."""
import itertools
import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "tools"))
from deduction_commun import (  # noqa: E402
    TYPES_BINAIRES, TYPES_UNAIRES, _vrai_binaire, _vrai_unaire, informations_autonomes,
)


def solutions(enonces, n, figures, couleurs):
    jetons = [(figures[f], couleurs[c]) for f in range(n) for c in range(n)]
    phrases = [informations_autonomes(p) for p in enonces]
    total, echantillon = 0, None
    for placement in itertools.permutations(range(n * n)):
        cases = {jetons[i]: placement[i] for i in range(len(jetons))}
        ok = True
        for infos in phrases:
            for a in infos:
                if a["type"] in TYPES_UNAIRES:
                    if not _vrai_unaire(a, cases[(a["figure"], a["couleur"])], n):
                        ok = False; break
                elif a["type"] in TYPES_BINAIRES:
                    if not _vrai_binaire(a, cases[(a["figure"], a["couleur"])],
                                         cases[(a["figure2"], a["couleur2"])], n):
                        ok = False; break
                else:
                    raise ValueError("type inconnu " + a["type"])
            if not ok:
                break
        if ok:
            total += 1
            if echantillon is None:
                echantillon = placement
    return total, echantillon


def charger_items(chemin):
    return json.loads(Path(chemin).read_text(encoding="utf-8"))


# 1. Contenu réparé (4 phrases pour dc-3-03)
items = charger_items(RACINE / "content/entrainement/deduction/paliers/palier-03.json")
it = next(i for i in items if i["id"] == "dc-3-03")
c = it["contenu"]
nb, ex = solutions(c["enonces"], 3, c["figures"], c["couleurs"])
fig, coul = c["figures"], c["couleurs"]
stockee = tuple((fig.index(f), coul.index(cl)) for f, cl in it["reponse"]["grille"])
print("dc-3-03 réparé (4 phrases) : %d solution(s) ; unique == stockée : %s" % (nb, tuple(ex) == stockee))

# 2. Contenu d'origine (5 phrases) extrait de git
brut = subprocess.run(["git", "show", "HEAD:content/entrainement/deduction/paliers/palier-03.json"],
                      cwd=RACINE, capture_output=True, text=True).stdout
items0 = json.loads(brut)
it0 = next(i for i in items0 if i["id"] == "df-3-03")
c0 = it0["contenu"]
nb0, _ = solutions(c0["enonces"], 3, c0["figures"], c0["couleurs"])
print("df-3-03 d'origine (5 phrases) : %d solution(s)" % nb0)
# 2b. é2 retirée (index 1), é5 retirée (index 4) : la redondance préexistait-elle ?
sans25 = [e for i, e in enumerate(c0["enonces"]) if i not in (1, 4)]
nb1, _ = solutions(sans25, 3, c0["figures"], c0["couleurs"])
print("df-3-03 sans é2 ni é5 (3 phrases) : %d solution(s)" % nb1)
sans2 = [e for i, e in enumerate(c0["enonces"]) if i != 1]
nb2, _ = solutions(sans2, 3, c0["figures"], c0["couleurs"])
print("df-3-03 sans é2 seule (4 phrases) : %d solution(s)" % nb2)
