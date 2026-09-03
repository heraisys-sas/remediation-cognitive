#!/usr/bin/env python3
"""Validateur minimal des items de contenu — sans dépendance externe.

Parcourt tous les fichiers JSON de ``content/`` (sauf ``schema-item.json``) et
vérifie, pour chaque item :

- présence des champs requis et absence de champs inconnus
  (``additionalProperties: false`` du schéma) ;
- enums : ``module``, ``type``, valeurs de ``fonctions_ciblees`` et statut de
  ``relecture_ortho`` — lus directement dans ``content/schema-item.json`` ;
- ``id`` : conforme au motif du schéma et unique sur tout ``content/`` ;
- ``palier`` : entier ≥ 1 ; ``prerequis`` : tableau de chaînes ;
- ``cap_complexite`` : chaîne ou null ; ``contenu`` / ``reponse`` : objets ;
- ``meta`` : champs connus seulement, dates au format ISO 8601.

Cohérence palier/manifest : tout fichier JSON contenant une liste ``paliers``
est traité comme manifest d'un thème. Pour chaque item dont le ``theme``
correspond à un manifest : le palier doit exister, l'``id`` doit suivre le
motif ``cm-<table>-<a>x<b>`` avec la table déclarée par le manifest, un des
deux facteurs doit valoir la table et la réponse doit valoir ``a × b``. Les
références ``cm-palier-N`` placées dans ``prerequis`` doivent pointer vers un
palier existant du manifest.

Usage :

    python3 tools/validate_items.py

Code de sortie : 0 si tout est conforme, 1 sinon.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

#: Racine du dépôt (parent du dossier tools/) et dossiers de référence.
RACINE_DEPOT = Path(__file__).resolve().parent.parent
DOSSIER_CONTENU = RACINE_DEPOT / "content"
FICHIER_SCHEMA = DOSSIER_CONTENU / "schema-item.json"

#: Références de paliers attendues dans les prerequis (convention calcul-mental).
MOTIF_REF_PALIER = re.compile(r"^cm-palier-\d+$")

#: Motif d'un identifiant d'item de calcul mental : cm-<table>-<a>x<b>.
MOTIF_ID_CALCUL = re.compile(r"^cm-(\d+)-(\d+)x(\d+)$")


# --- Lecture du schéma --------------------------------------------------------


def charger_regles() -> dict:
    """Extrait du schéma les règles vérifiables sans bibliothèque externe.

    Returns:
        Dictionnaire : champs requis, champs connus (niveau racine, ``meta``,
        ``relecture_ortho``) et enums (module, type, fonctions, statut),
        plus le motif d'identifiant compilé.
    """
    with FICHIER_SCHEMA.open(encoding="utf-8") as flux:
        schema = json.load(flux)
    proprietes = schema.get("properties", {})
    meta = proprietes.get("meta", {}).get("properties", {})
    relecture = meta.get("relecture_ortho", {}).get("properties", {})
    return {
        "champs_requis": set(schema.get("required", [])),
        "champs_connus": set(proprietes.keys()),
        "enum_module": set(proprietes.get("module", {}).get("enum", [])),
        "enum_type": set(proprietes.get("type", {}).get("enum", [])),
        "enum_fonctions": set(
            proprietes.get("fonctions_ciblees", {}).get("items", {}).get("enum", [])
        ),
        "motif_id": re.compile(proprietes.get("id", {}).get("pattern", r"^[a-z0-9-]+$")),
        "champs_meta": set(meta.keys()),
        "champs_relecture": set(relecture.keys()),
        "enum_statut_relecture": set(relecture.get("statut", {}).get("enum", [])),
    }


# --- Aides de typage ----------------------------------------------------------


def est_entier(valeur: object) -> bool:
    """Vrai pour un vrai entier (``bool`` exclu : sous-classe de ``int`` en Python)."""
    return isinstance(valeur, int) and not isinstance(valeur, bool)


def est_date_iso(valeur: object) -> bool:
    """Vrai pour une chaîne au format date ISO 8601 (AAAA-MM-JJ)."""
    if not isinstance(valeur, str):
        return False
    try:
        date.fromisoformat(valeur)
    except ValueError:
        return False
    return True


# --- Validation d'un item -----------------------------------------------------


def erreurs_item(item: object, chemin: Path, regles: dict, ids_vus: dict[str, Path],
                 manifest_par_theme: dict[str, dict[int, dict]],
                 ids_paliers_connus: set[str]) -> list[str]:
    """Vérifie un item et retourne ses erreurs (préfixées par le fichier).

    Args:
        item: donnée JSON candidate (normalement un dict).
        chemin: fichier d'origine, pour les messages.
        regles: règles extraites du schéma.
        ids_vus: identifiants déjà rencontrés → premier fichier qui les porte.
        manifest_par_theme: thème → numéro de palier → entrée du manifest.
        ids_paliers_connus: tous les identifiants de paliers des manifests.

    Returns:
        Liste de messages d'erreur, vide si l'item est conforme.
    """
    prefixe = f"{chemin.relative_to(RACINE_DEPOT)}: "
    if not isinstance(item, dict):
        return [prefixe + "item attendu comme objet JSON"]

    erreurs: list[str] = []
    ajouter = erreurs.append

    # Champs requis et champs inconnus (additionalProperties: false).
    for champ in sorted(regles["champs_requis"] - set(item)):
        ajouter(prefixe + f"champ requis manquant : {champ}")
    for champ in sorted(set(item) - regles["champs_connus"]):
        ajouter(prefixe + f"champ inconnu (refusé par le schéma) : {champ}")

    # Identifiant : type, motif du schéma, unicité globale.
    identifiant = item.get("id")
    if not isinstance(identifiant, str):
        ajouter(prefixe + "id doit être une chaîne")
    elif not regles["motif_id"].fullmatch(identifiant):
        ajouter(prefixe + f"id non conforme au motif du schéma : {identifiant!r}")
    elif identifiant in ids_vus:
        premier = ids_vus[identifiant].relative_to(RACINE_DEPOT)
        ajouter(prefixe + f"id dupliqué (déjà vu dans {premier}) : {identifiant}")
    else:
        ids_vus[identifiant] = chemin

    # Enums du schéma.
    if item.get("module") not in regles["enum_module"]:
        ajouter(prefixe + f"module hors enum : {item.get('module')!r}")
    if item.get("type") not in regles["enum_type"]:
        ajouter(prefixe + f"type hors enum : {item.get('type')!r}")

    if not isinstance(item.get("theme"), str) or not item.get("theme"):
        ajouter(prefixe + "theme doit être une chaîne non vide")

    fonctions = item.get("fonctions_ciblees")
    if not isinstance(fonctions, list):
        ajouter(prefixe + "fonctions_ciblees doit être un tableau")
    else:
        for fonction in fonctions:
            if fonction not in regles["enum_fonctions"]:
                ajouter(prefixe + f"fonction_ciblee hors enum : {fonction!r}")

    palier = item.get("palier")
    if not est_entier(palier) or palier < 1:
        ajouter(prefixe + f"palier doit être un entier ≥ 1 : {palier!r}")

    prerequis = item.get("prerequis")
    if prerequis is not None:
        if not isinstance(prerequis, list) or not all(isinstance(p, str) for p in prerequis):
            ajouter(prefixe + "prerequis doit être un tableau de chaînes")
        else:
            for reference in prerequis:
                if MOTIF_REF_PALIER.fullmatch(reference) and reference not in ids_paliers_connus:
                    ajouter(prefixe + f"prerequis vers un palier inexistant : {reference}")

    if item.get("cap_complexite") is not None and not isinstance(item.get("cap_complexite"), str):
        ajouter(prefixe + "cap_complexite doit être une chaîne ou null")

    for champ in ("contenu", "reponse"):
        if champ in item and not isinstance(item[champ], dict):
            ajouter(prefixe + f"{champ} doit être un objet")

    erreurs.extend(erreurs_meta(item.get("meta"), prefixe, regles))
    erreurs.extend(
        erreurs_coherence_calcul(item, prefixe, manifest_par_theme)
    )
    return erreurs


def erreurs_meta(meta: object, prefixe: str, regles: dict) -> list[str]:
    """Vérifie le bloc ``meta`` (champs connus, auteur, dates, statut)."""
    if meta is None:
        return []
    if not isinstance(meta, dict):
        return [prefixe + "meta doit être un objet"]
    erreurs = []
    for champ in sorted(set(meta) - regles["champs_meta"]):
        erreurs.append(prefixe + f"champ meta inconnu : {champ}")
    if "auteur" in meta and not isinstance(meta["auteur"], str):
        erreurs.append(prefixe + "meta.auteur doit être une chaîne")
    if "date_creation" in meta and not est_date_iso(meta["date_creation"]):
        erreurs.append(prefixe + "meta.date_creation doit être une date ISO (AAAA-MM-JJ)")
    relecture = meta.get("relecture_ortho")
    if relecture is not None:
        if not isinstance(relecture, dict):
            erreurs.append(prefixe + "meta.relecture_ortho doit être un objet")
        else:
            for champ in sorted(set(relecture) - regles["champs_relecture"]):
                erreurs.append(prefixe + f"champ relecture_ortho inconnu : {champ}")
            statut = relecture.get("statut")
            if statut is not None and statut not in regles["enum_statut_relecture"]:
                erreurs.append(prefixe + f"statut de relecture hors enum : {statut!r}")
            if "date" in relecture and not est_date_iso(relecture["date"]):
                erreurs.append(prefixe + "relecture_ortho.date doit être une date ISO (AAAA-MM-JJ)")
    return erreurs


def erreurs_coherence_calcul(item: dict, prefixe: str,
                             manifest_par_theme: dict[str, dict[int, dict]]) -> list[str]:
    """Vérifie la cohérence item ↔ manifest pour le thème « calcul-mental ».

    Contrôles : le palier existe dans le manifest du thème ; l'identifiant suit
    ``cm-<table>-<a>x<b>`` avec la table du manifest ; un des deux facteurs
    vaut la table ; la réponse vaut bien ``a × b``.
    """
    theme = item.get("theme")
    if theme not in manifest_par_theme:
        return []
    paliers = manifest_par_theme[theme]
    palier = item.get("palier")
    if not est_entier(palier) or palier not in paliers:
        return [prefixe + f"palier {palier!r} absent du manifest du thème {theme!r}"]

    table = paliers[palier]["table"]
    identifiant = item.get("id", "")
    correspondence = MOTIF_ID_CALCUL.fullmatch(identifiant)
    if not correspondence:
        return [prefixe + f"id non conforme au motif cm-<table>-<a>x<b> : {identifiant!r}"]
    table_id, a, b = (int(groupe) for groupe in correspondence.groups())
    erreurs = []
    if table_id != table:
        erreurs.append(prefixe + f"table de l'id ({table_id}) ≠ table du manifest ({table})")
    if not (1 <= a <= 10 and 1 <= b <= 10):
        erreurs.append(prefixe + f"facteurs hors 1..10 dans l'id : {identifiant!r}")
    if a != table and b != table:
        erreurs.append(prefixe + f"aucun facteur ne vaut la table du palier : {identifiant!r}")
    reponse = item.get("reponse", {}).get("valeur")
    if reponse != a * b:
        erreurs.append(prefixe + f"reponse {reponse!r} ≠ {a} × {b} = {a * b}")
    return erreurs


# --- Validation d'un manifest -------------------------------------------------


def erreurs_manifest(manifest: object, chemin: Path, donnees_par_fichier: dict[Path, object],
                     themes_manifests: dict[str, dict[int, dict]],
                     ids_paliers_connus: set[str]) -> list[str]:
    """Vérifie un manifest de paliers et l'enregistre pour les items.

    Contrôles : structure (thème + liste de paliers), ids uniques, prerequis
    résolubles, fichiers référencés présents, ``nb_items`` exact et numéro de
    palier cohérent avec les items du fichier.

    Args:
        manifest: donnée JSON candidate.
        chemin: fichier d'origine du manifest.
        donnees_par_fichier: JSON déjà parsé de tous les fichiers de content/.
        themes_manifests: registre thème → paliers (rempli au fil de l'eau).
        ids_paliers_connus: ensemble global des ids de paliers (rempli au fil de l'eau).

    Returns:
        Liste de messages d'erreur, vide si le manifest est conforme.
    """
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

        if not est_entier(entree.get("table")) or not 1 <= entree.get("table", 0) <= 10:
            erreurs.append(prefixe + f"palier {position} : table doit être un entier 1..10")

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


# --- Orchestration ------------------------------------------------------------


def main() -> int:
    """Point d'entrée : valide tout le contenu et affiche un bilan.

    Returns:
        0 si tout est conforme, 1 sinon.
    """
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

    # Passe 2a : manifests d'abord (les items en dépendent).
    themes_manifests: dict[str, dict[int, dict]] = {}
    ids_paliers_connus: set[str] = set()
    erreurs_manifests: dict[Path, list[str]] = {}
    for chemin, donnees in donnees_par_fichier.items():
        if est_manifest(donnees):
            erreurs_manifests[chemin] = erreurs_manifest(
                donnees, chemin, donnees_par_fichier, themes_manifests, ids_paliers_connus
            )

    # Passe 2b : items.
    ids_vus: dict[str, Path] = {}
    erreurs_items: dict[Path, list[str]] = {}
    total_items = 0
    for chemin, donnees in donnees_par_fichier.items():
        if est_manifest(donnees):
            continue
        items = donnees if isinstance(donnees, list) else [donnees]
        messages: list[str] = []
        for item in items:
            messages.extend(
                erreurs_item(item, chemin, regles, ids_vus, themes_manifests, ids_paliers_connus)
            )
        total_items += len(items)
        erreurs_items[chemin] = messages

    # Restitution.
    print(f"Validation du contenu : {len(fichiers)} fichier(s) JSON sous content/")
    print(f"Schéma de référence : {FICHIER_SCHEMA.relative_to(RACINE_DEPOT)}")
    total_erreurs = len(erreurs_parse)
    for chemin in fichiers:
        if chemin in erreurs_parse:
            print(f"[ERREUR] {erreurs_parse[chemin]}")
            continue
        if chemin in erreurs_manifests:
            messages = erreurs_manifests[chemin]
            etiquette = "manifest"
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


if __name__ == "__main__":
    raise SystemExit(main())
