"""Corpus déterministe cm4 : quatre familles alternées dans chaque palier adulte.

Les méthodes sont rédigées par famille, pas devinées à partir des nombres.
Les réponses sont vérifiées séparément depuis les phrases par verifier_calcul_adulte.
"""
import hashlib
import json
from decimal import Decimal

DESCRIPTIONS = [
    "Calcul souple : compensation, décomposition et écarts à deux chiffres",
    "Produits et partages : distribuer, factoriser et vérifier",
    "Tenir un résultat : deux transformations et calcul inverse",
    "Montants et décimaux : achats, budgets et prix unitaires",
    "Proportions et durées : changer d’échelle et convertir",
    "Pourcentages : remise, variation et recherche de la base",
    "Comparer des offres : frais fixes, quantités et seuils",
    "Synthèse : coûts, rendements et variations successives",
]
METHODES = {
 'addition': 'Arrondis un des termes à une dizaine, additionne, puis corrige exactement ce que tu as ajouté. Vérifie avec une estimation du total.',
 'soustraction': 'Retire un nombre rond proche, puis compense la différence. Vérifie en ajoutant le retrait au résultat.',
 'ecart': 'Avance du départ à la dizaine suivante, puis jusqu’à la cible. Rassemble ces écarts et vérifie en sens inverse.',
 'regrouper': 'Repère les termes qui se regroupent facilement avant de calculer. Garde le signe de chaque terme et vérifie l’ordre de grandeur.',
 'produit': 'Décompose le facteur à deux chiffres en dizaines et unités, multiplie chaque partie, puis rassemble les produits.',
 'division': 'Décompose le total en multiples faciles du diviseur. Additionne les quotients et vérifie par multiplication.',
 'lots': 'Calcule séparément chaque groupe, puis additionne. Vérifie que tous les groupes sont comptés une seule fois.',
 'inverse': 'Pars du résultat final et annule les opérations dans l’ordre inverse. Vérifie en refaisant le trajet vers l’avant.',
 'chaine': 'Calcule la première étape et garde son résultat, puis applique la seconde. Vérifie chaque changement avant de répondre.',
 'stock': 'Calcule le total ajouté, puis retranche les sorties du stock. Vérifie que tu comptes des unités et non des boîtes.',
 'moyenne': 'Retrouve le total nécessaire à partir de la moyenne visée, puis retire les valeurs déjà connues. Vérifie la moyenne obtenue.',
 'panier': 'Multiplie chaque prix par sa quantité, additionne les sous-totaux, puis retire la remise fixe. Vérifie en euros.',
 'budget': 'Rassemble d’abord les dépenses, puis retire leur total du budget. Vérifie que reste et dépenses reconstituent le budget.',
 'unitaire': 'Exprime le prix en centimes si cela facilite le partage, divise par la quantité, puis reconvertis en euros.',
 'monnaie': 'Calcule le total de l’achat, puis complète jusqu’à la somme payée. Vérifie que achat et monnaie reconstituent le paiement.',
 'proportion_reserve': 'Calcule la quantité pour le nouvel effectif par proportionnalité, puis retire la réserve disponible. Vérifie les unités.',
 'pourcentage': 'Décompose le taux en repères faciles, comme dix pour cent et cinq pour cent. Applique-les à la base puis additionne.',
 'proportion': 'Cherche le facteur entre les deux effectifs, ou passe par une part. Applique le même rapport à la quantité.',
 'duree': 'Convertis toutes les durées en minutes, additionne le travail, puis les pauses entre les séquences. Une pause de moins que de séquences.',
 'debit': 'Ramène la production à une minute, puis applique la nouvelle durée. Vérifie que la quantité varie dans le même rapport que le temps.',
 'horaire': 'Convertis les heures en minutes. Calcule la durée entre début et fin, puis retire la pause.',
 'remise': 'Calcule la réduction avec des repères comme dix pour cent, la moitié ou le quart, puis soustrais-la au prix initial.',
 'hausse': 'Calcule d’abord l’augmentation, puis ajoute-la à la valeur de départ. Vérifie que la valeur finale est supérieure.',
 'base': 'Le prix final représente cent pour cent moins la remise. Retrouve la base en divisant par cette proportion, puis vérifie vers l’avant.',
 'taux': 'Calcule l’écart, divise-le par la valeur de départ, puis exprime le rapport sur cent. Le dénominateur est la valeur initiale.',
 'offres': 'Calcule le coût complet de chaque offre, frais fixes compris, pour la même quantité. Soustrais ensuite les deux coûts dans l’ordre demandé.',
 'seuil': 'Calcule l’écart des frais fixes et l’économie par utilisation. Cherche combien d’utilisations compensent exactement cet écart.',
 'condition': 'Calcule le panier avant la livraison. Applique ensuite le seuil à ce montant précis, puis ajoute les frais éventuels.',
 'rendement': 'Calcule combien d’éléments restent utilisables après les pertes, puis répartis le coût total entre eux.',
 'successif': 'Applique la première variation. La seconde porte sur le nouveau montant : ne cumule pas simplement les pourcentages.',
 'projet': 'Sépare les coûts fixes et les coûts par personne. Calcule les recettes, puis retire toutes les dépenses. Vérifie ce que représente le solde.',
 'marge': 'Calcule le produit brut, retire d’abord les frais proportionnels puis les frais fixes. Vérifie que chaque dépense est comptée une fois.',
}

def nombre(n):
    return format(Decimal(str(n)).normalize(), 'f').replace('.', ',')


def construire(date='2026-10-03'):
    paliers = {n: [] for n in range(5, 13)}
    def add(p, famille, phrase, resultat):
        resultat = Decimal(str(resultat))
        valeur = int(resultat) if resultat == int(resultat) else float(resultat)
        contenu = {'enonce': phrase, 'methode': METHODES[famille], 'famille_calcul': famille}
        empreinte = hashlib.sha256(json.dumps([p, contenu, valeur], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]
        paliers[p].append({'id': f'cm4-{p}-{empreinte}', 'type': 'production',
            'module': 'entrainement', 'theme': 'calcul-mental', 'palier': p,
            'fonctions_ciblees': ['flexibilite', 'memoire-travail', 'automatisation'],
            'prerequis': [], 'cap_complexite': 'Énoncé visible ; calcul mental sans contrainte de vitesse ; une réponse numérique avec unité précisée.',
            'contenu': contenu, 'reponse': {'valeur': valeur},
            'meta': {'auteur': 'tools/calcul_adulte.py', 'date_creation': date,
                     'relecture_ortho': {'statut': 'a_revoir'}}})
    for i in range(6):
        # Les quatre familles alternent : chaque demi-séance est variée.
        a, b = 47+7*i, 38+3*i
        add(5,'addition',f'Combien font {a} + {b} ?',a+b)
        a, b = 143+13*i, 68+7*i
        add(5,'soustraction',f'Combien font {a} − {b} ?',a-b)
        a,b=137+17*i,250+50*i
        add(5,'ecart',f'Combien manque-t-il à {a} pour faire {b} ?',b-a)
        a,b,c=68+3*i,27+2*i,18+3*i
        add(5,'regrouper',f'Combien font {a} + {b} − {c} ?',a+b-c)
        a,b=24+3*i,7+i
        add(6,'produit',f'Combien font {a} × {b} ?',a*b)
        q,d=24+7*i,6+i
        add(6,'division',f'Combien font {q*d} ÷ {d} ?',q)
        a,b,c,d=4+i,27+2*i,3+i,18+3*i
        add(6,'lots',f'Une commande contient {a} lots de {b} pièces et {c} lots de {d} pièces. Combien de pièces au total ?',a*b+c*d)
        a,b=25+5*i,6+i
        add(6,'inverse',f'{a*b} = ? × {b}',a)
        a,b,c=23+4*i,6+i,37+3*i
        add(7,'chaine',f'Combien font {a} × {b} − {c} ?',a*b-c)
        a,b,c=7+i,29+3*i,8+i
        add(7,'inverse',f'Un nombre est multiplié par {a}, puis on ajoute {b}. Le résultat est {c*a+b}. Quel était le nombre ?',c)
        a,b,c,d=145+11*i,3+i,24+2*i,67+4*i
        add(7,'stock',f'Un atelier possède {a} pièces, reçoit {b} boîtes de {c} pièces, puis utilise {d} pièces. Combien en reste-t-il ?',a+b*c-d)
        a,b,c=68+3*i,79+2*i,82+4*i
        add(7,'moyenne',f'Trois mesures doivent avoir une moyenne de {c}. Les deux premières valent {a} et {b}. Quelle doit être la troisième ?',3*c-a-b)
        a,b,c,d=3+i,Decimal('12.50')+i,Decimal('8.75')+i,5+i
        add(8,'panier',f'Achat de {a} carnets à {nombre(b)} € et d’un classeur à {nombre(c)} €, avec une remise fixe de {d} € sur le total. Quel montant payer en euros ?',a*b+c-d)
        a,b,c=150+25*i,Decimal('47.80')+i,Decimal('36.65')+2*i
        add(8,'budget',f'Budget de {a} €. Deux dépenses de {nombre(b)} € et {nombre(c)} €. Quel montant reste disponible en euros ?',a-b-c)
        q,n=Decimal('7.25')+Decimal('0.50')*i,4+2*i
        add(8,'unitaire',f'Un lot de {n} dossiers coûte {nombre(q*n)} €. Quel est le prix d’un dossier en euros ?',q)
        n,prix,paye=3+i,Decimal('6.75')+i,100+20*i
        add(8,'monnaie',f'On paie {n} billets à {nombre(prix)} € avec {paye} €. Quelle monnaie rendre en euros ?',paye-n*prix)
        base,cible,quantite=8,12+4*i,280+40*i
        add(9,'proportion',f'Pour {base} personnes, il faut {quantite} g de riz. Quelle quantité faut-il pour {cible} personnes, en grammes ?',quantite*cible/base)
        n,d,p=3+i,35+5*i,10
        add(9,'duree',f'{n} interventions de {d} minutes, avec une pause de {p} minutes entre deux interventions successives. Quelle durée totale en minutes ?',n*d+(n-1)*p)
        n,t,d=84+12*i,6,15+3*i
        add(9,'debit',f'Une machine produit {n} pièces en {t} minutes à débit constant. Combien en produit-elle en {d} minutes ?',n*d/t)
        h,m,hh,mm,p=8,35,12+i,10,25
        add(9,'horaire',f'Travail de {h} h {m:02d} à {hh} h {mm:02d}, avec {p} minutes de pause. Combien de minutes de travail effectif ?',60*(hh-h)+mm-m-p)
        a,p=160+40*i,[15,25,20,15,25,20][i]
        add(10,'remise',f'Un article coûte {a} €. Une remise de {p} % est appliquée. Quel est le prix final en euros ?',Decimal(a)*(100-p)/100)
        a,p=240+80*i,[15,25,10,20,15,25][i]
        add(10,'hausse',f'Un budget de {a} € augmente de {p} %. Quel est le nouveau budget en euros ?',Decimal(a)*(100+p)/100)
        a,p=160+40*i,20
        add(10,'base',f'Après une remise de {p} %, un article coûte {nombre(Decimal(a)*(100-p)/100)} €. Quel était son prix initial en euros ?',a)
        a,p=200+100*i,15+5*i
        add(10,'taux',f'Une quantité passe de {a} à {a*(100+p)//100}. Quel est le pourcentage d’augmentation ?',p)
        n,a,b,c,d=6+i,18+2*i,7,6+i,11
        add(11,'offres',f'Pour {n} utilisations : offre A, {a} € fixes puis {b} € par utilisation ; offre B, {c} € fixes puis {d} € par utilisation. De combien B coûte-t-elle plus que A, en euros ?',c+d*n-a-b*n)
        a,b,c,d=60+12*i,4,12+4*i,8
        add(11,'seuil',f'Offre A : {a} € fixes et {b} € par utilisation. Offre B : {c} € fixes et {d} € par utilisation. À combien d’utilisations leurs coûts sont-ils égaux ?',(a-c)/(d-b))
        n,p,seuil,frais=3+i,17,[60,68,80,110,119,130][i],8
        add(11,'condition',f'{n} articles à {p} €. Livraison de {frais} €, gratuite dès {seuil} € d’achats (seuil inclus). Quel total payer en euros ?',n*p+(0 if n*p>=seuil else frais))
        n,perte,q=50+10*i,5+i,4+i
        add(11,'rendement',f'Un lot de {n} pièces coûte {(n-perte)*q} €. Parmi elles, {perte} sont inutilisables. Quel coût par pièce utilisable, en euros ?',q)
        a,p,q=200+100*i,20,10
        add(12,'successif',f'Un prix de {a} € augmente de {p} %, puis baisse de {q} % sur le nouveau prix. Quel est le prix final en euros ?',Decimal(a)*(100+p)*(100-q)/10000)
        n,p,f,c=18+2*i,32+3*i,145+15*i,12+i
        add(12,'projet',f'Un atelier accueille {n} participants payant chacun {p} €. La salle coûte {f} € et le matériel {c} € par participant. Quel solde reste en euros ?',n*p-f-n*c)
        n,p,t,f=12+2*i,25+5*i,10,27+3*i
        add(12,'marge',f'Vente de {n} objets à {p} € chacun. La plateforme retient {t} % du montant des ventes, puis {f} € de frais fixes. Quel montant net reste en euros ?',Decimal(n*p)*(100-t)/100-f)
        # Deux facteurs d'échelle et une réserve à déduire avant l'achat.
        n,q,cible,reserve=8,320+40*i,14+2*i,75+5*i
        add(12,'proportion_reserve',f'Pour {n} personnes, une recette utilise {q} g de riz. Pour {cible} personnes, on dispose déjà de {reserve} g. Combien de grammes faut-il encore acheter ?',q*cible/n-reserve)
        # Calcul pur maintenu aux niveaux avancés, en alternance avec les applications.
        for p in range(8, 13):
            a = Decimal('37.5') + 7*i + 10*(p-8)
            b = Decimal('18.75') + 3*i
            if p >= 10:
                facteur = 4 + 2*(p-10)
                add(p,'chaine',f'Combien font ({nombre(a)} + {nombre(b)}) × {facteur} ?', (a+b)*facteur)
            else:
                add(p,'addition',f'Combien font {nombre(a)} + {nombre(b)} ?',a+b)
            if p >= 10:
                base,taux=240+80*i+40*(p-10),15+5*(p-10)
                add(p,'pourcentage',f'Combien font {taux} % de {base} ?',Decimal(base)*taux/100)
            else:
                a,b=36+7*i,12+3*(p-8)
                add(p,'produit',f'Combien font {a} × {b} ?',a*b)
    return paliers
