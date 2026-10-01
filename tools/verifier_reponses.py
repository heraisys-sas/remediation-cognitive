#!/usr/bin/env python3
"""Vérifie que la réponse de chaque item est recalculable depuis son énoncé.

Contrôle indépendant du générateur : pour chaque item de contenu, on recalcule
la réponse attendue à partir du stimulus présent dans l'item, et on la compare
au champ ``reponse.valeur``. Familles couvertes :

- ``empan`` : la séquence affichée, dans l'ordre (ou inversée si l'énoncé le
  demande) ;
- ``n-back`` : l'élément situé N positions avant la fin de la séquence ;
- ``paires-associatives`` : le nombre apparié au mot sondé ;

Ne modifie aucun fichier : lecture seule, code de sortie 1 si une anomalie est
détectée.

Usage :

    python3 tools/verifier_reponses.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
DOSSIER_CONTENU = RACINE_DEPOT / "content" / "entrainement"

MOTIF_EMPRUNT = re.compile(r"[«\"]\s*([A-ZÉÈÀÇÊÎÔÛ]+)\s*[»\"]")
MOTIF_NOMBRE_AVANT = re.compile(r"(\d+)\s*positions?\s*avant la fin")

#: Familles pour lesquelles une réponse est recalculable automatiquement.
FAMILLES_CALCULABLES = {
    "empan", "empan-mots", "n-back", "paires-associatives",
}


def verifier_item(item: dict) -> list[str]:
    """Retourne la liste des anomalies de l'item (vide si tout est cohérent)."""
    anomalies: list[str] = []
    ident, typ = item.get("id"), item.get("type")
    if typ not in FAMILLES_CALCULABLES:
        return anomalies
    contenu = item.get("contenu", {})
    enonce = contenu.get("enonce", "")
    reponse = item.get("reponse", {}).get("valeur")

    if typ == "empan":
        elements = contenu.get("affichage", {}).get("elements", [])
        bas = enonce.lower()
        attendu = "".join(reversed(elements)) if ("invers" in bas or "envers" in bas) else "".join(elements)
        if str(reponse) != attendu:
            anomalies.append(f"{ident} : attendu {attendu!r}, fichier {reponse!r}")

    elif typ == "empan-mots":
        elements = contenu.get("affichage", {}).get("elements", [])
        bas = enonce.lower()
        inverse = "invers" in bas or "envers" in bas
        attendu = " ".join(reversed(elements)) if inverse else " ".join(elements)
        if str(reponse) != attendu:
            anomalies.append(f"{ident} : attendu {attendu!r}, fichier {reponse!r}")
        if len(set(elements)) != len(elements):
            anomalies.append(f"{ident} : mot répété dans la séquence {elements}")

    elif typ == "n-back":
        elements = contenu.get("affichage", {}).get("elements", [])
        trouve = MOTIF_NOMBRE_AVANT.search(enonce)
        if not trouve:
            anomalies.append(f"{ident} : N non déductible de l'énoncé {enonce!r}")
        else:
            attendu = elements[-(int(trouve.group(1)) + 1)]
            if str(reponse) != attendu:
                anomalies.append(f"{ident} : attendu {attendu!r}, fichier {reponse!r}")

    elif typ == "paires-associatives":
        paires = contenu.get("affichage", {}).get("elements", [])
        mots = [mot for mot, _ in paires]
        if len(set(mots)) != len(mots):
            anomalies.append(f"{ident} : mots dupliqués {mots}")
        trouve = MOTIF_EMPRUNT.search(enonce)
        if not trouve:
            anomalies.append(f"{ident} : mot sondé illisible dans {enonce!r}")
        else:
            correspondances = [nombre for mot, nombre in paires if mot == trouve.group(1)]
            if len(correspondances) != 1:
                anomalies.append(f"{ident} : mot sondé absent {trouve.group(1)!r}")
            elif str(reponse) != correspondances[0]:
                anomalies.append(f"{ident} : attendu {correspondances[0]!r}, fichier {reponse!r}")

    return anomalies


def main() -> int:
    compte: Counter[str] = Counter()
    ids: dict[str, str] = {}
    anomalies: list[str] = []

    for fichier in sorted(DOSSIER_CONTENU.rglob("*.json")):
        if fichier.name == "paliers.json":
            continue
        items = json.loads(fichier.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            continue
        for item in items:
            ident = item.get("id")
            compte[item.get("type", "?")] += 1
            if ident in ids:
                anomalies.append(f"{ident} : identifiant dupliqué ({ids[ident]} et {fichier.name})")
            ids[ident] = fichier.name
            anomalies.extend(verifier_item(item))

    print(f"Items examinés : {sum(compte.values())} ({dict(compte)})")
    print(f"Identifiants uniques : {len(ids)}")
    print(f"Anomalies : {len(anomalies)}")
    for ligne in anomalies:
        print("  -", ligne)
    return 1 if anomalies else 0


if __name__ == "__main__":
    raise SystemExit(main())
