from __future__ import annotations

import json
from pathlib import Path




from .calculation import (
    couverture_calcul,
)
from .common import (
    DOSSIER_CONTENU, FICHIER_SCHEMA, RACINE_DEPOT, charger_regles,
)
from .items import (
    erreurs_item, erreurs_regularite,
)
from .manifests import (
    erreurs_manifest,
)
from .programme import (
    erreurs_missions, erreurs_programme,
)

def main() -> int:
    regles = charger_regles()
    fichiers = sorted(p for p in DOSSIER_CONTENU.rglob("*.json") if p != FICHIER_SCHEMA)

    # Passe 1 : parsage JSON et classification (manifest vs items).
    donnees_par_fichier: dict[Path, object] = {}
    erreurs_parse: dict[Path, str] = {}
    for chemin in fichiers:
        try:
            with chemin.open(encoding="utf-8") as flux:
                donnees_par_fichier[chemin] = json.load(flux)
        except (json.JSONDecodeError, UnicodeDecodeError) as exception:
            erreurs_parse[chemin] = (
                f"{chemin.relative_to(RACINE_DEPOT)}: JSON invalide ({exception})"
            )

    est_manifest = lambda donnees: isinstance(donnees, dict) and isinstance(donnees.get("paliers"), list)
    est_missions = lambda donnees: isinstance(donnees, dict) and isinstance(donnees.get("missions"), list)
    est_programme = lambda donnees: isinstance(donnees, dict) and isinstance(donnees.get("semaines"), list)

    # Passe 2a : manifests d'abord (les items en dépendent).
    themes_manifests: dict[str, dict[int, dict]] = {}
    ids_paliers_connus: set[str] = set()
    erreurs_manifests: dict[Path, list[str]] = {}
    for chemin, donnees in donnees_par_fichier.items():
        if est_manifest(donnees):
            erreurs_manifests[chemin] = erreurs_manifest(
                donnees, chemin, donnees_par_fichier, themes_manifests, ids_paliers_connus
            )

    # Passe 2b : items (et fichiers de missions hors écran).
    ids_vus: dict[str, Path] = {}
    erreurs_items: dict[Path, list[str]] = {}
    total_items = 0
    # Couverture du contrôle indépendant du calcul mental : [vérifiables, total].
    couverts: list[int] = [0, 0]
    for chemin, donnees in donnees_par_fichier.items():
        if est_manifest(donnees):
            continue
        if est_missions(donnees):
            erreurs_items[chemin] = erreurs_missions(donnees, chemin)
            continue
        if est_programme(donnees):
            paliers_par_theme = {
                theme: len(registre) for theme, registre in themes_manifests.items()
            }
            erreurs_items[chemin] = erreurs_programme(donnees, chemin, paliers_par_theme)
            continue
        items = donnees if isinstance(donnees, list) else [donnees]
        messages: list[str] = []
        for item in items:
            messages.extend(
                erreurs_item(item, chemin, regles, ids_vus, themes_manifests, ids_paliers_connus)
            )
        messages.extend(erreurs_regularite(chemin, items))
        couverts[0] += couverture_calcul(items)[0]
        couverts[1] += couverture_calcul(items)[1]
        total_items += len(items)
        erreurs_items[chemin] = messages

    # Restitution.
    print(f"Validation du contenu : {len(fichiers)} fichier(s) JSON sous content/")
    print(f"Schéma de référence : {FICHIER_SCHEMA.relative_to(RACINE_DEPOT)}")
    total_erreurs = len(erreurs_parse)
    # Le contrôle du calcul mental doit réellement porter sur le contenu : un motif cassé
    # le rendait silencieusement inopérant (régression constatée).
    if couverts[1] >= 20 and couverts[0] / couverts[1] < 0.6:
        total_erreurs += 1
        print(f"[ERREUR] couverture du contrôle calcul mental : {couverts[0]}/{couverts[1]} items "
              "recalculables — un motif de contrôle est probablement cassé")
    for chemin in fichiers:
        if chemin in erreurs_parse:
            print(f"[ERREUR] {erreurs_parse[chemin]}")
            continue
        if chemin in erreurs_manifests:
            messages = erreurs_manifests[chemin]
            etiquette = "manifest"
        elif est_missions(donnees_par_fichier[chemin]):
            messages = erreurs_items.get(chemin, [])
            etiquette = f"{len(donnees_par_fichier[chemin]['missions'])} mission(s)"
        elif est_programme(donnees_par_fichier[chemin]):
            messages = erreurs_items.get(chemin, [])
            etiquette = f"{len(donnees_par_fichier[chemin]['semaines'])} semaine(s)"
        else:
            messages = erreurs_items.get(chemin, [])
            donnees = donnees_par_fichier[chemin]
            etiquette = f"{len(donnees) if isinstance(donnees, list) else 1} item(s)"
        if messages:
            total_erreurs += len(messages)
            print(f"[ERREUR] {chemin.relative_to(RACINE_DEPOT)} ({etiquette})")
            for message in messages:
                print(f"         - {message}")
        else:
            print(f"[OK]     {chemin.relative_to(RACINE_DEPOT)} ({etiquette})")
    print(
        f"Bilan : {len(fichiers)} fichier(s), {total_items} item(s), "
        f"{len(erreurs_manifests)} manifest(s), {total_erreurs} erreur(s)."
    )
    return 1 if total_erreurs else 0
