#!/usr/bin/env python3
"""Contrôle automatique des garde-fous cliniques (non médical).

Les garde-fous sont écrits dans AGENTS.md et docs/10-clinique/. Ce script les
vérifie sur le code et le contenu réels, de façon reproductible :

1. **Vocabulaire** — le vocabulaire « entraînement » (et rééducation / social)
   ne contient aucun terme clinique ou normatif (diagnostic, norme, score,
   trouble, déficit…). Le module bilan garde son propre vocabulaire.
2. **Photophobie** — thème sombre par défaut, zéro animation définie
   (`@keyframes` absent), respect de `prefers-reduced-motion`.
3. **Matériel protégé** — aucun instrument normé (PASAT, MMSE, MoCA, ECPA,
   Pearson, Raven, GREFEX, TEA-Ch, BCEFA, RL/RI, « 15 mots de Rey »…) n'apparaît
   dans le CONTENU des items ; les citations de principe dans les README sont
   admises, jamais le matériel lui-même.
4. **Relecture** — chaque item porte un statut `meta.relecture_ortho` ; un statut
   « valide_informel » doit être daté (sinon une validation non tracée serait
   prétendue). Le bilan final donne la répartition des statuts.

Lecture seule — aucun fichier n'est modifié. Code de sortie 1 si une violation
est détectée.

Usage :

    python3 tools/verifier_clinique.py
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent

#: Termes cliniques ou normatifs interdits dans le vocabulaire non médical.
#: (le module « bilan » possède son propre vocabulaire et n'est pas scanné ici).
TERMES_CLINIQUES = [
    "diagnostic", "diagnostique", "percentile", "norme", "normé", "score",
    "déficit", "déficience", "démence", "alzheimer", "pathologie", "handicap",
    "trouble", "maladie", "évaluation", "test de", "échelle de",
]

#: Instruments normés protégés — ils ne doivent jamais figurer dans le contenu
#: des items (les citer dans une documentation est permis, les reproduire non).
MATERIEL_PROTEGE = [
    "PASAT", "MMSE", "MoCA", "ECPA", "Pearson", "Raven", "RL/RI",
    "15 mots de Rey", "GREFEX", "TEA-Ch", "BCEFA", "BEM", "Stroop", "Trail",
]

#: Fichiers de contenu où le matériel protégé est interdit (les items, les
#: missions et le programme — pas les README ni la documentation).
MOTIFS_CONTENU = [
    "content/entrainement/**/paliers/*.json",
    "content/entrainement/**/missions.json",
    "content/programmes/*.json",
]

VOCABULAIRES_NON_MEDICAUX = ("entrainement", "reeducation", "social")


def charger_vocabulaires() -> dict:
    """Extrait le bloc VOCABULAIRES de messages.py (ast : sans exécuter)."""
    source = (RACINE_DEPOT / "backend" / "app" / "domain" / "messages.py").read_text(encoding="utf-8")
    arbre = ast.parse(source)
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Assign):
            for cible in noeud.targets:
                if isinstance(cible, ast.Name) and cible.id == "VOCABULAIRES":
                    return ast.literal_eval(noeud.value)
    return {}


def aplatir_textes(valeur) -> list[str]:
    """Tous les textes d'une structure (dict/liste), pour le scan de vocabulaire."""
    textes: list[str] = []
    if isinstance(valeur, str):
        textes.append(valeur)
    elif isinstance(valeur, dict):
        for sous in valeur.values():
            textes.extend(aplatir_textes(sous))
    elif isinstance(valeur, list):
        for sous in valeur:
            textes.extend(aplatir_textes(sous))
    return textes


def verifier_vocabulaire(vocabulaires: dict) -> list[str]:
    """Termes cliniques ou normatifs dans le vocabulaire non médical."""
    violations: list[str] = []
    for module in VOCABULAIRES_NON_MEDICAUX:
        for texte in aplatir_textes(vocabulaires.get(module, {})):
            bas = texte.casefold()
            for terme in TERMES_CLINIQUES:
                if terme.casefold() in bas:
                    violations.append(f"vocabulaire {module!r} : terme « {terme} » dans {texte!r}")
    return violations


def verifier_photophobie() -> list[str]:
    """Thème sombre, zéro animation définie, motion réduite respectée."""
    violations: list[str] = []
    css = (RACINE_DEPOT / "frontend" / "src" / "styles.css").read_text(encoding="utf-8")
    if "color-scheme: dark" not in css:
        violations.append("styles.css : color-scheme: dark absent")
    if "@media (prefers-reduced-motion: reduce)" not in css:
        violations.append("styles.css : préférence prefers-reduced-motion non respectée")
    if "@keyframes" in css:
        violations.append("styles.css : une animation @keyframes est définie (zéro scintillement attendu)")
    return violations


def verifier_materiel_protege() -> list[str]:
    """Aucun instrument normé dans le contenu des items."""
    violations: list[str] = []
    fichiers: list[Path] = []
    for motif in MOTIFS_CONTENU:
        fichiers.extend(RACINE_DEPOT.glob(motif))
    for fichier in sorted(set(fichiers)):
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        items = donnees if isinstance(donnees, list) else (donnees.get("missions") or donnees.get("semaines") or [])
        for item in items:
            if not isinstance(item, dict):
                continue
            # Seul le CORPS d'exercice est scanné (enoncé, options, indices…).
            corps = json.dumps({cle: item.get(cle) for cle in ("contenu", "reponse")}, ensure_ascii=False)
            for nom in MATERIEL_PROTEGE:
                if re.search(rf"\b{re.escape(nom)}\b", corps, re.IGNORECASE):
                    violations.append(f"{fichier.relative_to(RACINE_DEPOT)} ({item.get('id')}) : « {nom} »")
    return violations


def verifier_relecture() -> tuple[list[str], dict]:
    """Statut de relecture présent, « valide » daté, et répartition."""
    violations: list[str] = []
    repartition: dict[str, int] = {}
    for fichier in sorted((RACINE_DEPOT / "content" / "entrainement").rglob("*.json")):
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        items = donnees if isinstance(donnees, list) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            relecture = (item.get("meta") or {}).get("relecture_ortho") or {}
            statut = relecture.get("statut", "(absent)")
            repartition[statut] = repartition.get(statut, 0) + 1
            if statut == "(absent)":
                violations.append(f"{item.get('id')} : meta.relecture_ortho absent")
            if statut == "valide_informel" and not relecture.get("date"):
                violations.append(f"{item.get('id')} : valide_informel sans date (validation non tracée)")
    return violations, repartition


def main() -> int:
    violations: list[str] = []
    vocabulaires = charger_vocabulaires()
    violations.extend(verifier_vocabulaire(vocabulaires))
    violations.extend(verifier_photophobie())
    violations.extend(verifier_materiel_protege())
    relecture_violations, repartition = verifier_relecture()
    violations.extend(relecture_violations)

    print("Garde-fous cliniques (contrôle automatique)")
    print(f"  Vocabulaire non médical         : {'OK' if not verifier_vocabulaire(vocabulaires) else 'VIOLATION'}")
    print(f"  Photophobie (sombre, sans animation) : {'OK' if not verifier_photophobie() else 'VIOLATION'}")
    print(f"  Matériel protégé absent du contenu   : {'OK' if not verifier_materiel_protege() else 'VIOLATION'}")
    print(f"  Relecture : {dict(sorted(repartition.items()))}")
    print(f"  -> {repartition.get('a_revoir', 0)} items à revoir, "
          f"{repartition.get('valide_informel', 0)} validés (informel)")

    if violations:
        print(f"\n{len(violations)} violation(s) :")
        for violation in violations:
            print("  -", violation)
        return 1
    print("\nAucune violation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
