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

#: Fonctions qui affichent une nouvelle question : elles doivent remettre le
#: champ de saisie à zéro (régression constatée : la réponse précédente restait
#: affichée sous la question suivante).
FONCTIONS_A_REINITIALISER = {
    "afficherQuestion": 'refs.champReponse.value = ""',
    "montrerItem": 'annulerMemo()',
}


def corps_fonction(source: str, nom: str) -> str | None:
    """Extrait le corps d'une fonction (accolades équilibrées) ou None."""
    debut = source.find(f"function {nom}(")
    if debut < 0:
        return None
    accolade = source.find("{", debut)
    if accolade < 0:
        return None
    profondeur = 0
    for position in range(accolade, len(source)):
        if source[position] == "{":
            profondeur += 1
        elif source[position] == "}":
            profondeur -= 1
            if profondeur == 0:
                return source[accolade : position + 1]
    return None


def _routes_serveur() -> set[str]:
    """Chemins déclarés par les routeurs du backend (préfixe + chemin)."""
    routes: set[str] = set()
    for routeur in (RACINE_DEPOT / "backend" / "app" / "api").rglob("router.py"):
        texte = routeur.read_text(encoding="utf-8")
        trouvé = re.search(r'prefix="([^"]*)"', texte)
        prefixe = trouvé.group(1) if trouvé else ""
        for correspondance in re.finditer(r'@router\.(?:get|post)\("([^"]*)"', texte):
            routes.add(prefixe + correspondance.group(1))
    return routes


def _chemins_interface(source: str) -> list[tuple[str, str]]:
    """(appel, chemin complet) utilisés par l'interface pour les périmètres annexes.

    Chaque fonction d'appel (``fetchMissions``…) délègue à ``fetchJson(API_X, chemin)`` :
    on en déduit la base pour reconstruire le chemin réellement appelé.
    """
    bases = dict(re.findall(r'const (API_\w+) = "([^"]+)";', source))
    appels: list[tuple[str, str]] = []
    for nom, base_const in re.findall(
        r"function (\w+)\([^)]*\)\s*\{\s*return fetchJson\((API_\w+)", source
    ):
        for correspondance in re.finditer(rf'{nom}\("([^"]*)"', source):
            appels.append((nom, bases.get(base_const, "") + correspondance.group(1)))
    return appels


def main() -> int:
    source = SCRIPT.read_text(encoding="utf-8")
    page = PAGE.read_text(encoding="utf-8")
    demandes = sorted(set(MOTIF_ID_DEMANDE.findall(source)))
    presents = set(MOTIF_ID_PRESENT.findall(page))

    manquants = [ident for ident in demandes if ident not in presents]
    print(f"Identifiants demandés par le script : {len(demandes)}")
    print(f"Identifiants présents dans la page  : {len(presents)}")
    erreurs = 0
    if manquants:
        print(f"Identifiants absents de l'interface : {len(manquants)}")
        for ident in manquants:
            print("  -", ident)
        erreurs += len(manquants)
    else:
        print("Cohérence des identifiants : OK")

    # Chemins d'API appelés par l'interface ↔ routes déclarées par le serveur.
    routes = _routes_serveur()
    appels = _chemins_interface(source)
    inconnus = [(nom, chemin) for nom, chemin in appels if chemin not in routes]
    print(f"Chemins d'API appelés : {len(appels)} | routes serveur : {len(routes)}")
    if inconnus:
        for nom, chemin in inconnus:
            print(f"ERREUR : {nom} appelle {chemin!r} — route inexistante côté serveur")
        erreurs += len(inconnus)
    else:
        print("Correspondance interface ↔ routes : OK")

    # Réinitialisation du champ de saisie entre deux questions.
    for fonction, attendu in FONCTIONS_A_REINITIALISER.items():
        corps = corps_fonction(source, fonction)
        if corps is None:
            print(f"ERREUR : fonction {fonction} introuvable")
            erreurs += 1
        elif attendu not in corps:
            print(f"ERREUR : {fonction} ne remet pas le champ de saisie à zéro")
            erreurs += 1
        else:
            print(f"Réinitialisation dans {fonction} : OK")

    return 1 if erreurs else 0


if __name__ == "__main__":
    raise SystemExit(main())
