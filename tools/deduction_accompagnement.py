"""Aides vérifiables : orienter, réduire les possibilités, expliquer un placement.

Aucune contrainte supplémentaire cachée : les aides utilisent les seuls énoncés.
Le repère d'entrée de P2, lorsqu'il est ajouté, est visible dans ces énoncés.
"""
from itertools import combinations
from deduction_commun import propager, informations_autonomes, phrases_qui_fixent_seules, TYPES_UNAIRES


def positions(domaines, pion):
    if domaines is None:
        raise ValueError('Contradiction dans une aide')
    return [k for k,d in enumerate(domaines) if pion in d]


def aide_raisonnement(enonces,n,figures,couleurs):
    """Cherche une intersection lisible de deux/trois phrases, sinon un croisement.

    Le secours par propagation reste explicite : il annonce que les autres pions
    et l'unicité des cases interviennent, sans prétendre à une simple intersection.
    """
    seuls=[propager([ph],n,figures,couleurs) for ph in enonces]
    for taille in (2,3):
        for choix in combinations(range(len(enonces)),taille):
            for f in range(n):
                for c in range(n):
                    domaines=[positions(seuls[k],(f,c)) for k in choix]
                    intersection=set.intersection(*(set(d) for d in domaines))
                    if len(intersection)==1 and all(len(d)>1 for d in domaines):
                        return dict(mode='intersection',figure=figures[f],couleur=couleurs[c],
                                    phrases=[k+1 for k in choix],possibilites=domaines,case=next(iter(intersection)))
    from deduction_contraintes import compiler, reduire
    contraintes=[compiler([ph],n,figures,couleurs) for ph in enonces]
    domaines=[set(range(n*n)) for _ in range(n*n)]
    demonstration=[]
    while True:
        avance=False
        for k,contrainte in enumerate(contraintes):
            apres=reduire(contrainte,n,domaines)
            if apres is None: raise ValueError('Contradiction dans la démonstration')
            changements=[dict(figure=figures[i//n],couleur=couleurs[i%n],cases=sorted(apres[i]))
                          for i in range(n*n) if apres[i]!=domaines[i]]
            if changements:
                demonstration.append(dict(phrase=k+1,reductions=changements))
                avance=True
            domaines=apres
            for pion,places in enumerate(domaines):
                if len(places)==1:
                    references=list(dict.fromkeys(e['phrase'] for e in demonstration))
                    f,c=divmod(pion,n)
                    return dict(mode='croisement',figure=figures[f],couleur=couleurs[c],
                                phrases=references,possibilites=[positions(seuls[r-1],(f,c)) for r in references],
                                case=next(iter(places)),demonstration=demonstration)
        if not avance: break
    raise ValueError('Aucun placement explicable')


def regrouper_meme_pion(enonces,n,figures,couleurs):
    """Deux repères individuels au plus ; jamais de changement de sujet."""
    atomes=[a for ph in enonces for a in informations_autonomes(ph)]
    resultat=[]
    while atomes:
        a=atomes.pop(0)
        if a['type'] in TYPES_UNAIRES:
            for k,b in enumerate(atomes):
                if (b['type'] in TYPES_UNAIRES and (a['figure'],a['couleur'])==(b['figure'],b['couleur'])):
                    compose={**a,'et':[b]}
                    if not phrases_qui_fixent_seules([compose],n,figures,couleurs):
                        a=compose; atomes.pop(k); break
        resultat.append(a)
    return resultat


def accompagner(item):
    """Transformation déterministe, sans toucher aux solutions ni aux tirages."""
    from generer_deduction import identifiant_item
    contenu=item['contenu']; n=len(contenu['figures'])
    figures,couleurs=contenu['figures'],contenu['couleurs']
    if item['palier']==2:
        enonces=regrouper_meme_pion(contenu['enonces'],n,figures,couleurs)
        if contenu['etape_progression']==1:
            # Une phrase de repère supplémentaire, annoncée et visible, fournit
            # un premier croisement simple. Elle ne donne jamais seule une case.
            trouve=False
            for case,(f,c) in enumerate(item['reponse']['grille']):
                for t,valeur in [('ligne',case//n),('colonne',case%n)]:
                    repere=dict(type=t,figure=f,couleur=c,**{t:valeur})
                    if repere in [a for ph in enonces for a in informations_autonomes(ph)]: continue
                    for ph in enonces:
                        d=propager([repere,ph],n,figures,couleurs)
                        if positions(d,(figures.index(f),couleurs.index(c)))==[case]:
                            enonces.insert(0,repere)
                            contenu['repere_accompagnement']=1
                            trouve=True; break
                    if trouve: break
                if trouve: break
            contenu['methode_depart']=("Commence par le repère de la phrase 1. Dans le tableau de déduction, "
                "barre les cases exclues pour ce pion, puis cherche une autre phrase qui le concerne. "
                "Tu peux noter des possibilités sans placer de pion. Le bouton « Aide au raisonnement » te guide si besoin.") if trouve else (
                "Note les cases possibles dans le tableau de déduction avant de placer un pion. "
                "Cherche deux phrases qui concernent le même pion.")
        contenu['enonces']=enonces
    contenu['aide_raisonnement']=aide_raisonnement(contenu['enonces'],n,figures,couleurs)
    # Les anciens secours étaient des coordonnées tirées de la solution. Ils
    # disparaissent de ces nouveaux items ; seul le raisonnement reste accessible.
    contenu['indices']=[]
    item['id']=identifiant_item(item['palier'],contenu,item['reponse'])
    return item
