from __future__ import annotations

from collections import Counter
from pathlib import Path




from .calculation import (
    erreurs_coherence_calcul,
)
from .common import (
    MODES_AFFICHAGE, MOTIF_REF_PALIER, RACINE_DEPOT, TYPES_A_CHOIX, TYPES_A_INDICES, TYPES_INDICE, _normaliser_texte, est_date_iso, est_entier,
)
from .deduction import (
    _erreurs_grille_deduction,
)
from .recall import (
    erreurs_rappel_libre, erreurs_sequence_pqrst,
)

RYTHME_MIN_MS, RYTHME_MAX_MS = 400, 2000

def erreurs_item(item: object, chemin: Path, regles: dict, ids_vus: dict[str, Path],
                 manifest_par_theme: dict[str, dict[int, dict]],
                 ids_paliers_connus: set[str]) -> list[str]:
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

    if type_item == "reperer-info":
        document = contenu.get("document")
        if not isinstance(document, str) or not document.strip():
            erreurs.append(prefixe + "reperer-info : document permanent requis")
        if "affichage" in contenu:
            erreurs.append(prefixe + "reperer-info : pas de phase de mémorisation temporisée")
    if type_item == "plan-a-verifier":
        plan = contenu.get("plan")
        if not isinstance(plan, list) or len(plan) != 3 or not all(isinstance(x, str) for x in plan):
            erreurs.append(prefixe + "plan-a-verifier : trois étapes requises")
        elif (len(set(plan)) != 3 or not isinstance(options, list)
              or not all(isinstance(x, str) for x in options) or set(plan) != set(options)):
            erreurs.append(prefixe + "plan-a-verifier : les choix doivent correspondre aux étapes")

    if type_item in {"actualiser-consigne", "comparer-documents", "reperer-essentiel"}:
        champs = contenu.get("messages") if type_item == "reperer-essentiel" else contenu.get("champs")
        if not isinstance(champs, list) or not champs or not all(isinstance(x, dict) and x.get("id") for x in champs):
            erreurs.append(prefixe + "champs/messages fonctionnels requis")
        elif not isinstance(reponse, dict) or set(reponse) != {x["id"] for x in champs} or len(reponse) != len(champs):
            erreurs.append(prefixe + "une réponse requise pour chaque champ/message distinct")
        if type_item == "actualiser-consigne":
            etapes = contenu.get("etapes")
            if not isinstance(etapes, list) or len(etapes) < 2 or not all(isinstance(e, dict) and e.get("texte") for e in etapes):
                erreurs.append(prefixe + "consigne initiale et mises à jour requises")
        elif type_item == "comparer-documents":
            documents = contenu.get("documents")
            if not isinstance(documents, list) or len(documents) != 2:
                erreurs.append(prefixe + "deux documents consultables requis")
            elif isinstance(reponse, dict):
                try:
                    a, b = [{l["id"]: l["texte"] for l in d["lignes"]} for d in documents]
                    calcule = {k: "conforme" if a[k] == b[k] else "ecart" for k in a}
                    if set(a) != set(b) or calcule != reponse:
                        erreurs.append(prefixe + "écarts incohérents avec les documents")
                except (KeyError, TypeError):
                    erreurs.append(prefixe + "lignes des documents invalides")
        elif isinstance(reponse, dict):
            if not contenu.get("objectif") or not contenu.get("critere") or set(reponse.values()) != {"oui", "non"}:
                erreurs.append(prefixe + "objectif, critères et deux catégories de messages requis")

    if type_item == "reprise-interrompue":
        points = contenu.get("points")
        interruption = contenu.get("interruption")
        apres = contenu.get("interruption_apres")
        if not isinstance(points, list) or len(points) != 4 or not all(
                isinstance(p, dict) and p.get("id") and p.get("label") and p.get("etat")
                and p.get("options") == ["Déjà validé", "À reprendre"] for p in points):
            erreurs.append(prefixe + "reprise-interrompue : quatre points structurés requis")
        elif not isinstance(reponse, dict) or set(reponse) != {"points", "reprise"}:
            erreurs.append(prefixe + "reprise-interrompue : réponse points + reprise requise")
        else:
            ids = [p["id"] for p in points]
            if len(set(ids)) != len(ids) or set(reponse["points"]) != set(ids):
                erreurs.append(prefixe + "reprise-interrompue : réponse requise pour chaque point distinct")
            if set(reponse["points"].values()) != {"valide", "reprendre"}:
                erreurs.append(prefixe + "reprise-interrompue : les deux états doivent être présents")
            if not isinstance(apres, int) or apres not in {1, 2, 3} or reponse["reprise"] != ids[apres]:
                erreurs.append(prefixe + "reprise-interrompue : point de reprise incohérent")
        if not isinstance(interruption, dict) or not interruption.get("enonce") or not isinstance(interruption.get("options"), list) or len(interruption["options"]) < 2:
            erreurs.append(prefixe + "reprise-interrompue : interruption brève avec choix requise")

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
                pause = affichage.get("pause_item_ms")
                if duree != 2000 or pause != 2000:
                    erreurs.append(
                        prefixe
                        + "séquence à mémoriser : 2000 ms d'affichage et 2000 ms de pause attendus"
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

    # Séquence « PQRST mis en œuvre » : cinq étapes, et faisabilité de la reformulation.
    if type_item == "pqrst-mise-en-oeuvre":
        erreurs.extend(erreurs_sequence_pqrst(item, prefixe, contenu))

    return erreurs

def erreurs_meta(meta: object, prefixe: str, regles: dict) -> list[str]:
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
