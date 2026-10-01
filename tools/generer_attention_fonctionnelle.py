#!/usr/bin/env python3
"""Génère trois banques de situations fonctionnelles adultes, sans vitesse imposée."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = {'auteur': 'redaction-assistee (tools/generer_attention_fonctionnelle.py)',
        'date_creation': '2026-10-01', 'relecture_ortho': {'statut': 'a_revoir'}}


def item(theme, palier, numero, contenu, reponse, fonctions):
    return {'id': f'{theme}-v2-{palier}-{numero:02}', 'module': 'entrainement',
            'theme': theme, 'type': theme, 'palier': palier, 'prerequis': [],
            'fonctions_ciblees': fonctions, 'contenu': contenu,
            'reponse': {'valeur': reponse}, 'meta': META.copy()}


def c(cle, libelle, initial, changement, correction):
    return (cle, libelle, initial, changement, correction)


ACTUALISATIONS = [
 ('Préparer une réunion',[c('heure','Horaire','14 h','15 h','16 h'),c('lieu','Salle','Atlas','Orion','Vega'),c('piece','Document','budget','contrat','synthèse'),c('format','Format','sur place','hybride','à distance')]),
 ('Retirer un dossier',[c('jour','Jour','mardi','jeudi','vendredi'),c('lieu','Guichet','accueil','bureau 12','secrétariat'),c('piece','Justificatif','badge','convocation','pièce d’identité'),c('heure','Créneau','10 h','11 h 30','14 h')]),
 ('Réceptionner une livraison',[c('heure','Horaire','10 h','11 h','12 h'),c('acces','Entrée','nord','sud','est'),c('piece','Document','bon de commande','facture','bon signé'),c('contact','Contact','Mme Roy','M. Diallo','Mme Chen')]),
 ('Organiser une visite culturelle',[c('jour','Jour','lundi','mercredi','samedi'),c('lieu','Rendez-vous','gare','musée','bibliothèque'),c('piece','Document','plan','billet','invitation'),c('heure','Horaire','9 h 30','10 h','10 h 45')]),
 ('Préparer un déplacement',[c('depart','Départ','8 h 20','8 h 40','9 h 05'),c('quai','Quai','3','7','11'),c('bagage','Bagage','valise cabine','sac à dos','aucun bagage'),c('adresse','Destination','centre de congrès','hôtel Central','site universitaire')]),
 ('Suivre une formation',[c('date','Date','7 décembre','8 décembre','9 décembre'),c('format','Format','sur place','à distance','hybride'),c('support','Support','ordinateur','tablette','documents imprimés'),c('heure','Début','9 h','9 h 30','10 h')]),
 ('Préparer un rendez-vous administratif',[c('jour','Jour','lundi','mardi','jeudi'),c('service','Service','urbanisme','état civil','impôts'),c('dossier','Dossier','original','copie','version signée'),c('heure','Horaire','13 h','14 h 15','15 h')]),
 ('Coordonner une intervention à domicile',[c('date','Date','12 octobre','14 octobre','16 octobre'),c('plage','Plage horaire','matin','13 h–15 h','16 h–18 h'),c('acces','Accès','porte principale','cour intérieure','garage'),c('presence','Présence','toi-même','voisin','gardien')]),
 ('Animer un atelier',[c('jour','Jour','samedi','dimanche','vendredi'),c('salle','Salle','atelier 2','auditorium','salle 5'),c('materiel','Matériel','ordinateur','vidéoprojecteur','tableau mobile'),c('public','Participants','8','10','12')]),
 ('Préparer une consultation',[c('heure','Horaire','11 h','11 h 45','13 h'),c('lieu','Site','cabinet A','centre B','téléconsultation'),c('document','Document','résultats','courrier','ordonnance'),c('transport','Trajet','métro','taxi','à pied')]),
 ('Finaliser un dossier associatif',[c('date','Échéance','20 mars','22 mars','25 mars'),c('format','Format','PDF','formulaire en ligne','dossier papier'),c('signature','Signature','présidente','trésorier','deux responsables'),c('envoi','Envoi','courriel','plateforme','courrier suivi')]),
 ('Organiser un dîner',[c('heure','Horaire','19 h 30','20 h','20 h 30'),c('lieu','Lieu','restaurant Rivage','restaurant Jardin','domicile'),c('nombre','Couverts','4','5','6'),c('contrainte','Menu','sans contrainte','sans gluten','végétarien')]),
]


def actualiser():
    resultat = []
    for palier in range(1, 4):
        items = []
        for numero, (titre, champs) in enumerate(ACTUALISATIONS, 1):
            actifs = champs[:palier + 1]
            pivot = (numero - 1) % len(actifs)
            etat = {cle: initial for cle, _, initial, _, _ in actifs}
            etapes = [{'titre': 'Consigne initiale', 'evenement': 'initial',
                       'texte': '. '.join(f'{label} : {initial}' for _, label, initial, _, _ in actifs) + '.'}]

            def modifier(index, correction=False):
                cle, label, _, changement, valeur_corrigee = actifs[index]
                valeur = valeur_corrigee if correction else changement
                etapes.append({'titre': 'Mise à jour', 'evenement': 'mise_a_jour',
                               'champ': cle, 'nouveau': valeur,
                               'texte': f'{label} : désormais {valeur}. Conserve les autres éléments mémorisés.'})
                etat[cle] = valeur

            modifier(pivot)
            if palier >= 2:
                modifier((pivot + 1) % len(actifs))
            if palier == 3:
                etapes.insert(2, {'titre': 'Message reçu', 'evenement': 'autre_tache',
                                  'texte': 'Le même service annonce une opération le mois prochain pour un autre groupe.'})
                modifier(pivot, correction=True)
                # Un dernier champ change ; au moins un élément initial doit être conservé.
                dernier = next(i for i in range(len(actifs)) if i not in {pivot, (pivot + 1) % len(actifs)})
                modifier(dernier)
            contenu = {
                'enonce': titre + ' — restitue la consigne finale.',
                'consigne': 'Lis chaque message à ton rythme. Il sera masqué au suivant. Garde ce qui reste valable et remplace seulement ce qui change.',
                'methode': 'Reformule la consigne en quelques éléments. À chaque message, remplace l’élément modifié puis répète mentalement la version à jour.',
                'etat_initial': {cle: initial for cle, _, initial, _, _ in actifs},
                'etapes': etapes, 'champs': [{'id': cle, 'label': label} for cle, label, *_ in actifs],
            }
            items.append(item('actualiser-consigne', palier, numero, contenu, etat,
                              ['memoire-travail', 'inhibition']))
        resultat.append(items)
    return resultat


DOCUMENTS = [
 ('Réservation de salle',[('jour','Jour','jeudi','vendredi'),('debut','Début','14 h','15 h'),('duree','Durée','90 minutes','60 minutes'),('salle','Salle','Orion','Atlas'),('places','Places','12','10'),('equipement','Équipement','vidéoprojecteur','écran seul')]),
 ('Confirmation de voyage',[('date','Date','18 novembre','19 novembre'),('depart','Départ','8 h 20','8 h 40'),('destination','Destination','Lyon','Dijon'),('voyageurs','Voyageurs','2','1'),('classe','Classe','seconde','première'),('retour','Retour','20 novembre','21 novembre')]),
 ('Commande de matériel',[('ref','Référence','AX-24','AX-42'),('quantite','Quantité','6','8'),('prix','Prix total','480 euros','840 euros'),('delai','Livraison','12 octobre','14 octobre'),('adresse','Adresse','18 rue des Pins','81 rue des Pins'),('garantie','Garantie','24 mois','12 mois')]),
 ('Inscription à une formation',[('intitule','Intitulé','Analyse de données','Gestion de projet'),('date','Date','7 décembre','8 décembre'),('duree','Durée','2 jours','1 jour'),('format','Format','à distance','sur place'),('tarif','Tarif','320 euros','350 euros'),('attestation','Attestation','incluse','non incluse')]),
 ('Devis de travaux',[('lot','Lot','bibliothèque','bureau'),('debut','Début','4 mai','14 mai'),('duree','Durée','3 jours','5 jours'),('montant','Montant','2 850 euros','2 580 euros'),('peinture','Finition','mate','satinée'),('acompte','Acompte','30 %','40 %')]),
 ('Programme de colloque',[('session','Session','Neurosciences','Éthique'),('jour','Jour','vendredi','jeudi'),('heure','Horaire','10 h 15','10 h 45'),('salle','Salle','Aubrac','Aurore'),('intervenant','Intervenante','L. Martin','L. Martineau'),('langue','Langue','français','anglais')]),
 ('Contrat de location',[('adresse','Adresse','24 rue Hugo','42 rue Hugo'),('debut','Prise d’effet','1er juin','1er juillet'),('duree','Durée','12 mois','10 mois'),('loyer','Loyer','940 euros','980 euros'),('charges','Charges','80 euros','60 euros'),('depot','Dépôt','940 euros','1 880 euros')]),
 ('Ordre de mission',[('ville','Destination','Nantes','Rennes'),('depart','Départ','3 février','4 février'),('retour','Retour','5 février','6 février'),('transport','Transport','train','voiture'),('hotel','Hôtel','Grand Hôtel','Hôtel Central'),('plafond','Plafond repas','25 euros','35 euros')]),
 ('Invitation culturelle',[('spectacle','Spectacle','Le Cid','Cyrano'),('date','Date','16 avril','18 avril'),('heure','Horaire','20 h 30','20 h'),('lieu','Lieu','Théâtre Nord','Théâtre Neuf'),('places','Places','balcon B12-B13','orchestre B12-B13'),('tarif','Tarif total','76 euros','67 euros')]),
 ('Dossier d’assurance',[('contrat','Contrat','Habitat 284','Habitat 248'),('sinistre','Référence','S-1038','S-1083'),('date','Date déclarée','9 janvier','19 janvier'),('montant','Franchise','180 euros','280 euros'),('expert','Expert','Mme Simon','M. Simon'),('visite','Visite','22 janvier','24 janvier')]),
 ('Planning associatif',[('activite','Activité','atelier lecture','atelier écriture'),('jour','Jour','mercredi','vendredi'),('heure','Horaire','18 h','18 h 30'),('salle','Salle','3','8'),('animateur','Animateur','M. Lopez','Mme Lopez'),('capacite','Capacité','14','12')]),
 ('Réservation de restaurant',[('nom','Nom','Le Rivage','Le Virage'),('date','Date','12 septembre','21 septembre'),('heure','Horaire','19 h 45','20 h 15'),('couverts','Couverts','5','6'),('menu','Menu','végétarien','dégustation'),('acompte','Acompte','50 euros','80 euros')]),
]


def comparer():
    resultat = []
    for palier in range(1, 4):
        items = []
        for numero, (titre, lignes) in enumerate(DOCUMENTS, 1):
            actifs = lignes[:2 * palier]
            rng = random.Random(f'doc-v2:{palier}:{numero}')
            nb_ecarts = 0 if numero in {3, 8, 12} else (1 if palier == 1 else 1 + (numero + palier) % palier)
            faux = set(rng.sample([ligne[0] for ligne in actifs], nb_ecarts))
            gauche = [{'id': cle, 'label': label, 'texte': valeur} for cle, label, valeur, _ in actifs]
            droite = [{'id': cle, 'label': label, 'texte': autre if cle in faux else valeur}
                      for cle, label, valeur, autre in actifs]
            if palier >= 2:
                rng.shuffle(droite)
            contenu = {
                'enonce': titre + ' — vérifie chaque point de la confirmation.',
                'consigne': 'Les deux documents restent consultables. Pour chaque point, indique si la confirmation respecte la demande. Une confirmation peut être entièrement conforme.',
                'methode': 'Prends un critère de la demande, retrouve-le dans la confirmation, compare sa valeur puis passe au suivant. Termine par une vérification des points non traités.',
                'documents': [{'titre': 'Demande', 'lignes': gauche}, {'titre': 'Confirmation', 'lignes': droite}],
                'champs': [{'id': cle, 'label': label} for cle, label, *_ in actifs],
            }
            reponse = {cle: ('ecart' if cle in faux else 'conforme') for cle, *_ in actifs}
            items.append(item('comparer-documents', palier, numero, contenu, reponse,
                              ['attention-selective', 'fonctions-executives']))
        resultat.append(items)
    return resultat


# but, contexte, référence courte, nouvel horaire, autre tâche, rappel connu,
# nouvelle préparation, autre action nécessaire, information connexe facultative
FLUX = [
 ('Préparer le déplacement pour la conférence de jeudi à Lyon','Train jeudi à 8 h 20, quai 3. Billet enregistré. Badge fourni sur place.','la conférence de jeudi','8 h 40','Le train de vendredi pour Lyon partira à 8 h 40.','Le train pour la conférence est annoncé jeudi à 8 h 20.','Imprime désormais le badge avant le départ.','L’entrée se fera rue Pasteur plutôt que rue Curie.','Une formule de restauration peut être réservée.'),
 ('Préparer la réunion Atlas de mardi','Réunion mardi à 14 h, salle 2. Quatre participants. Dossier version 3 prêt.','la réunion Atlas','14 h 30','La réunion Orion de mardi passe à 14 h 30.','La salle 2 accueille la réunion Atlas mardi à 14 h.','Prépare un cinquième exemplaire pour le participant ajouté.','La réunion aura finalement lieu à distance.','Le café du hall propose une nouvelle carte.'),
 ('Réceptionner la commande AX-24 jeudi','Six unités AX-24 jeudi, entrée nord. Bon prêt. Paiement après livraison.','la commande AX-24','vendredi','La commande AX-42 arrivera vendredi.','Six unités AX-24 sont annoncées pour jeudi.','Fais signer le bon avant la réception.','Accueille le livreur à l’entrée est plutôt qu’au nord.','Le catalogue présente aussi des accessoires pour AX-24.'),
 ('Préparer l’atelier de samedi','Atelier samedi à 10 h, huit inscrits. Ordinateur chargé. Supports disponibles sur place.','l’atelier de samedi','11 h','L’atelier de dimanche commencera à 11 h.','Huit personnes sont inscrites samedi à 10 h.','Télécharge les supports avant de venir.','Présente-toi à l’annexe plutôt qu’à l’entrée principale.','La bibliothèque publie son programme trimestriel.'),
 ('Finaliser le dossier Habitat 284','Dossier Habitat 284 à envoyer lundi avant 17 h. Pièces et signature réunies.','le dossier Habitat 284','mardi avant 12 h','Le dossier Auto 284 doit partir mardi avant 12 h.','Le dépôt du dossier Habitat 284 est prévu lundi avant 17 h.','Ajoute l’attestation fiscale reçue ce matin.','Dépose le dossier sur le portail plutôt que par courriel.','Une brochure explique les garanties optionnelles.'),
 ('Organiser le dîner de vendredi','Table vendredi à 20 h pour cinq personnes au Rivage. Menu végétarien signalé.','le dîner de vendredi','20 h 30','La réservation de samedi est avancée à 20 h 30.','La table du vendredi est inscrite à 20 h pour cinq.','Préviens le restaurant qu’une sixième personne vient.','Rends-toi au Jardin : le Rivage transfère la réservation.','Le chef publie une recette sur le site du restaurant.'),
 ('Préparer la visite du chantier mardi','Visite mardi à 9 h, entrée ouest. Casque disponible sur place.','la visite du chantier','9 h 45','La livraison du chantier arrivera mardi à 9 h 45.','Le rendez-vous de visite figure mardi à 9 h.','Apporte désormais tes propres chaussures de sécurité.','Entre par le portail sud plutôt que par l’ouest.','Le bulletin météo annonce un ciel couvert.'),
 ('Participer à la formation Analyse de données','Formation lundi à 9 h, salle Vega. Ordinateur fourni. Support imprimé.','la formation Analyse de données','9 h 30','La formation Gestion de projet commence à 9 h 30.','La session Analyse de données est inscrite lundi à 9 h.','Installe le logiciel indiqué avant la séance.','Rejoins la salle Atlas plutôt que Vega.','Le centre propose un webinaire facultatif le mois prochain.'),
 ('Préparer le rendez-vous fiscal','Rendez-vous jeudi à 15 h, centre B. Déclaration et justificatifs prêts.','le rendez-vous fiscal','16 h','Le rendez-vous bancaire de jeudi passe à 16 h.','Le centre B attend le dossier fiscal jeudi à 15 h.','Ajoute le relevé annuel demandé dans le dernier message.','Présente-toi au centre C plutôt qu’au centre B.','Le site publie un guide général sur les déductions.'),
 ('Coordonner l’intervention de plomberie','Intervention mercredi entre 13 h et 15 h. Accès par la cour. Gardien présent.','l’intervention de plomberie','16 h–18 h','Le contrôle électrique est fixé mercredi de 16 h à 18 h.','Le plombier dispose du créneau de 13 h à 15 h mercredi.','Transmets au gardien la photo de la fuite avant midi.','Ouvre le garage plutôt que la cour intérieure.','L’entreprise propose un contrat annuel d’entretien.'),
 ('Préparer la présentation du projet Rivage','Présentation vendredi à 11 h, auditorium. Version 6 sur la tablette.','la présentation Rivage','11 h 45','La présentation Atlas commencera vendredi à 11 h 45.','L’auditorium est réservé vendredi à 11 h pour Rivage.','Ajoute la diapositive financière reçue ce matin.','Utilise la version 7 envoyée par la direction.','Une conférence publique occupera le hall en soirée.'),
 ('Organiser le retrait du colis 684','Retrait samedi à partir de 10 h, bureau 4. Pièce d’identité prête.','le retrait du colis 684','11 h 30','Le colis 648 sera disponible samedi à 11 h 30.','Le colis 684 est inscrit au bureau 4 dès 10 h.','Apporte aussi le code imprimé reçu par courriel.','Va au bureau 7 plutôt qu’au bureau 4.','Le transporteur propose une enquête de satisfaction.'),
]


def reperer():
    resultat = []
    criteres = ['Uniquement les changements d’horaire ou de date de ta tâche.',
                'Les changements d’horaire ou de date, ainsi que les nouvelles préparations à effectuer pour ta tâche.',
                'Tous les changements qui nécessitent une action pour ta tâche.']
    for palier in range(1, 4):
        items = []
        for numero, (but, contexte, cible, heure, autre, rappel, preparation, action, connexe) in enumerate(FLUX, 1):
            messages = [(f'{cible.capitalize()} est désormais prévu pour {heure}.','horaire','Le moment prévu pour ta tâche est modifié.'),
                        (autre,'autre','Le message concerne une autre tâche.'),
                        (rappel,'rappel','Le message reprend une information déjà connue.'),
                        (preparation,'preparation','Une préparation nouvelle est demandée.'),
                        (connexe,'connexe','Cette possibilité ne modifie pas ce que tu dois faire.'),
                        (action,'action','Une autre action nécessaire est modifiée.')]
            # Le nombre de sélections n'est pas une règle cachée à apprendre.
            if palier == 2 and numero % 3 == 0:
                messages.pop(3)
            if palier == 3 and numero % 2 == 0:
                messages.pop()
            rng = random.Random(f'flux-v2:{palier}:{numero}')
            rng.shuffle(messages)
            categories = {'horaire'} if palier == 1 else ({'horaire','preparation'} if palier == 2 else {'horaire','preparation','action'})
            flux, reponse, explications = [], {}, {}
            for index, (texte, categorie, explication) in enumerate(messages, 1):
                cle = f'm{index}'
                flux.append({'id': cle, 'texte': texte})
                reponse[cle] = 'oui' if categorie in categories else 'non'
                explications[cle] = explication if categorie in categories or categorie in {'autre','rappel','connexe'} else 'Ce changement ne relève pas des critères affichés.'
            contenu = {'enonce': but, 'objectif': contexte, 'critere': criteres[palier - 1],
                       'consigne': 'Pour chaque message, décide s’il change la tâche selon les critères affichés. Compare le message au but et aux informations déjà connues.',
                       'methode': 'Relis le but et les critères. Identifie d’abord la tâche concernée, puis compare l’information au plan actuel. Ne retiens que ce qui répond aux critères.',
                       'messages': flux}
            objet = item('reperer-essentiel', palier, numero, contenu, reponse,
                         ['attention-selective', 'inhibition'])
            objet['reponse']['explications'] = explications
            items.append(objet)
        resultat.append(items)
    return resultat


DESCRIPTIONS = {
 'actualiser-consigne':['Deux éléments, un remplacement','Trois éléments, deux mises à jour','Quatre éléments, correction d’une correction et message connexe'],
 'comparer-documents':['Deux points à comparer','Quatre points dans un ordre différent','Six points, ordre différent et valeurs proches'],
 'reperer-essentiel':['Un critère temporel','Deux catégories de changements','Tous les changements nécessitant une action'],
}


def construire():
    return {'actualiser-consigne': actualiser(), 'comparer-documents': comparer(),
            'reperer-essentiel': reperer()}


def main():
    for theme, paliers in construire().items():
        base = ROOT / 'content/entrainement' / theme
        (base / 'paliers').mkdir(parents=True, exist_ok=True)
        manifeste = {'theme': theme, 'paliers': []}
        for numero, items in enumerate(paliers, 1):
            fichier = f'paliers/palier-{numero:02}.json'
            (base / fichier).write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n')
            manifeste['paliers'].append({'id': f'{theme}-palier-{numero}',
                 'description': DESCRIPTIONS[theme][numero - 1], 'prerequis': [],
                 'fichier': fichier, 'nb_items': len(items)})
        (base / 'paliers.json').write_text(json.dumps(manifeste, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
