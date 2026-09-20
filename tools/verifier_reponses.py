#!/usr/bin/env python3
"""Vérifie que la réponse de chaque item est recalculable depuis son énoncé.

Contrôle indépendant du générateur : pour chaque item de contenu, on recalcule
la réponse attendue à partir du stimulus présent dans l'item, et on la compare
au champ ``reponse.valeur``. Familles couvertes :

- ``empan`` : la séquence affichée, dans l'ordre (ou inversée si l'énoncé le
  demande) ;
- ``n-back`` : l'élément situé N positions avant la fin de la séquence ;
- ``paires-associatives`` : le nombre apparié au mot sondé ;
- ``chaine-calcul`` : expression évaluée de gauche à droite, ou cascade
  « départ − pas × n » ;
- ``double-tache`` : somme des chiffres ou nombre de lettres de la suite ;
- ``serie-manquante`` : le terme manqué doit être déterminé par une règle
  simple (arithmétique, géométrique, alternée) et cette règle doit être UNIQUE.

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

MOTIF_CHAINE = re.compile(r"^\d+(?:\s*[−+]\s*\d+)+$")
MOTIF_CASCADE = re.compile(r"[Dd]épart\D*(\d+)\D*(\d+)\D*(\d+)\s*fois")
MOTIF_EMPRUNT = re.compile(r"[«\"]\s*([A-ZÉÈÀÇÊÎÔÛ]+)\s*[»\"]")
MOTIF_NOMBRE_AVANT = re.compile(r"(\d+)\s*positions?\s*avant la fin")

#: Familles pour lesquelles une réponse est recalculable automatiquement.
FAMILLES_CALCULABLES = {
    "empan", "n-back", "paires-associatives", "chaine-calcul",
    "double-tache", "serie-manquante",
}


def regles_simples(suite: list[int]) -> list[str]:
    """Familles de règles simples qui expliquent toute la suite."""
    trouvees = []
    ecarts = [b - a for a, b in zip(suite, suite[1:])]
    if len(set(ecarts)) == 1:
        trouvees.append(f"arithmetique(d={ecarts[0]})")
    if len(ecarts) >= 2:
        pairs, impairs = ecarts[::2], ecarts[1::2]
        if len(set(pairs)) == 1 and len(set(impairs)) == 1 and pairs[0] != impairs[0]:
            trouvees.append(f"alternee(d1={pairs[0]}, d2={impairs[0]})")
    ratios = []
    for a, b in zip(suite, suite[1:]):
        if a == 0 or b % a != 0:
            ratios = None
            break
        ratios.append(b // a)
    if ratios and len(set(ratios)) == 1 and suite[1] > suite[0]:
        trouvees.append(f"geometrique(q={ratios[0]})")
    return trouvees


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

    elif typ == "chaine-calcul":
        if MOTIF_CHAINE.match(enonce):
            total, signe = None, "+"
            for morceau in re.split(r"\s*([−+])\s*", enonce):
                if morceau in ("−", "+"):
                    signe = morceau
                elif morceau.isdigit():
                    valeur = int(morceau)
                    total = valeur if total is None else total + valeur * (1 if signe == "+" else -1)
            if int(reponse) != total:
                anomalies.append(f"{ident} : attendu {total}, fichier {reponse} ({enonce})")
            elif not 0 <= total <= 300:
                anomalies.append(f"{ident} : résultat {total} hors bornes ({enonce})")
        else:
            cascade = MOTIF_CASCADE.search(enonce)
            if not cascade:
                anomalies.append(f"{ident} : forme d'énoncé inconnue {enonce!r}")
            else:
                depart, pas, fois = (int(g) for g in cascade.groups())
                if int(reponse) != depart - pas * fois:
                    anomalies.append(f"{ident} : attendu {depart - pas * fois}, fichier {reponse} ({enonce})")

    elif typ == "double-tache":
        elements = contenu.get("affichage", {}).get("elements", [])
        bas = enonce.lower()
        if "chiffres" in bas:
            attendu = sum(int(e) for e in elements if e.isdigit())
        elif "lettres" in bas:
            attendu = sum(1 for e in elements if e.isalpha())
        else:
            return [f"{ident} : question inconnue {enonce!r}"]
        if int(reponse) != attendu:
            anomalies.append(f"{ident} : attendu {attendu}, fichier {reponse}")

    elif typ == "serie-manquante":
        termes = [t.strip() for t in enonce.split("—")[0].split(",")]
        candidats: dict[int, list[str]] = {}
        for valeur in range(0, 1000):
            suite = [valeur if t == "__" else int(t) for t in termes]
            regles = regles_simples(suite)
            if regles:
                candidats[valeur] = regles
        if not candidats:
            anomalies.append(f"{ident} : aucune règle simple ({enonce!r})")
        elif len(candidats) > 1:
            anomalies.append(f"{ident} : réponse ambiguë — candidats {sorted(candidats)} ({enonce!r})")
        elif int(reponse) != next(iter(candidats)):
            anomalies.append(f"{ident} : attendu {next(iter(candidats))}, fichier {reponse} ({enonce!r})")

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
