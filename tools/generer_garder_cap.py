"""Situations originales de reprise, adaptation et contrôle, inspirées de stratégies métacognitives."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
    base=ROOT/'content/entrainement/garder-cap';(base/'paliers').mkdir(parents=True,exist_ok=True)
    paliers=construire()
    manifest={'theme':'garder-cap','paliers':[{'id':f'cap-palier-{n}','description':SERIES[n-1][0], 'prerequis':[] if n==1 else [f'cap-palier-{n-1}'], 'fichier':f'paliers/palier-{n:02}.json','nb_items':len(items)} for n,items in enumerate(paliers,1)]}
    for n,items in enumerate(paliers,1):
        (base/f'paliers/palier-{n:02}.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
    (base/'paliers.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
