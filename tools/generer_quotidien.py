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

try:
    from tools.generation import ecrire_json, arguments_generation
except ModuleNotFoundError:
    from generation import ecrire_json, arguments_generation

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
ETAPE_SUIVANTE = [('La recette demande un four déjà chaud avant de mélanger la pâte. Les ingrédients sont prêts et le four '
  'est éteint. Que faire maintenant ?',
  'Préchauffer le four',
  ['Mélanger la pâte', 'Beurrer le moule avant d’allumer le four']),
 ('L’ordonnance renouvelée est prête. La pharmacie demande de la recevoir en ligne avant de confirmer la '
  'disponibilité. Que faire maintenant ?',
  'Transmettre l’ordonnance à la pharmacie',
  ['Partir chercher les médicaments', 'Demander au médecin une seconde ordonnance']),
 ('Ta liste du marché est faite. Tu veux acheter uniquement ce qui manque et tu n’as pas encore regardé les '
  'réserves. Quelle étape vient maintenant ?',
  'Comparer la liste avec les réserves',
  ['Acheter les produits de la liste', 'Classer les achats par étal avant de vérifier les réserves']),
 ('Le salon propose deux créneaux. Tu as le numéro mais tu ne connais pas encore tes disponibilités. Quelle '
  'étape évite un second appel ?',
  'Vérifier ton agenda avant de rappeler',
  ['Choisir le premier créneau proposé', 'Rappeler pour demander les mêmes créneaux']),
 ('Les assiettes propres sont sur la table. Tu dois libérer cette table maintenant pour travailler ; aucun '
  'repas n’est prévu avant ce soir.',
  'Ranger les assiettes dans le placard',
  ['Mettre la table pour le dîner', 'Trier les couverts déjà rangés']),
 ('La valise ne doit pas dépasser 8 kg. Elle est remplie mais pas encore pesée. Quelle vérification manque '
  'avant de la considérer prête ?',
  'Peser la valise',
  ['Vérifier une seconde fois la météo', 'Réorganiser les vêtements par couleur']),
 ('La mairie demande une copie, pas l’original. Tu as trouvé le justificatif et préparé l’enveloppe. Quelle '
  'étape manque ?',
  'Faire une copie du justificatif',
  ['Mettre l’original dans l’enveloppe', 'Affranchir l’enveloppe avant de préparer la copie']),
 ('Le restaurant attend le nombre définitif de personnes pour confirmer la réservation. Deux invités n’ont '
  'pas encore répondu.',
  'Obtenir la réponse des deux invités',
  ['Confirmer pour le nombre maximal', 'Choisir les plats avant de confirmer le nombre']),
 ('Tu dois arroser avec 2 litres d’eau ; le récipient contient déjà 1 litre. Quelle action prépare la '
  'quantité demandée ?',
  'Ajouter 1 litre d’eau',
  ['Ajouter 2 litres d’eau', 'Vider le récipient puis ajouter 1 litre']),
 ('La pâte est prête. La recette exige que le moule soit graissé avant d’y verser la pâte. Le moule est '
  'encore sec.',
  'Graisser le moule',
  ['Verser la pâte', 'Lancer le minuteur de cuisson']),
 ('Le colis est fermé et l’étiquette est imprimée. Le point de dépôt exige une étiquette collée et lisible.',
  'Coller l’étiquette sur le colis',
  ['Glisser l’étiquette dans ton sac', 'Déposer le colis avec l’étiquette séparée']),
 ('Tu dois partir à 8 h 30. Le trajet jusqu’au rendez-vous prend 20 minutes et tout est prêt, sauf les '
  'documents encore sur le bureau.',
  'Mettre les documents dans le sac',
  ['Rechercher un autre itinéraire sans changement annoncé',
   'Vérifier à nouveau les horaires déjà confirmés'])]


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
PAR_OU_COMMENCER = [('Un invité arrive dans 20 minutes. Il utilisera seulement l’entrée et le salon, actuellement encombrés. '
  'Par où commencer ?',
  'Dégager l’entrée et le salon',
  ['Réorganiser le rangement de la chambre', 'Trier les papiers dans un placard fermé']),
 ('La liste des pièces de ta demande a changé cette année. Tu as un ancien dossier mais tu ignores les '
  'nouvelles exigences.',
  'Consulter la liste actuelle des pièces',
  ['Photocopier toutes les pièces de l’ancien dossier', 'Rédiger la lettre avec l’ancien modèle']),
 ('Pour ton déménagement, l’ascenseur se réserve au moins trois semaines avant. Tu déménages dans 23 jours ; '
  'les cartons peuvent attendre.',
  'Réserver le créneau de l’ascenseur',
  ['Commencer par emballer les livres', 'Choisir la décoration du nouveau logement']),
 ('Un projet reprend après un mois. Ton collègue a laissé un bilan des tâches achevées et de la prochaine '
  'étape.',
  'Lire le bilan de reprise',
  ['Recommencer la première tâche du projet', 'Planifier toutes les tâches sans lire le bilan']),
 ('Tu reçois six personnes dont une suit un régime particulier. Le menu n’est pas choisi. Quelle première '
  'action évite de devoir changer les courses ?',
  'Demander les contraintes alimentaires',
  ['Acheter les ingrédients de ton menu habituel', 'Préparer le plan de table']),
 ('Deux cours t’intéressent. Ils ont lieu à des horaires différents et tu ne peux te libérer qu’un soir '
  'précis.',
  'Comparer les horaires avec ta disponibilité',
  ['Choisir la tenue adaptée à chaque cours', 'Comparer les durées d’abonnement avant les horaires']),
 ('Trois courriers sont à traiter : l’un expire demain, les autres dans trois semaines. Ils demandent chacun '
  'environ dix minutes.',
  'Traiter le courrier qui expire demain',
  ['Commencer par le courrier le plus récent', 'Commencer par celui dont l’enveloppe est déjà ouverte']),
 ('Tu dois contester un montant. Le service demande la référence de facture dès le début de l’appel ; tu ne '
  'l’as pas sous les yeux.',
  'Retrouver la facture et sa référence',
  ['Composer le numéro immédiatement', 'Chercher les tarifs d’un concurrent']),
 ('Un déplacement dépend d’un rendez-vous dont la date n’est pas confirmée. Les billets envisagés ne sont '
  'pas échangeables.',
  'Faire confirmer la date du rendez-vous',
  ['Acheter les billets au tarif actuel', 'Préparer la valise pour la date supposée']),
 ('Tu veux retrouver rapidement tes documents. Les dossiers thématiques existent déjà mais les papiers '
  'récents sont en pile.',
  'Classer la pile dans les dossiers existants',
  ['Créer un second jeu de dossiers identiques', 'Changer toutes les étiquettes déjà lisibles']),
 ('Ton rendez-vous est demain à 8 h. Un justificatif est obligatoire et le service qui le fournit ferme dans '
  'une heure.',
  'Obtenir le justificatif avant la fermeture',
  ['Préparer d’abord les vêtements de demain', 'Chercher un café près du rendez-vous']),
 ('Tu veux démonter un appareil pour le réparer. La notice précise les précautions et l’ordre d’ouverture, '
  'que tu ne connais pas.',
  'Lire les précautions et l’ordre d’ouverture',
  ['Retirer d’abord les vis visibles', 'Commander des pièces avant d’identifier le défaut'])]


# --- Mémoire prospective : implémentation d'intention (« si … alors … ») --------
#: (chose à se rappeler de faire, plan « si-alors » efficace, deux leurres)
SI_ALORS = [('Tu veux vérifier ton agenda chaque soir. Tu te brosses toujours les dents après le dîner ; l’heure du '
  'dîner varie.',
  'Quand j’ai fini de me brosser les dents, je consulte mon agenda',
  ['À 19 h exactement, je consulte mon agenda pendant le dîner',
   'Quand je consulte mon agenda, je décide quand dîner']),
 ('Tu rends un livre demain en allant au travail. Tu prépares toujours ton sac avant de te coucher.',
  'Quand je prépare mon sac ce soir, j’y mets le livre',
  ['Quand je rentre du travail demain, je prépare le livre',
   'Quand je termine un autre livre, je cherche celui à rendre']),
 ('Tu veux arroser les plantes dimanche. Tu bois toujours ton café chez toi ce matin-là et tu veux '
  'l’utiliser comme repère.',
  'Après mon café du dimanche, j’arrose les plantes',
  ['Après mon café du lundi, j’arrose les plantes', 'Avant de rentrer dimanche soir, j’arrose les plantes']),
 ('Tu dois répondre avant 14 h. Ton déjeuner finit habituellement à 13 h et ta réunion commence à 13 h 30.',
  'Dès la fin du déjeuner, j’envoie ma réponse',
  ['Dès la fin de la réunion à 15 h, j’envoie ma réponse',
   'En rentrant chez moi le soir, j’envoie ma réponse']),
 ('Tu oublies de lancer le minuteur quand tu enfournes un plat. La durée de cuisson est connue.',
  'Dès que j’enfourne le plat, je lance le minuteur',
  ['Dès que je sors le plat, je lance le minuteur',
   'Quand le four préchauffe, je compte toute la durée de cuisson']),
 ('Tu veux enregistrer les factures dès leur réception, puis les payer à la date prévue dans ton agenda.',
  'Quand une facture arrive, je note son échéance dans l’agenda',
  ['Quand l’échéance passe, je classe la facture',
   'Quand je règle une autre facture, je cherche les nouvelles']),
 ('Tu perds tes clés en changeant d’endroit. Un crochet est installé juste à l’entrée et tu veux en faire '
  'une habitude.',
  'Dès que je rentre, j’accroche les clés à ce crochet',
  ['Avant de sortir, je décide où les poser au retour',
   'Quand je cherche les clés, je vérifie toutes les pièces']),
 ('Tu veux noter tout nouveau rendez-vous avant de quitter le cabinet. Tu as ton téléphone avec toi.',
  'Quand le rendez-vous est fixé, je l’enregistre avant de partir',
  ['Quand j’arrive au prochain rendez-vous, je l’enregistre',
   'Quand je range les papiers en fin de mois, je le note']),
 ('Le secrétariat ouvre à 9 h. Tu prends ta pause chaque jour à 9 h 15 et tu dois appeler demain matin.',
  'Quand ma pause de 9 h 15 commence demain, j’appelle',
  ['Quand ma journée finit à 18 h, j’appelle', 'Quand ma pause de midi commence, je vérifie les horaires']),
 ('La collecte a lieu vendredi matin. Tu veux sortir les bacs jeudi soir après ton dîner habituel.',
  'Quand je termine le dîner du jeudi, je sors les bacs',
  ['Quand je termine le dîner du vendredi, je sors les bacs',
   'Quand j’entends le camion vendredi, je prépare les bacs']),
 ('Tu veux emporter ta bouteille. Tu prépares toujours ton déjeuner dans la cuisine avant de partir.',
  'Quand je range mon déjeuner dans le sac, j’ajoute la bouteille',
  ['Quand je commence le déjeuner au travail, je prépare la bouteille chez moi',
   'Quand je rentre du travail, je mets la bouteille près du déjeuner passé']),
 ('Après chaque utilisation du scanner partagé, tu veux récupérer immédiatement tes originaux.',
  'Quand la numérisation se termine, je récupère les originaux',
  ['Quand j’ai besoin d’un autre document, je retourne au scanner',
   'Quand le bureau ferme, je vérifie si mes documents y sont'])]


# --- Résolution de problème : la meilleure solution ---------------------------
#: (problème pratique, meilleure action, deux leurres)
MEILLEURE_SOLUTION = [('L’imprimante indique « bac papier vide ». Tu as du papier du format demandé et aucun autre message '
  'd’erreur.',
  'Remplir le bac demandé puis relancer l’impression',
  ['Réinstaller le pilote de l’imprimante', 'Changer la cartouche d’encre']),
 ('Tu viens de découvrir que tu as manqué ton rendez-vous de ce matin. Tu veux régler la situation actuelle '
  'avant d’organiser les prochains.',
  'Contacter le service pour convenir de la suite',
  ['Ajouter une alarme au rendez-vous déjà passé',
   'Préparer uniquement un calendrier pour le mois prochain']),
 ('Tu ne retrouves pas un document. Le registre indique qu’il a été classé dans le dossier « logement ». Tu '
  'veux le retrouver maintenant.',
  'Consulter le dossier indiqué dans le registre',
  ['Créer un nouveau dossier de rangement', 'Renommer tous les dossiers avant de chercher']),
 ('Une seule rubrique du formulaire t’est incompréhensible. Les autres sont remplies et une assistance est '
  'disponible pour expliquer les rubriques.',
  'Demander une explication sur cette rubrique précise',
  ['Recommencer les rubriques déjà complétées',
   'Envoyer le formulaire en laissant la rubrique obligatoire vide']),
 ('Deux tâches attendent : l’une bloque ton collègue maintenant, l’autre n’est due que demain. Elles '
  'prennent le même temps.',
  'Faire la tâche dont ton collègue a besoin maintenant',
  ['Faire d’abord celle due demain', 'Alterner toutes les minutes entre les deux']),
 ('Une conversation voisine empêche d’entendre ton appel. Une pièce calme est libre et tu peux t’y déplacer.',
  'Poursuivre l’appel dans la pièce calme',
  ['Augmenter seulement le volume au maximum', 'Demander de répéter chaque phrase sans changer de pièce']),
 ('Tu es au magasin avec une liste enregistrée sur ton téléphone. Tu ne te rappelles plus le dernier '
  'produit.',
  'Consulter la liste enregistrée',
  ['Reconstituer de mémoire la liste complète', 'Acheter un produit supplémentaire au cas où']),
 ('Un rendez-vous passe du mardi au jeudi. Ton agenda contient encore le mardi et doit ne garder que le '
  'nouveau créneau.',
  'Modifier l’entrée existante pour le jeudi',
  ['Ajouter jeudi en conservant l’entrée mardi', 'Mettre une note générale sans modifier la date']),
 ('Tu dois traiter 30 dossiers identiques. Tu te perds lorsque plusieurs sont ouverts. Chaque dossier peut '
  'être terminé séparément.',
  'Terminer un dossier avant d’ouvrir le suivant',
  ['Ouvrir les 30 pour voir l’ensemble', 'Commencer la première page de chaque dossier']),
 ('Tu lis une notice longue pour trouver uniquement la procédure de retour. Le sommaire indique cette '
  'rubrique.',
  'Aller à la rubrique de retour indiquée',
  ['Relire d’abord toutes les caractéristiques techniques',
   'Chercher uniquement dans la rubrique d’installation']),
 ('Tu veux connaître les pièces exigées pour une inscription. L’accueil répond à une question précise à la '
  'fois.',
  'Demander la liste des pièces pour cette inscription',
  ['Demander tous les horaires de l’établissement', 'Raconter d’abord toutes les démarches déjà faites']),
 ('Tu effectues une étape qui ne peut pas être interrompue pendant deux minutes. Un appel non urgent arrive '
  '; la messagerie est active.',
  'Finir cette étape puis consulter le message et rappeler',
  ['Interrompre l’étape pour répondre immédiatement',
   'Commencer une autre tâche avant de vérifier le message'])]


# --- Aide externe (mémoire prospective) : quelle aide est adaptée ? ------------
#: (situation, aide adaptée, deux aides moins efficaces)
AIDE_EXTERNE = [('Tu dois sortir les bacs jeudi à 20 h. Tu seras chez toi avec ton téléphone, mais tu ne consulteras plus '
  'tes mails après 18 h.',
  'Programmer une alarme jeudi à 20 h',
  ['Programmer un courriel jeudi à 20 h', 'Mettre une alarme vendredi à 20 h']),
 ('Tu dois appeler demain à 9 h avec un numéro et une référence. Tu seras dehors avec ton téléphone.',
  'Créer un rappel à 9 h avec le numéro et la référence',
  ['Noter le numéro seul sur le bureau de la maison',
   'Créer un rappel à 9 h sans les informations nécessaires']),
 ('Tu dois emporter une carte professionnelle. Ton téléphone restera éteint et tu prends toujours ton sac '
  'près de la porte.',
  'Mettre la carte dans le sac avant le départ',
  ['Prévoir une notification sur le téléphone éteint',
   'Poser la carte dans un dossier que tu n’emportes pas']),
 ('Tu dois emporter un dossier demain. Il ne tient pas dans ton sac ; tu prends toujours tes clés sur une '
  'tablette dégagée.',
  'Poser le dossier sur la tablette avec les clés',
  ['Poser le dossier dans la pièce où tu ne passes pas',
   'Mettre un rappel sur le calendrier du mois suivant']),
 ('Tu dois vérifier les fenêtres en partant. Tu regardes toujours la poignée de la porte d’entrée ; le '
  'passage doit rester libre.',
  'Fixer un petit rappel visible près de la poignée',
  ['Poser un objet au sol dans le passage', 'Mettre le rappel au dos d’une porte de placard fermée']),
 ('Le livre doit être rendu aujourd’hui. Tu pars directement à la bibliothèque et ton sac est déjà près de '
  'toi.',
  'Mettre le livre dans le sac maintenant',
  ['Créer un rappel pour ce soir après la fermeture', 'Noter seulement la date de retour dans l’agenda']),
 ('Tu dois transmettre un code à ta sœur maintenant. Tu as le code et elle peut recevoir des messages '
  'écrits.',
  'Lui envoyer directement le code par message',
  ['Lui envoyer seulement « rappelle-moi »', 'Créer un rappel pour lui envoyer le code demain']),
 ('Tu dois acheter du pain sur le trajet du retour à 18 h. Tu auras ton téléphone et la boulangerie ferme à '
  '18 h 30.',
  'Régler un rappel à 18 h avec le lieu de l’achat',
  ['Régler un rappel à 19 h au retour chez toi', 'Mettre la note sur le réfrigérateur à la maison'])]

# --- Gestion de la pression temporelle (vitesse en situation) -------------------
#: (situation, stratégie utile, deux stratégies qui font perdre du temps)
GESTION_DU_TEMPS = [('Tu pars dans dix minutes. Préparer les documents obligatoires prend cinq minutes, plier le linge dix '
  'minutes. Le linge peut attendre.',
  'Préparer les documents et reporter le linge',
  ['Plier le linge puis chercher les documents', 'Partager les dix minutes également entre les deux']),
 ('Le bus part dans cinq minutes et l’arrêt est à trois minutes. Le billet et les clés sont prêts ; chercher '
  'un magazine prend quatre minutes.',
  'Prendre le billet et les clés puis partir',
  ['Chercher le magazine puis partir', 'Ranger le bureau pendant trois minutes puis partir']),
 ('Tu dois partir maintenant. L’appel en cours n’est pas urgent et ton interlocuteur est disponible ce soir.',
  'Convenir d’un rappel ce soir puis terminer l’appel',
  ['Poursuivre l’appel jusqu’à sa fin naturelle',
   'Commencer à chercher une autre heure de départ sans prévenir']),
 ('Un rendez-vous finit à 11 h et le suivant commence à 11 h 20. Le trajet dure 30 minutes. Les deux '
  'horaires peuvent encore être modifiés.',
  'Demander un décalage permettant le trajet',
  ['Conserver les horaires et réduire le trajet prévu à 20 minutes',
   'Préparer les documents sans modifier les horaires']),
 ('Un dossier est dû dans une heure. La pièce obligatoire prend 30 minutes ; une amélioration de '
  'présentation facultative prend 45 minutes.',
  'Terminer la pièce obligatoire avant la présentation',
  ['Finir la présentation avant la pièce obligatoire',
   'Consacrer 20 minutes à chaque tâche puis envoyer le dossier']),
 ('Le repas doit être prêt dans 40 minutes. Une cuisson dure 35 minutes et la salade 10 minutes ; tu peux '
  'préparer la salade pendant la cuisson.',
  'Lancer la cuisson puis préparer la salade pendant ce temps',
  ['Préparer la salade puis lancer la cuisson',
   'Attendre d’avoir fini les deux préparations pour lancer la cuisson']),
 ('Tu as deux minutes pour rejoindre un rendez-vous tout proche. Un voisin propose une discussion non '
  'urgente qui prendra dix minutes.',
  'Proposer de discuter au retour et poursuivre ton chemin',
  ['Commencer la discussion en espérant qu’elle dure deux minutes',
   'Décaler le rendez-vous sans vérifier la disponibilité']),
 ('Tu disposes de 15 minutes. L’envoi obligatoire prend dix minutes ; le classement facultatif prend dix '
  'minutes et peut attendre demain.',
  'Faire l’envoi et reporter le classement',
  ['Faire le classement puis commencer l’envoi', 'Commencer les deux tâches et les terminer demain'])]


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
                    "Choisis le plan « quand … alors … » adapté à la situation. Relie l’action au repère indiqué.",
                    "Un plan précis, lié à un repère, est plus sûr qu'une bonne intention.",
                    ["memoire-prospective", "planification"])
        for n in range(1, 13)
    ])
    # Palier 6 — meilleure solution (résolution de problème).
    paliers.append([
        _item_choix(n, 6, "solution", "meilleure-solution", ["qo-palier-5"],
                    MEILLEURE_SOLUTION,
                    "Choisis l'action la plus utile. Astuce : commence par ce qui est simple et vérifiable.",
                    "Compare chaque action avec le problème à résoudre maintenant.",
                    ["planification", "fonctions-executives"])
        for n in range(1, 13)
    ])
    # Palier 7 — aide externe adaptée (mémoire prospective : le bon support au bon endroit).
    paliers.append([
        _item_choix(n, 7, "aide", "aide-externe", ["qo-palier-6"],
                    AIDE_EXTERNE,
                    "Choisis l'aide la plus efficace. Astuce : une bonne aide est au bon endroit, au bon moment, et visible juste avant l'action.",
                    "Se souvenir, c'est plus facile quand le rappel est placé là où l'action aura lieu.",
                    ["memoire-prospective", "planification"])
        for n in range(1, 9)
    ])
    # Palier 8 — gestion de la pression temporelle.
    paliers.append([
        _item_choix(n, 8, "temps", "gestion-du-temps", ["qo-palier-7"],
                    GESTION_DU_TEMPS,
                    "Choisis une organisation compatible avec le temps disponible. Tu peux prendre le temps de comparer les propositions.",
                    "Dans l'urgence, on gagne du temps en simplifiant, pas en accélérant.",
                    ["planification", "fonctions-executives"])
        for n in range(1, 9)
    ])
    # Versions distinctes des anciens contenus servis ; les familles inchangées gardent leurs identifiants.
    for palier in (2, 4, 5, 6, 7, 8):
        for item in paliers[palier - 1]:
            item["id"] = item["id"].replace("qo-", "qo2-", 1)
            item["meta"]["date_creation"] = "2026-09-30"
    return paliers


def _manifest(paliers: list[list[dict]]) -> dict:
    descriptions = [
        "Retenir un message — rappeler un détail après sa lecture",
        "Choisir la prochaine étape — poursuivre une tâche commencée",
        "Estimer une durée — proposer un temps en minutes",
        "Choisir par où commencer — préparer une première action",
        "Prévoir un rappel — choisir une routine ou un repère pour penser à agir",
        "Choisir une action utile — comparer des solutions à une difficulté",
        "Choisir une aide-mémoire — placer un rappel au bon moment",
        "Prioriser quand le temps manque — choisir quoi préparer, simplifier ou reporter",
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
    options = arguments_generation("Génère le thème « quotidien ».")

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
            ecrire_json(chemin, donnees)
            print(f"[écrit] {chemin.relative_to(RACINE_DEPOT)} ({nb} entrées)")
    print(f"Total : {total} items, {len(paliers)} paliers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
