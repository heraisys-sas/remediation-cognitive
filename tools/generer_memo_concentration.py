#!/usr/bin/env python3
"""Générateur des thèmes « memoire » et « concentration » — sprint 2.

Génère, avec la seule bibliothèque standard et une graine fixe (déterminisme :
deux exécutions produisent des fichiers identiques), le contenu des deux
nouveaux thèmes d'entraînement :

- ``content/entrainement/memoire/paliers/palier-01.json`` … ``palier-12.json`` :
  empans de chiffres (endroit/envers), paires associatives mot–nombre, sondes
  n-back (rappel temporel), puis **empans de mots** (paliers 9 à 12, matériel
  verbal) — 18 items par palier ;
- ``content/entrainement/concentration/paliers/palier-01.json`` …
  ``palier-09.json`` : chaînes de calcul (additions/soustractions de gauche à
  droite, longueur croissante 3 → 7), cascades de soustractions, double tâche
  de filtrage, séries à règle — 18 items par palier, 162 au total.

Chaque thème est accompagné d'un manifest ``paliers.json`` (ordre, description,
prerequis, fichier, nb_items). Format des items : strictement conforme à
``content/schema-item.json`` (module « entrainement », meta traçable,
relecture orthophoniste à faire).

Les familles s'appuient sur des techniques classiques d'entraînement cognitif
(empan, n-back, double tâche, calcul sériel, apprentissage par paires, séries)
implémentées en 100 % original : la logique est assimilée, jamais le matériel
des tests protégés (PASAT, d2, MMSE, ECPA/Pearson).

Usage :

    python3 tools/generer_memo_concentration.py [--dry-run] [--date AAAA-MM-JJ]
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

# --- Paramètres généraux ------------------------------------------------------

#: Graine du générateur aléatoire (déterminisme du contenu versionné).
GRAINE: int = 20260904

#: Métadonnées traçables posées sur chaque item généré.
AUTEUR: str = "generation-automatique (tools/generer_memo_concentration.py)"
DATE_CREATION_DEFAUT: str = "2026-09-10"

#: Racine du dépôt (parent du dossier tools/) et base du contenu.
RACINE_DEPOT = Path(__file__).resolve().parent.parent
BASE_SORTIE = RACINE_DEPOT / "content" / "entrainement"

#: Lettres autorisées pour les séquences n-back (sans ambiguïté orthoacoustique).
LETTRES_NBACK = "BKLMPRT"

#: Lettres autorisées pour la double tâche de filtrage.
LETTRES_DOUBLE = "ACEFGHJKLNRST"

#: Pool de mots pour les paires associatives (majuscules, concrets).
MOTS_PAIRES = [
    "LUNE", "PONT", "ARBRE", "ROUE", "FLEUR", "TRAIN",
    "PORTE", "NUAGE", "PIERRE", "LIVRE", "PLUIE", "TABLE",
]

#: Pool de mots pour l'empan de mots et le rappel de séries : concrets, courts
#: (1–2 syllabes), et choisis pour limiter les confusions phonologiques entre eux.
MOTS_EMPAN = [
    "chat", "lune", "porte", "stylo", "table", "rivière", "pomme", "jardin",
    "montre", "nuage", "panier", "bougie", "fromage", "manteau", "chemin",
    "fenêtre", "sable", "crayon", "chapeau", "cuisine", "voiture", "orange",
    "marteau", "plage", "tapis", "guitare", "bureau", "soleil", "poisson",
    "chemise", "montagne", "bouteille", "chaussure", "journal", "musique",
    "neige", "bateau", "colline", "horloge", "feuille", "chocolat", "drapeau",
    "camion", "radis", "vélo", "ballon", "cahier", "jardinier",
]

#: Rythme d'affichage des séquences : un élément par seconde environ.
#: Le blanc inter-éléments sert seulement à marquer la séparation visuelle
#: (segmentation perceptive) — il n'ajoute aucune pause d'attente.
DUREE_ITEM_MS: int = 800
DUREE_ITEM_MOTS_MS: int = 900
BLANC_INTER_ITEM_MS: int = 120

#: Caps de complexité explicites (dosage anti sur-sollicitation).
CAP_CHAINE_7 = "7 opérations maximum"
CAP_NBACK_8 = "séquences de 8 éléments maximum"


# --- Socle commun -------------------------------------------------------------


def _item(
    identifiant: str,
    type_item: str,
    theme: str,
    fonctions: list[str],
    palier: int,
    prerequis: list[str],
    cap: str | None,
    contenu: dict,
    reponse: dict,
    date_creation: str,
) -> dict:
    """Construit un item complet conforme à content/schema-item.json."""
    return {
        "id": identifiant,
        "type": type_item,
        "module": "entrainement",
        "theme": theme,
        "fonctions_ciblees": fonctions,
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": cap,
        "contenu": contenu,
        "reponse": reponse,
        "meta": {
            "auteur": AUTEUR,
            "date_creation": date_creation,
            "relecture_ortho": {"statut": "a_revoir"},
        },
    }


def _chiffres_sans_doublon_adjacent(rng: random.Random, longueur: int) -> list[str]:
    """Chiffres 0..9 en chaînes, sans deux chiffres identiques consécutifs."""
    chiffres = [str(rng.randrange(10))]
    while len(chiffres) < longueur:
        candidat = str(rng.randrange(10))
        if candidat != chiffres[-1]:
            chiffres.append(candidat)
    return chiffres


def _lettres_sans_doublon_adjacent(rng: random.Random, longueur: int) -> list[str]:
    """Lettres majuscules sans deux identiques consécutifs (lisibilité)."""
    lettres = [rng.choice(LETTRES_NBACK)]
    while len(lettres) < longueur:
        candidat = rng.choice(LETTRES_NBACK)
        if candidat != lettres[-1]:
            lettres.append(candidat)
    return lettres


# --- Thème « memoire » ----------------------------------------------------------


def _empan(rng, palier, longueur, envers, nn, prerequis, date_creation):
    """Empan de chiffres : séquence montrée une à une, rappel endroit ou envers."""
    elements = _chiffres_sans_doublon_adjacent(rng, longueur)
    if envers:
        attendue = "".join(reversed(elements))
        enonce = "Tape la séquence à l'envers (de mémoire)."
    else:
        attendue = "".join(elements)
        enonce = "Tape la séquence de mémoire, dans l'ordre."
    contenu = {
        "consigne": "Mémorise la séquence de chiffres.",
        "affichage": {
            "mode": "sequence",
            "duree_par_item_ms": DUREE_ITEM_MS,
            "elements": elements,
        },
        "enonce": enonce,
        "aide": None,
    }
    return _item(
        f"me-{palier}-empan-{nn:02d}", "empan", "memoire", ["memoire-travail"],
        palier, prerequis, None, contenu, {"valeur": attendue}, date_creation,
    )


def _empan_mots(rng, palier, longueur, envers, nn, prerequis, date_creation):
    """Empan de mots : même logique que l'empan de chiffres, matériel verbal.

    Le rappel verbal est plus sensible à la similarité phonologique : les mots
    sont donc sans doublon dans la séquence et tirés d'un ensemble concret.
    """
    elements = rng.sample(MOTS_EMPAN, longueur)
    if envers:
        attendue = " ".join(reversed(elements))
        enonce = "Tape les mots à l'envers (le dernier d'abord)."
    else:
        attendue = " ".join(elements)
        enonce = "Tape les mots dans l'ordre, en les séparant par des espaces."
    contenu = {
        "consigne": "Mémorise les mots affichés.",
        "affichage": {
            "mode": "sequence",
            "duree_par_item_ms": DUREE_ITEM_MOTS_MS,
            "elements": elements,
        },
        "enonce": enonce,
        "aide": None,
    }
    return _item(
        f"me-{palier}-mots-{nn:02d}", "empan-mots", "memoire", ["memoire-travail"],
        palier, prerequis, None, contenu, {"valeur": attendue}, date_creation,
    )


def _nback(rng, palier, pas, nn, prerequis, date_creation):
    """Sonde n-back : rappel de l'élément N positions avant la fin de la séquence."""
    longueur = pas + 4
    elements = _lettres_sans_doublon_adjacent(rng, longueur)
    sonde = elements[longueur - 1 - pas]
    contenu = {
        "consigne": "Mémorise la séquence d'éléments.",
        "affichage": {
            "mode": "sequence",
            "duree_par_item_ms": 1200,
            "elements": elements,
        },
        "enonce": f"Quel élément était {pas} positions avant la fin ? Tape-le.",
        "aide": None,
    }
    cap = CAP_NBACK_8 if palier >= 8 else None
    return _item(
        f"me-{palier}-nback-{nn:02d}", "n-back", "memoire",
        ["memoire-travail", "attention-soutenue"], palier, prerequis, cap,
        contenu, {"valeur": sonde}, date_creation,
    )


def _paires(rng, palier, nb_paires, nn, prerequis, date_creation):
    """Paires associatives mot–nombre : mémorisation puis rappel sondé."""
    mots = rng.sample(MOTS_PAIRES, nb_paires)
    nombres = rng.sample(range(10, 100), nb_paires)
    elements = [[mot, str(nombre)] for mot, nombre in zip(mots, nombres)]
    sondage = rng.randrange(nb_paires)
    contenu = {
        "consigne": "Mémorise chaque paire mot–nombre.",
        "affichage": {
            "mode": "liste",
            "duree_totale_ms": nb_paires * 4000,
            "elements": elements,
        },
        "enonce": f"Nombre associé à « {mots[sondage]} » ?",
        "aide": None,
    }
    return _item(
        f"me-{palier}-paires-{nn:02d}", "paires-associatives", "memoire",
        ["memoire-travail", "memorisation-longue"], palier, prerequis, None,
        contenu, {"valeur": str(nombres[sondage])}, date_creation,
    )


# --- Thème « concentration » ------------------------------------------------------


def _chaine(rng, palier, nb_ops, borne, nn, prerequis, date_creation):
    """Chaîne d'additions/soustractions évaluée de gauche à droite.

    La longueur croissante (3 → 7 opérations) augmente la charge de mémoire de
    travail : le total courant doit être maintenu de tête, sans rien poser.
    """
    courant = rng.randrange(2, borne + 1)
    morceaux = [str(courant)]
    for _ in range(nb_ops):
        peut_soustraire = courant >= 5
        if peut_soustraire and rng.random() < 0.5:
            valeur = rng.randrange(2, min(borne, courant - 2) + 1)
            courant -= valeur
            morceaux.append(f"− {valeur}")
        else:
            valeur = rng.randrange(2, borne + 1)
            courant = min(courant + valeur, 300)
            morceaux.append(f"+ {valeur}")
    cap = CAP_CHAINE_7 if nb_ops >= 7 else None
    contenu = {
        "enonce": " ".join(morceaux),
        "aide": "Calcule de gauche à droite, étape par étape.",
    }
    return _item(
        f"co-{palier}-chaine-{nn:02d}", "chaine-calcul", "concentration",
        ["attention-soutenue", "memoire-travail"], palier, prerequis, cap,
        contenu, {"valeur": courant}, date_creation,
    )


def _cascade(rng, palier, nn, prerequis, date_creation):
    """Cascade de soustractions : départ moins un pas fixe, répété cinq fois."""
    depart = rng.randrange(60, 100)
    pas = rng.randrange(3, 10)
    expression = str(depart) + " " + " ".join([f"− {pas}"] * 5)
    contenu = {
        "enonce": expression,
        "aide": "Retranche toujours le même nombre — garde le rythme.",
    }
    return _item(
        f"co-{palier}-cascade-{nn:02d}", "chaine-calcul", "concentration",
        ["attention-soutenue", "automatisation"], palier, prerequis, None,
        contenu, {"valeur": depart - pas * 5}, date_creation,
    )


def _double_tache(rng, palier, nb_elements, variante, nn, prerequis, date_creation):
    """Double tâche de filtrage : suite mêlant lettres et chiffres.

    Le stimulus est affiché temporisé ; selon la variante, l'utilisateur doit
    retrouver la somme des chiffres ou compter les lettres — attention divisée
    et sélective sous charge.
    """
    nb_chiffres = max(2, nb_elements // 3)
    # Positions des chiffres : jamais deux chiffres consécutifs.
    positions = sorted(rng.sample(range(nb_elements), nb_chiffres))
    while any(b - a == 1 for a, b in zip(positions, positions[1:])):
        positions = sorted(rng.sample(range(nb_elements), nb_chiffres))

    elements: list[str] = []
    chiffres: list[str] = []
    lettres: list[str] = []
    for position in range(nb_elements):
        if position in positions:
            chiffre = str(rng.randrange(1, 10))
            elements.append(chiffre)
            chiffres.append(chiffre)
        else:
            lettre = rng.choice(LETTRES_DOUBLE)
            elements.append(lettre)
            lettres.append(lettre)

    if variante == "somme":
        consigne = ("Tu verras une suite mêlant lettres et chiffres : "
                    "prépare-toi à additionner les chiffres.")
        enonce = "Quelle était la somme des chiffres ?"
        reponse = sum(int(chiffre) for chiffre in chiffres)
    else:  # compte
        consigne = ("Tu verras une suite mêlant lettres et chiffres : "
                    "prépare-toi à compter les lettres.")
        enonce = "Combien de lettres y avait-il ?"
        reponse = len(lettres)

    contenu = {
        "consigne": consigne,
        "affichage": {
            "mode": "sequence",
            "duree_par_item_ms": 1000,
            "elements": elements,
        },
        "enonce": enonce,
        "aide": None,
    }
    return _item(
        f"co-{palier}-double-{nn:02d}", "double-tache", "concentration",
        ["attention-divisee", "attention-selective"], palier, prerequis, None,
        contenu, {"valeur": reponse}, date_creation,
    )


def _serie(rng, palier, regle, nn, prerequis, date_creation):
    """Série à règle : trouver le nombre manquant (arithmétique/géométrique/alternée)."""
    if regle == "arithmetique":
        depart = rng.randrange(2, 31)
        pas = rng.randrange(2, 10)
        termes = [depart + pas * i for i in range(5)]
        index_manquant = rng.choice([1, 2])
    elif regle == "geometrique":
        depart = rng.randrange(1, 7)
        ratio = rng.choice([2, 3])
        termes = [depart * ratio ** i for i in range(5)]
        index_manquant = rng.choice([1, 2])
    else:  # alternee : +a puis +b, en alternance
        depart = rng.randrange(2, 16)
        pas_a, pas_b = rng.sample(range(1, 6), 2)
        termes = [depart]
        for i in range(5):
            termes.append(termes[-1] + (pas_a if i % 2 == 0 else pas_b))
        index_manquant = rng.choice([3, 4])

    affichage = ", ".join(
        "__" if i == index_manquant else str(terme)
        for i, terme in enumerate(termes)
    )
    contenu = {
        "enonce": f"{affichage} — quel nombre manque ?",
        "aide": "Cherche la règle de la suite.",
    }
    return _item(
        f"co-{palier}-serie-{nn:02d}", "serie-manquante", "concentration",
        ["memoire-travail", "vitesse-traitement"], palier, prerequis, None,
        contenu, {"valeur": termes[index_manquant]}, date_creation,
    )


# --- Composition des paliers ------------------------------------------------------


def _paliers_memoire(rng, date_creation):
    """Construit les 8 paliers du thème « memoire » (18 items chacun)."""
    paliers = []
    compositions = [
        # (nb, type, paramètres) — voir spec .cluster/enrichissement/spec.md
        [("empan", {"longueur": 3, "envers": False})] * 18,
        [("empan", {"longueur": 4, "envers": False})] * 18,
        [("empan", {"longueur": 5, "envers": False})] * 10
        + [("paires", {"nb_paires": 2})] * 8,
        [("empan", {"longueur": 3, "envers": True})] * 9
        + [("empan", {"longueur": 6, "envers": False})] * 9,
        [("empan", {"longueur": 4, "envers": True})] * 10
        + [("nback", {"pas": 2})] * 8,
        [("empan", {"longueur": 5, "envers": True})] * 9
        + [("paires", {"nb_paires": 3})] * 9,
        [("empan", {"longueur": 6, "envers": True})] * 8
        + [("nback", {"pas": 3})] * 10,
        [("paires", {"nb_paires": 4})] * 8 + [("nback", {"pas": 4})] * 10,
        # Paliers 9 à 12 — empan de mots (matériel verbal, même logique que les chiffres).
        [("mots", {"longueur": 3, "envers": False})] * 18,
        [("mots", {"longueur": 4, "envers": False})] * 18,
        [("mots", {"longueur": 5, "envers": False})] * 18,
        [("mots", {"longueur": 3, "envers": True})] * 9
        + [("mots", {"longueur": 4, "envers": True})] * 9,
    ]
    compteurs: dict[str, int] = {}
    for numero, composition in enumerate(compositions, start=1):
        prerequis = [] if numero == 1 else [f"me-palier-{numero - 1}"]
        items = []
        for famille, parametres in composition:
            compteurs[famille] = compteurs.get(famille, 0) + 1
            nn = compteurs[famille]
            if famille == "empan":
                items.append(_empan(rng, numero, parametres["longueur"],
                                    parametres["envers"], nn, prerequis, date_creation))
            elif famille == "mots":
                items.append(_empan_mots(rng, numero, parametres["longueur"],
                                         parametres["envers"], nn, prerequis, date_creation))
            elif famille == "paires":
                items.append(_paires(rng, numero, parametres["nb_paires"],
                                     nn, prerequis, date_creation))
            else:
                items.append(_nback(rng, numero, parametres["pas"],
                                    nn, prerequis, date_creation))
        paliers.append(items)
    return paliers


def _paliers_concentration(rng, date_creation):
    """Construit les 9 paliers du thème « concentration » (18 items chacun)."""
    paliers = []
    compositions = [
        [("chaine", {"nb_ops": 3, "borne": 20})] * 18,
        [("chaine", {"nb_ops": 4, "borne": 20})] * 18,
        [("cascade", {})] * 18,
        [("double", {"nb_elements": 5, "variante": "somme"})] * 18,
        [("chaine", {"nb_ops": 5, "borne": 30})] * 12
        + [("serie", {"regle": "arithmetique"})] * 6,
        [("double", {"nb_elements": 7, "variante": "somme"})] * 9
        + [("double", {"nb_elements": 7, "variante": "compte"})] * 9,
        [("chaine", {"nb_ops": 6, "borne": 40})] * 12
        + [("serie", {"regle": "geometrique"})] * 6,
        [("chaine", {"nb_ops": 7, "borne": 50})] * 12
        + [("double", {"nb_elements": 9, "variante": "somme"})] * 6,
        [("chaine", {"nb_ops": 7, "borne": 60})] * 9
        + [("serie", {"regle": "alternee"})] * 9,
    ]
    compteurs: dict[str, int] = {}
    for numero, composition in enumerate(compositions, start=1):
        prerequis = [] if numero == 1 else [f"co-palier-{numero - 1}"]
        items = []
        for famille, parametres in composition:
            compteurs[famille] = compteurs.get(famille, 0) + 1
            nn = compteurs[famille]
            if famille == "chaine":
                items.append(_chaine(rng, numero, parametres["nb_ops"],
                                     parametres["borne"], nn, prerequis, date_creation))
            elif famille == "cascade":
                items.append(_cascade(rng, numero, nn, prerequis, date_creation))
            elif famille == "double":
                items.append(_double_tache(rng, numero, parametres["nb_elements"],
                                           parametres["variante"], nn, prerequis,
                                           date_creation))
            else:
                items.append(_serie(rng, numero, parametres["regle"],
                                    nn, prerequis, date_creation))
        paliers.append(items)
    return paliers


# --- Manifests et écriture ---------------------------------------------------------


def _manifest(theme: str, prefixe: str, descriptions: list[str],
              paliers: list[list[dict]]) -> dict:
    """Manifest ordonné d'un thème (id, description, prerequis, fichier, nb_items)."""
    entrees = []
    for numero, items in enumerate(paliers, start=1):
        entrees.append({
            "id": f"{prefixe}-palier-{numero}",
            "description": descriptions[numero - 1],
            "prerequis": [] if numero == 1 else [f"{prefixe}-palier-{numero - 1}"],
            "fichier": f"paliers/palier-{numero:02d}.json",
            "nb_items": len(items),
        })
    return {"theme": theme, "paliers": entrees}


DESCRIPTIONS_MEMOIRE = [
    "Empan 3 chiffres, endroit",
    "Empan 4 chiffres, endroit",
    "Empan 5 + premières paires mot–nombre",
    "Empan envers 3, endroit 6",
    "Envers 4 + sonde n-back (pas 2)",
    "Envers 5 + paires 3",
    "Envers 6 + sonde n-back (pas 3)",
    "Paires 4 + sonde n-back (pas 4)",
    "Empan de mots 3, endroit",
    "Empan de mots 4, endroit",
    "Empan de mots 5, endroit",
    "Empan de mots envers 3 et 4",
]

DESCRIPTIONS_CONCENTRATION = [
    "Chaîne de 3 opérations",
    "Chaîne de 4 opérations",
    "Cascade de soustractions",
    "Double tâche : somme des chiffres",
    "Chaîne de 5 + premières séries",
    "Double tâche 7 éléments",
    "Chaîne de 6 + séries géométriques",
    "Chaîne de 7 + double tâche 9",
    "Chaînes longues et séries alternées",
]


def _ecrire_json(chemin: Path, donnees) -> None:
    """Écriture JSON UTF-8 lisible (parents créés si besoin)."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8") as flux:
        json.dump(donnees, flux, ensure_ascii=False, indent=2)
        flux.write("\n")


def main() -> int:
    """Point d'entrée : génère les paliers et manifests des deux thèmes."""
    parseur = argparse.ArgumentParser(
        description="Génère les items « memoire » et « concentration » (sprint 2)."
    )
    parseur.add_argument("--dry-run", action="store_true",
                         help="affiche le plan sans écrire de fichier")
    parseur.add_argument("--date", default=DATE_CREATION_DEFAUT,
                         help="date_creation (meta), AAAA-MM-JJ (défaut : %(default)s)")
    options = parseur.parse_args()

    rng = random.Random(GRAINE)
    memoire = _paliers_memoire(rng, options.date)
    concentration = _paliers_concentration(rng, options.date)

    cibles: dict[Path, object] = {}
    for numero, items in enumerate(memoire, start=1):
        cibles[BASE_SORTIE / "memoire" / "paliers" / f"palier-{numero:02d}.json"] = items
    cibles[BASE_SORTIE / "memoire" / "paliers.json"] = _manifest(
        "memoire", "me", DESCRIPTIONS_MEMOIRE, memoire
    )
    for numero, items in enumerate(concentration, start=1):
        cibles[BASE_SORTIE / "concentration" / "paliers" / f"palier-{numero:02d}.json"] = items
    cibles[BASE_SORTIE / "concentration" / "paliers.json"] = _manifest(
        "concentration", "co", DESCRIPTIONS_CONCENTRATION, concentration
    )

    for chemin in sorted(cibles):
        donnees = cibles[chemin]
        taille = len(donnees) if isinstance(donnees, list) else len(donnees["paliers"])
        relatif = chemin.relative_to(RACINE_DEPOT)
        if options.dry_run:
            print(f"[simulation] {relatif} ({taille} entrées)")
        else:
            _ecrire_json(chemin, donnees)
            print(f"[écrit] {relatif} ({taille} entrées)")

    total = sum(len(items) for items in memoire + concentration)
    print(f"Total : {len(memoire)} paliers mémoire, {len(concentration)} paliers "
          f"concentration, {total} items.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
