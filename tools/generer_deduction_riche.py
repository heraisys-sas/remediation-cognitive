"""Construction déterministe : indices vrais, utiles et résolus sans hypothèse.

Les contraintes collectives sont sélectionnées comme des phrases, jamais comme
règles globales. Le nettoyage n'impose aucun quota de mots/informations.
"""
from itertools import combinations
import random
from deduction_commun import (_vrai_binaire, _vrai_unaire, arrangement, pred_indice,
                              resoudre_par_deduction, phrases_qui_fixent_seules, propager, TYPES_UNAIRES)
from deduction_contraintes import est_entre, TYPES_RICHES


def famille(a):
    t = a['type']
    if t == 'compte-categorie':
        return 'exclusion' if a['nombre'] == 0 else 'repartition'
    return t


def candidats(paire, n, figures, couleurs, palier, etape):
    pions = [(figures[f], couleurs[c]) for f,c in zip(*paire)]
    resultat = []
    for zone in ('ligne', 'colonne'):
        for attribut, valeurs in (('figure', figures), ('couleur', couleurs)):
            for v in valeurs:
                counts = [sum(1 for p,t in enumerate(pions) if t[0 if attribut=='figure' else 1] == v
                              and (p//n if zone=='ligne' else p%n)==k) for k in range(n)]
                for k,nb in enumerate(counts):
                    if nb==0 or palier>=3 and nb==1:
                        resultat.append(dict(type='compte-categorie',categorie={attribut:v},zone=zone,numero=k,nombre=nb))
                if palier>=3 and all(nb==1 for nb in counts):
                    resultat.append(dict(type='compte-categorie',categorie={attribut:v},zone=zone,numero='chaque',nombre=1))
            if palier>=4:
                for numero in [*range(n), 'chaque']:
                    a = dict(type='diversite',attribut=attribut,zone=zone,numero=numero)
                    if pred_indice(a,paire,n,figures,couleurs):
                        resultat.append(a)
    if palier>=3:
        for p,(f,c) in enumerate(pions):
            for q,r in combinations(range(n*n),2):
                for axe in (['ligne','colonne','diagonale'] if n==4 else ['ligne','colonne']):
                    if not est_entre(p,q,r,axe,n):
                        continue
                    # Au P3 entrée, références nommées ; ensuite une catégorie partielle.
                    if palier==3 and etape==1:
                        sels=[dict(figure=pions[x][0],couleur=pions[x][1]) for x in (q,r)]
                    else:
                        attribut = 0 if pions[q][0]==pions[r][0] else 1
                        if pions[q][attribut] != pions[r][attribut]:
                            continue
                        sels=[{('figure','couleur')[attribut]:pions[x][attribut]} for x in (q,r)]
                    resultat.append(dict(type='entre',figure=f,couleur=c,extremites=sels,axe=axe))
    # Repères simples au départ ; leur nombre décroît par l'absence de ces
    # candidats à l'étape finale des paliers avancés.
    unaires = ['pas-ligne','pas-colonne','pas-coin']
    if etape==1:
        unaires += ['ligne','colonne']
    if (palier==2 or palier>=4) and etape==3:
        unaires=[]
    for p,(f,c) in enumerate(pions):
        for t in unaires:
            for valeur in (range(n) if 'ligne' in t or 'colonne' in t else [0]):
                a=dict(type=t,figure=f,couleur=c)
                if 'ligne' in t: a['ligne']=valeur
                if 'colonne' in t: a['colonne']=valeur
                if _vrai_unaire(a,p,n): resultat.append(a)
        for q,(f2,c2) in enumerate(pions):
            if p==q: continue
            types=['voisin-gauche','voisin-dessus','autre-ligne','autre-colonne']
            if palier>=3:
                types += ['oppose','a-gauche-de','au-dessus-de','comparaison']
            if palier>=4:
                types += ['voisin-diagonale']
            if palier==3 and etape==3:
                types=[t for t in types if not t.startswith('voisin-')]
            for t in types:
                a=dict(type=t,figure=f,couleur=c,figure2=f2,couleur2=c2)
                if _vrai_binaire(a,p,q,n): resultat.append(a)
    return resultat


def requis(palier, etape):
    return {2: {'exclusion'}, 3:{'repartition','entre'},
            4:{'exclusion','diversite','entre'},5:{'exclusion','diversite','entre','repartition'}}[palier]


def construire(paire,n,figures,couleurs,palier,etape,rng):
    pool=candidats(paire,n,figures,couleurs,palier,etape)
    rng.shuffle(pool)
    besoins=requis(palier,etape)
    riches=[a for a in pool if a['type'] in TYPES_RICHES]
    if not besoins <= {famille(a) for a in riches}:
        return None
    # Donner la priorité aux indices collectifs qui s'appliquent à toutes les
    # lignes/colonnes. Ils ne sont conservés que s'ils restent utiles.
    choisis=[]
    for fam in sorted(besoins):
        options=[a for a in riches if famille(a)==fam]
        if fam=='entre' and palier==5 and etape>=2:
            options=[a for a in options if a['axe']=='diagonale']
        if not options: return None
        options.sort(key=lambda a:a.get('numero')!='chaque')
        choisis.append(options[0])
    groupe_requis=[]
    if palier == 2 and etape == 2:
        for a,b in combinations([a for a in pool if a['type'] in TYPES_UNAIRES],2):
            if (a['figure'],a['couleur'])==(b['figure'],b['couleur']) and not phrases_qui_fixent_seules([{**a,'et':[b]}],n,figures,couleurs):
                groupe_requis=[a,b]
                choisis.extend(groupe_requis)
                break
        if not groupe_requis: return None
    if n == 4:
        choisis.extend([a for a in riches if a not in choisis][:4])
    restants=[a for a in pool if a not in choisis and a['type'] not in TYPES_RICHES]
    # Quelques informations simples supplémentaires, puis retrait de TOUT
    # indice dispensable, y compris des familles riches : pas de décoration.
    if palier == 2:
        # Éviter une accumulation de négations faibles : sélectionner une
        # information qui réduit réellement les possibilités à chaque ajout.
        while restants and not resoudre_par_deduction(choisis,n,figures,couleurs):
            def poids(a):
                d=propager(choisis+[a],n,figures,couleurs)
                return sum(map(len,d)) if d else n**5
            meilleur=min(restants,key=poids)
            choisis.append(meilleur)
            restants.remove(meilleur)
        restants=[]
    for a in restants:
        choisis.append(a)
        if len(choisis)%3==0 and resoudre_par_deduction(choisis,n,figures,couleurs):
            break
    if not resoudre_par_deduction(choisis,n,figures,couleurs):
        return None
    for a in list(reversed(choisis)):
        essai=[b for b in choisis if b is not a]
        if resoudre_par_deduction(essai,n,figures,couleurs):
            choisis=essai
    if not besoins <= {famille(a) for a in choisis} or any(a not in choisis for a in groupe_requis):
        return None
    if len(choisis) > (21 if n==3 else 32):
        return None
    if phrases_qui_fixent_seules(choisis,n,figures,couleurs):
        return None
    # Relier deux informations utiles portant sur un même pion, seulement si
    # leur réunion ne fournit pas une position à elle seule. Les contraintes
    # collectives restent des phrases autonomes, lisibles et sans règle cachée.
    if etape>=2 or len(choisis)>18:
        for a in list(choisis):
            if a not in choisis or a['type'] in TYPES_RICHES or a.get('et'): continue
            for b in list(choisis):
                if b is a or b['type'] in TYPES_RICHES or b.get('et'): continue
                sujets_a={(a.get('figure'),a.get('couleur')),(a.get('figure2'),a.get('couleur2'))}-{(None,None)}
                sujets_b={(b.get('figure'),b.get('couleur')),(b.get('figure2'),b.get('couleur2'))}-{(None,None)}
                if not sujets_a & sujets_b or len(sujets_a|sujets_b)>3: continue
                compose={**a,'et':[b]}
                if not phrases_qui_fixent_seules([compose],n,figures,couleurs):
                    choisis.remove(a)
                    choisis.remove(b)
                    choisis.append(compose)
                    break
    rng.shuffle(choisis)
    return choisis


def generer(palier, rng, nombre, deja_vus):
    from generer_deduction import FIGURES, COULEURS, _item, _secours, identifiant_item
    n=3 if palier<=4 else 4
    figures,couleurs=FIGURES[:n],COULEURS[:n]
    items=[]
    for essai in range(10000):
        if len(items)==nombre: return items
        etape=min(3,1+len(items)*3//nombre)
        paire=arrangement(rng,n)
        if paire in deja_vus: continue
        phrases=construire(paire,n,figures,couleurs,palier,etape,rng)
        if not phrases: continue
        item=_item(palier,paire,phrases,_secours(paire,n,figures,couleurs,rng),n,figures,couleurs)
        item['contenu']['etape_progression']=etape
        item['contenu']['consigne']=(f'Place les {n*n} figures colorées : chacune une seule fois, une par case. '
            'Toute autre contrainte est écrite dans les indices. Croise les phrases, '
            'note les possibilités et ne place un pion que lorsque sa case est certaine.')
        item['cap_complexite']='Croisement de contraintes explicites ; étape %d/3, grille %d×%d.'%(etape,n,n)
        item['id']=identifiant_item(palier,item['contenu'],item['reponse'])
        items.append(item)
        deja_vus.add(paire)
        print('P%d étape%d : %d/%d, %d indices (essai%d)'%(palier,etape,len(items),nombre,len(phrases),essai+1),flush=True)
    raise RuntimeError('Génération incomplète au palier %d : %d/%d'%(palier,len(items),nombre))
