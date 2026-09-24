#!/usr/bin/env python3
"""Génère le contenu du thème « evocation » (accès au mot) et les missions hors écran.

Contenu rédigé puis assemblé de façon déterministe (aucun aléatoire non maîtrisé) :
- ``evocation`` : retrouver un mot à partir de sa définition, avec indices
  progressifs (catégorie → attaque phonologique → lettres), reconnaissance
  parmi trois mots, et rappel du contexte d'une information (mémoire de la
  source) ;
- ``missions`` : les missions d'interaction réelle (hors écran) — préparées ici,
  réalisées dans la vie réelle, notées dans le carnet.

Note : le thème d'entraînement « vie sociale » (vignettes d'émotion, réponses
adaptées, intentions) a été RETIRÉ — jugé trop simple à l'usage. Les missions
sont conservées : c'est l'exposition réelle qui agit, pas l'exercice à l'écran.

Les mots, définitions et situations sont originaux ; aucun matériel protégé
n'est reproduit. Les indices ne doivent jamais contenir la réponse — la
révélation complète est un mode d'interface, pas un indice de contenu.

Usage :

    python3 tools/generer_evocation.py            # écrit le contenu
    python3 tools/generer_evocation.py --dry-run  # affiche sans écrire
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent
DOSSIER_CONTENU = RACINE_DEPOT / "content" / "entrainement"
GRAINE = 20260920
DATE_CREATION = "2026-09-20"
AUTEUR = "redaction-assistee (tools/generer_evocation.py)"


def meta() -> dict:
    """Métadonnées d'item (relecture orthophoniste à tracer, jamais présentée comme clinique)."""
    return {
        "auteur": AUTEUR,
        "date_creation": DATE_CREATION,
        "relecture_ortho": {"statut": "a_revoir"},
    }


#: Générateurs aléatoires isolés par « thème:famille » (règle du dépôt :
#: un tirage partagé fait qu'ajouter un contenu réécrit silencieusement le
#: contenu existant — voir docs/30-technique/contenu-versionne.md).
_RNG_FAMILLES: dict[str, random.Random] = {}


def melanger(theme: str, famille: str, options: list) -> None:
    """Mélange l'ordre des propositions avec le générateur isolé de la famille.

    Seul l'ORDRE des propositions dépend du hasard ici (les mots et situations
    sont rédigés) : l'isolation garantit qu'ajouter une famille ne change pas
    l'ordre des propositions des autres.
    """
    rng = _RNG_FAMILLES.setdefault(
        f"{theme}:{famille}", random.Random(f"{GRAINE}:{theme}:{famille}")
    )
    rng.shuffle(options)


def indices_mot(mot: str, categorie: str, attaque: str) -> list[dict]:
    """Hiérarchie d'indices d'un mot : catégorie, attaque phonologique, forme écrite."""
    return [
        {"type": "semantique", "texte": f"Catégorie : {categorie}."},
        {"type": "phonologique", "texte": f"Ça commence par « {attaque}… »."},
        {"type": "orthographique", "texte": f"{len(mot)} lettres, première lettre « {mot[0].upper()} »."},
    ]


# --------------------------------------------------------------------------
# Thème « evocation » — accès au mot
# --------------------------------------------------------------------------

#: (mot, définition affichée, catégorie pour l'indice, attaque phonologique,
#:  deux mots de la même famille servant de leurres en reconnaissance)
MOTS_CONCRETS = [
    ("verre", "Objet en verre dans lequel on boit.", "objets de la table", "ver", ["assiette", "bouteille"]),
    ("clé", "Petit objet qui ouvre une porte.", "objets du quotidien", "cl", ["cadenas", "poignée"]),
    ("parapluie", "Objet qu'on ouvre quand il pleut.", "objets du quotidien", "pa", ["manteau", "bottes"]),
    ("escalier", "Série de marches pour changer d'étage.", "parties d'un bâtiment", "es", ["ascenseur", "couloir"]),
    ("cuillère", "Ustensile pour manger la soupe.", "ustensiles de cuisine", "cui", ["fourchette", "couteau"]),
    ("bougie", "Bâton de cire qui éclaire quand on l'allume.", "objets de la maison", "bou", ["lampe", "allumette"]),
    ("miroir", "Objet dans lequel on voit son reflet.", "objets de la maison", "mi", ["cadre", "vitre"]),
    ("marteau", "Outil pour enfoncer un clou.", "outils", "mar", ["tournevis", "pince"]),
    ("brouette", "Chariot à une roue pour transporter la terre.", "matériel de jardin", "brou", ["râteau", "pelle"]),
    ("arrosoir", "Récipient pour arroser les plantes.", "matériel de jardin", "a", ["seau", "tuyau"]),
    ("boussole", "Instrument qui indique le nord.", "objets de voyage", "bous", ["carte", "lampe"]),
    ("thermomètre", "Instrument qui indique la température.", "objets du quotidien", "ther", ["baromètre", "balance"]),
    ("cadenas", "Serrure mobile qu'on accroche à une porte.", "objets du quotidien", "ca", ["chaîne", "clé"]),
    ("tablier", "Vêtement qu'on met pour cuisiner sans se tacher.", "vêtements", "ta", ["serviette", "torchon"]),
    ("entonnoir", "Objet en forme de cône pour verser sans renverser.", "ustensiles de cuisine", "en", ["passoire", "louche"]),
]

MOTS_ABSTRAITS = [
    ("patience", "Capacité à attendre sans s'énerver.", "qualités", "pa", ["prudence", "tolérance"]),
    ("habitude", "Geste qu'on fait sans y penser, toujours de la même façon.", "notions du quotidien", "ha", ["manie", "routine"]),
    ("silence", "Absence de bruit.", "notions du quotidien", "si", ["calme", "repos"]),
    ("souvenir", "Ce qui reste en mémoire d'un moment passé.", "notions de mémoire", "sou", ["image", "récit"]),
    ("décision", "Choix qu'on arrête après avoir hésité.", "notions du quotidien", "dé", ["avis", "projet"]),
    ("promesse", "Engagement qu'on prend devant quelqu'un.", "notions du quotidien", "pro", ["excuse", "remerciement"]),
    ("retard", "Fait d'arriver après l'heure prévue.", "notions du quotidien", "re", ["avance", "attente"]),
    ("confiance", "Sentiment de pouvoir compter sur quelqu'un.", "sentiments", "con", ["amitié", "estime"]),
    ("fatigue", "Sensation d'être vidé, d'avoir besoin de repos.", "états du corps", "fa", ["sommeil", "effort"]),
    ("attention", "Fait de se concentrer sur une seule chose.", "notions de mémoire", "at", ["mémoire", "vigilance"]),
    ("inquiétude", "Sentiment d'être préoccupé par ce qui pourrait arriver.", "sentiments", "in", ["surprise", "curiosité"]),
    ("timidité", "Gêne ressentie devant des personnes qu'on connaît peu.", "sentiments", "ti", ["réserve", "pudeur"]),
    ("prudence", "Fait d'agir avec précaution.", "qualités", "pru", ["patience", "calme"]),
    ("énergie", "Force qui permet d'agir et de tenir la journée.", "états du corps", "é", ["souffle", "entrain"]),
    ("curiosité", "Envie d'apprendre et de savoir.", "qualités", "cu", ["envie", "intérêt"]),
]

#: (id, contexte affiché, information à retrouver, leurres de contexte)
FICHES_SOURCE = [
    ("fr-1", "Note collée sur le frigo", "Le code du garage est 4721.", ["Message sur le répondeur", "Carnet de courses", "SMS reçu le matin"]),
    ("fr-2", "SMS de l'orthophoniste", "Le rendez-vous est décalé au mardi 14 h.", ["Affichette du cabinet", "Courriel de l'assurance", "Note sur le frigo"]),
    ("fr-3", "Affichette dans le hall de l'immeuble", "Coupure d'eau jeudi entre 9 h et 12 h.", ["Message sur le répondeur", "Bulletin municipal", "SMS de la gardienne"]),
    ("fr-4", "Post-it sur le plan de travail", "Il reste deux boîtes de thé dans le placard.", ["Carnet de courses", "Liste partagée sur le téléphone", "Note vocale"]),
    ("fr-5", "Bulletin municipal reçu par courrier", "La collecte du verre passe le premier lundi du mois.", ["Affichette dans le hall", "Site de la mairie", "SMS reçu le matin"]),
    ("fr-6", "Courriel de la banque", "Le prélèvement part le 5 de chaque mois.", ["SMS de la banque", "Relevé papier", "Application de paiement"]),
    ("fr-7", "Note lue dans le carnet de santé", "Allergie signalée à la pénicilline.", ["Ordonnance de la pharmacie", "Carnet de rendez-vous", "Courriel du médecin"]),
    ("fr-8", "Mémos du téléphone", "Le mot de passe du wifi a été changé en août.", ["Étiquette au dos du boîtier", "SMS de l'opérateur", "Notebook de la cuisine"]),
    ("fr-9", "Panneau à l'entrée du parc", "Le portail ferme à 20 h en semaine.", ["Site de la ville", "Affiche du marché", "Message vocal"]),
    ("fr-10", "Note dans l'agenda papier", "Le vélo doit être récupéré chez le réparateur vendredi.", ["SMS de la boutique", "Fil de discussion familial", "Ticket de dépôt"]),
]


#: SFA — analyse sémantique : (définition du concept, mot cible)
ANALYSE_SFA = [
    ("Ce mot désigne un objet qui sert à enfoncer des clous.", "marteau"),
    ("Ce mot désigne un objet qui sert à se protéger de la pluie.", "parapluie"),
    ("Ce mot désigne un objet qui sert à couper du papier.", "ciseaux"),
    ("Ce mot désigne un lieu où l'on emprunte des livres.", "bibliothèque"),
    ("Ce mot désigne un objet qui sert à ouvrir une porte.", "clé"),
    ("Ce mot désigne un véhicule à deux roues que l'on fait avancer en pédalant.", "vélo"),
]

#: PCA — analyse phonologique : (définition du concept, mot cible)
ANALYSE_PCA = [
    ("Ce mot désigne un appareil qui conserve les aliments au froid.", "réfrigérateur"),
    ("Ce mot désigne un objet qui sert à écrire et que l'on peut effacer.", "crayon"),
    ("Ce mot désigne un endroit où l'on attend le train.", "gare"),
    ("Ce mot désigne un objet que l'on met sur la tête quand il fait froid.", "bonnet"),
    ("Ce mot désigne un meuble où l'on range les vêtements.", "armoire"),
    ("Ce mot désigne un objet qui sert à mesurer une longueur.", "mètre"),
]

SFA_ETAPES = [
    "À quelle catégorie appartient-il ? (outil, meuble, lieu, véhicule…)",
    "À quoi sert-il ?",
    "Où le trouve-t-on ?",
    "À quoi cela te fait-il penser ?",
]
PCA_ETAPES = [
    "Par quel son commence-t-il ?",
    "Combien de syllabes a-t-il ?",
    "Avec quel mot rime-t-il ?",
    "Quel est son dernier son ?",
]


def _item_analyse(numero: int, palier: int, methode: str, definition: str, mot: str,
                  prerequis: list[str]) -> dict:
    """Item d'analyse du mot (SFA ou PCA) : l'utilisateur génère les attributs, puis nomme."""
    if methode == "semantique":
        consigne = ("Méthode SFA : analyse le mot avant de le dire. Décris-le par ses caractéristiques "
                    "(catégorie, usage, lieu), puis retrouve-le.")
        etapes, aide = SFA_ETAPES, "Dis à voix haute ce que tu as trouvé : sa catégorie, son usage, le lieu."
    else:
        consigne = ("Méthode PCA : analyse le mot par ses sons. Commence par son premier son, compte ses "
                    "syllabes, cherche une rime, puis retrouve-le.")
        etapes, aide = PCA_ETAPES, "Dis le mot à voix haute en détachant les syllabes."
    return {
        "id": f"ev-{palier}-analyse-{numero:02d}",
        "type": "analyse-mot",
        "module": "entrainement",
        "theme": "evocation",
        "fonctions_ciblees": ["acces-lexical", "recuperation"],
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": {
            "consigne": consigne,
            "methode": methode,
            "definition": definition,
            "etapes": list(etapes),
            "enonce": "Quel est ce mot ?",
            "aide": aide,
        },
        "reponse": {"valeur": mot},
        "meta": meta(),
    }


def items_evocation() -> list[dict]:
    """Assemble les items du thème evocation (5 paliers de 10 items)."""
    items: list[dict] = []

    def ajouter(palier: int, famille: str, numero: int, item: dict) -> None:
        item["id"] = f"ev-{palier}-{famille}-{numero:02d}"
        item["palier"] = palier
        item["prerequis"] = [f"ev-palier-{palier - 1}"] if palier > 1 else []
        item["module"] = "entrainement"
        item["theme"] = "evocation"
        item["cap_complexite"] = None
        item["meta"] = meta()
        items.append(item)

    # Palier 1 — reconnaissance : la réponse est proposée avec deux leurres.
    for numero, (mot, definition, _cat, _att, leurres) in enumerate(MOTS_ABSTRAITS[:5] + MOTS_CONCRETS[:5], start=1):
        options = [mot] + list(leurres)
        melanger("evocation", "reconnaissance", options)
        ajouter(1, "reconnaissance", numero, {
            "type": "reconnaissance",
            "fonctions_ciblees": ["acces-lexical"],
            "contenu": {
                "consigne": "Choisis le mot qui correspond à la définition.",
                "enonce": definition,
                "options": options,
                "aide": "Relis la définition en entier avant de choisir.",
            },
            "reponse": {"valeur": mot},
        })

    # Palier 2 — rappel indicé sur des mots concrets.
    for numero, (mot, definition, categorie, attaque, _leurres) in enumerate(MOTS_CONCRETS[:10], start=1):
        ajouter(2, "rappel", numero, {
            "type": "rappel-indice",
            "fonctions_ciblees": ["acces-lexical", "recuperation"],
            "contenu": {
                "consigne": "Retrouve le mot à partir de la définition. Demande un indice seulement si le mot ne vient pas.",
                "enonce": definition,
                "indices": indices_mot(mot, categorie, attaque),
                "aide": "Dis la définition à voix basse : le mot vient souvent en la reformulant.",
            },
            "reponse": {"valeur": mot},
        })

    # Palier 3 — rappel indicé sur des notions moins fréquentes.
    for numero, (mot, definition, categorie, attaque, _leurres) in enumerate(MOTS_ABSTRAITS[:10], start=1):
        ajouter(3, "rappel", numero, {
            "type": "rappel-indice",
            "fonctions_ciblees": ["acces-lexical", "recuperation"],
            "contenu": {
                "consigne": "Retrouve le mot à partir de la définition. Demande un indice seulement si le mot ne vient pas.",
                "enonce": definition,
                "indices": indices_mot(mot, categorie, attaque),
                "aide": "Pense à une situation où tu as vécu cela récemment.",
            },
            "reponse": {"valeur": mot},
        })

    # Palier 4 — rappel de la source : où l'information a-t-elle été vue ?
    for numero, (ident, contexte, information, leurres) in enumerate(FICHES_SOURCE, start=1):
        options = [contexte] + list(leurres)
        melanger("evocation", "source", options)
        ajouter(4, "source", numero, {
            "type": "rappel-source",
            "fonctions_ciblees": ["memorisation-longue", "recuperation"],
            "contenu": {
                "consigne": "Mémorise la fiche affichée : tu devras dire dans quel contexte tu l'as vue.",
                "affichage": {
                    "mode": "liste",
                    "duree_totale_ms": 12000,
                    "elements": [[contexte, information]],
                },
                "enonce": f"Dans quel contexte as-tu vu : « {information} » ?",
                "options": options,
                "aide": "Repense à l'endroit, pas seulement au texte.",
            },
            "reponse": {"valeur": contexte},
        })

    # Palier 5 — alternance rappel indicé / reconnaissance.
    ajouter(5, "rappel", 1, {
        "type": "rappel-indice",
        "fonctions_ciblees": ["acces-lexical", "recuperation"],
        "contenu": {
            "consigne": "Retrouve le mot à partir de la définition.",
            "enonce": MOTS_CONCRETS[10][1],
            "indices": indices_mot(*MOTS_CONCRETS[10][:1], MOTS_CONCRETS[10][2], MOTS_CONCRETS[10][3]),
            "aide": None,
        },
        "reponse": {"valeur": MOTS_CONCRETS[10][0]},
    })
    for numero, (mot, definition, categorie, attaque, _leurres) in enumerate(MOTS_CONCRETS[11:], start=2):
        ajouter(5, "rappel", numero, {
            "type": "rappel-indice",
            "fonctions_ciblees": ["acces-lexical", "recuperation"],
            "contenu": {
                "consigne": "Retrouve le mot à partir de la définition.",
                "enonce": definition,
                "indices": indices_mot(mot, categorie, attaque),
                "aide": None,
            },
            "reponse": {"valeur": mot},
        })
    for numero, (mot, definition, _cat, _att, leurres) in enumerate(MOTS_ABSTRAITS[10:], start=6):
        options = [mot] + list(leurres)
        melanger("evocation", "reconnaissance", options)
        ajouter(5, "reconnaissance", numero, {
            "type": "reconnaissance",
            "fonctions_ciblees": ["acces-lexical"],
            "contenu": {
                "consigne": "Choisis le mot qui correspond à la définition.",
                "enonce": definition,
                "options": options,
                "aide": None,
            },
            "reponse": {"valeur": mot},
        })


    # Palier 6 — SFA : analyse sémantique du mot (l'utilisateur génère les attributs).
    for numero, (definition, mot) in enumerate(ANALYSE_SFA, start=1):
        items.append(_item_analyse(numero, 6, "semantique", definition, mot, ["ev-palier-5"]))

    # Palier 7 — PCA : analyse phonologique du mot.
    for numero, (definition, mot) in enumerate(ANALYSE_PCA, start=1):
        items.append(_item_analyse(numero, 7, "phonologique", definition, mot, ["ev-palier-6"]))

    return items


# --------------------------------------------------------------------------
# Thème « social » — vie sociale
# --------------------------------------------------------------------------

#: (situation, émotion attendue, deux autres émotions plausibles)
MISSIONS = [
    {
        "id": "ms-01",
        "niveau": 1,
        "titre": "Saluer une personne croisée",
        "pourquoi": "Rétablir un geste simple qui demande peu d'énergie et qui ouvre la journée.",
        "etapes": [
            "Choisis une personne que tu croises régulièrement (voisin, commerçant).",
            "Prépare deux phrases : « Bonjour » puis « Bonne journée ».",
            "Dis-les au prochain passage, sans attendre de conversation.",
        ],
        "duree_estimee_min": 2,
        "repere": "Tu as dit les deux phrases — c'est réussi, même si la réponse a été brève.",
    },
    {
        "id": "ms-02",
        "niveau": 1,
        "titre": "Demander une information simple",
        "pourquoi": "S'entraîner à ouvrir une demande courte, dans un lieu où c'est normal de la poser.",
        "etapes": [
            "Choisis un lieu familier (boulangerie, pharmacie, accueil).",
            "Écris ta question en une phrase : « Où puis-je trouver… ? »",
            "Pose-la, écoute la réponse, remercie.",
        ],
        "duree_estimee_min": 5,
        "repere": "La question a été posée à voix haute — peu importe la réponse obtenue.",
    },
    {
        "id": "ms-03",
        "niveau": 2,
        "titre": "Répondre à un message en attente",
        "pourquoi": "Un message sans réponse entretient l'évitement ; y répondre en ferme la boucle.",
        "etapes": [
            "Repère un message en attente depuis plusieurs jours.",
            "Écris une réponse courte (deux phrases suffisent).",
            "Relis-la, puis envoie-la.",
        ],
        "duree_estimee_min": 10,
        "repere": "Le message est parti, même s'il tient en deux lignes.",
    },
    {
        "id": "ms-04",
        "niveau": 2,
        "titre": "Passer un appel court",
        "pourquoi": "Le téléphone fait souvent peur après une longue période de retrait : une durée limitée rend l'exercice supportable.",
        "etapes": [
            "Écris sur un papier l'objet de l'appel en une phrase.",
            "Note une phrase d'ouverture et une phrase de sortie.",
            "Appelle, dis tes deux phrases, puis termine l'appel.",
        ],
        "duree_estimee_min": 10,
        "repere": "L'appel a eu lieu et tu as raccroché toi-même.",
    },
    {
        "id": "ms-05",
        "niveau": 3,
        "titre": "Proposer une rencontre courte",
        "pourquoi": "Proposer est plus difficile que répondre : c'est le pas qui change vraiment la situation.",
        "etapes": [
            "Choisis une personne avec qui tu as déjà passé un bon moment.",
            "Propose un créneau court et précis (café de 45 minutes, marche de 20 minutes).",
            "Précise ce que tu proposes, sans justification longue.",
        ],
        "duree_estimee_min": 15,
        "repere": "La proposition a été envoyée ; la réponse ne dépend pas de toi.",
    },
    {
        "id": "ms-06",
        "niveau": 3,
        "titre": "Participer sans parler",
        "pourquoi": "Être présent sans obligation de parler fatigue moins et relance l'habitude d'être avec d'autres.",
        "etapes": [
            "Repère un moment collectif accessible (cours, club, repas partagé).",
            "Fixe-toi un objectif minimal : rester vingt minutes.",
            "Prépare une phrase de sortie pour partir tranquillement.",
        ],
        "duree_estimee_min": 30,
        "repere": "Tu es resté le temps prévu — c'est la réussite de la mission.",
    },
    {
        "id": "ms-07",
        "niveau": 4,
        "titre": "Reprendre contact avec une personne perdue de vue",
        "pourquoi": "Renouer évite de repartir de zéro : le lien existe déjà, il faut juste le réactiver.",
        "etapes": [
            "Choisis une personne dont tu as de bons souvenirs.",
            "Écris un message simple : un souvenir précis, puis une question.",
            "Envoie. Si la réponse tarde, ce n'est pas un verdict sur toi.",
        ],
        "duree_estimee_min": 20,
        "repere": "Le message est envoyé.",
    },
    {
        "id": "ms-08",
        "niveau": 4,
        "titre": "Demander de l'aide à quelqu'un",
        "pourquoi": "Demander aide maintient les liens, alors que ne jamais demander finit par éloigner.",
        "etapes": [
            "Repère un petit service que quelqu'un peut rendre facilement.",
            "Formule la demande en précisant la durée : « Est-ce que tu pourrais m'aider dix minutes ? »",
            "Remercie explicitement après.",
        ],
        "duree_estimee_min": 15,
        "repere": "La demande a été formulée clairement.",
    },
]


def ecrire_contenu(dry_run: bool = False) -> dict:
    """Écrit les paliers, les manifestes et les missions ; retourne les compteurs."""
    paliers_evocation = 7
    items_ev = items_evocation()

    def paquet(items: list[dict], thème: str, palier: int) -> list[dict]:
        return [item for item in items if item["palier"] == palier]

    ecritures = []
    for thème, items, nb_paliers in (("evocation", items_ev, paliers_evocation),):
        for palier in range(1, nb_paliers + 1):
            chemin = DOSSIER_CONTENU / thème / "paliers" / f"palier-{palier:02d}.json"
            ecritures.append((chemin, paquet(items, thème, palier)))
        manifeste = {
            "theme": thème,
            "paliers": [
                {
                    "id": f"{'ev' if thème == 'evocation' else 'so'}-palier-{palier}",
                    "description": DESCRIPTION_PALIERS[thème][palier - 1],
                    "prerequis": [f"{'ev' if thème == 'evocation' else 'so'}-palier-{palier - 1}"] if palier > 1 else [],
                    "fichier": f"paliers/palier-{palier:02d}.json",
                    "nb_items": len(paquet(items, thème, palier)),
                }
                for palier in range(1, nb_paliers + 1)
            ],
        }
        ecritures.append((DOSSIER_CONTENU / thème / "paliers.json", manifeste))
    ecritures.append((RACINE_DEPOT / "content" / "missions" / "missions.json", {"theme": "missions", "missions": MISSIONS}))

    for chemin, donnees in ecritures:
        if not dry_run:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "evocation": len(items_ev),
        "missions": len(MISSIONS),
        "paliers": {"evocation": paliers_evocation},
    }


DESCRIPTION_PALIERS = {
    "evocation": [
        "Reconnaître le mot juste parmi trois propositions",
        "Retrouver des mots concrets à partir de leur définition",
        "Retrouver des notions plus abstraites, avec indices progressifs",
        "Retrouver le contexte d'une information (mémoire de la source)",
        "Alterner reconnaissance et rappel indicé",
        "Analyse sémantique (SFA) : décrire le mot par ses caractéristiques, puis le nommer",
        "Analyse phonologique (PCA) : décomposer le mot par ses sons, puis le nommer",
    ],
}


def main() -> None:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--dry-run", action="store_true", help="afficher les compteurs sans écrire")
    args = analyseur.parse_args()
    compteurs = ecrire_contenu(dry_run=args.dry_run)
    prefixe = "[dry-run] " if args.dry_run else ""
    print(
        f"{prefixe}evocation : {compteurs['evocation']} items "
        f"({compteurs['paliers']['evocation']} paliers) | "
        f"missions : {compteurs['missions']}"
    )


if __name__ == "__main__":
    main()
