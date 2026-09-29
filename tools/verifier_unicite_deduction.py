#!/usr/bin/env python3
"""Contre-vérification d'unicité par recherche indépendante, limitée à deux solutions.

Aucun appel au compilateur ni au propagateur de production. Seules les relations
élémentaires historiques sont partagées. Les indices collectifs et entre-deux
sont interprétés ici. Cette recherche prouve l'unicité, pas une résolution humaine
sans hypothèse : cette seconde propriété relève du contrôle de propagation.
"""
import argparse
import json
from itertools import product
from pathlib import Path
import time

from deduction_commun import TYPES_UNAIRES, TYPES_BINAIRES, _vrai_unaire, _vrai_binaire


class BudgetDepasse(RuntimeError):
    pass


def solutions_independantes(item, budget=200_000):
    contenu = item['contenu']
    figures, couleurs = contenu['figures'], contenu['couleurs']
    n = len(figures)
    pions = list(product(figures, couleurs))
    taille = n*n
    univers = set(range(taille))
    domaines_initiaux = [set(univers) for _ in pions]
    relations, comptes, entre_deux = [], [], []

    def selection(categorie):
        return {i for i, (f,c) in enumerate(pions)
                if categorie.get('figure',f)==f and categorie.get('couleur',c)==c}

    for phrase in contenu['enonces']:
        suite = phrase.get('et', [])
        if isinstance(suite, dict):
            suite = [suite]
        for a in [phrase] + suite:
            t = a['type']
            if t in TYPES_UNAIRES | TYPES_BINAIRES:
                i = pions.index((a.get('figure',phrase.get('figure')), a.get('couleur',phrase.get('couleur'))))
                if t in TYPES_UNAIRES:
                    domaines_initiaux[i] &= {p for p in univers if _vrai_unaire(a,p,n)}
                else:
                    j = pions.index((a['figure2'],a['couleur2']))
                    autorises = {(p,q) for p,q in product(univers,repeat=2)
                                 if p!=q and _vrai_binaire(a,p,q,n)}
                    relations.append((i,j,autorises))
            elif t in ('compte-categorie','diversite'):
                regions = [{p for p in univers if (p//n if a['zone']=='ligne' else p%n)==r}
                           for r in (range(n) if a['numero']=='chaque' else [a['numero']])]
                categories = ([a['categorie']] if t=='compte-categorie' else
                              [{a['attribut']:v} for v in (figures if a['attribut']=='figure' else couleurs)])
                for categorie in categories:
                    for region in regions:
                        comptes.append((selection(categorie),region,a['nombre'] if t=='compte-categorie' else 1))
            elif t=='entre':
                i = pions.index((a['figure'],a['couleur']))
                groupe1, groupe2 = map(selection,a['extremites'])
                triples = []
                for c,g,d in product(univers,repeat=3):
                    if len({c,g,d})!=3:
                        continue
                    rc,cc=divmod(c,n); rg,cg=divmod(g,n); rd,cd=divmod(d,n)
                    if a['axe']=='ligne':
                        vrai = rc==rg==rd and min(cg,cd)<cc<max(cg,cd)
                    elif a['axe']=='colonne':
                        vrai = cc==cg==cd and min(rg,rd)<rc<max(rg,rd)
                    elif a['axe']=='diagonale':
                        vrai = any(cc-s*rc==cg-s*rg==cd-s*rd and min(rg,rd)<rc<max(rg,rd) for s in (-1,1))
                    else:
                        raise ValueError('Axe inconnu')
                    if vrai:
                        triples.append((c,g,d))
                entre_deux.append([(i,j,k,c,g,d) for j,k in product(groupe1,groupe2)
                                   if len({i,j,k})==3 for c,g,d in triples])
            else:
                raise ValueError('Indice non pris en charge : '+t)

    noeuds = 0
    solutions = []
    def cherche(affectation):
        nonlocal noeuds
        noeuds += 1
        if noeuds > budget:
            raise BudgetDepasse(f"{item['id']} : budget de {budget} nœuds dépassé")
        occupees = set(affectation.values())
        domaines = [{affectation[i]} if i in affectation else domaines_initiaux[i]-occupees for i in range(taille)]
        for i,j,autorises in relations:
            if i in affectation:
                domaines[j] &= {q for p,q in autorises if p==affectation[i]}
            if j in affectation:
                domaines[i] &= {p for p,q in autorises if q==affectation[j]}
        if any(not d for d in domaines):
            return
        for groupe,region,k in comptes:
            minimum=sum(domaines[i]<=region for i in groupe)
            maximum=sum(bool(domaines[i]&region) for i in groupe)
            if not minimum<=k<=maximum:
                return
            if minimum==k:
                for i in groupe:
                    if not domaines[i]<=region:
                        domaines[i]-=region
            if maximum==k:
                for i in groupe:
                    if domaines[i]&region:
                        domaines[i]&=region
        if any(not d for d in domaines):
            return
        for table in entre_deux:
            if not any(c in domaines[i] and g in domaines[j] and d in domaines[k]
                       for i,j,k,c,g,d in table):
                return
        if len(affectation)==taille:
            solutions.append(tuple(affectation[i] for i in range(taille)))
            return
        i=min((i for i in range(taille) if i not in affectation),key=lambda i:len(domaines[i]))
        for p in sorted(domaines[i]):
            cherche({**affectation,i:p})
            if len(solutions)==2:
                return
    cherche({})
    return solutions,noeuds


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repertoire',type=Path,default=Path(__file__).resolve().parents[1]/'content/entrainement/deduction')
    parser.add_argument('--budget',type=int,default=200_000,help='Budget maximal de nœuds par grille ; dépassement = échec explicite')
    args=parser.parse_args()
    debut=time.monotonic()
    total=0; noeuds_total=0
    fichiers=sorted(args.repertoire.rglob('palier-*.json'))
    if not fichiers:
        parser.error('Aucun fichier de palier trouvé')
    for fichier in fichiers:
        for item in json.loads(fichier.read_text()):
            if item.get('type')!='grille-deduction':
                continue
            solutions,noeuds=solutions_independantes(item,args.budget)
            if len(solutions)!=1:
                raise AssertionError(f"{item['id']} : {len(solutions)} solutions (recherche arrêtée à deux)")
            pions=list(product(item['contenu']['figures'],item['contenu']['couleurs']))
            grille=[None]*len(pions)
            for i,p in enumerate(solutions[0]):
                grille[p]=list(pions[i])
            if grille!=item['reponse']['grille']:
                raise AssertionError(f"{item['id']} : solution différente de la réponse enregistrée")
            total+=1; noeuds_total+=noeuds
        print(f'{fichier.name} : unicité vérifiée',flush=True)
    print(f'{total} grilles uniques, {noeuds_total} nœuds, {time.monotonic()-debut:.2f} s')


if __name__=='__main__':
    main()
