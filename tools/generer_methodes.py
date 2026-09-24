#!/usr/bin/env python3
"""Génère le thème « methodes » — méthodes et stratégies (remédiation).

Trois méthodes orthophoniques / neuropsychologiques, appliquées à des tâches :

- ``pqrst`` — mémoire de textes : on lit un court texte avec une méthode
  (Parcourir, Question, Lire, énoncer, Tester) puis on répond à une question ;
- ``but-etapes`` — Goal Management Training : choisir le but, puis le plan
  d'étapes correct (et « vérifier » son plan) ;
- ``auto-instruction`` — auto-instruction (Meichenbaum) : quelle question se
  poser d'abord, puis quelle action en découle.

Toutes les questions sont à choix, pour une correction objective ; la méthode
est rappelée dans la consigne (c'est elle qui est entraînée).

Usage :

    python3 tools/generer_methodes.py            # écrit le contenu
    python3 tools/generer_methodes.py --dry-run  # affiche un résumé
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
BASE_SORTIE = RACINE_DEPOT / "content" / "entrainement" / "methodes"

GRAINE: int = 20260924
DATE_CREATION: str = "2026-09-24"
AUTEUR: str = "redaction-assistee (tools/generer_methodes.py)"

_RNG_FAMILLES: dict[str, random.Random] = {}


def melanger(famille: str, options: list) -> None:
    rng = _RNG_FAMILLES.setdefault(famille, random.Random(f"{GRAINE}:{famille}"))
    rng.shuffle(options)


# --- PQRST : mémoire de textes ------------------------------------------------
#: (titre, texte, question, réponse, deux leurres)
TEXTES_PQRST = [
    ("Le rendez-vous chez le dentiste",
     "Le rendez-vous est fixé au mardi 12 mars à 15 h. Le cabinet se trouve au deuxième étage, "
     "sans ascenseur. Il faut apporter la carte de mutuelle et arriver dix minutes avant.",
     "À quelle heure est le rendez-vous ?", "15 h", ["12 h", "16 h"]),
    ("La sortie au marché",
     "Le marché a lieu le samedi matin, place de l'église. Les producteurs arrivent vers 7 h et "
     "repartent à 13 h. Le stationnement est gratuit jusqu'à 11 h.",
     "Quand les producteurs repartent-ils ?", "à 13 h", ["à 7 h", "à 11 h"]),
    ("La réparation de la chaudière",
     "Le technicien passera jeudi entre 9 h et 11 h. Il faut dégager l'accès au sous-sol et "
     "laisser le portail ouvert. Le devis est de 180 euros.",
     "Que faut-il laisser ouvert ?", "le portail", ["la fenêtre", "la cave"]),
    ("Le covoiturage",
     "Le départ est prévu à 8 h 15 devant la gare. La voiture est bleue et il reste deux places. "
     "Le trajet dure environ une heure.",
     "Combien de places restent ?", "deux", ["trois", "une"]),
    ("L'inscription à la piscine",
     "L'inscription se fait le mercredi après-midi, au guichet du premier étage. Il faut un "
     "certificat médical et une photo. Les cours commencent la semaine suivante.",
     "Où se fait l'inscription ?", "au guichet du premier étage", ["à l'accueil du rez-de-chaussée", "au bord du bassin"]),
    ("Le colis en attente",
     "Le colis est arrivé lundi et sera gardé sept jours au point relais. Il se trouve au "
     "tabac de la place. Il faut présenter une pièce d'identité.",
     "Combien de temps le colis est-il gardé ?", "sept jours", ["trois jours", "un mois"]),
]

# --- GMT : but, étapes, vérification -----------------------------------------
#: (situation, plan correct, deux plans incorrects)
PLANS_GMT = [
    ("Tu veux inviter des amis à dîner samedi soir.",
     "Choisir le menu, vérifier les ingrédients, faire les courses, puis cuisiner",
     ["Cuisiner, puis décider du menu", "Attendre samedi et improviser"]),
    ("Tu dois déménager dans deux semaines.",
     "Lister les affaires par pièce, réserver le camion, emballer, puis transporter",
     ["Transporter d'abord, emballer ensuite", "Tout faire la veille du départ"]),
    ("Tu prépares un dossier pour un logement.",
     "Lire la liste des pièces demandées, rassembler les documents, puis déposer le dossier",
     ["Déposer le dossier vide", "Écrire une lettre d'abord"]),
    ("Tu veux repeindre la cuisine.",
     "Protéger les meubles, préparer les murs, peindre, puis ranger",
     ["Peindre, puis protéger les meubles", "Commencer par ranger le matériel"]),
    ("Tu organises un week-end avec un ami.",
     "Choisir les dates, réserver le logement, puis préparer les affaires",
     ["Préparer la valise avant de choisir les dates", "Partir sans rien réserver"]),
    ("Tu dois rendre un dossier administratif avant vendredi.",
     "Vérifier la date limite, remplir le formulaire, joindre les pièces, puis envoyer",
     ["Envoyer un dossier incomplet", "Attendre le dernier jour pour commencer"]),
    ("Tu veux préparer une soupe pour la semaine.",
     "Lister les légumes, faire les courses, cuisiner, puis répartir en portions",
     ["Cuisiner sans avoir les légumes", "Acheter au hasard"]),
    ("Tu décides de reprendre le sport.",
     "Choisir une activité, fixer un créneau, prévoir une tenue, puis commencer doucement",
     ["Acheter tout l'équipement avant de choisir l'activité", "Attendre d'être motivé"]),
]

# --- Auto-instruction (Meichenbaum) ------------------------------------------
#: (tâche, première question à se poser, deux questions moins utiles)
AUTO_INSTRUCTION = [
    ("Tu ouvres une boîte de médicaments avec une notice.",
     "Qu'est-ce que je dois faire exactement, et dans quel ordre ?",
     ["Est-ce que je vais y arriver ?", "Combien de temps ça va me prendre ?"]),
    ("Tu reçois un courrier administratif que tu ne comprends pas.",
     "De quoi parle ce courrier, et qu'attend-on de moi ?",
     ["Pourquoi m'envoie-t-on toujours des papiers ?", "Ai-je déjà vu ça ?"]),
    ("Tu commences un nouveau livre.",
     "De quoi parle-t-il, et qu'est-ce que je cherche à retenir ?",
     ["Combien de pages il reste ?", "Est-ce que je vais aimer ?"]),
    ("Tu dois remplir un formulaire de plusieurs pages.",
     "Par quoi je commence, et que me faut-il sous les yeux ?",
     ["Est-ce que je vais me tromper ?", "Est-ce long ?"]),
    ("Tu prépares un repas jamais essayé.",
     "Quelles sont les étapes, et ai-je tout ce qu'il faut ?",
     ["Est-ce que ce sera bon ?", "Ai-je le temps ?"]),
    ("Tu ranges une pièce en désordre.",
     "Qu'est-ce que je veux obtenir, et par quel coin je commence ?",
     ["Où tout cela va-t-il aller ?", "Est-ce que c'est fini bientôt ?"]),
    ("Tu appelles pour un problème de facture.",
     "Quel est mon problème, et quel résultat je veux obtenir ?",
     ["Vont-ils me croire ?", "Combien de temps ça va durer ?"]),
    ("Tu dois réviser un texte pour le lendemain.",
     "Qu'est-ce que je dois savoir dire, et comment je vais le vérifier ?",
     ["Est-ce que je vais retenir ?", "Ai-je tout lu ?"]),
]


def _item_choix(famille: str, palier: int, numero: int, type_item: str,
                prerequis: list[str], bonne: str, leurres: list[str],
                consigne: str, enonce: str, aide: str,
                fonctions: list[str], extra: dict | None = None) -> dict:
    options = [bonne] + list(leurres)
    melanger(famille, options)
    contenu = {
        "consigne": consigne,
        "enonce": enonce,
        "options": options,
        "aide": aide,
    }
    if extra:
        contenu.update(extra)
    return {
        "id": f"mt-{palier}-{famille}-{numero:02d}",
        "type": type_item,
        "module": "entrainement",
        "theme": "methodes",
        "fonctions_ciblees": fonctions,
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": contenu,
        "reponse": {"valeur": bonne},
        "meta": {
            "auteur": AUTEUR,
            "date_creation": DATE_CREATION,
            "relecture_ortho": {"statut": "a_revoir"},
        },
    }


def construire_paliers() -> list[list[dict]]:
    paliers: list[list[dict]] = []

    # Palier 1 — PQRST : lire avec une méthode, puis répondre de mémoire.
    items = []
    for numero, (titre, texte, question, bonne, leurres) in enumerate(TEXTES_PQRST, start=1):
        items.append(_item_choix(
            "pqrst", 1, numero, "pqrst", [],
            bonne, leurres,
            "Méthode PQRST : Parcours le texte, pose-toi une question, Lis-le, reformule-le pour toi, "
            "puis Teste-toi en répondant de mémoire (le texte est caché).",
            question,
            "Reformule le texte en une phrase avant de répondre.",
            ["memorisation-longue", "recuperation"],
            extra={"affichage": {"mode": "texte", "duree_totale_ms": 25000, "elements": [texte]}} ,
        ))
    paliers.append(items)

    # Palier 2 — Goal Management Training : le but, puis le plan.
    items = []
    for numero, (situation, bonne, leurres) in enumerate(PLANS_GMT, start=1):
        items.append(_item_choix(
            "gmt", 2, numero, "but-etapes", ["mt-palier-1"],
            bonne, leurres,
            "Goal Management Training : pose d'abord ton but, puis choisis le plan d'étapes cohérent, "
            "et vérifie-le avant de te lancer.",
            situation,
            "Un bon plan met d'abord ce qui rend la suite possible.",
            ["planification", "fonctions-executives"],
        ))
    paliers.append(items)

    # Palier 3 — Auto-instruction : la question à se poser d'abord.
    items = []
    for numero, (tache, bonne, leurres) in enumerate(AUTO_INSTRUCTION, start=1):
        items.append(_item_choix(
            "autoinstruction", 3, numero, "auto-instruction", ["mt-palier-2"],
            bonne, leurres,
            "Auto-instruction : avant d'agir, mets-toi une consigne à voix basse — "
            "« qu'est-ce que je dois faire ? » puis « comment ? » puis « vérifie ».",
            tache,
            "La première question porte sur le but et le moyen, pas sur le résultat attendu.",
            ["fonctions-executives", "planification"],
        ))
    paliers.append(items)

    return paliers


def _manifest(paliers: list[list[dict]]) -> dict:
    descriptions = [
        "PQRST : lire un texte avec une méthode, puis répondre de mémoire",
        "Goal Management Training : choisir le but et le plan d'étapes",
        "Auto-instruction : quelle question se poser avant d'agir",
    ]
    return {
        "theme": "methodes",
        "paliers": [
            {
                "id": f"mt-palier-{numero}",
                "description": descriptions[numero - 1],
                "prerequis": [] if numero == 1 else [f"mt-palier-{numero - 1}"],
                "fichier": f"paliers/palier-{numero:02d}.json",
                "nb_items": len(items),
            }
            for numero, items in enumerate(paliers, start=1)
        ],
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le thème « methodes ».")
    parseur.add_argument("--dry-run", action="store_true", help="afficher sans écrire")
    options = parseur.parse_args()

    paliers = construire_paliers()
    cibles = {BASE_SORTIE / "paliers.json": _manifest(paliers)}
    for numero, items in enumerate(paliers, start=1):
        cibles[BASE_SORTIE / "paliers" / f"palier-{numero:02d}.json"] = items

    total = 0
    for chemin, donnees in cibles.items():
        nb = len(donnees["paliers"]) if isinstance(donnees, dict) else len(donnees)
        if isinstance(donnees, list):
            total += nb
        if options.dry_run:
            print(f"[dry-run] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
        else:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"[écrit] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
    print(f"Total : {total} items, {len(paliers)} paliers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
