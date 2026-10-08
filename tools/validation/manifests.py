from __future__ import annotations

from pathlib import Path




from .common import (
    RACINE_DEPOT, est_entier,
)

def erreurs_manifest(manifest: object, chemin: Path, donnees_par_fichier: dict[Path, object],
                     themes_manifests: dict[str, dict[int, dict]],
                     ids_paliers_connus: set[str]) -> list[str]:
    prefixe = f"{chemin.relative_to(RACINE_DEPOT)}: "
    if not isinstance(manifest, dict) or not isinstance(manifest.get("paliers"), list):
        return [prefixe + "manifest attendu : objet avec une liste 'paliers'"]
    if not isinstance(manifest.get("theme"), str) or not manifest.get("theme"):
        return [prefixe + "manifest.theme doit être une chaîne non vide"]

    erreurs: list[str] = []
    theme = manifest["theme"]
    registre: dict[int, dict] = {}
    ids_vus_manifest: set[str] = set()

    for position, entree in enumerate(manifest["paliers"], start=1):
        if not isinstance(entree, dict):
            erreurs.append(prefixe + f"palier {position} : entrée attendue comme objet")
            continue
        identifiant = entree.get("id")
        if not isinstance(identifiant, str) or not identifiant:
            erreurs.append(prefixe + f"palier {position} : id manquant")
        elif identifiant in ids_vus_manifest or identifiant in ids_paliers_connus:
            erreurs.append(prefixe + f"palier {position} : id dupliqué {identifiant!r}")
        else:
            ids_vus_manifest.add(identifiant)
            ids_paliers_connus.add(identifiant)

        # Tous les thèmes décrivent leurs paliers ; le calcul mental suit désormais
        # une progression par familles (comme les autres), plus par table.
        if "table" in entree:
            erreurs.append(prefixe + f"palier {position} : champ table obsolète (description attendue)")
        if "description" in entree and not isinstance(entree["description"], str):
            erreurs.append(prefixe + f"palier {position} : description doit être une chaîne")

        prerequis = entree.get("prerequis", [])
        if not isinstance(prerequis, list) or not all(isinstance(p, str) for p in prerequis):
            erreurs.append(prefixe + f"palier {position} : prerequis doit être un tableau de chaînes")

        fichier = entree.get("fichier")
        chemin_items: Path | None = None
        if not isinstance(fichier, str) or not fichier:
            erreurs.append(prefixe + f"palier {position} : fichier manquant")
        else:
            chemin_items = (chemin.parent / fichier).resolve()
            if chemin_items not in donnees_par_fichier:
                erreurs.append(prefixe + f"palier {position} : fichier introuvable : {fichier}")

        nb_items = donnees_par_fichier.get(chemin_items) if chemin_items else None
        comptage = len(nb_items) if isinstance(nb_items, list) else None
        if "nb_items" in entree:
            if not est_entier(entree["nb_items"]) or (comptage is not None and entree["nb_items"] != comptage):
                erreurs.append(
                    prefixe
                    + f"palier {position} : nb_items {entree['nb_items']!r} ≠ {comptage!r} items dans le fichier"
                )
        if comptage is None:
            erreurs.append(prefixe + f"palier {position} : fichier illisible ou vide : {fichier}")

        # Cohérence des numéros de palier portés par les items du fichier.
        if isinstance(nb_items, list):
            for item in nb_items:
                if isinstance(item, dict) and item.get("palier") != position:
                    erreurs.append(
                        prefixe
                        + f"palier {position} : item {item.get('id')!r} porte palier={item.get('palier')!r}"
                    )

        registre[position] = entree

    # Résolution des prerequis une fois tous les ids connus.
    for position, entree in enumerate(manifest["paliers"], start=1):
        if not isinstance(entree, dict):
            continue
        for reference in entree.get("prerequis", []) if isinstance(entree.get("prerequis"), list) else []:
            if reference not in ids_paliers_connus:
                erreurs.append(prefixe + f"palier {position} : prerequis inexistant {reference!r}")

    themes_manifests[theme] = registre
    return erreurs
