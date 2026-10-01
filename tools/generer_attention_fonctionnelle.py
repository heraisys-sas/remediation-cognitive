#!/usr/bin/env python3
"""Situations adultes : actualiser, comparer, sélectionner. Données reproductibles.

Chaque palier augmente une charge identifiable ; aucune vitesse imposée.
Les réponses dérivent de changements explicites ou de comparaisons vérifiables.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = {'auteur':'redaction-assistee (tools/generer_attention_fonctionnelle.py)',
        'date_creation':'2026-10-01','relecture_ortho':{'statut':'a_revoir'}}

def item(theme, n, i, contenu, reponse, fonction):
    return {'id':f'{theme}-v1-{n}-{i:02}', 'module':'entrainement', 'theme':theme,
            'type':theme,'palier':n,'prerequis':[], 'fonctions_ciblees':fonction,
            'contenu':contenu,'reponse':{'valeur':reponse},'meta':META.copy()}

# Une consigne concrète et trois attributs indépendants. P1 : deux attributs, un changement.
# P2 : trois attributs, deux changements. P3 : correction d'une correction + information hors sujet.
CAS = [
 ('Préparer une réunion', [('heure','Horaire','14 h','15 h','16 h'),
  ('lieu','Salle','Atlas','Orion','Vega'),('piece','Document à apporter','budget','aucun','contrat')]),
 ('Organiser un retrait de dossier', [('jour','Jour','mardi','jeudi','vendredi'),
  ('lieu','Lieu','accueil','bureau 12','secrétariat'),('piece','Pièce à présenter','badge','aucune','convocation')]),
 ('Préparer une livraison', [('heure','Horaire','10 h','11 h','12 h'),
  ('lieu','Entrée','nord','sud','est'),('piece','Document à remettre','bon de commande','aucun','facture')]),
 ('Organiser une visite', [('jour','Jour','lundi','mercredi','samedi'),
  ('lieu','Rendez-vous','gare','musée','bibliothèque'),('piece','Document à emporter','plan','aucun','billet')]),
]

def actualiser():
    paliers=[]
    for n in range(1,4):
        items=[]
        for i,(titre,champs) in enumerate(CAS,1):
            actifs=champs[:2] if n==1 else champs
            # Alterner le champ modifié : ne pas apprendre une position fixe.
            pivot=(i-1)%2
            premier=actifs[pivot]
            etapes=[{'titre':'Consigne initiale', 'texte':'. '.join(f'{label} : {val}' for _,label,val,*_ in actifs)+'.'}]
            reponse={key:val for key,_,val,*_ in actifs}
            changements=[(premier[0],premier[1],premier[3])]
            if n>=2: changements.append((actifs[2][0],actifs[2][1],actifs[2][3]))
            if n==3:
                changements.extend([(premier[0],premier[1],premier[4]), (actifs[1-pivot][0],actifs[1-pivot][1],actifs[1-pivot][3])])
            for key,label,val in changements:
                etapes.append({'titre':'Mise à jour', 'texte':f'{label} : désormais {val}. Les autres informations restent valables.'})
                reponse[key]=val
            if n==3:
                etapes.insert(2,{'titre':'Information séparée','texte':'Une autre équipe prépare une activité la semaine prochaine. Cela ne change rien à ta consigne.'})
            contenu={'enonce':titre+' — restitue la consigne finale.',
              'consigne':'Lis chaque message à ton rythme. Il sera masqué au suivant. Garde ce qui reste valable et remplace seulement ce qui change.',
              'methode':'Reformule la consigne en quelques éléments. À chaque message, remplace l’élément modifié et répète mentalement la version à jour.',
              'etapes':etapes,'champs':[{'id':k,'label':l} for k,l,*_ in actifs]}
            items.append(item('actualiser-consigne',n,i,contenu,reponse,['memoire-travail','inhibition']))
        paliers.append(items)
    return paliers

DOCUMENTS = [
 ('Réservation de salle', [('jour','Jour','jeudi','vendredi'),('debut','Début','14 h','15 h'),
  ('duree','Durée','90 minutes','60 minutes'),('salle','Salle','Orion','Atlas'),
  ('places','Places','12','10'),('equipement','Équipement','vidéoprojecteur','écran seul')]),
 ('Confirmation de voyage', [('date','Date','18 novembre','19 novembre'),('depart','Départ','8 h 20','8 h 40'),
  ('destination','Destination','Lyon','Dijon'),('voyageurs','Voyageurs','2','1'),
  ('classe','Classe','seconde','première'),('retour','Retour','20 novembre','21 novembre')]),
 ('Commande de matériel', [('ref','Référence','AX-24','AX-42'),('quantite','Quantité','6','8'),
  ('prix','Prix total','480 euros','840 euros'),('delai','Livraison','12 octobre','14 octobre'),
  ('adresse','Adresse','18 rue des Pins','81 rue des Pins'),('garantie','Garantie','24 mois','12 mois')]),
 ('Inscription à une formation', [('intitule','Intitulé','Analyse de données','Gestion de projet'),
  ('date','Date','7 décembre','8 décembre'),('duree','Durée','2 jours','1 jour'),
  ('format','Format','à distance','sur place'),('tarif','Tarif','320 euros','350 euros'),
  ('attestation','Attestation','incluse','non incluse')]),
]

def comparer():
    paliers=[]
    for n in range(1,4):
        items=[]
        for i,(titre,lignes) in enumerate(DOCUMENTS,1):
            actifs=lignes[:2*n]
            rng=random.Random(f'doc:{n}:{i}')
            # Des confirmations entièrement conformes évitent de supposer une erreur partout.
            nb_ecarts=0 if i==4 else n
            faux=set(rng.sample([x[0] for x in actifs],nb_ecarts))
            gauche=[{'id':k,'label':l,'texte':v} for k,l,v,_ in actifs]
            droite=[{'id':k,'label':l,'texte':alt if k in faux else v} for k,l,v,alt in actifs]
            if n>=2: rng.shuffle(droite)
            contenu={'enonce':titre+' — vérifie chaque point de la confirmation.',
              'consigne':'Les deux documents restent consultables. Pour chaque point, indique si la confirmation respecte la demande. Une confirmation peut être entièrement conforme.',
              'methode':'Prends un critère de la demande, retrouve-le dans la confirmation, compare sa valeur puis passe au suivant. Termine par une vérification des points non traités.',
              'documents':[{'titre':'Demande','lignes':gauche},{'titre':'Confirmation','lignes':droite}],
              'champs':[{'id':k,'label':l} for k,l,*_ in actifs]}
            reponse={k:('ecart' if k in faux else 'conforme') for k,*_ in actifs}
            items.append(item('comparer-documents',n,i,contenu,reponse,['attention-selective','fonctions-executives']))
        paliers.append(items)
    return paliers

# Jugement fonctionnel explicite : nouveau / déjà connu, bonne tâche / autre tâche.
FLUX = [
 ('Préparer le déplacement pour la conférence de jeudi à Lyon',
  'Tu pars jeudi pour Lyon, train de 8 h 20, quai 3. Ton billet est enregistré. Le badge est fourni sur place.',
  [('Le train de jeudi à 8 h 20 partira désormais à 8 h 40.','oui','L’horaire de ton train change.'),
   ('Le train de vendredi à 8 h 20 pour Lyon est retardé.','non','Ce message concerne vendredi.'),
   ('Le billet de ton train est confirmé, sans modification.','non','Aucune information nouvelle ne change ta préparation.'),
   ('Pour la conférence de jeudi, il faut désormais imprimer le badge avant le départ.','oui','Une action nouvelle est nécessaire avant le départ.'),
   ('Une offre de restauration est proposée pour le voyage, sans réservation obligatoire.','non','Cette offre facultative ne modifie pas la tâche.'),
   ('L’entrée de la conférence se fera rue Pasteur, et non à l’adresse indiquée sur le billet.','oui','L’accès à destination doit être actualisé.')]),
 ('Préparer la réunion de mardi du dossier Atlas',
  'La réunion Atlas est mardi à 14 h, salle 2, avec quatre participants. Le dossier version 3 est prêt.',
  [('La réunion Atlas de mardi commencera à 14 h 30.','oui','L’horaire de ta réunion change.'),
   ('La réunion Orion de mardi est déplacée en salle 5.','non','Ce n’est pas le dossier Atlas.'),
   ('La salle 2 reste réservée pour la réunion Atlas.','non','Cela confirme une information déjà acquise.'),
   ('Un cinquième participant rejoint la réunion Atlas de mardi : prévoir son exemplaire.','oui','Il faut préparer un exemplaire supplémentaire.'),
   ('Le dossier Atlas version 3 est toujours la version à utiliser.','non','Le document déjà prêt reste valable.'),
   ('La réunion Atlas de mardi se tiendra finalement à distance.','oui','Le mode de participation change.')]),
 ('Finaliser la commande AX-24 pour jeudi',
  'Six unités AX-24 sont commandées pour jeudi, à livrer à l’entrée nord. Le bon est prêt, paiement après livraison.',
  [('La livraison AX-24 prévue jeudi est reportée à vendredi.','oui','La date de cette livraison change.'),
   ('La commande AX-42 sera livrée à l’entrée sud.','non','La référence AX-42 concerne une autre commande.'),
   ('Six unités AX-24 sont confirmées, sans changement.','non','La quantité était déjà prévue.'),
   ('Pour AX-24, présenter désormais le bon signé à la livraison. Le bon prêt ne porte pas de signature.','oui','Le bon doit être signé.'),
   ('Une brochure sur des accessoires facultatifs est disponible.','non','Aucune modification nécessaire de la commande.'),
   ('La livraison AX-24 doit passer par l’entrée est, l’entrée nord étant fermée.','oui','Le point de réception change.')]),
 ('Préparer l’atelier de samedi à la bibliothèque',
  'L’atelier est samedi à 10 h, pour huit inscrits. Il faut apporter un ordinateur chargé. Les supports sont sur place.',
  [('L’atelier de samedi commencera à 11 h.','oui','L’horaire de ton atelier change.'),
   ('L’atelier de dimanche demande un casque audio.','non','Cela concerne dimanche.'),
   ('L’atelier de samedi est confirmé pour huit personnes.','non','La situation prévue reste identique.'),
   ('Pour samedi, les supports sont désormais à télécharger avant de venir.','oui','Une préparation nouvelle est demandée.'),
   ('Le programme mensuel de la bibliothèque est disponible.','non','Ce message ne change pas la préparation de cet atelier.'),
   ('L’atelier de samedi sera dans l’annexe ; l’entrée principale sera fermée.','oui','Le lieu d’accès change.')]),
]

def reperer():
    paliers=[]
    for n in range(1,4):
        items=[]
        for i,(but,contexte,messages) in enumerate(FLUX,1):
            # P1 : horaire seulement. P2 : horaire + préparation. P3 : tous changements utiles.
            domaines=['Uniquement les changements d’horaire de ta tâche.',
                      'Les changements d’horaire ET les nouvelles préparations à effectuer pour ta tâche.',
                      'Tous les changements qui nécessitent une action pour ta tâche.'][n-1]
            choisis=list(enumerate(messages[:4] if n==1 else messages))
            random.Random(f'flux:{n}:{i}').shuffle(choisis)
            flux=[]; reponse={}; raisons={}
            for j,(origine,(texte,decision,raison)) in enumerate(choisis,1):
                key=f'm{j}'
                # Seul le premier message satisfait la consigne restrictive P1.
                retenu = decision=='oui' and (n==3 or origine in ([0] if n==1 else [0,3]))
                # Le changement de quai/date dans le premier scénario n'est pas un horaire.
                if i==3 and origine==0: retenu=True # date = calendrier dans consigne ci-dessous
                raison_finale=raison if retenu or decision=='non' else 'Ce changement ne relève pas des critères retenus pour cette série.'
                flux.append({'id':key,'texte':texte}); reponse[key]='oui' if retenu else 'non'; raisons[key]=raison_finale
            if i==3: domaines=domaines.replace('d’horaire','de date')
            contenu={'enonce':but, 'objectif':contexte, 'critere':domaines,
              'consigne':'Pour chaque message, décide s’il change la tâche selon les critères affichés. Les confirmations et les informations sur une autre tâche sont à écarter.',
              'methode':'Relis le but et les critères. Vérifie de quelle tâche parle le message, puis ce qu’il change réellement. Une information liée au thème n’est pas forcément utile.',
              'messages':flux}
            obj=item('reperer-essentiel',n,i,contenu,reponse,['attention-selective','inhibition'])
            obj['reponse']['explications']=raisons
            items.append(obj)
        paliers.append(items)
    return paliers

DESCRIPTIONS={
 'actualiser-consigne':['Deux éléments, un remplacement','Trois éléments, deux mises à jour','Corrections successives et information à écarter'],
 'comparer-documents':['Deux points à comparer','Quatre points, ordre différent','Six points et valeurs proches'],
 'reperer-essentiel':['Un critère stable','Deux critères stables','Plusieurs types de changements utiles'],
}

def construire():
    return {'actualiser-consigne':actualiser(), 'comparer-documents':comparer(), 'reperer-essentiel':reperer()}

def main():
    for theme,paliers in construire().items():
        base=ROOT/'content/entrainement'/theme
        (base/'paliers').mkdir(parents=True,exist_ok=True)
        manifest={'theme':theme,'paliers':[]}
        for n,items in enumerate(paliers,1):
            fichier=f'paliers/palier-{n:02}.json'
            (base/fichier).write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
            manifest['paliers'].append({'id':f'{theme}-palier-{n}','description':DESCRIPTIONS[theme][n-1],
               'prerequis':[],'fichier':fichier,'nb_items':len(items)})
        (base/'paliers.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__': main()
