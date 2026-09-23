#!/usr/bin/env python3
"""Génère le thème « quotidien » — remédiation fonctionnelle (sprint 6).

Contrairement aux épreuves d'évaluation (empan, n-back, séries…), ces exercices
travaillent la fonction **altérée dans des situations de vie**, avec une
stratégie enseignée par la consigne (voir docs/10-clinique/remediation.md) :

- ``prise-message`` (mémoire de travail fonctionnelle) : retenir qui / quoi /
  quand le temps d'agir, puis répondre à une question ciblée ;
- ``etape-suivante`` (planification) : choisir la prochaine étape d'une tâche ;
- ``estimation-temps`` (anticipation / gestion du temps) : estimer une durée,
  acceptée dans une fourchette (une estimation n'est pas une mesure exacte).

Le contenu est rédigé puis assemblé de façon déterministe : seules les positions
des propositions sont mélangées avec un générateur isolé par famille.

Usage :

    python3 tools/generer_quotidien.py            # écrit le contenu
    python3 tools/generer_quotidien.py --dry-run  # affiche un résumé
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
BASE_SORTIE = RACINE_DEPOT / "content" / "entrainement" / "quotidien"

GRAINE: int = 20260923
DATE_CREATION: str = "2026-09-23"
AUTEUR: str = "redaction-assistee (tools/generer_quotidien.py)"

#: Générateurs isolés par famille (règle : docs/30-technique/contenu-versionne.md).
_RNG_FAMILLES: dict[str, random.Random] = {}


def melanger(famille: str, options: list) -> None:
    """Mélange l'ordre des propositions avec le générateur isolé de la famille."""
    rng = _RNG_FAMILLES.setdefault(famille, random.Random(f"{GRAINE}:{famille}"))
    rng.shuffle(options)


def _meta() -> dict:
    return {
        "auteur": AUTEUR,
        "date_creation": DATE_CREATION,
        "relecture_ortho": {"statut": "a_revoir"},
    }


# --- Mémoire de travail fonctionnelle : prise de message ----------------------
#: (message affiché, question, réponse attendue, fait de rappel en clair)
PRISE_MESSAGE = [
    ("Le cabinet médical a appelé : le rendez-vous de jeudi est avancé à 14 h 30.",
     "À quelle heure est le rendez-vous ?", "14 h 30", "l'heure"),
    ("Maman a laissé un message : achète du pain, deux bouteilles de lait et six œufs.",
     "Combien de bouteilles de lait ?", "deux", "une quantité"),
    ("La pharmacie ferme à 19 h le samedi et rouvre le lundi matin.",
     "Quand la pharmacie rouvre-t-elle ?", "le lundi matin", "le jour"),
    ("Le plombier passera mardi entre 8 h et 10 h ; il faut laisser la porte de la cave ouverte.",
     "Que faut-il laisser ouvert ?", "la porte de la cave", "un détail à retenir"),
    ("Ta sœur rappelle qu'il faut prendre le train de 16 h 42, pas celui de 17 h.",
     "Quel train faut-il prendre ?", "16 h 42", "l'horaire"),
    ("Le voisin a déposé un colis au troisième étage, chez la gardienne.",
     "Où est le colis ?", "chez la gardienne", "le lieu"),
    ("Le médecin a demandé de refaire la prise de sang vendredi, à jeun.",
     "Quand faut-il refaire la prise de sang ?", "vendredi", "le jour"),
    ("Le garagiste annonce que la voiture sera prête jeudi soir, autour de 18 h.",
     "Quand la voiture sera-t-elle prête ?", "jeudi soir", "le jour"),
    ("L'orthophoniste propose de décaler la séance au mardi 10 h au lieu du jeudi.",
     "Quel jour est proposé pour la nouvelle séance ?", "mardi", "le jour"),
    ("Le livreur passera demain ; il faut un code à quatre chiffres pour la porte : 4721.",
     "Quel est le code de la porte ?", "4721", "le code"),
    ("La boulangère te rappelle que la commande de dix croissants est prête depuis midi.",
     "Combien de croissants sont commandés ?", "dix", "une quantité"),
    ("La banque signale un rendez-vous conseiller le 3 du mois prochain, à 11 h 15.",
     "À quelle date est le rendez-vous ?", "le 3 du mois prochain", "la date"),
]


# --- Planification : l'étape suivante -----------------------------------------
#: (situation, étape suivante correcte, deux leurres)
ETAPE_SUIVANTE = [
    ("Tu veux préparer un repas pour deux. Les ingrédients sont posés sur le plan de travail.",
     "Préchauffer le four", ["Servir à table", "Ranger les courses"]),
    ("Tu dois renouveler une ordonnance. Le médecin vient de te la remettre.",
     "Aller à la pharmacie avec l'ordonnance", ["Jeter les anciennes boîtes", "Rappeler le médecin pour redemander"]),
    ("Tu organises une sortie au marché samedi. Tu as noté la liste des achats.",
     "Préparer un sac ou un cabas", ["Payer à la caisse", "Ranger les achats en rentrant"]),
    ("Tu veux prendre rendez-vous chez le coiffeur. Tu as le numéro sous les yeux.",
     "Appeler et proposer un créneau", ["Couper les cheveux", "Choisir une nouvelle coupe"]),
    ("Tu viens de vider le lave-vaisselle. Les assiettes sont sur la table.",
     "Ranger les assiettes dans le placard", ["Lancer une nouvelle machine", "Mettre la table pour le soir"]),
    ("Tu prépares ta valise pour deux jours. Les vêtements sont sortis de l'armoire.",
     "Plier et ranger les vêtements dans la valise", ["Fermer la valise", "Appeler le taxi"]),
    ("Tu reçois un courrier de la mairie demandant un justificatif. Tu as trouvé le document.",
     "Faire une copie du justificatif", ["Poster l'enveloppe", "Ranger le courrier"]),
    ("Tu veux réserver une table pour vendredi. Tu es devant le site du restaurant.",
     "Choisir le nombre de personnes et l'heure", ["Commander le menu", "Aller au restaurant"]),
    ("Tu dois arroser les plantes. L'arrosoir est vide.",
     "Remplir l'arrosoir", ["Vider l'eau des soucoupes", "Ranger l'arrosoir"]),
    ("Tu prépares un gâteau. La recette est ouverte et les œufs sont sortis.",
     "Casser les œufs dans le saladier", ["Sortir le gâteau du four", "Couper des parts"]),
    ("Tu veux envoyer un colis. Le colis est fermé mais pas encore adressé.",
     "Écrire l'adresse sur le colis", ["Le déposer au bureau de poste", "Ouvrir le colis"]),
    ("Tu planifies ta matinée. Le réveil est réglé à 8 h.",
     "Préparer les vêtements la veille", ["Prendre le petit-déjeuner", "Partir à l'heure"]),
]


# --- Anticipation : estimer une durée -----------------------------------------
#: (situation, durée attendue en minutes, fourchette [min, max] acceptée)
ESTIMATION_TEMPS = [
    ("Aller à pied à la boulangerie du coin (à 500 mètres).", 10, [3, 25]),
    ("Prendre une douche complète.", 15, [5, 30]),
    ("Remplir un formulaire administratif de deux pages.", 20, [5, 45]),
    ("Préparer un repas simple : pâtes et sauce.", 25, [10, 50]),
    ("Descendre les poubelles au local.", 5, [1, 15]),
    ("Étendre une lessive.", 10, [3, 25]),
    ("Faire les courses pour deux ou trois jours.", 40, [15, 75]),
    ("Réserver un billet de train en ligne.", 10, [3, 25]),
    ("Nettoyer la salle de bain.", 30, [10, 60]),
    ("Prendre un rendez-vous par téléphone.", 5, [1, 15]),
    ("Préparer un courrier avec une enveloppe et un timbre.", 8, [2, 20]),
    ("Aller à la pharmacie et revenir (10 minutes à pied).", 20, [8, 40]),
]


# --- Assemblage ---------------------------------------------------------------


def _item_prise_message(numero: int, palier: int, prerequis: list[str]) -> dict:
    message, question, attendue, _rappel = PRISE_MESSAGE[numero - 1]
    return {
        "id": f"qo-{palier}-message-{numero:02d}",
        "type": "prise-message",
        "module": "entrainement",
        "theme": "quotidien",
        "fonctions_ciblees": ["memoire-travail", "recuperation"],
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": {
            "consigne": "Lis le message, puis réponds de mémoire. Astuce : retiens qui, quoi et quand — tu peux te le répéter dans ta tête.",
            "affichage": {
                "mode": "liste",
                "duree_totale_ms": 12000,
                "elements": [[message]],
            },
            "enonce": question,
            "aide": "Regroupe les informations : qui ? quoi ? quand ? où ?",
        },
        "reponse": {"valeur": attendue},
        "meta": _meta(),
    }


def _item_etape(numero: int, palier: int, prerequis: list[str]) -> dict:
    situation, bonne, leurres = ETAPE_SUIVANTE[numero - 1]
    options = [bonne] + list(leurres)
    melanger("etape-suivante", options)
    return {
        "id": f"qo-{palier}-etape-{numero:02d}",
        "type": "etape-suivante",
        "module": "entrainement",
        "theme": "quotidien",
        "fonctions_ciblees": ["planification", "fonctions-executives"],
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": {
            "consigne": "Choisis la prochaine étape. Astuce : demande-toi ce qui doit venir AVANT le reste.",
            "enonce": situation,
            "options": options,
            "aide": "Pense à l'ordre logique : que faut-il faire d'abord pour que la suite soit possible ?",
        },
        "reponse": {"valeur": bonne},
        "meta": _meta(),
    }


def _item_estimation(numero: int, palier: int, prerequis: list[str]) -> dict:
    situation, duree, intervalle = ESTIMATION_TEMPS[numero - 1]
    return {
        "id": f"qo-{palier}-temps-{numero:02d}",
        "type": "estimation-temps",
        "module": "entrainement",
        "theme": "quotidien",
        "fonctions_ciblees": ["planification", "vitesse-traitement"],
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": {
            "consigne": "Estime le temps nécessaire, en minutes. Astuce : compare avec une fois où tu l'as déjà fait.",
            "enonce": situation,
            "aide": "Une estimation, pas une mesure exacte : une fourchette large est acceptée.",
        },
        "reponse": {"valeur": duree, "intervalle": intervalle},
        "meta": _meta(),
    }


# --- Initiation / planification : par où commencer ----------------------------
#: (situation, première action adaptée, deux leurres)
PAR_OU_COMMENCER = [
    ("Tu dois ranger l'appartement avant l'arrivée d'un invité.",
     "Ranger une pièce à la fois, en commençant par la plus visible",
     ["Passer d'une pièce à l'autre au hasard", "Acheter de nouvelles étagères"]),
    ("Tu prépares un dossier pour une demande d'aide.",
     "Lister d'abord les documents demandés",
     ["Rédiger la lettre sans savoir quoi joindre", "Attendre la date limite"]),
    ("Tu organises un déménagement dans un mois.",
     "Faire une liste des choses à faire et la classer par échéance",
     ["Tout faire le dernier jour", "Espérer que ça se fasse tout seul"]),
    ("Tu reprends un projet laissé de côté depuis des semaines.",
     "Relire où tu t'étais arrêté",
     ["Recommencer depuis le début", "Le laisser encore de côté"]),
    ("Tu prépares un repas pour six personnes.",
     "Vérifier les ingrédients et les quantités",
     ["Allumer le four sans savoir quoi cuisiner", "Dresser la table d'abord"]),
    ("Tu veux te remettre à une activité physique.",
     "Choisir une activité simple et un créneau fixe",
     ["Acheter tout l'équipement avant de commencer", "Attendre d'être en forme"]),
    ("Tu as trois papiers administratifs à traiter.",
     "Traiter d'abord celui dont l'échéance est la plus proche",
     ["Les empiler et ne plus y toucher", "Tout faire en même temps"]),
    ("Tu dois appeler pour faire une réclamation.",
     "Noter en trois mots ce que tu veux dire avant d'appeler",
     ["Appeler sans préparation", "Repousser l'appel"]),
    ("Tu prépares un déplacement de deux jours.",
     "Réserver le trajet et l'hébergement d'abord",
     ["Choisir d'abord ce que tu mettras dans la valise", "Partir sans rien réserver"]),
    ("Tu veux ranger les papiers de la maison.",
     "Créer des dossiers par thème et tout y ranger",
     ["Tout mettre dans un même carton", "Jeter sans trier"]),
    ("Tu as un rendez-vous important demain matin.",
     "Préparer les papiers et le trajet la veille",
     ["Tout improviser le matin", "Annuler le rendez-vous"]),
    ("Tu dois réparer un objet cassé.",
     "Chercher la notice ou un tutoriel avant de démonter",
     ["Démonter sans regarder comment c'est fait", "Le jeter directement"]),
]


# --- Mémoire prospective : implémentation d'intention (« si … alors … ») --------
#: (chose à se rappeler de faire, plan « si-alors » efficace, deux leurres)
SI_ALORS = [
    ("Prendre ton traitement le soir.",
     "Quand je me brosserai les dents, je prendrai le traitement",
     ["J'essaierai d'y penser", "Je le prendrai si j'y pense"]),
    ("Rendre un livre à la bibliothèque.",
     "Quand je sortirai avec mon sac, je mettrai le livre dedans",
     ["J'essaierai de m'en souvenir", "Je le rendrai un jour"]),
    ("Arroser les plantes le dimanche.",
     "Le dimanche après le café, j'arrose les plantes",
     ["Je le ferai quand j'aurai le temps", "J'espère ne pas oublier"]),
    ("Répondre à un message important.",
     "Quand je m'installerai après le repas, je répondrai",
     ["Je répondrai plus tard", "Je laisserai le message en attente"]),
    ("Ne pas oublier le four allumé.",
     "Je règle une minuterie dès que j'allume le four",
     ["Je ferai attention", "Je vérifierai de temps en temps"]),
    ("Payer une facture avant le 5.",
     "Quand la facture arrivera, je la paie tout de suite",
     ["Je la paierai à la dernière minute", "Je la classerai pour plus tard"]),
    ("Toujours retrouver tes clés.",
     "Je les pose toujours au même endroit, près de la porte",
     ["Je les poserai où je peux", "Je les chercherai quand j'en aurai besoin"]),
    ("Ne pas manquer le rendez-vous.",
     "Je le note dans le téléphone avec une alarme la veille",
     ["Je m'en souviendrai tout seul", "Je le retiendrai de tête"]),
    ("Rappeler le médecin.",
     "Je programme le rappel dans le téléphone maintenant",
     ["Je rappellerai quand j'y penserai", "J'attendrai qu'on me rappelle"]),
    ("Sortir les poubelles le jeudi soir.",
     "Le jeudi soir après le dîner, je sors les poubelles",
     ["Je les sortirai quand elles seront pleines", "J'attendrai de m'en souvenir"]),
    ("Boire de l'eau dans la journée.",
     "Je remplis une bouteille le matin et je la garde près de moi",
     ["J'essaierai d'y penser", "Je boirai seulement quand j'aurai soif"]),
    ("Ranger après avoir cuisiné.",
     "Je range au fur et à mesure pendant la cuisson",
     ["Je rangerai tout à la fin", "Je laisserai pour demain"]),
]


# --- Résolution de problème : la meilleure solution ---------------------------
#: (problème pratique, meilleure action, deux leurres)
MEILLEURE_SOLUTION = [
    ("La lumière de la salle de bain ne s'allume plus.",
     "Vérifier l'ampoule puis le disjoncteur",
     ["Changer toute l'installation", "Appeler un électricien sans rien vérifier"]),
    ("Tu as oublié un rendez-vous.",
     "Le noter avec une alarme dès maintenant",
     ["Te reprocher de l'avoir oublié", "Ne plus prendre de rendez-vous"]),
    ("Tu ne retrouves plus tes papiers.",
     "Leur créer une place fixe et les y ranger",
     ["Chercher partout à chaque fois", "Les laisser là où ils tombent"]),
    ("Un formulaire te semble compliqué.",
     "Le remplir section par section, et demander de l'aide si besoin",
     ["Le remplir au hasard", "Le laisser de côté"]),
    ("Tu te sens perdu face à plusieurs tâches.",
     "En choisir une, la finir, puis passer à la suivante",
     ["Tout commencer en même temps", "Attendre que ça passe"]),
    ("Le bruit t'empêche de te concentrer.",
     "Réduire les sources de bruit ou faire une pause",
     ["Continuer en s'énervant", "Abandonner la tâche"]),
    ("Tu as du mal à te souvenir des courses.",
     "Écrire une liste et la garder sur toi",
     ["Compter sur ta mémoire", "Acheter au hasard"]),
    ("Un rendez-vous change de jour.",
     "Le noter tout de suite au bon endroit",
     ["Le mémoriser de tête", "S'en occuper plus tard"]),
    ("Une tâche te paraît énorme.",
     "La découper en petites étapes",
     ["La faire d'un seul bloc", "La reporter indéfiniment"]),
    ("Tu te fatigues vite en lisant.",
     "Faire des pauses courtes",
     ["Lire d'une traite jusqu'au bout", "Arrêter de lire"]),
    ("Tu hésites avant de demander un renseignement.",
     "Préparer ta question en une phrase",
     ["Renoncer à demander", "Improviser sans savoir quoi dire"]),
    ("Ton téléphone sonne pendant que tu es occupé.",
     "Le mettre en silencieux et rappeler plus tard",
     ["Répondre en abandonnant ce que tu fais", "Couper le téléphone"]),
]


def _item_choix(numero: int, palier: int, famille: str, type_item: str,
                prerequis: list[str], donnees: list, consigne: str, aide: str,
                fonctions: list[str]) -> dict:
    """Item fonctionnel à choix : la meilleure action/stratégie parmi trois."""
    situation, bonne, leurres = donnees[numero - 1]
    options = [bonne] + list(leurres)
    melanger(famille, options)
    return {
        "id": f"qo-{palier}-{famille}-{numero:02d}",
        "type": type_item,
        "module": "entrainement",
        "theme": "quotidien",
        "fonctions_ciblees": fonctions,
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": {
            "consigne": consigne,
            "enonce": situation,
            "options": options,
            "aide": aide,
        },
        "reponse": {"valeur": bonne},
        "meta": _meta(),
    }


def construire_paliers() -> list[list[dict]]:
    paliers = []
    # Palier 1 — prise de message (mémoire de travail fonctionnelle).
    paliers.append([
        _item_prise_message(n, 1, []) for n in range(1, 13)
    ])
    # Palier 2 — étape suivante (planification).
    paliers.append([
        _item_etape(n, 2, ["qo-palier-1"]) for n in range(1, 13)
    ])
    # Palier 3 — estimation de durée (anticipation).
    paliers.append([
        _item_estimation(n, 3, ["qo-palier-2"]) for n in range(1, 13)
    ])
    # Palier 4 — par où commencer (initiation).
    paliers.append([
        _item_choix(n, 4, "debut", "par-ou-commencer", ["qo-palier-3"],
                    PAR_OU_COMMENCER,
                    "Choisis par où commencer. Astuce : commence par ce qui rend la suite possible.",
                    "Quelle première action débloque toutes les autres ?",
                    ["planification", "fonctions-executives"])
        for n in range(1, 13)
    ])
    # Palier 5 — implémentation d'intention (mémoire prospective).
    paliers.append([
        _item_choix(n, 5, "sialors", "si-alors", ["qo-palier-4"],
                    SI_ALORS,
                    "Choisis le plan « si … alors … » le plus fiable. Astuce : accroche l'action à un moment précis de ta journée.",
                    "Un plan précis, lié à un repère, est plus sûr qu'une bonne intention.",
                    ["memoire-prospective", "planification"])
        for n in range(1, 13)
    ])
    # Palier 6 — meilleure solution (résolution de problème).
    paliers.append([
        _item_choix(n, 6, "solution", "meilleure-solution", ["qo-palier-5"],
                    MEILLEURE_SOLUTION,
                    "Choisis l'action la plus utile. Astuce : commence par ce qui est simple et vérifiable.",
                    "La bonne solution est souvent la plus simple et la plus directe.",
                    ["planification", "fonctions-executives"])
        for n in range(1, 13)
    ])
    return paliers


def _manifest(paliers: list[list[dict]]) -> dict:
    descriptions = [
        "Prendre un message et en retenir les détails (mémoire de travail)",
        "Choisir la prochaine étape d'une tâche (planification)",
        "Estimer le temps nécessaire (anticipation)",
        "Choisir par où commencer (initiation)",
        "Construire un plan « si … alors » pour ne rien oublier (mémoire prospective)",
        "Choisir la meilleure solution à un problème (résolution de problème)",
    ]
    return {
        "theme": "quotidien",
        "paliers": [
            {
                "id": f"qo-palier-{numero}",
                "description": descriptions[numero - 1],
                "prerequis": [] if numero == 1 else [f"qo-palier-{numero - 1}"],
                "fichier": f"paliers/palier-{numero:02d}.json",
                "nb_items": len(items),
            }
            for numero, items in enumerate(paliers, start=1)
        ],
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description="Génère le thème « quotidien ».")
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
