#!/usr/bin/env python3
"""Génère le thème « methodes » — méthodes et stratégies (remédiation).

Cinq familles, chacune appliquant une méthode établie :

- ``pqrst`` — mémoire de textes : lire avec une intention (Parcourir, Question,
  Lire, énoncer, Tester), puis répondre **deux fois** de mémoire au même texte ;
- ``but-etapes`` — Goal Management Training : choisir le plan d'étapes cohérent ;
- ``auto-instruction`` — auto-instruction (Meichenbaum) : la question à se poser
  avant d'agir ;
- ``plan-a-verifier`` — le « Vérifier » de GMT : repérer l'étape mal placée d'un plan ;
- ``reperer-info`` — attention sélective : retrouver l'information utile dans un
  document court (courrier, notice, affichette).

Les questions sont à choix (correction objective) ; la méthode est rappelée dans
la consigne — c'est elle qui est entraînée.

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
#: Date du palier « PQRST mis en œuvre » (contenu ajouté après les cinq premiers).
DATE_PQRST: str = "2026-09-27"

#: Séquences du palier « PQRST mis en œuvre » : un texte de quatre phrases, cinq étapes.
#: Chaque texte porte un `parcours` (question de survol à choix), une `question_modele`
#: (production libre non notée), une `reformulation` (5 idées-clés, seuil 4/5) et deux
#: questions de `test` (mémoire, à choix). Arbitrages de l'orthophoniste du 2026-09-27.
SEQUENCES_PQRST: list[dict] = [
    {
        "titre": "Le colis à retirer",
        "texte": (
            "Le colis est arrivé au bureau de tabac de la place. Il faut le retirer avant "
            "jeudi, avec une pièce d'identité. Le bureau ferme à 18 h, sauf le samedi midi. "
            "Si le colis n'est pas retiré, il repart à l'expéditeur."
        ),
        "attendu": "l'enlèvement d'un colis, l'identité, le délai et les horaires",
        "seuil": 0.8,
        "etapes": [
            {"etape": 1, "nom": "Parcours", "enonce": "De quoi parle ce texte ?",
             "options": ["de l'enlèvement d'un colis", "d'une recette de cuisine", "d'un voyage en train"],
             "bonne": "de l'enlèvement d'un colis"},
            {"etape": 2, "nom": "Question",
             "enonce": "Écris la question que tu te poses sur ce texte.",
             "modele": "Que faut-il apporter pour retirer le colis ?"},
            {"etape": 3, "nom": "Lecture",
             "enonce": "Lis le texte entier, en cherchant la réponse à ta question."},
            {"etape": 4, "nom": "Reformulation",
             "enonce": "Redis le texte en une phrase, avec tes mots.",
             "modele": "Le colis attend au bureau de tabac : il faut le retirer avant jeudi, avec une pièce d'identité, avant 18 h.",
             "idees_cles": ["colis", "bureau", "jeudi", "identite", "18"], "seuil": 0.8},
            {"etape": 5, "nom": "Test", "questions": [
                {"enonce": "Jusqu'à quand peut-on retirer le colis ?",
                 "options": ["jusqu'à jeudi", "jusqu'à samedi", "jusqu'à la fin du mois"],
                 "bonne": "jusqu'à jeudi"},
                {"enonce": "Que faut-il apporter ?",
                 "options": ["une pièce d'identité", "un bon de commande", "la carte de fidélité"],
                 "bonne": "une pièce d'identité"},
            ]},
        ],
    },
    {
        "titre": "Le nouveau lave-linge",
        "texte": (
            "Avant la première lessive, ouvrir le robinet d'arrivée d'eau. Verser un verre "
            "de vinaigre blanc dans le tambour et lancer un cycle à vide à 60 degrés. "
            "Trier ensuite le linge par couleur et remplir le tambour sans le tasser. "
            "Nettoyer le filtre une fois par mois pour éviter les mauvaises odeurs."
        ),
        "attendu": "la préparation du lave-linge, le cycle à vide, le tri du linge, le filtre",
        "seuil": 0.8,
        "etapes": [
            {"etape": 1, "nom": "Parcours", "enonce": "De quoi parle ce texte ?",
             "options": ["de la mise en route d'un lave-linge", "du montage d'une étagère", "de l'entretien d'un vélo"],
             "bonne": "de la mise en route d'un lave-linge"},
            {"etape": 2, "nom": "Question",
             "enonce": "Écris la question que tu te poses sur ce texte.",
             "modele": "Que fait-on avant la première lessive ?"},
            {"etape": 3, "nom": "Lecture",
             "enonce": "Lis le texte entier, en cherchant la réponse à ta question."},
            {"etape": 4, "nom": "Reformulation",
             "enonce": "Redis le texte en une phrase, avec tes mots.",
             "modele": "Avant la première lessive : ouvrir le robinet, lancer un cycle à vide à 60 degrés avec du vinaigre, puis trier le linge et nettoyer le filtre chaque mois.",
             "idees_cles": ["robinet", "vinaigre", "60", "trier", "filtre"], "seuil": 0.8},
            {"etape": 5, "nom": "Test", "questions": [
                {"enonce": "Quel cycle lancer avant la première lessive ?",
                 "options": ["un cycle à vide à 60 degrés", "un cycle court à froid", "un cycle avec du linge blanc"],
                 "bonne": "un cycle à vide à 60 degrés"},
                {"enonce": "Tous les combien nettoyer le filtre ?",
                 "options": ["une fois par mois", "une fois par semaine", "une fois par an"],
                 "bonne": "une fois par mois"},
            ]},
        ],
    },
    {
        "titre": "Le courrier de la mutuelle",
        "texte": (
            "La mutuelle accuse réception du dossier envoyé le 4 septembre. Les pièces sont "
            "complètes, aucun justificatif supplémentaire n'est demandé. Le remboursement "
            "sera versé sous quinze jours sur le compte habituel. Pour toute question, "
            "utiliser le numéro indiqué en haut de la lettre, pas la messagerie."
        ),
        "attendu": "le accusé de réception, les pièces complètes, le délai de remboursement, le numéro",
        "seuil": 0.8,
        "etapes": [
            {"etape": 1, "nom": "Parcours", "enonce": "De quoi parle ce texte ?",
             "options": ["du suivi d'un dossier de remboursement", "de la résiliation d'un contrat", "d'une convocation à un contrôle"],
             "bonne": "du suivi d'un dossier de remboursement"},
            {"etape": 2, "nom": "Question",
             "enonce": "Écris la question que tu te poses sur ce texte.",
             "modele": "Quand vais-je recevoir le remboursement ?"},
            {"etape": 3, "nom": "Lecture",
             "enonce": "Lis le texte entier, en cherchant la réponse à ta question."},
            {"etape": 4, "nom": "Reformulation",
             "enonce": "Redis le texte en une phrase, avec tes mots.",
             "modele": "Le dossier est complet et sera remboursé sous quinze jours ; on peut appeler le numéro de la lettre pour toute question.",
             "idees_cles": ["dossier", "complet", "rembourse", "quinze", "numero"], "seuil": 0.8},
            {"etape": 5, "nom": "Test", "questions": [
                {"enonce": "Sous quel délai le remboursement sera-t-il versé ?",
                 "options": ["sous quinze jours", "sous deux mois", "immédiatement"],
                 "bonne": "sous quinze jours"},
                {"enonce": "Comment poser une question ?",
                 "options": ["en appelant le numéro de la lettre", "par la messagerie du site", "en écrivant au tribunal"],
                 "bonne": "en appelant le numéro de la lettre"},
            ]},
        ],
    },
    {
        "titre": "La séance à la piscine",
        "texte": (
            "La piscine propose des créneaux tranquilles le mardi et le jeudi matin. "
            "L'entrée coûte quatre euros, le carnet de dix entrées trente euros. "
            "Il faut un bonnet de bain et une pièce de un euro pour le casier. "
            "Les lignes 3 et 4 sont réservées aux nageurs lents."
        ),
        "attendu": "les créneaux tranquilles, les tarifs, le bonnet et le casier, les lignes lentes",
        "seuil": 0.8,
        "etapes": [
            {"etape": 1, "nom": "Parcours", "enonce": "De quoi parle ce texte ?",
             "options": ["des conditions pour aller à la piscine", "d'un match de natation", "d'un cours de plongée"],
             "bonne": "des conditions pour aller à la piscine"},
            {"etape": 2, "nom": "Question",
             "enonce": "Écris la question que tu te poses sur ce texte.",
             "modele": "Quels jours y a-t-il des créneaux tranquilles ?"},
            {"etape": 3, "nom": "Lecture",
             "enonce": "Lis le texte entier, en cherchant la réponse à ta question."},
            {"etape": 4, "nom": "Reformulation",
             "enonce": "Redis le texte en une phrase, avec tes mots.",
             "modele": "La piscine a des créneaux tranquilles mardi et jeudi matin, avec un tarif simple, un bonnet obligatoire et des lignes réservées aux nageurs lents.",
             "idees_cles": ["mardi", "jeudi", "tarif", "bonnet", "ligne"], "seuil": 0.8},
            {"etape": 5, "nom": "Test", "questions": [
                {"enonce": "Quels jours sont tranquilles ?",
                 "options": ["mardi et jeudi matin", "samedi après-midi", "tous les soirs"],
                 "bonne": "mardi et jeudi matin"},
                {"enonce": "Que faut-il prévoir pour le casier ?",
                 "options": ["une pièce de un euro", "un cadenas personnel", "rien du tout"],
                 "bonne": "une pièce de un euro"},
            ]},
        ],
    },
]

_RNG_FAMILLES: dict[str, random.Random] = {}


def melanger(famille: str, options: list) -> None:
    rng = _RNG_FAMILLES.setdefault(famille, random.Random(f"{GRAINE}:{famille}"))
    rng.shuffle(options)


def _meta() -> dict:
    return {
        "auteur": AUTEUR,
        "date_creation": DATE_CREATION,
        "relecture_ortho": {"statut": "a_revoir"},
    }


# --- PQRST : un texte, deux questions de mémoire -------------------------------
#: (titre, texte, [(question, bonne, [leurres]), …])
TEXTES_PQRST = [
    ("Le rendez-vous chez le dentiste",
     "Le rendez-vous est fixé au mardi 12 mars à 15 h. Le cabinet se trouve au deuxième étage, "
     "sans ascenseur. Il faut apporter la carte de mutuelle et arriver dix minutes avant.",
     [("À quelle heure est le rendez-vous ?", "15 h", ["12 h", "16 h"]),
      ("Que faut-il apporter ?", "la carte de mutuelle", ["le carnet de santé", "une ordonnance"])]),
    ("La sortie au marché",
     "Le marché a lieu le samedi matin, place de l'église. Les producteurs arrivent vers 7 h et "
     "repartent à 13 h. Le stationnement est gratuit jusqu'à 11 h.",
     [("Quel jour a lieu le marché ?", "le samedi", ["le dimanche", "le vendredi"]),
      ("Jusqu'à quelle heure le stationnement est-il gratuit ?", "11 h", ["13 h", "7 h"])]),
    ("La réparation de la chaudière",
     "Le technicien passera jeudi entre 9 h et 11 h. Il faut dégager l'accès au sous-sol et "
     "laisser le portail ouvert. Le devis est de 180 euros.",
     [("Quel jour passe le technicien ?", "jeudi", ["mardi", "vendredi"]),
      ("Quel est le montant du devis ?", "180 euros", ["80 euros", "280 euros"])]),
    ("Le covoiturage",
     "Le départ est prévu à 8 h 15 devant la gare. La voiture est bleue et il reste deux places. "
     "Le trajet dure environ une heure.",
     [("Où est le point de départ ?", "devant la gare", ["devant la mairie", "sur le parking de l'école"]),
      ("Combien de places restent ?", "deux", ["trois", "une"])]),
    ("L'inscription à la piscine",
     "L'inscription se fait le mercredi après-midi, au guichet du premier étage. Il faut un "
     "certificat médical et une photo. Les cours commencent la semaine suivante.",
     [("Quand se fait l'inscription ?", "le mercredi après-midi", ["le lundi matin", "le samedi"]) ,
      ("Quels documents faut-il ?", "un certificat médical et une photo", ["une pièce d'identité", "une attestation d'assurance"])]),
    ("Le colis en attente",
     "Le colis est arrivé lundi et sera gardé sept jours au point relais. Il se trouve au "
     "tabac de la place. Il faut présenter une pièce d'identité.",
     [("Où se trouve le colis ?", "au tabac de la place", ["à la poste", "chez le gardien"]),
      ("Combien de temps le colis est-il gardé ?", "sept jours", ["trois jours", "un mois"])]),
]

# --- GMT : but et plan d'étapes ------------------------------------------------
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

# --- Plan à vérifier : repérer l'étape mal placée -------------------------------
#: (plan proposé (ordre erroné), étape mal placée, deux autres étapes)
PLANS_A_VERIFIER = [
    (["Protéger les meubles", "Peindre le mur", "Acheter la peinture"], "Acheter la peinture"),
    (["Emballer les affaires", "Réserver le camion", "Transporter les cartons"], "Réserver le camion"),
    (["Remplir le formulaire", "Lire la liste des pièces", "Joindre les documents"], "Lire la liste des pièces"),
    (["Verser l'eau", "Faire bouillir l'eau", "Ajouter les pâtes"], "Faire bouillir l'eau"),
    (["Éteindre le four", "Préchauffer le four", "Enfourner le gâteau"], "Préchauffer le four"),
    (["Signer le courrier", "Écrire l'adresse", "Mettre le timbre"], "Écrire l'adresse"),
    (["Prendre le médicament", "Lire la posologie", "Ouvrir la boîte"], "Lire la posologie"),
    (["Déposer le colis", "Fermer le colis", "Écrire l'adresse"], "Fermer le colis"),
]

# --- Auto-instruction : la question à se poser d'abord --------------------------
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

# --- Repérer l'information utile dans un document -------------------------------
#: (document court, question, bonne réponse, deux leurres)
REPERER_INFO = [
    ("Votre rendez-vous du 12 mars est reporté au 19 mars à 14 h.",
     "À quelle date est le rendez-vous reporté ?", "le 19 mars", ["le 12 mars", "le 14 mars"]),
    ("Ne pas utiliser cet appareil près d'une source d'eau.",
     "Que ne faut-il pas faire ?", "l'utiliser près de l'eau", ["le laisser allumé", "le poser par terre"]),
    ("Piscine fermée du 1er au 15 août pour travaux.",
     "Pourquoi la piscine est-elle fermée ?", "pour travaux", ["pour les vacances", "pour nettoyage"]),
    ("Je passe te prendre à 18 h devant la pharmacie.",
     "Où se retrouve-t-on ?", "devant la pharmacie", ["devant la gare", "à la maison"]),
    ("La collecte des encombrants a lieu le premier mardi du mois.",
     "Quand a lieu la collecte ?", "le premier mardi du mois", ["le premier lundi du mois", "tous les mardis"]),
    ("Prendre un comprimé le matin, deux le soir.",
     "Combien de comprimés le soir ?", "deux", ["un", "trois"]),
    ("Facture à régler avant le 30, par virement ou par chèque.",
     "Quels moyens de paiement sont acceptés ?", "virement ou chèque", ["espèces uniquement", "carte bancaire uniquement"]),
    ("Le magasin ferme exceptionnellement à 16 h aujourd'hui.",
     "À quelle heure le magasin ferme-t-il aujourd'hui ?", "16 h", ["18 h", "19 h"]),
]


def _item(famille: str, palier: int, numero: int, type_item: str, prerequis: list[str],
          bonne: str, leurres: list[str], consigne: str, enonce: str, aide: str,
          fonctions: list[str], extra: dict | None = None) -> dict:
    options = [bonne] + list(leurres)
    melanger(famille, options)
    contenu = {"consigne": consigne, "enonce": enonce, "options": options, "aide": aide}
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
        "meta": _meta(),
    }


def construire_paliers() -> list[list[dict]]:
    paliers: list[list[dict]] = []
    methode_pqrst = ("Méthode PQRST : Parcours le texte, pose-toi une question, Lis-le, reformule-le, "
                     "puis Teste-toi de mémoire (le texte sera caché).")

    # Palier 1 — PQRST : deux questions de mémoire par texte.
    items = []
    numero = 0
    for titre, texte, questions in TEXTES_PQRST:
        for question, bonne, leurres in questions:
            numero += 1
            items.append(_item(
                "pqrst", 1, numero, "pqrst", [], bonne, leurres,
                methode_pqrst, question,
                "Reformule le texte en une phrase avant de répondre.",
                ["memorisation-longue", "recuperation"],
                extra={"affichage": {"mode": "texte", "duree_totale_ms": 25000, "elements": [texte]},
                       "titre_texte": titre},
            ))
    paliers.append(items)

    # Palier 2 — GMT : le but, puis le plan.
    items = [
        _item("gmt", 2, numero, "but-etapes", ["mt-palier-1"], bonne, leurres,
              "Goal Management Training : pose d'abord ton but, puis choisis le plan d'étapes cohérent, "
              "et vérifie-le avant de te lancer.", situation,
              "Un bon plan met d'abord ce qui rend la suite possible.",
              ["planification", "fonctions-executives"])
        for numero, (situation, bonne, leurres) in enumerate(PLANS_GMT, start=1)
    ]
    paliers.append(items)

    # Palier 3 — Auto-instruction : la question à se poser d'abord.
    items = [
        _item("autoinstruction", 3, numero, "auto-instruction", ["mt-palier-2"], bonne, leurres,
              "Auto-instruction : avant d'agir, mets-toi une consigne à voix basse — "
              "« qu'est-ce que je dois faire ? » puis « comment ? » puis « vérifie ».",
              tache,
              "La première question porte sur le but et le moyen, pas sur le résultat attendu.",
              ["fonctions-executives", "planification"])
        for numero, (tache, bonne, leurres) in enumerate(AUTO_INSTRUCTION, start=1)
    ]
    paliers.append(items)

    # Palier 4 — Plan à vérifier : le « Vérifier » de GMT.
    items = []
    for numero, (plan, fautive) in enumerate(PLANS_A_VERIFIER, start=1):
        leurres = [etape for etape in plan if etape != fautive]
        items.append(_item(
            "verif", 4, numero, "plan-a-verifier", ["mt-palier-3"], fautive, leurres,
            "Goal Management Training — étape « Vérifier » : relis le plan dans l'ordre et repère "
            "l'étape qui n'est pas à sa place.",
            "Ce plan est mal ordonné. Quelle étape n'est pas à sa place ?",
            "Demande-toi ce qui doit forcément venir avant le reste.",
            ["planification", "fonctions-executives"],
            extra={"plan": plan},
        ))
    paliers.append(items)

    # Palier 5 — Repérer l'information utile.
    items = []
    for numero, (document, question, bonne, leurres) in enumerate(REPERER_INFO, start=1):
        items.append(_item(
            "reperer", 5, numero, "reperer-info", ["mt-palier-4"], bonne, leurres,
            "Stratégie de lecture : avant de chercher, repère ce que la question demande, "
            "puis cherche seulement cette information dans le document.",
            question,
            "Cherche le mot de la question (date, heure, lieu) dans le document.",
            ["attention-selective", "recuperation"],
            extra={"affichage": {"mode": "texte", "duree_totale_ms": 20000, "elements": [document]}},
        ))
    paliers.append(items)

    # Sixième palier : la méthode PQRST **mise en œuvre** (ADR-015), ajoutée après coup.
    paliers.append(construire_palier_pqrst_mis_en_oeuvre())
    return paliers


def construire_palier_pqrst_mis_en_oeuvre() -> list[dict]:
    """Palier « PQRST mis en œuvre » : une séquence guidée par texte (ADR-015).

    Un item = une séquence complète : Parcours (jugé), Question (production libre, non
    notée, modèle affiché), Lecture (sans chronomètre), Reformulation (4 idées-clés sur 5,
    résumé modèle), Test (2 questions de mémoire). Les deux étapes qui portent
    l'apprentissage — écrire sa question, reformuler — sont des **productions** : c'est
    ce qui manquait au palier PQRST « test ».
    """
    items = []
    for numero, sequence in enumerate(SEQUENCES_PQRST, start=1):
        items.append({
            "id": f"mt-6-pqrst-{numero:02d}",
            "type": "pqrst-mise-en-oeuvre",
            "module": "entrainement",
            "theme": "methodes",
            "fonctions_ciblees": ["memorisation-longue", "recuperation", "fonctions-executives"],
            "palier": 6,
            "prerequis": ["mt-palier-5"],
            "cap_complexite": "un texte court et cinq étapes guidées, une seule fois",
            "contenu": {
                "consigne": ("Méthode PQRST, appliquée pas à pas : Parcours le texte, écris "
                             "la question que tu te poses, Lis-le, Reformule-le avec tes mots, "
                             "puis Teste-toi de mémoire."),
                "titre_texte": sequence["titre"],
                "texte": sequence["texte"],
                "etapes": sequence["etapes"],
                "fiche_methode": [
                    "Parcours : je regarde le titre et le début, je devine le sujet.",
                    "Question : j'écris la question que je me pose.",
                    "Lecture : je lis en cherchant la réponse à ma question.",
                    "Reformulation : je redis le texte en une phrase, avec mes mots.",
                    "Test : je me teste de mémoire, sans regarder.",
                ],
            },
            "reponse": {"valeur": sequence["attendu"], "seuil": sequence["seuil"]},
            "meta": {
                "auteur": "redaction-assistee (tools/generer_methodes.py)",
                "date_creation": DATE_PQRST,
                "relecture_ortho": {"statut": "a_revoir"},
            },
        })
    return items


def _manifest(paliers: list[list[dict]]) -> dict:
    descriptions = [
        "Retenir un texte — répondre de mémoire, avec un rappel de la méthode PQRST",
        "Choisir un plan — comparer des suites d’étapes pour atteindre un but",
        "Se guider avant d’agir — choisir une question à se poser",
        "Vérifier un plan — repérer une étape mal placée",
        "Retenir une information utile — répondre après masquage du document",
        "Appliquer PQRST pas à pas — questionner, lire, reformuler et se tester",
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
