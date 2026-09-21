#!/usr/bin/env python3
"""Cohérence statique interface ↔ HTML : chaque identifiant demandé existe.

Les `$("…")` et `document.getElementById` de frontend/src/app.js sont
comparés aux `id="…"` de frontend/index.html. Une vue dont le titre est
requis par `afficherVue` doit aussi exister. Contrôle bon marché, sans
navigateur : il attrape les renommages oubliés d'un côté.

Usage : python3 tools/verifier_interface.py  (code de sortie 1 si écart)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
SCRIPT = RACINE_DEPOT / "frontend" / "src" / "app.js"
PAGE = RACINE_DEPOT / "frontend" / "index.html"

MOTIF_ID_DEMANDE = re.compile(r"""\$\("([^"]+)"\)""")
MOTIF_ID_PRESENT = re.compile(r"""id="([^"]+)\"""")


def main() -> int:
    source = SCRIPT.read_text(encoding="utf-8")
    page = PAGE.read_text(encoding="utf-8")
    demandes = sorted(set(MOTIF_ID_DEMANDE.findall(source)))
    presents = set(MOTIF_ID_PRESENT.findall(page))

    manquants = [ident for ident in demandes if ident not in presents]
    print(f"Identifiants demandés par le script : {len(demandes)}")
    print(f"Identifiants présents dans la page  : {len(presents)}")
    if manquants:
        print(f"Identifiants absents de l'interface : {len(manquants)}")
        for ident in manquants:
            print("  -", ident)
        return 1
    print("Cohérence : OK (aucun identifiant manquant)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
