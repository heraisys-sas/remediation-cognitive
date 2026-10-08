"""Situations originales de reprise, adaptation et contrôle, inspirées de stratégies métacognitives."""

try:
    from tools.generation import ecrire_json, arguments_generation
except ModuleNotFoundError:
    from generation import ecrire_json, arguments_generation
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Une tâche de contrôle réellement commencée, interrompue après 1, 2 ou 3 points,
# puis reprise. L'interruption occupe brièvement l'attention mais n'est pas notée.
REPRISES = [
 ('Finaliser un dossier associatif','Le dossier doit être complet et cohérent avant son dépôt.',[
   ('formulaire','Formulaire','Le formulaire principal est rempli et signé.','valide'),
   ('budget','Budget','Le budget total a été recalculé et validé.','valide'),
   ('annexe','Annexe','Le brouillon contient encore l’ancienne annexe B.','reprendre'),
   ('pieces','Pièces','Les trois justificatifs demandés sont joints.','valide')]),
 ('Préparer un déplacement professionnel','Tous les éléments du déplacement doivent correspondre aux dates retenues.',[
   ('train','Train','Le billet correspond au départ du 18 novembre.','valide'),
   ('hotel','Hôtel','La chambre est réservée du 19 au 21 au lieu du 18 au 20.','reprendre'),
   ('identite','Identité','La pièce d’identité est disponible et valide.','valide'),
   ('transfert','Transfert','Aucun trajet entre la gare et l’hôtel n’est réservé.','reprendre')]),
 ('Préparer une réunion hybride','La réunion doit être accessible sur place et à distance avec les bons documents.',[
   ('ordre','Ordre du jour','L’ordre du jour final a été envoyé.','valide'),
   ('salle','Salle','La réservation porte encore sur Atlas alors que la réunion passe en Vega.','reprendre'),
   ('participants','Participants','Les six participants ont répondu.','valide'),
   ('lien','Lien distant','L’invitation contient le lien de la réunion précédente.','reprendre')]),
 ('Vérifier une commande de matériel','La commande doit respecter la référence, la quantité, le budget et le lieu de livraison.',[
   ('reference','Référence','La référence AX-24 figure sur le bon.','valide'),
   ('quantite','Quantité','Le bon indique huit unités au lieu de six.','reprendre'),
   ('budget','Budget','Le total de 480 euros respecte le plafond.','valide'),
   ('livraison','Livraison','L’adresse correspond à l’ancien site.','reprendre')]),
 ('Clore une note de synthèse','La note et ses annexes doivent utiliser les mêmes données actualisées.',[
   ('texte','Texte','Les chiffres du texte proviennent de la version 7.','valide'),
   ('tableau','Tableau','Le tableau central utilise encore la version 6.','reprendre'),
   ('graphique','Graphique','Le graphique a été recalculé depuis la version 7.','valide'),
   ('export','Export','Le PDF final a été produit avant la dernière correction.','reprendre')]),
 ('Préparer une inscription à une formation','Le dossier doit correspondre à la session choisie et être complet.',[
   ('session','Session','La session du 8 décembre est sélectionnée.','valide'),
   ('identite','Identité','Le nom comporte une inversion de deux lettres.','reprendre'),
   ('accord','Accord','L’accord de prise en charge est joint.','valide'),
   ('format','Format','Le formulaire mentionne sur place au lieu d’à distance.','reprendre')]),
 ('Organiser un atelier public','Le matériel, le lieu, l’horaire et la capacité doivent suivre la fiche validée.',[
   ('materiel','Matériel','Le vidéoprojecteur est réservé.','valide'),
   ('lieu','Lieu','L’affiche indique la salle 3 au lieu de la salle 5.','reprendre'),
   ('horaire','Horaire','Le début à 18 h 30 est correctement annoncé.','valide'),
   ('capacite','Capacité','Le formulaire accepte encore 18 inscriptions pour une limite de 14.','reprendre')]),
 ('Contrôler une facture avant paiement','La facture doit correspondre au devis et aux paiements déjà enregistrés.',[
   ('fournisseur','Fournisseur','Le nom et le compte bancaire correspondent au devis.','valide'),
   ('montant','Montant','Le total est de 1 840 euros au lieu de 1 480 euros.','reprendre'),
   ('acompte','Acompte','L’acompte de 480 euros est bien déduit.','valide'),
   ('reference','Référence','La facture porte F81 au lieu de F18.','reprendre')]),
 ('Préparer une visite de chantier','Les informations transmises doivent permettre l’accès et respecter les consignes.',[
   ('date','Date','La visite est indiquée mardi 12 octobre.','valide'),
   ('acces','Accès','Le message conseille l’entrée nord, désormais fermée.','reprendre'),
   ('equipement','Équipement','Le port de chaussures de sécurité est mentionné.','valide'),
   ('contact','Contact','Le numéro indiqué appartient à l’ancien responsable.','reprendre')]),
 ('Finaliser une réservation culturelle','La réservation doit correspondre au spectacle, aux personnes et aux contraintes choisies.',[
   ('spectacle','Spectacle','Le billet porte bien Le Cid.','valide'),
   ('date','Date','La confirmation indique le 18 avril au lieu du 16.','reprendre'),
   ('places','Places','Deux places contiguës sont attribuées.','valide'),
   ('acces','Accès','La demande d’accès sans escalier n’apparaît pas.','reprendre')]),
 ('Préparer un dossier d’assurance','Les références et pièces doivent permettre le traitement du sinistre déclaré.',[
   ('contrat','Contrat','Le numéro Habitat 284 est exact.','valide'),
   ('sinistre','Sinistre','La référence saisie est S-1083 au lieu de S-1038.','reprendre'),
   ('photos','Photos','Les quatre photos demandées sont jointes.','valide'),
   ('date','Date','La déclaration porte le 19 janvier au lieu du 9.','reprendre')]),
 ('Publier un programme associatif','Le programme publié doit reprendre les décisions du dernier comité.',[
   ('activite','Activité','L’atelier lecture apparaît dans le programme.','valide'),
   ('animateur','Animateur','Le nom affiché est celui de l’animateur remplacé.','reprendre'),
   ('horaire','Horaire','Le créneau du mercredi à 18 h est exact.','valide'),
   ('contact','Contact','Le courriel renvoie vers une adresse qui n’est plus utilisée.','reprendre')]),
]

INTERRUPTIONS = [
 ('Quel mot désigne un moyen de transport ?', ['Train','Dossier','Budget']),
 ('Quel nombre vient juste après 27 ?', ['26','28','37']),
 ('Quel mot appartient à la catégorie des lieux ?', ['Bibliothèque','Signature','Mercredi']),
 ('Quelle proposition est une couleur ?', ['Vega','Orange','Facture']),
 ('Quel objet sert à écrire ?', ['Stylo','Billet','Salle']),
 ('Quel mois vient après avril ?', ['Mars','Mai','Juin']),
 ('Quel mot désigne un document ?', ['Annexe','Portail','Matin']),
 ('Quel nombre est le plus grand ?', ['18','81','28']),
 ('Quel mot désigne une personne ?', ['Trésorier','Guichet','Contrat']),
 ('Quel jour vient avant vendredi ?', ['Jeudi','Samedi','Mardi']),
 ('Quel mot désigne une action ?', ['Vérifier','Atlas','Facture']),
 ('Quelle proposition est une durée ?', ['Deux heures','Mardi','Centre B']),
]
# Situation, choix justifié, alternatives liées à la même tâche.
SERIES = [('Reprendre après une interruption',
  'Arrête-toi un instant, retrouve le but et le dernier point achevé, puis choisis la prochaine action.',
  [('Tu finalises un dossier avant 16 h. Le formulaire et le budget sont validés. Avant un appel, tu as noté '
    ': « remplacer l’annexe B par la version signée, puis contrôler les pièces ». Pendant l’appel, on '
    'confirme que le budget ne change pas. Le brouillon contient encore l’annexe B non signée. Quelle '
    'reprise évite à la fois un oubli et un travail inutile ?',
    'Remplacer B, contrôler les pièces, puis envoyer',
    ['Revalider le budget, contrôler les pièces, puis envoyer',
     'Remplacer B, envoyer, puis contrôler les pièces']),
   ('Tu compares trois offres selon deux critères obligatoires : livraison vendredi et installation incluse. '
    'A échoue sur la date ; B satisfait les deux critères ; C est moins chère mais son installation reste à '
    'confirmer. Après une interruption, la confirmation arrive : C ne comprend pas l’installation. Quelle '
    'suite exploite correctement le travail déjà fait ?',
    'Retenir B et consigner pourquoi A et C sont écartées',
    ['Retenir C pour son prix et consigner sa livraison',
     'Redemander les trois offres avant de relire les critères']),
   ('Tu prépares une note avec des chiffres actualisés. Les sections 1 et 2 sont vérifiées. Ta note de '
    'reprise précise : « tableau 3 actualisé, commentaire 3 encore ancien ». Une pause interrompt ton '
    'travail. Quelle action permet de reprendre sans conserver une contradiction ?',
    'Revoir le commentaire 3 à partir du tableau actualisé',
    ['Recalculer le tableau 3 en conservant son commentaire',
     'Uniformiser la présentation des trois sections avant l’envoi']),
   ('Trois inscriptions sont suivies dans un tableau. A est confirmée ; B attendait une pièce désormais '
    'reçue ; C est complète mais ne peut être envoyée qu’après B. Tu reprends après un appel, avec dix '
    'minutes disponibles. Quelle séquence respecte les dépendances ?',
    'Finaliser B, puis transmettre C',
    ['Transmettre C, puis finaliser B', 'Vérifier de nouveau A, puis transmettre C'])]),
 ('Adapter le plan à un changement',
  'Repère ce qui a changé, garde le but et les contraintes encore valables, puis ajuste seulement ce qui est '
  'nécessaire.',
  [('Tu dois arriver avant 10 h avec un budget maximal de 25 €. Le train prévu est annulé. Bus A : arrivée 9 '
    'h 50, 18 € ; bus B : arrivée 10 h 05, 12 € ; taxi : arrivée 9 h 40, 38 €. Les documents sont déjà '
    'prêts. Quel ajustement conserve les contraintes ?',
    'Choisir le bus A et conserver les documents prêts',
    ['Choisir le bus B et conserver les documents prêts',
     'Choisir le taxi et conserver les documents prêts']),
   ('Le dépôt d’un dossier doit être terminé avant 17 h, avec une preuve horodatée. Le guichet ferme '
    'exceptionnellement à 15 h. À 15 h 30, tu disposes d’un portail ouvert jusqu’à 17 h avec reçu immédiat, '
    'd’un courriel avec accusé manuel demain, ou d’un envoi postal suivi livré demain.',
    'Utiliser le portail et conserver son reçu',
    ['Envoyer le courriel et conserver la copie envoyée',
     'Utiliser le courrier suivi et conserver le numéro']),
   ('La réunion exige six personnes et un accès distant confidentiel. La salle initiale est indisponible. A '
    ': huit places, visioconférence, espace partagé ; B : six places, visioconférence, salle fermée ; C : '
    'six places, salle fermée, sans réseau. Quel remplacement conserve les deux exigences ?',
    'Réserver B avec son équipement de visioconférence',
    ['Réserver A avec son équipement de visioconférence', 'Réserver C et conserver l’horaire prévu']),
   ('Une intervention de 30 minutes était prévue entre 14 h et 15 h. Elle doit désormais durer 45 minutes, '
    'après la livraison de matériel à 14 h 10 et avant une autre activité fixe à 15 h. Quel créneau reste '
    'compatible ?',
    '14 h 10–14 h 55',
    ['14 h–14 h 45', '14 h 20–15 h 05'])]),
 ('Vérifier avant de terminer',
  'Compare le résultat avec toutes les conditions du but. Une tâche presque terminée peut encore manquer '
  'd’un élément essentiel.',
  [('Tu dois transmettre à Léa un devis signé de 1 480 € avec l’annexe révisée. Le brouillon affiche Léa et '
    'les deux pièces. Le devis joint est signé, mais indique 1 840 € ; l’annexe est bien la dernière '
    'version. Quel contrôle appelle une correction avant l’envoi ?',
    'Faire corriger puis signer le devis au montant convenu',
    ['Conserver le devis signé et actualiser l’annexe',
     'Modifier seulement le montant dans le texte du courriel']),
   ('Tu réserves deux billets pour samedi, départ après 18 h et arrivée avant 21 h. Le récapitulatif indique '
    'deux voyageurs, samedi, départ 18 h 20, arrivée 21 h 10. Quel point faut-il corriger ?',
    'Choisir un trajet dont l’arrivée est avant 21 h',
    ['Choisir un trajet dont le départ est avant 18 h',
     'Conserver le trajet et modifier le nombre de voyageurs']),
   ('La facture F18 est de 160 €. Un acompte F18 de 80 € a déjà été encaissé ; le solde dû est donc distinct '
    'de cet acompte. Deux ordres futurs F18 de 80 € sont programmés. Quel ajustement règle exactement la '
    'facture sans annuler le solde ?',
    'Conserver un seul des deux ordres futurs',
    ['Conserver les deux ordres futurs', 'Annuler les deux ordres futurs']),
   ('Le livrable doit être un PDF avec les chiffres révisés et un graphique cohérent. Les chiffres ont été '
    'corrigés dans la source après le dernier export ; le graphique de la source utilise encore les '
    'anciennes valeurs. Quelle clôture satisfait toutes les conditions ?',
    'Actualiser le graphique, exporter le PDF, puis vérifier le PDF',
    ['Exporter le PDF, puis vérifier seulement les chiffres du tableau',
     'Actualiser le graphique, puis renommer le dernier PDF exporté'])])]


def construire():
    paliers=[]
    for n, (titre,methode,cas) in enumerate(SERIES,1):
        items=[]
        if n == 1:
            for i,(nom,but,points) in enumerate(REPRISES,1):
                question,options=INTERRUPTIONS[i-1]
                points=list(points)
                random.Random(f'cap-reprise-points:{i}').shuffle(points)
                apres=1+(i-1)%3
                prochain=points[apres][0]
                items.append({'id':f'cap-2-reprise-{i:02}','type':'reprise-interrompue',
                    'module':'entrainement','theme':'garder-cap',
                    'fonctions_ciblees':['fonctions-executives','planification','memoire-travail'],
                    'palier':1,'prerequis':[],'cap_complexite':None,
                    'contenu':{'enonce':nom,'but':but,
                        'points':[{'id':cle,'label':label,'etat':etat,
                                   'options':['Déjà validé','À reprendre']}
                                  for cle,label,etat,_ in points],
                        'interruption_apres':apres,
                        'interruption':{'enonce':question,'options':options},
                        'methode':'Avant l’interruption, avance point par point. Après le détour, retrouve le dernier point traité et reprends au suivant.',
                        'consigne':'Commence le contrôle. Un bref message interrompra réellement la tâche ; réponds-y, puis retrouve où reprendre sans contrainte de temps.'},
                    'reponse':{'valeur':{'points':{cle:etat for cle,_,_,etat in points},
                                           'reprise':prochain}},
                    'meta':{'auteur':'redaction-assistee (tools/generer_garder_cap.py)',
                            'date_creation':'2026-10-02','relecture_ortho':{'statut':'a_revoir'}}})
            paliers.append(items)
            continue
        for i,(situation,bonne,leurres) in enumerate(cas,1):
            options=[bonne,*leurres];random.Random(f'cap:{n}:{i}').shuffle(options)
            items.append({'id':f'cap-1-{n}-{i:02}', 'type':'but-etapes','module':'entrainement','theme':'garder-cap',
                'fonctions_ciblees':['fonctions-executives','planification'] if n!=2 else ['fonctions-executives','flexibilite'],
                'palier':n,'prerequis':[] if n==1 else [f'cap-palier-{n-1}'],'cap_complexite':None,
                'contenu':{'enonce':situation,'options':options,'methode':methode,
                    'consigne':'Lis la situation à ton rythme. Choisis l’action qui respecte le but et toutes les contraintes ; les informations restent visibles.'},
                'reponse':{'valeur':bonne},'meta':{'auteur':'redaction-assistee (tools/generer_garder_cap.py)','date_creation':'2026-09-30','relecture_ortho':{'statut':'a_revoir'}}})
        paliers.append(items)
    return paliers


def main():
    options = arguments_generation(__doc__)
    base=ROOT/'content/entrainement/garder-cap'
    paliers=construire()
    descriptions=['Reprendre une tâche après une interruption réellement vécue', SERIES[1][0], SERIES[2][0]]
    manifest={'theme':'garder-cap','paliers':[{'id':f'cap-palier-{n}','description':descriptions[n-1], 'prerequis':[] if n==1 else [f'cap-palier-{n-1}'], 'fichier':f'paliers/palier-{n:02}.json','nb_items':len(items)} for n,items in enumerate(paliers,1)]}
    for n,items in enumerate(paliers,1):
        ecrire_json(base/f'paliers/palier-{n:02}.json', items, dry_run=options.dry_run)
    ecrire_json(base/'paliers.json', manifest, dry_run=options.dry_run)

if __name__=='__main__':main()
