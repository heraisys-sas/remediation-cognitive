#!/usr/bin/env python3
"""Validateur minimal des items de contenu - sans dépendance externe.

Parcourt tous les fichiers JSON de ``content/`` (sauf ``schema-item.json``) et
vérifie, pour chaque item :

- présence des champs requis et absence de champs inconnus
  (``additionalProperties: false`` du schéma) ;
- enums : ``module``, ``type``, valeurs de ``fonctions_ciblees`` et statut de
  ``relecture_ortho`` - lus directement dans ``content/schema-item.json`` ;
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
palier existant du manifest. Multi-thèmes : chaque manifest déclare son thème
(calcul-mental, memoire, concentration...) ; le contrôle de cohérence spécifique
(tables, produits) ne s'applique qu'au calcul-mental, les autres thèmes ayant
des identifiants à structure libre.

Usage :

    python3 tools/validate_items.py

Code de sortie : 0 si tout est conforme, 1 sinon.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

# Le solveur de déduction sert de juge : un puzzle de grille qui n'est pas
# entièrement résoluble par propagation (sans hypothèse) est refusé.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from deduction_commun import TYPES_BINAIRES as TYPES_BINAIRES_DEDUCTION, pred_indice, resoudre_par_deduction  # noqa: E402

#: Racine du dépôt (parent du dossier tools/) et dossiers de référence.
RACINE_DEPOT = Path(__file__).resolve().parent.parent
DOSSIER_CONTENU = RACINE_DEPOT / "content"
FICHIER_SCHEMA = DOSSIER_CONTENU / "schema-item.json"

#: Références de paliers attendues dans les prerequis (convention multi-thèmes :
# cm-palier-N, me-palier-N, co-palier-N...).
MOTIF_REF_PALIER = re.compile(r"^[a-z]+-palier-\d+$")

#: Motif d'un identifiant d'item de calcul mental : cm-<table>-<a>x<b>.
MOTIF_ID_CALCUL = re.compile(r"^cm2-(\d+)-(\d+)$")
MOTIF_CALCUL_ARITHMETIQUE = re.compile(r"Combien font (\d+) ([+−×]) (\d+)((?: [+−] \d+)?) ?\?")
MOTIF_COMPLEMENT = re.compile(r"Combien manque-t-il à (\d+) pour faire (\d+) \?")
MOTIF_TOTAL_ARTICLES = re.compile(r"(\d+) articles à ([\d,]+) € — combien en tout \?")
MOTIF_RENDU = re.compile(r"Un article à (\d+) €, payé avec (\d+) € — combien te rend-on \?")
#: Suites et faits à l'envers : d'autres séries pour l'attention et les lacunes.
MOTIF_SUITE_CONTINUE = re.compile(r"(?:Continue la suite|Compte à rebours) : ([\d, ]+), \s*\?")
MOTIF_SUITE_ERREUR = re.compile(r"([\d, ]+) — quel nombre est faux \?")
MOTIF_FAIT_INVERSE_GAUCHE = re.compile(r"(\d+) = (\d+) × \?")
MOTIF_FAIT_INVERSE_DROITE = re.compile(r"(\d+) = \? × (\d+)")

#: Séries de calcul (attention soutenue) : « 75 − 9 − 9 − 9 », « 8 + 4 − 3 ».
MOTIF_CHAINE = re.compile(r"^\d+(?: [+−] \d+)+$")

#: Types dont la réponse est choisie parmi ``contenu.options``.
TYPES_A_CHOIX = {
    "reconnaissance",
    "rappel-source",
    "etape-suivante",
    "par-ou-commencer",
    "si-alors",
    "meilleure-solution",
    "pqrst",
    "but-etapes",
    "auto-instruction",
    "plan-a-verifier",
    "reperer-info",
    "aide-externe",
    "gestion-du-temps",
}

#: Types dont le contenu porte une hiérarchie d'indices (``contenu.indices``).
TYPES_A_INDICES = {"rappel-indice"}

#: Modes d'affichage temporisé admis.
MODES_AFFICHAGE = {"sequence", "liste", "series", "texte"}

#: Bornes du rythme d'affichage d'un élément (ms). Au-delà, ce n'est plus une
#: présentation d'empan mais une pause d'attente : le contenu serait mal calibré.
RYTHME_MIN_MS, RYTHME_MAX_MS = 400, 2000

#: Types d'indices admis dans ``contenu.indices``.
TYPES_INDICE = {"semantique", "phonologique", "orthographique", "contextuel"}


def _normaliser_texte(valeur: str) -> str:
    """Minuscules sans accents ni espaces - comparaison indice ↔ réponse."""
    import unicodedata

    decompose = unicodedata.normalize("NFD", valeur.casefold())
    sans_accents = "".join(c for c in decompose if not unicodedata.combining(c))
    return "".join(sans_accents.split())


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
    erreurs.extend(erreurs_contenu(item, prefixe))
    if item.get("theme") == "calcul-mental":
        erreurs.extend(
            erreurs_coherence_calcul(item, prefixe, manifest_par_theme)
        )
    if item.get("theme") == "concentration":
        erreurs.extend(erreurs_coherence_chaine(item, prefixe))
    return erreurs


def erreurs_contenu(item: dict, prefixe: str) -> list[str]:
    """Vérifie les conventions de ``contenu`` liées au type d'exercice.

    - types à choix : ``options`` (≥ 3 propositions distinctes) et la réponse
      attendue doit figurer parmi elles ;
    - types à indices : ``indices`` (≥ 2) avec type et texte, et **aucun indice
      ne doit contenir la réponse** (sinon l'essai n'est plus un rappel).
    """
    erreurs: list[str] = []
    type_item = item.get("type")
    contenu = item.get("contenu")
    if not isinstance(contenu, dict):
        return erreurs
    reponse = item.get("reponse", {}).get("valeur") if isinstance(item.get("reponse"), dict) else None

    options = contenu.get("options")
    if type_item in TYPES_A_CHOIX:
        if not isinstance(options, list) or len(options) < 3:
            erreurs.append(prefixe + f"type {type_item} : contenu.options doit lister au moins 3 propositions")
        else:
            if not all(isinstance(option, str) and option.strip() for option in options):
                erreurs.append(prefixe + "contenu.options doit être une liste de chaînes non vides")
            elif len({_normaliser_texte(option) for option in options}) != len(options):
                erreurs.append(prefixe + "contenu.options contient des propositions identiques")
            elif not isinstance(reponse, str) or _normaliser_texte(reponse) not in {
                _normaliser_texte(option) for option in options
            }:
                erreurs.append(prefixe + f"la réponse attendue {reponse!r} n'est pas proposée dans options")
    elif options is not None and (not isinstance(options, list) or len(options) < 2):
        erreurs.append(prefixe + "contenu.options doit être une liste d'au moins 2 propositions")

    indices = contenu.get("indices")
    if type_item in TYPES_A_INDICES:
        if not isinstance(indices, list) or len(indices) < 2:
            erreurs.append(prefixe + f"type {type_item} : contenu.indices doit contenir au moins 2 indices")
        else:
            for position, indice in enumerate(indices, start=1):
                if not isinstance(indice, dict):
                    erreurs.append(prefixe + f"indice {position} : objet attendu")
                    continue
                if indice.get("type") not in TYPES_INDICE:
                    erreurs.append(prefixe + f"indice {position} : type d'indice inconnu {indice.get('type')!r}")
                texte = indice.get("texte")
                if not isinstance(texte, str) or not texte.strip():
                    erreurs.append(prefixe + f"indice {position} : texte manquant")
                    continue
                if isinstance(reponse, str) and _normaliser_texte(reponse) in _normaliser_texte(texte):
                    erreurs.append(
                        prefixe + f"indice {position} contient la réponse - un indice ne doit pas la donner"
                    )

    # Affichage temporisé : mode connu et rythme d'un élément plausible.
    affichage = contenu.get("affichage")
    if affichage is not None:
        if not isinstance(affichage, dict):
            erreurs.append(prefixe + "contenu.affichage doit être un objet")
        else:
            mode = affichage.get("mode")
            if mode not in MODES_AFFICHAGE:
                erreurs.append(prefixe + f"affichage.mode inconnu : {mode!r}")
            if mode in ("sequence", "series"):
                duree = affichage.get("duree_par_item_ms")
                if not est_entier(duree) or not RYTHME_MIN_MS <= duree <= RYTHME_MAX_MS:
                    erreurs.append(
                        prefixe
                        + f"affichage.duree_par_item_ms hors {RYTHME_MIN_MS}..{RYTHME_MAX_MS} ms : {duree!r}"
                    )

    # Empan de mots : séquence de mots distincts, réponse = séquence ou inverse.
    if type_item == "empan-mots":
        elements = affichage.get("elements") if isinstance(affichage, dict) else None
        if not isinstance(elements, list) or len(elements) < 3:
            erreurs.append(prefixe + "empan-mots : au moins 3 mots attendus")
        elif not all(isinstance(mot, str) and mot.strip() for mot in elements):
            erreurs.append(prefixe + "empan-mots : mots attendus sous forme de chaînes non vides")
        elif len({_normaliser_texte(mot) for mot in elements}) != len(elements):
            erreurs.append(prefixe + "empan-mots : mots dupliqués dans la séquence")
        elif isinstance(reponse, str):
            direct = _normaliser_texte(" ".join(elements))
            inverse = _normaliser_texte(" ".join(reversed(elements)))
            if _normaliser_texte(reponse) not in {direct, inverse}:
                erreurs.append(prefixe + "empan-mots : la réponse n'est pas la séquence ni son inverse")
        else:
            erreurs.append(prefixe + "empan-mots : réponse attendue sous forme de texte")

    # Rappel libre de séries : cohérence séries ↔ cibles, seuil et délai bornés.
    if type_item == "rappel-libre":
        erreurs.extend(erreurs_rappel_libre(item, prefixe, contenu, affichage))

    # Prise de message (mémoire de travail fonctionnelle) : le fait demandé
    # doit être présent dans le message affiché - sinon la question serait
    # introuvable depuis le stimulus (exercice mal formé).
    if type_item == "prise-message":
        elements = (affichage or {}).get("elements") if isinstance(affichage, dict) else None
        message = " ".join(
            ligne[0] if isinstance(ligne, list) and ligne else str(ligne)
            for ligne in (elements or [])
        )
        if not message.strip():
            erreurs.append(prefixe + "prise-message : affichage.elements doit contenir le message")
        elif isinstance(reponse, str) and _normaliser_texte(reponse) not in _normaliser_texte(message):
            erreurs.append(prefixe + "prise-message : la réponse n'est pas dans le message affiché")

    # Estimation de durée : réponse bornée par une fourchette cohérente.
    if type_item == "estimation-temps":
        reponse_bloc = item.get("reponse") if isinstance(item.get("reponse"), dict) else {}
        valeur = reponse_bloc.get("valeur")
        intervalle = reponse_bloc.get("intervalle")
        if not isinstance(valeur, (int, float)) or isinstance(valeur, bool):
            erreurs.append(prefixe + "estimation-temps : reponse.valeur doit être un nombre")
        if not isinstance(intervalle, list) or len(intervalle) != 2 or not all(
            isinstance(b, (int, float)) and not isinstance(b, bool) for b in intervalle
        ):
            erreurs.append(prefixe + "estimation-temps : reponse.intervalle doit être [min, max]")
        elif isinstance(valeur, (int, float)) and not intervalle[0] <= valeur <= intervalle[1]:
            erreurs.append(prefixe + "estimation-temps : la valeur attendue doit être dans la fourchette")

    # Variantes acceptées (facultatif) : liste de chaînes non vides, distinctes de la réponse.
    variantes = (item.get("reponse") or {}).get("variantes") if isinstance(item.get("reponse"), dict) else None
    if variantes is not None:
        if not isinstance(variantes, list) or not all(
            isinstance(v, str) and v.strip() for v in variantes
        ):
            erreurs.append(prefixe + "reponse.variantes doit être une liste de chaînes non vides")
        elif isinstance(reponse, str) and any(
            _normaliser_texte(v) == _normaliser_texte(reponse) for v in variantes
        ):
            erreurs.append(prefixe + "reponse.variantes répète la réponse attendue")

    # Analyse du mot (SFA/PCA) : méthode, définition, étapes de génération, mot cible.
    if type_item == "analyse-mot":
        if contenu.get("methode") not in ("semantique", "phonologique"):
            erreurs.append(prefixe + "analyse-mot : contenu.methode doit être 'semantique' ou 'phonologique'")
        if not isinstance(contenu.get("definition"), str) or not contenu.get("definition", "").strip():
            erreurs.append(prefixe + "analyse-mot : contenu.definition manquante")
        etapes = contenu.get("etapes")
        if not isinstance(etapes, list) or len(etapes) < 2 or not all(
            isinstance(e, str) and e.strip() for e in etapes
        ):
            erreurs.append(prefixe + "analyse-mot : contenu.etapes doit être une liste d'au moins 2 questions")
        if not isinstance(reponse, str) or not reponse.strip():
            erreurs.append(prefixe + "analyse-mot : réponse attendue (le mot) manquante")

    # Grille de déduction : structure, carré latin, indices vrais pour la solution.
    if type_item == "grille-deduction":
        erreurs.extend(_erreurs_grille_deduction(item, prefixe, contenu))

    return erreurs


#: Types d'indices admis dans une grille de déduction.
TYPES_INDICE_GRILLE = {
    "case", "ligne", "colonne", "pas-ligne", "pas-colonne",
    "coin", "pas-coin", "pas-bord", "ni-ni",
    "diagonale", "diagonale-inverse", "pas-diagonale", "pas-diagonale-inverse",
    "voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous", "voisin-diagonale",
    "oppose",
    "autre-ligne", "autre-colonne", "comparaison",
    "a-droite-de", "a-gauche-de", "au-dessus-de", "en-dessous-de",
    "si-alors", "regle",
}

#: Nombre minimal d'informations par phrase, par palier : au début, les phrases sont
#: **denses** (chaîne d'une ancre et de deux relations) pour raccourcir l'exercice ;
#: ensuite elles se resserrent à deux informations et il faut recouper davantage.
QUOTA_MIN_COMPOSE = {1: 3, 2: 2, 3: 2, 4: 2}

#: Types d'indices admis dans une grille de déduction.


def _cellule_grille(fig: list[int], coul: list[int], i_f: int, i_c: int) -> int:
    """Case de la figure colorée (i_f, i_c) ; -1 si absente (grille non orthogonale)."""
    for i in range(len(fig)):
        if fig[i] == i_f and coul[i] == i_c:
            return i
    return -1


def _predicat_grille(indice: dict, fig: list[int], coul: list[int],
                     index_figure: dict, index_couleur: dict, n: int) -> bool:
    """Un indice (et ses **deux informations**) est-il vrai pour la solution ?

    Le contrôle passe par le solveur commun : une seule définition de la vérité
    des phrases, partagée par le générateur, le dépôt et les tests.
    """
    if indice.get("type") == "regle":
        return True
    noms_f = [nom for nom, _ in sorted(index_figure.items(), key=lambda kv: kv[1])]
    noms_c = [nom for nom, _ in sorted(index_couleur.items(), key=lambda kv: kv[1])]
    return pred_indice(indice, (tuple(fig), tuple(coul)), n, noms_f, noms_c)


def _sens_contredit(indice: dict, fig: list[int], coul: list[int],
                    index_figure: dict, index_couleur: dict, n: int) -> str | None:
    """Contradiction entre le **sens français** de la phrase et la solution.

    Contrôle écrit indépendamment du solveur, à partir de la signification des
    phrases : « Le carré bleu est juste à gauche du cercle rouge » exige que le
    carré bleu soit dans la colonne immédiatement à gauche. C'est ce contrôle qui
    manquait quand une paire droite/gauche ou dessus/dessous a été inversée -
    l'inversion rendait la grille insoluble sans qu'aucun outil ne s'en aperçoive.
    """
    def case_de(nom_f: str, nom_c: str) -> int:
        return _cellule_grille(fig, coul, index_figure[nom_f], index_couleur[nom_c])

    coins_n = {0, n - 1, n * (n - 1), n * n - 1}
    bords_n = {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}
    for atome in [indice] + list(indice.get("et") or []):
        if not isinstance(atome, dict):
            continue
        nom_f = atome.get("figure", indice.get("figure"))
        nom_c = atome.get("couleur", indice.get("couleur"))
        if nom_f not in index_figure or nom_c not in index_couleur:
            continue
        ligne, colonne = divmod(case_de(nom_f, nom_c), n)
        type_indice = atome.get("type")
        if type_indice == "ligne" and ligne != atome["ligne"]:
            return "la phrase annonce une autre ligne"
        if type_indice == "colonne" and colonne != atome["colonne"]:
            return "la phrase annonce une autre colonne"
        if type_indice == "pas-ligne" and ligne == atome["ligne"]:
            return "la phrase exclut la ligne où se trouve la figure"
        if type_indice == "pas-colonne" and colonne == atome["colonne"]:
            return "la phrase exclut la colonne où se trouve la figure"
        if type_indice == "pas-coin" and case_de(nom_f, nom_c) in coins_n:
            return "la figure est dans un coin alors que la phrase l'exclut"
        if type_indice == "coin" and case_de(nom_f, nom_c) not in coins_n:
            return "la phrase annonce un coin, la figure n'y est pas"
        if type_indice == "diagonale" and ligne != colonne:
            return "la phrase annonce la diagonale descendante, la figure n'y est pas"
        if type_indice == "diagonale-inverse" and ligne + colonne != n - 1:
            return "la phrase annonce la diagonale montante, la figure n'y est pas"
        if type_indice == "pas-diagonale" and ligne == colonne:
            return "la phrase exclut la diagonale descendante où se trouve la figure"
        if type_indice == "pas-diagonale-inverse" and ligne + colonne == n - 1:
            return "la phrase exclut la diagonale montante où se trouve la figure"
        if type_indice == "pas-bord" and case_de(nom_f, nom_c) in bords_n:
            return "la figure est sur le bord alors que la phrase l'exclut"
        if type_indice == "ni-ni" and (case_de(nom_f, nom_c) in coins_n or case_de(nom_f, nom_c) in bords_n):
            return "la figure est dans un coin ou sur le bord alors que la phrase l'exclut"
        if type_indice in ("voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
                           "voisin-diagonale", "oppose",
                           "comparaison", "a-droite-de", "a-gauche-de", "au-dessus-de",
                           "en-dessous-de", "autre-ligne", "autre-colonne"):
            l2, c2 = divmod(case_de(atome["figure2"], atome["couleur2"]), n)
            attendu = {
                "voisin-gauche": (l2, c2 - 1),      # juste à gauche : une colonne avant
                "voisin-droite": (l2, c2 + 1),
                "voisin-dessus": (l2 - 1, c2),       # juste au-dessus : une ligne avant
                "voisin-dessous": (l2 + 1, c2),
            }.get(type_indice)
            if attendu and (ligne, colonne) != attendu:
                return (f"« {type_indice} » place la figure en ({ligne}, {colonne}) "
                        f"alors que la solution la donne en ({l2}, {c2})")
            if type_indice == "a-droite-de" and colonne <= c2:
                return "la phrase dit « plus à droite » sans que ce soit vrai"
            if type_indice == "a-gauche-de" and colonne >= c2:
                return "la phrase dit « plus à gauche » sans que ce soit vrai"
            if type_indice == "au-dessus-de" and ligne >= l2:
                return "la phrase dit « plus haut » sans que ce soit vrai"
            if type_indice == "en-dessous-de" and ligne <= l2:
                return "la phrase dit « plus bas » sans que ce soit vrai"
            if type_indice == "autre-ligne" and ligne == l2:
                return "la phrase dit « pas la même ligne » alors que c'est la même"
            if type_indice == "autre-colonne" and colonne == c2:
                return "la phrase dit « pas la même colonne » alors que c'est la même"
            if type_indice == "comparaison" and (ligne != l2 or colonne >= c2):
                return "la phrase dit « sur la même ligne, à gauche » sans que ce soit vrai"
            if type_indice == "voisin-diagonale" and not (abs(ligne - l2) == 1 and abs(colonne - c2) == 1):
                return "la phrase dit que les deux figures se touchent en diagonale sans que ce soit vrai"
            if type_indice == "oppose" and case_de(nom_f, nom_c) != n * n - 1 - case_de(atome["figure2"], atome["couleur2"]):
                return "la phrase dit « à l'opposé » sans que les deux figures soient symétriques par le centre"
    return None


def _erreurs_grille_deduction(item: dict, prefixe: str, contenu: dict) -> list[str]:
    """Vérifie une grille de déduction : structure, carré latin, indices vrais."""
    erreurs: list[str] = []
    figures = contenu.get("figures")
    couleurs = contenu.get("couleurs")
    if not (isinstance(figures, list) and len(figures) in (3, 4) and len(set(figures)) == len(figures)):
        erreurs.append(prefixe + "grille-deduction : contenu.figures doit être 3 ou 4 figures distinctes")
        return erreurs
    if not (isinstance(couleurs, list) and len(couleurs) == len(figures) and len(set(couleurs)) == len(couleurs)):
        erreurs.append(prefixe + "grille-deduction : contenu.couleurs doit avoir autant de couleurs distinctes que de figures")
        return erreurs
    n = len(figures)

    enonces = contenu.get("enonces")
    if not isinstance(enonces, list) or len(enonces) < 4 or not all(
        isinstance(e, dict) and e.get("type") in TYPES_INDICE_GRILLE for e in enonces
    ):
        erreurs.append(prefixe + "grille-deduction : indices structurés attendus")

    reponse_bloc = item.get("reponse") if isinstance(item.get("reponse"), dict) else {}
    grille = reponse_bloc.get("grille")
    valeur = reponse_bloc.get("valeur")
    if not isinstance(grille, list) or len(grille) != n * n:
        erreurs.append(prefixe + f"grille-deduction : reponse.grille doit contenir {n * n} cases")
        return erreurs

    cellules = []
    for case in grille:
        if not (isinstance(case, list) and len(case) == 2
                and case[0] in figures and case[1] in couleurs):
            erreurs.append(prefixe + "grille-deduction : case [figure, couleur] attendue")
            return erreurs
        cellules.append(case)

    # Chaque figure colorée (figure × couleur) est posée une seule fois : aucune
    # combinaison ne se répète. C'est la SEULE règle du puzzle - aucune contrainte
    # de ligne ou de colonne n'est supposée : tout doit venir des phrases.
    combinaisons = [(f, c) for f, c in cellules]
    if len(set(combinaisons)) != n * n:
        erreurs.append(prefixe + "grille-deduction : une figure colorée apparaît plusieurs fois (chaque combinaison doit être unique)")

    if valeur != ";".join(f"{f}:{c}" for f, c in cellules):
        erreurs.append(prefixe + "grille-deduction : reponse.valeur ne correspond pas à reponse.grille")

    # Chaque indice (principal et de secours) est vrai pour la solution.
    index_figure = {f: i for i, f in enumerate(figures)}
    index_couleur = {c: i for i, c in enumerate(couleurs)}
    fig = [index_figure[f] for f, _ in cellules]
    coul = [index_couleur[c] for _, c in cellules]
    for position, indice in enumerate(enonces, start=1):
        if not isinstance(indice, dict):
            continue
        if indice.get("type") not in TYPES_INDICE_GRILLE:
            erreurs.append(prefixe + f"grille-deduction : indice {position} de type inconnu")
        elif any(isinstance(a, dict) and a.get("type") not in TYPES_INDICE_GRILLE
                 for a in (indice.get("et") or [])):
            erreurs.append(prefixe + f"grille-deduction : information {position} de type inconnu")
        elif not _predicat_grille(indice, fig, coul, index_figure, index_couleur, n):
            erreurs.append(prefixe + f"grille-deduction : l'indice {position} contredit la solution")

    # Sens des phrases : contrôle INDÉPENDANT du solveur.
    for position, indice in enumerate(enonces, start=1):
        if not isinstance(indice, dict):
            continue
        souci = _sens_contredit(indice, fig, coul, index_figure, index_couleur, n)
        if souci:
            erreurs.append(prefixe + f"grille-deduction : phrase {position} contredit la solution ({souci})")

    # Pédagogie verrouillée : les phrases doivent contenir la résolution.
    palier = item.get("palier")
    minimum = QUOTA_MIN_COMPOSE.get(palier, 2)
    if any(isinstance(i, dict) and i.get("type") == "case" for i in enonces):
        erreurs.append(prefixe + "grille-deduction : placement direct interdit "
                                "(toute la résolution doit venir des phrases)")
    for position, indice in enumerate(enonces, start=1):
        if not isinstance(indice, dict):
            continue
        informations = 1 + len(indice.get("et") or [])
        if informations < minimum:
            erreurs.append(prefixe + f"grille-deduction : phrase {position} à {informations} information(s) "
                                    f"(minimum {minimum} au palier {palier})")
        if not any(a.get("type") in TYPES_BINAIRES_DEDUCTION for a in [indice] + list(indice.get("et") or [])):
            erreurs.append(prefixe + f"grille-deduction : phrase {position} ne relie aucune figure "
                                    "(aucune déduction provoquée)")
    secours = contenu.get("indices")
    if isinstance(secours, list):
        for position, indice in enumerate(secours, start=1):
            if isinstance(indice, dict) and indice.get("type") not in TYPES_INDICE_GRILLE:
                erreurs.append(prefixe + f"grille-deduction : indice de secours {position} de type inconnu")
            elif isinstance(indice, dict) and not _predicat_grille(indice, fig, coul, index_figure, index_couleur, n):
                erreurs.append(prefixe + f"grille-deduction : l'indice de secours {position} contredit la solution")

    # Les indices doivent suffire : la grille se reconstruit par déduction, sans deviner.
    if (isinstance(enonces, list) and enonces
            and all(isinstance(i, dict) for i in enonces)
            and not resoudre_par_deduction(enonces, n, figures, couleurs)):
        erreurs.append(prefixe + "grille-deduction : puzzle non résoluble par déduction "
                                "(ajouter des indices jusqu'à ce que le solveur termine)")
    return erreurs


def erreurs_rappel_libre(item: dict, prefixe: str, contenu: dict, affichage: object) -> list[str]:
    """Vérifie un item de rappel libre (séries, portée, seuil, délai, cibles)."""
    erreurs: list[str] = []
    series = affichage.get("series") if isinstance(affichage, dict) else None
    if not isinstance(series, list) or not series:
        erreurs.append(prefixe + "rappel-libre : affichage.series doit lister au moins une série")
        return erreurs

    mots: list[str] = []
    for position, serie in enumerate(series, start=1):
        if not isinstance(serie, list) or len(serie) < 3:
            erreurs.append(prefixe + f"rappel-libre : série {position} - au moins 3 mots attendus")
            continue
        if not all(isinstance(mot, str) and mot.strip() for mot in serie):
            erreurs.append(prefixe + f"rappel-libre : série {position} - mots attendus comme chaînes non vides")
            continue
        mots.extend(_normaliser_texte(mot) for mot in serie)
    if len(set(mots)) != len(mots):
        erreurs.append(
            prefixe + "rappel-libre : un mot revient dans plusieurs séries - le comptage serait ambigu"
        )

    portee = contenu.get("portee")
    if portee not in {"toutes-series", "premiere-serie"}:
        erreurs.append(prefixe + f"rappel-libre : portee inconnue {portee!r}")
    delai = contenu.get("delai_s", 0)
    if not est_entier(delai) or not 0 <= delai <= 180:
        erreurs.append(prefixe + f"rappel-libre : delai_s doit être un entier 0..180 : {delai!r}")

    reponse = item.get("reponse") if isinstance(item.get("reponse"), dict) else {}
    cibles, seuil = reponse.get("valeur"), reponse.get("seuil")
    if not isinstance(cibles, list) or not cibles or not all(
        isinstance(mot, str) and mot.strip() for mot in cibles
    ):
        erreurs.append(prefixe + "rappel-libre : reponse.valeur doit lister les mots cibles")
        return erreurs
    if isinstance(seuil, bool) or not isinstance(seuil, (int, float)) or not 0.25 <= float(seuil) <= 1:
        erreurs.append(prefixe + f"rappel-libre : reponse.seuil hors 0.25..1 : {seuil!r}")

    attendu = (
        [_normaliser_texte(mot) for mot in series[0]]
        if portee == "premiere-serie"
        else list(mots)
    )
    if sorted(_normaliser_texte(mot) for mot in cibles) != sorted(attendu):
        erreurs.append(
            prefixe + "rappel-libre : les cibles déclarées ne correspondent pas aux séries affichées"
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


def _reponse_calculee(enonce: str) -> int | None:
    """Recalcule la réponse d'un énoncé de calcul mental — ou None si non calculable.

    Contrôle **indépendant du générateur** : on relit la question telle qu'elle sera
    lue, et on refait le calcul. Une erreur de contenu (mauvais résultat associé à une
    question) est ainsi détectée mécaniquement. Les énoncés de la vie quotidienne
    (quantités, durées) ne sont pas calculables automatiquement : on n'invente rien,
    ils sont contrôlés en forme seulement.
    """
    correspondance = MOTIF_CALCUL_ARITHMETIQUE.fullmatch(enonce.strip())
    if correspondance:
        a, operateur, b, suite = (
            int(correspondance.group(1)), correspondance.group(2),
            int(correspondance.group(3)), correspondance.group(4),
        )
        resultat = a + b if operateur == "+" else a - b if operateur == "−" else a * b
        if suite:
            reste = suite.strip()
            operateur2, nombre2 = reste[0], reste[1:].strip()
            resultat = resultat + int(nombre2) if operateur2 == "+" else resultat - int(nombre2)
        return resultat

    correspondance = MOTIF_COMPLEMENT.fullmatch(enonce.strip())
    if correspondance:
        return int(correspondance.group(2)) - int(correspondance.group(1))

    correspondance = MOTIF_TOTAL_ARTICLES.fullmatch(enonce.strip())
    if correspondance:
        prix = float(correspondance.group(2).replace(",", "."))
        return int(round(int(correspondance.group(1)) * prix))

    correspondance = MOTIF_RENDU.fullmatch(enonce.strip())
    if correspondance:
        return int(correspondance.group(2)) - int(correspondance.group(1))

    # Série de calcul : évaluation de gauche à droite, comme la personne la fait.
    if MOTIF_CHAINE.match(enonce.strip()):
        jetons = enonce.split()
        total = int(jetons[0])
        for rang in range(1, len(jetons) - 1, 2):
            operateur, valeur = jetons[rang], int(jetons[rang + 1])
            total = total + valeur if operateur == "+" else total - valeur
        return total

    # Suite à continuer : le pas se lit sur les deux premiers nombres.
    correspondance = MOTIF_SUITE_CONTINUE.fullmatch(enonce.strip())
    if correspondance:
        nombres = [int(n) for n in correspondance.group(1).split(",")]
        pas = nombres[1] - nombres[0]
        return nombres[-1] + pas

    # Repérer l'erreur : le pas se lit sur les deux premiers nombres.
    correspondance = MOTIF_SUITE_ERREUR.fullmatch(enonce.strip())
    if correspondance:
        nombres = [int(n) for n in correspondance.group(1).split(",")]
        pas = nombres[1] - nombres[0]
        attendus = [nombres[0] + pas * rang for rang in range(len(nombres))]
        fautifs = [reel for reel, attendu in zip(nombres, attendus) if reel != attendu]
        return fautifs[0] if len(fautifs) == 1 else None

    # Fait cherché par l'autre bout : « 42 = 6 × ? ».
    correspondance = MOTIF_FAIT_INVERSE_GAUCHE.fullmatch(enonce.strip())
    if correspondance:
        produit, facteur = int(correspondance.group(1)), int(correspondance.group(2))
        return produit // facteur if facteur and produit % facteur == 0 else None
    correspondance = MOTIF_FAIT_INVERSE_DROITE.fullmatch(enonce.strip())
    if correspondance:
        produit, facteur = int(correspondance.group(1)), int(correspondance.group(2))
        return produit // facteur if facteur and produit % facteur == 0 else None
    return None


def erreurs_coherence_chaine(item: dict, prefixe: str) -> list[str]:
    """Série de calcul (attention soutenue) : on refait le calcul de gauche à droite.

    Contrôle indépendant du générateur : une série associée à un mauvais total — ou dont
    le total change selon l'ordre des opérations — est refusée au dépôt.
    """
    enonce = str((item.get("contenu") or {}).get("enonce") or "")
    if not MOTIF_CHAINE.match(enonce.strip()):
        return []
    reponse = (item.get("reponse") or {}).get("valeur")
    attendue = _reponse_calculee(enonce)
    if attendue is None or attendue == reponse:
        return []
    return [prefixe + f"série « {enonce} » : total {attendue}, pas {reponse}"]


def erreurs_coherence_calcul(item: dict, prefixe: str,
                             manifest_par_theme: dict[str, dict[int, dict]]) -> list[str]:
    """Vérifie un item de calcul mental d'après son **énoncé**, pas d'après son rang.

    Contrôles : le palier existe dans le manifest ; la réponse est un entier positif ;
    et — quand l'énoncé est calculable — la réponse recalculée correspond. C'est ce
    dernier contrôle qui attrape une question associée au mauvais résultat.
    """
    theme = item.get("theme")
    if theme not in manifest_par_theme:
        return []
    palier = item.get("palier")
    if not est_entier(palier) or palier not in manifest_par_theme[theme]:
        return [prefixe + f"palier {palier!r} absent du manifest du thème {theme!r}"]

    identifiant = item.get("id", "")
    if not MOTIF_ID_CALCUL.fullmatch(identifiant):
        return [prefixe + f"id non conforme au motif cm2-<palier>-<rang> : {identifiant!r}"]

    enonce = str((item.get("contenu") or {}).get("enonce") or "")
    reponse = (item.get("reponse") or {}).get("valeur")
    if isinstance(reponse, bool) or not isinstance(reponse, int) or reponse < 0:
        return [prefixe + f"réponse entière positive attendue, reçue {reponse!r}"]
    attendue = _reponse_calculee(enonce)
    if attendue is not None and attendue != reponse:
        return [prefixe + f"« {enonce} » vaut {attendue}, pas {reponse}"]
    return []


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


#: Thèmes réellement jouables (contrat GET /api/entrainement/themes) : le
#: programme ne peut proposer qu'un thème que l'API expose.
THEMES_CONNUS = {
    "calcul-mental", "anglais", "python", "memoire", "concentration",
    "evocation", "rappel-series", "quotidien", "deduction", "methodes",
}

#: Types de jour admis dans un programme.
TYPES_JOUR = {"seance", "legere", "repos"}


def erreurs_programme(
    donnees: object, chemin: Path, paliers_par_theme: dict[str, int]
) -> list[str]:
    """Vérifie un programme d'entraînement (semaines, jours, plafonds, thèmes).

    Contrôles : structure des 7 jours, thèmes proposés réellement jouables,
    plafonds de palier cohérents avec le contenu disponible, jour de repos sans
    thème, séance d'un seul thème à la fois (alternance), durées bornées.
    """
    prefixe = f"{chemin.relative_to(RACINE_DEPOT)}: "
    if not isinstance(donnees, dict) or not isinstance(donnees.get("semaines"), list):
        return [prefixe + "programme attendu : objet avec une liste 'semaines'"]

    erreurs: list[str] = []
    semaines = donnees["semaines"]
    if not est_entier(donnees.get("duree_semaines")) or donnees["duree_semaines"] != len(semaines):
        erreurs.append(prefixe + "duree_semaines doit correspondre au nombre de semaines listées")

    for position, semaine in enumerate(semaines, start=1):
        if not isinstance(semaine, dict):
            erreurs.append(prefixe + f"semaine {position} : objet attendu")
            continue
        if semaine.get("semaine") != position:
            erreurs.append(prefixe + f"semaine {position} : champ semaine = {semaine.get('semaine')!r}")
        duree = semaine.get("duree_min")
        if not est_entier(duree) or not 1 <= duree <= 15:
            erreurs.append(prefixe + f"semaine {position} : duree_min doit être un entier 1..15")

        plafonds = semaine.get("plafond_palier")
        if not isinstance(plafonds, dict) or not plafonds:
            erreurs.append(prefixe + f"semaine {position} : plafond_palier manquant")
        else:
            for theme, plafond in plafonds.items():
                if theme not in THEMES_CONNUS:
                    erreurs.append(prefixe + f"semaine {position} : thème inconnu {theme!r}")
                    continue
                if not est_entier(plafond) or plafond < 1:
                    erreurs.append(prefixe + f"semaine {position} : plafond {theme} doit être ≥ 1")
                elif theme in paliers_par_theme and plafond > paliers_par_theme[theme]:
                    erreurs.append(
                        prefixe
                        + f"semaine {position} : plafond {theme} ({plafond}) dépasse les "
                        + f"{paliers_par_theme[theme]} paliers disponibles"
                    )

        jours = semaine.get("jours")
        if not isinstance(jours, list) or len(jours) != 7:
            erreurs.append(prefixe + f"semaine {position} : 7 jours attendus")
            continue
        for jour in jours:
            if not isinstance(jour, dict):
                erreurs.append(prefixe + f"semaine {position} : jour attendu comme objet")
                continue
            type_jour = jour.get("type")
            if type_jour not in TYPES_JOUR:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')!r} : type {type_jour!r}")
            themes = jour.get("themes")
            if not isinstance(themes, list) or not all(isinstance(t, str) for t in themes):
                erreurs.append(prefixe + f"semaine {position} : themes doit être un tableau")
                continue
            for theme in themes:
                if theme != "au-choix" and theme not in THEMES_CONNUS:
                    erreurs.append(prefixe + f"semaine {position} : thème inconnu {theme!r}")
            if type_jour == "repos" and themes:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')} : un jour de repos ne propose pas de thème")
            if type_jour == "seance" and len(themes) != 1:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')} : une séance propose un seul thème")
            duree_jour = jour.get("duree_min")
            if not est_entier(duree_jour) or not 0 <= duree_jour <= 15:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')} : duree_min 0..15 attendu")
    return erreurs


def erreurs_missions(donnees: object, chemin: Path) -> list[str]:
    """Vérifie le fichier de missions hors écran (``content/.../missions.json``)."""
    prefixe = f"{chemin.relative_to(RACINE_DEPOT)}: "
    if not isinstance(donnees, dict) or not isinstance(donnees.get("missions"), list):
        return [prefixe + "fichier de missions attendu : objet avec une liste 'missions'"]
    erreurs: list[str] = []
    ids_vus: set[str] = set()
    for position, mission in enumerate(donnees["missions"], start=1):
        if not isinstance(mission, dict):
            erreurs.append(prefixe + f"mission {position} : objet attendu")
            continue
        identifiant = mission.get("id")
        if not isinstance(identifiant, str) or not identifiant:
            erreurs.append(prefixe + f"mission {position} : id manquant")
        elif identifiant in ids_vus:
            erreurs.append(prefixe + f"mission {position} : id dupliqué {identifiant!r}")
        else:
            ids_vus.add(identifiant)
        if not isinstance(mission.get("titre"), str) or not mission["titre"].strip():
            erreurs.append(prefixe + f"mission {position} : titre manquant")
        if not est_entier(mission.get("niveau")) or mission["niveau"] < 1:
            erreurs.append(prefixe + f"mission {position} : niveau doit être un entier ≥ 1")
        etapes = mission.get("etapes")
        if not isinstance(etapes, list) or not etapes or not all(isinstance(e, str) and e.strip() for e in etapes):
            erreurs.append(prefixe + f"mission {position} : etapes doit être une liste non vide de chaînes")
        for champ in ("pourquoi", "repere"):
            if not isinstance(mission.get(champ), str) or not mission[champ].strip():
                erreurs.append(prefixe + f"mission {position} : {champ} manquant")
        if "duree_estimee_min" in mission and (
            not est_entier(mission["duree_estimee_min"]) or mission["duree_estimee_min"] < 1
        ):
            erreurs.append(prefixe + f"mission {position} : duree_estimee_min doit être un entier ≥ 1")
    return erreurs


# --- Orchestration ------------------------------------------------------------


def erreurs_regularite(chemin: Path, items: list) -> list[str]:
    """Contrôle d'ensemble : un fichier ne doit pas présenter de motif systématique.

    Régression constatée : toutes les grilles d'un palier commençaient par le même type
    de phrase (« coin » en tête des 20 grilles du palier 1), parce que les phrases du
    vocabulaire obligatoire étaient placées en premier. Un tel motif met sur la piste
    sans rien dire de la solution.
    """
    grilles = [
        item for item in items
        if isinstance(item, dict) and item.get("type") == "grille-deduction"
        and (item.get("contenu") or {}).get("enonces")
    ]
    if len(grilles) < 5:
        return []
    premiers = Counter(grille["contenu"]["enonces"][0].get("type") for grille in grilles)
    type_dominant, nombre = premiers.most_common(1)[0]
    if nombre > len(grilles) * 0.6:
        return [f"{chemin.parent.name}/{chemin.name} : {nombre}/{len(grilles)} grilles commencent "
                f"par le même type de phrase (« {type_dominant} ») - varier l'ordre des phrases"]
    if len(premiers) < 3:
        return [f"{chemin.parent.name}/{chemin.name} : {len(premiers)} type(s) de phrase en tête "
                f"seulement sur {len(grilles)} grilles - varier l'ordre des phrases"]
    return []


def couverture_calcul(items: list) -> tuple[int, int]:
    """Nombre d'items de calcul mental recalculables, et total.

    Mesure de **couverture** : si un motif de contrôle se casse (un point d'interrogation
    non échappé, par exemple), une famille entière cesse d'être vérifiée sans que rien ne
    le signale. Un contrôle qui ne contrôle rien est plus dangereux que pas de contrôle :
    la couverture du thème est donc mesurée et seuilée.
    """
    calcul = [item for item in items if isinstance(item, dict)
              and item.get("theme") == "calcul-mental"]
    verifiables = sum(1 for item in calcul
                      if _reponse_calculee(str((item.get("contenu") or {}).get("enonce") or "")) is not None)
    return verifiables, len(calcul)


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


if __name__ == "__main__":
    raise SystemExit(main())
