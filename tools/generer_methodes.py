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
#: (production libre non notée), une `reformulation` (5 critères bornés, seuil 4/5) et deux
#: questions de `test` (mémoire, à choix). Arbitrages de l'orthophoniste du 2026-09-27.
SEQUENCES_PQRST: list[dict] = [
    {
        "titre": "Le colis à retirer",
        "texte": (
            "Le colis est arrivé au bureau de tabac de la place. Il faut le retirer avant "
            "jeudi, avec une pièce d'identité. Le bureau ferme à 18 h. "
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
             "modele": "Le colis attend au bureau de tabac : il faut le retirer avant jeudi, avec une pièce d'identité, avant la fermeture à 18 h.",
             "criteres": [
                 {"label": "le colis", "expressions": ["colis"], "contradictions": []},
                 {"label": "le bureau de tabac", "expressions": ["bureau de tabac", "bureau", "buraliste"],
                  "contradictions": ["pas au bureau", "n est pas au bureau", "ailleurs que le bureau"]},
                 {"label": "avant jeudi", "expressions": ["avant jeudi", "mercredi", "jeudi au plus tard"],
                  "contradictions": ["apres jeudi", "vendredi", "samedi"]},
                 {"label": "une pièce d'identité", "expressions": ["piece d identite", "carte d identite", "identite"],
                  "contradictions": ["sans piece d identite", "pas apporter d identite", "ne pas apporter d identite"]},
                 {"label": "la fermeture à 18 h", "expressions": ["fermeture a 18 h", "18 h", "18"],
                  "contradictions": ["19 h", "19", "20 h", "20"]},
             ], "seuil": 0.8},
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
             "criteres": [
                 {"label": "ouvrir le robinet", "expressions": ["ouvrir le robinet", "robinet ouvert"],
                  "contradictions": ["fermer le robinet", "sans ouvrir le robinet"]},
                 {"label": "utiliser du vinaigre", "expressions": ["vinaigre blanc", "vinaigre"],
                  "contradictions": ["sans vinaigre", "pas de vinaigre"]},
                 {"label": "un cycle à vide à 60 degrés", "expressions": ["cycle a vide a 60 degres"],
                  "groupes": [["cycle a vide"], ["60 degres", "60"]],
                  "contradictions": ["cycle avec du linge", "cycle a froid", "30 degres", "30"]},
                 {"label": "trier le linge", "expressions": ["trier le linge", "tri du linge", "trier"],
                  "contradictions": ["sans trier", "ne pas trier"]},
                 {"label": "nettoyer le filtre chaque mois", "expressions": ["filtre chaque mois", "filtre mensuel"],
                  "groupes": [["filtre"], ["chaque mois", "mensuel", "une fois par mois"]],
                  "contradictions": ["filtre chaque semaine", "filtre chaque annee", "ne pas nettoyer le filtre"]},
             ], "seuil": 0.8},
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
             "modele": "Le dossier a bien été reçu, il est complet et sera remboursé sous quinze jours ; on peut appeler le numéro de la lettre pour toute question.",
             "criteres": [
                 {"label": "le dossier reçu", "expressions": ["dossier recu", "accuse reception"],
                  "groupes": [["dossier"], ["recu", "reception"]],
                  "contradictions": ["dossier non recu", "pas recu le dossier"]},
                 {"label": "les pièces complètes", "expressions": ["pieces completes", "dossier complet"],
                  "contradictions": ["pieces manquantes", "dossier incomplet", "pas complet"]},
                 {"label": "le remboursement", "expressions": ["remboursement", "rembourse"],
                  "contradictions": ["pas de remboursement", "ne sera pas rembourse"]},
                 {"label": "sous quinze jours", "expressions": ["sous quinze jours", "15 jours", "quinze"],
                  "contradictions": ["deux mois", "2 mois", "immediatement"]},
                 {"label": "appeler le numéro de la lettre", "expressions": ["appeler le numero de la lettre", "appeler le numero"],
                  "groupes": [["appeler", "telephone", "telephoner"], ["numero de la lettre", "numero"]],
                  "contradictions": ["par la messagerie", "utiliser la messagerie"]},
             ], "seuil": 0.8},
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
             "modele": "La piscine a des créneaux tranquilles mardi et jeudi matin, avec un tarif simple, un bonnet obligatoire, une pièce pour le casier et des lignes réservées aux nageurs lents.",
             "criteres": [
                 {"label": "le mardi matin", "expressions": ["mardi matin", "mardi"],
                  "contradictions": ["pas le mardi", "samedi"]},
                 {"label": "le jeudi matin", "expressions": ["jeudi matin", "jeudi"],
                  "contradictions": ["pas le jeudi", "vendredi"]},
                 {"label": "les tarifs", "expressions": ["tarif", "quatre euros", "4 euros", "trente euros", "30 euros"],
                  "contradictions": ["gratuit"]},
                 {"label": "le bonnet et la pièce pour le casier", "expressions": ["bonnet et piece pour le casier"],
                  "groupes": [["bonnet"], ["piece pour le casier", "piece de un euro", "piece d un euro"]],
                  "contradictions": ["sans bonnet", "pas de bonnet", "cadenas"]},
                 {"label": "les lignes réservées aux nageurs lents", "expressions": ["lignes reservees aux nageurs lents", "lignes lentes"],
                  "groupes": [["ligne", "lignes"], ["nageurs lents", "lents", "lentes"]],
                  "contradictions": ["nageurs rapides"]},
             ], "seuil": 0.8},
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
PLANS_GMT = [('Tu prépares un dîner. Une invitée doit confirmer ses allergies avant le choix du menu. Les courses '
  'dépendent du menu.',
  'Confirmer les allergies, choisir le menu, faire les courses',
  ['Choisir le menu, confirmer les allergies, faire les courses',
   'Confirmer les allergies, faire les courses, choisir le menu']),
 ('Pour déménager, tu dois mesurer le meuble avant de choisir un véhicule. Le transport exige une '
  'réservation confirmée.',
  'Mesurer le meuble, réserver le véhicule adapté, transporter',
  ['Réserver le véhicule, mesurer le meuble, transporter',
   'Mesurer le meuble, transporter, confirmer la réservation']),
 ('Un dossier en ligne exige la liste des pièces à jour. Les fichiers doivent être contrôlés avant '
  'validation définitive.',
  'Lire la liste à jour, réunir et contrôler les fichiers, valider',
  ['Réunir les fichiers habituels, valider, lire la liste à jour',
   'Lire la liste à jour, valider, contrôler les fichiers']),
 ('Pour repeindre, la notice exige de protéger le sol avant le ponçage, puis de dépoussiérer avant la '
  'peinture.',
  'Protéger le sol, poncer et dépoussiérer, peindre',
  ['Poncer et dépoussiérer, protéger le sol, peindre', 'Protéger le sol, peindre, poncer et dépoussiérer']),
 ('Le logement du week-end est non remboursable. Ton ami doit confirmer ses dates avant la réservation ; les '
  'billets seront achetés après confirmation du logement.',
  'Confirmer les dates, réserver le logement, acheter les billets',
  ['Réserver le logement, confirmer les dates, acheter les billets',
   'Confirmer les dates, acheter les billets, réserver le logement']),
 ('Le formulaire génère une référence après validation. Cette référence est indispensable pour payer, et le '
  'reçu de paiement doit être joint à l’envoi.',
  'Valider le formulaire, payer avec la référence, envoyer avec le reçu',
  ['Payer, valider le formulaire, envoyer avec le reçu',
   'Valider le formulaire, envoyer le dossier, payer avec la référence']),
 ('Pour préparer une soupe selon une recette, tu veux éviter les achats en double. Tu dois vérifier le stock '
  'avant de compléter la liste, puis acheter ce qui manque.',
  'Vérifier le stock, compléter la liste, acheter les manquants',
  ['Compléter la liste, acheter, vérifier le stock', 'Vérifier le stock, acheter, compléter la liste']),
 ('Le cours de sport exige une séance d’essai avant l’abonnement. Il faut réserver un créneau avant de venir '
  'à l’essai.',
  'Réserver un essai, participer à l’essai, choisir l’abonnement',
  ['Choisir l’abonnement, réserver un essai, participer',
   'Participer à l’essai, réserver le créneau, choisir l’abonnement'])]

# --- Plan à vérifier : repérer l'étape mal placée -------------------------------
#: (plan proposé (ordre erroné), étape mal placée, deux autres étapes)
PLANS_A_VERIFIER = [('La peinture choisie doit être achetée avant de préparer le mélange. Le mur doit ensuite être peint avec '
  'ce mélange.',
  ['Acheter la peinture', 'Préparer le mélange', 'Peindre le mur']),
 ('Le loueur confirme une réservation seulement après validation du devis. Le retrait du camion exige cette '
  'confirmation.',
  ['Valider le devis', 'Confirmer la réservation', 'Retirer le camion']),
 ('Le portail produit un formulaire seulement après sélection de la demande. Il faut compléter ce formulaire '
  'avant de transmettre le dossier.',
  ['Sélectionner la demande', 'Compléter le formulaire', 'Transmettre le dossier']),
 ('La recette demande de verser l’eau dans la casserole, de la porter à ébullition puis d’y ajouter les '
  'pâtes.',
  ['Verser l’eau dans la casserole', 'Porter l’eau à ébullition', 'Ajouter les pâtes']),
 ('Pour ce gâteau, la recette impose un four préchauffé avant l’enfournement. Le minuteur démarre une fois '
  'le gâteau enfourné.',
  ['Préchauffer le four', 'Enfourner le gâteau', 'Démarrer le minuteur']),
 ('Le courrier doit être signé avant d’être mis sous enveloppe. L’enveloppe doit être fermée avant le dépôt '
  'au guichet.',
  ['Signer le courrier', 'Fermer l’enveloppe contenant le courrier', 'Déposer l’enveloppe au guichet']),
 ('Le service envoie un code après validation du compte. Ce code est nécessaire pour confirmer le '
  'rendez-vous.',
  ['Valider le compte', 'Recevoir le code', 'Confirmer le rendez-vous avec le code']),
 ('L’étiquette est calculée à partir du poids du colis fermé. Le dépôt exige que cette étiquette soit collée '
  'sur le colis.',
  ['Fermer et peser le colis', 'Éditer et coller l’étiquette', 'Déposer le colis'])]

# --- Auto-instruction : la question à se poser d'abord --------------------------
AUTO_INSTRUCTION = [('Tu vas assembler une étagère. La notice et toutes les pièces sont disponibles, mais tu n’as pas encore '
  'repéré l’ordre du montage. Quelle question traite ce point ?',
  'Quelle pièce se monte d’abord et de quoi dépend la suivante ?',
  ['À quel endroit placer l’étagère une fois montée ?',
   'Combien de livres faudra-t-il ranger sur l’étagère ?']),
 ('Un courrier demande une réponse mais tu ne sais pas encore laquelle. Quelle question clarifie d’abord la '
  'demande ?',
  'Quelle action m’est demandée et pour quelle échéance ?',
  ['Dans quel dossier vais-je classer le courrier ?',
   'Quel moyen de transport utiliser pour aller au guichet ?']),
 ('Tu lis un chapitre pour expliquer demain deux causes d’un phénomène. Quelle question guide une lecture '
  'adaptée à ce but ?',
  'Quels passages expliquent ces deux causes ?',
  ['Quels passages racontent les conséquences du phénomène ?',
   'Quels mots du chapitre sont les plus inhabituels ?']),
 ('Tu vas remplir un formulaire qui demande plusieurs justificatifs. Tu veux éviter de t’interrompre pour '
  'les chercher. Quelle question t’aide ?',
  'Quels documents dois-je réunir avant de commencer ?',
  ['Quelle sera la dernière rubrique à signer ?', 'Comment classer le dossier après son envoi ?']),
 ('La recette est nouvelle. Tu as tous les ingrédients mais seulement 40 minutes et certaines étapes '
  'nécessitent du repos. Quelle question vérifier avant de commencer ?',
  'Quelle est la durée totale, repos compris ?',
  ['Quelle est la quantité totale d’ingrédients ?', 'Quelle présentation choisir pour le plat terminé ?']),
 ('Tu ranges une pièce pour libérer le passage jusqu’à la fenêtre. Quelle question garde ce but en vue ?',
  'Quels objets empêchent actuellement ce passage ?',
  ['Quels objets faudrait-il remplacer prochainement ?', 'Comment réorganiser tous les livres par auteur ?']),
 ('Tu appelles pour un prélèvement en double. La référence est prête ; tu veux formuler clairement ce que tu '
  'demandes. Quelle question t’aide ?',
  'Quel prélèvement contester et quelle régularisation demander ?',
  ['Quel autre forfait pourrait être intéressant ?', 'Quel jour sont émises les prochaines factures ?']),
 ('Tu dois expliquer demain une procédure sans tes notes. Quelle question permet de vérifier ta préparation '
  '?',
  'Puis-je redire les étapes dans l’ordre sans regarder ?',
  ['Ai-je lu chaque page au moins une fois ?', 'Ai-je souligné tous les titres de la procédure ?'])]

# --- Repérer l'information utile dans un document -------------------------------
#: (document court, question, bonne réponse, deux leurres)
REPERER_INFO = [('Votre rendez-vous initial du 12 mars à 9 h est reporté au 19 mars à 14 h. Merci de confirmer avant le 14 '
  'mars. L’accueil téléphonique ouvre à 8 h.',
  'À quelle date le rendez-vous aura-t-il lieu ?',
  'le 19 mars',
  ['le 12 mars', 'le 14 mars']),
 ('Notice de la lampe : installer sur une surface stable et sèche. Ne pas utiliser près d’une source d’eau. '
  'Débrancher avant le nettoyage. Nettoyer avec un chiffon sec.',
  'Que faut-il faire avant le nettoyage ?',
  'débrancher la lampe',
  ['installer la lampe sur une surface stable', 'passer un chiffon sec']),
 ('La piscine est fermée pour travaux du 1er au 15 août. Les inscriptions restent ouvertes sur le site. Le '
  'nettoyage hebdomadaire reprendra le lundi 17 août.',
  'Pourquoi la piscine est-elle fermée du 1er au 15 août ?',
  'pour travaux',
  ['pour nettoyage', 'pour les inscriptions']),
 ('Je pars de la gare à 17 h 30. Je te retrouve à 18 h devant la pharmacie, puis nous passons chez Luc à 18 '
  'h 15. Il nous attend chez lui.',
  'Où dois-tu retrouver la personne qui t’écrit ?',
  'devant la pharmacie',
  ['devant la gare', 'chez Luc']),
 ('Les ordures ménagères passent tous les mardis. Les encombrants sont collectés le premier mardi du mois, '
  'sur inscription avant le lundi précédent. Le verre passe le premier jeudi du mois.',
  'Quand les encombrants sont-ils collectés ?',
  'le premier mardi du mois',
  ['tous les mardis', 'le premier jeudi du mois']),
 ('Atelier photo : apporter deux tirages pour la séance du matin et trois pour celle du soir. Une photo '
  'numérique suffit pour l’inscription. Les tirages seront rendus en fin de séance.',
  'Combien de tirages faut-il pour la séance du soir ?',
  'trois',
  ['deux', 'un']),
 ('Cette facture doit être réglée avant le 30 par virement ou par chèque. La carte bancaire est acceptée '
  'uniquement au guichet pour les nouveaux achats. Les espèces ne sont pas acceptées.',
  'Comment peux-tu régler cette facture ?',
  'par virement ou par chèque',
  ['par carte bancaire ou par chèque', 'par virement ou en espèces']),
 ('Horaires habituels : 9 h–18 h, jusqu’à 19 h le vendredi. Aujourd’hui, inventaire : fermeture '
  'exceptionnelle à 16 h. Demain, retour aux horaires habituels.',
  'À quelle heure le magasin ferme-t-il aujourd’hui ?',
  '16 h',
  ['18 h', '19 h'])]


def _item(famille: str, palier: int, numero: int, type_item: str, prerequis: list[str],
          bonne: str, leurres: list[str], consigne: str, enonce: str, aide: str,
          fonctions: list[str], extra: dict | None = None) -> dict:
    options = [bonne] + list(leurres)
    melanger(famille, options)
    contenu = {"consigne": consigne, "enonce": enonce, "options": options, "aide": aide}
    if extra:
        contenu.update(extra)
    return {
        "id": f"mt3-{palier}-{famille}-{numero:02d}" if palier in {2, 3, 4, 5} else f"mt-{palier}-{famille}-{numero:02d}",
        "type": type_item,
        "module": "entrainement",
        "theme": "methodes",
        "fonctions_ciblees": fonctions,
        "palier": palier,
        "prerequis": prerequis,
        "cap_complexite": None,
        "contenu": contenu,
        "reponse": {"valeur": bonne},
        "meta": {**_meta(), "date_creation": "2026-09-30"} if palier in {2, 3, 4, 5} else _meta(),
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
              "Planifier : repère le but et les contraintes, puis choisis le plan d’étapes cohérent, "
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
              "Choisis la question qui répond au point à clarifier dans cette situation.",
              ["fonctions-executives", "planification"])
        for numero, (tache, bonne, leurres) in enumerate(AUTO_INSTRUCTION, start=1)
    ]
    paliers.append(items)

    # Palier 4 — Plan à vérifier : le « Vérifier » de GMT.
    items = []
    for numero, (situation, ordre) in enumerate(PLANS_A_VERIFIER, start=1):
        # Alternance des deux rotations : une seule relocalisation restaure l'ordre.
        plan = ordre[1:] + ordre[:1] if numero % 2 else ordre[-1:] + ordre[:-1]
        fautive = ordre[0] if numero % 2 else ordre[-1]
        leurres = [etape for etape in plan if etape != fautive]
        items.append(_item(
            "verif", 4, numero, "plan-a-verifier", ["mt-palier-3"], fautive, leurres,
            "Vérifier un plan : lis les contraintes, puis le plan. Choisis la seule étape "
            "à déplacer pour que tout le plan respecte ces contraintes.",
            situation + " Quelle seule étape faut-il déplacer, sans changer l’ordre des deux autres ?",
            "Pour chaque étape, cherche ce qui doit être terminé avant elle.",
            ["planification", "fonctions-executives"], extra={"plan": plan},
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
            ["attention-selective"],
            extra={"document": document},
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
            "id": f"mt2-6-pqrst-{numero:02d}",
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
        "Chercher une information utile — consulter le document pour répondre",
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
