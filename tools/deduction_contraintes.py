"""Contraintes collectives explicites et relations à trois pions.

Domaines = positions possibles par pion. La propagation ne fait aucune hypothèse.
Les sélecteurs partiels désignent les pions existants, jamais de nouveaux pions.
"""
from itertools import product
from functools import lru_cache
import json

TYPES_RICHES = {'compte-categorie', 'diversite', 'entre'}


def selection(sel, figures, couleurs):
    if not isinstance(sel, dict) or not sel or set(sel) - {'figure', 'couleur'}:
        raise ValueError('Sélecteur de pion invalide')
    if ('figure' in sel and sel['figure'] not in figures or
            'couleur' in sel and sel['couleur'] not in couleurs):
        raise ValueError('Catégorie inconnue')
    return {i for i, (f, c) in enumerate(product(figures, couleurs))
            if sel.get('figure', f) == f and sel.get('couleur', c) == c}


def regions(a, n):
    if a.get('zone') not in ('ligne', 'colonne'):
        raise ValueError('Zone attendue : ligne ou colonne')
    numero = a.get('numero')
    if numero != 'chaque' and (type(numero) is not int or not 0 <= numero < n):
        raise ValueError('Numéro de zone invalide')
    return [{p for p in range(n*n) if (p // n if a['zone'] == 'ligne' else p % n) == k}
            for k in (range(n) if numero == 'chaque' else [numero])]


def est_entre(centre, gauche, droite, axe, n):
    r, c = divmod(centre, n)
    r1, c1 = divmod(gauche, n)
    r2, c2 = divmod(droite, n)
    if len({centre, gauche, droite}) != 3:
        return False
    if axe == 'ligne':
        return r1 == r == r2 and min(c1, c2) < c < max(c1, c2)
    if axe == 'colonne':
        return c1 == c == c2 and min(r1, r2) < r < max(r1, r2)
    return (abs(r1-r2) == abs(c1-c2) and
            (r-r1)*(c2-c1) == (c-c1)*(r2-r1) and min(r1,r2) < r < max(r1,r2))


@lru_cache(maxsize=4096)
def _table_entre(serialisee, n, figures, couleurs):
    a = json.loads(serialisee)
    if a.get('axe') not in ('ligne', 'colonne', 'diagonale'):
        raise ValueError('Axe entre-deux invalide')
    centre = selection({'figure': a.get('figure'), 'couleur': a.get('couleur')}, figures, couleurs)
    extremites = a.get('extremites')
    if not isinstance(extremites, list) or len(extremites) != 2:
        raise ValueError('Deux extrémités attendues')
    gauche, droite = [selection(s, figures, couleurs) for s in extremites]
    triples = [(p, q, r) for p, q, r in product(range(n*n), repeat=3)
               if est_entre(p, q, r, a['axe'], n)]
    return tuple(tuple(zip((i,j,k), cases)) for i,j,k in product(centre, gauche, droite)
                 if len({i,j,k}) == 3 for cases in triples)


def compiler(indices, n, figures, couleurs):
    from deduction_commun import atomes, sujet, TYPES_UNAIRES, TYPES_BINAIRES, _vrai_unaire, _vrai_binaire
    unaires, binaires, comptes, tables = [], [], [], []
    for phrase in indices:
        for a in atomes(phrase):
            t = a.get('type')
            if t in TYPES_RICHES and (a is not phrase or phrase.get('et')):
                raise ValueError('Un indice collectif ou entre-deux doit être une phrase autonome')
            if t == 'compte-categorie':
                cat = a.get('categorie')
                if not isinstance(cat, dict) or len(cat) != 1:
                    raise ValueError('Une catégorie de forme OU de couleur attendue')
                groupe = selection(cat, figures, couleurs)
                k = a.get('nombre')
                if type(k) is not int or not 0 <= k <= n:
                    raise ValueError('Compte de catégorie invalide')
                if a.get('numero') == 'chaque' and k != 1:
                    raise ValueError('Répartition impossible : la catégorie contient exactement n pions')
                comptes.extend((groupe, region, k) for region in regions(a, n))
            elif t == 'diversite':
                attribut = a.get('attribut')
                if attribut not in ('figure', 'couleur'):
                    raise ValueError('Attribut de diversité invalide')
                for valeur in (figures if attribut == 'figure' else couleurs):
                    groupe = selection({attribut: valeur}, figures, couleurs)
                    comptes.extend((groupe, region, 1) for region in regions(a, n))
            elif t == 'entre':
                table = _table_entre(json.dumps(a, sort_keys=True), n, tuple(figures), tuple(couleurs))
                if not table:
                    raise ValueError('Entre-deux impossible')
                tables.append(table)
            elif t in TYPES_UNAIRES | TYPES_BINAIRES:
                f,c = sujet(phrase, a)
                i = next(iter(selection({'figure': f, 'couleur': c}, figures, couleurs)))
                if t in TYPES_UNAIRES:
                    unaires.append((i, {p for p in range(n*n) if _vrai_unaire(a,p,n)}))
                else:
                    j = next(iter(selection({'figure': a.get('figure2'), 'couleur': a.get('couleur2')}, figures, couleurs)))
                    if i == j:
                        raise ValueError('Une relation exige deux pions distincts')
                    binaires.append((i,j,tuple((p,q) for p in range(n*n) for q in range(n*n)
                                              if p != q and _vrai_binaire(a,p,q,n))))
            else:
                raise ValueError('Type inconnu : ' + str(t))
    return unaires, binaires, comptes, tables


def reduire(compilation, n, domaines=None):
    """Consistance d'arc, bornes de cardinalité et unicité des cases/pions."""
    d = [set(range(n*n)) for _ in range(n*n)] if domaines is None else [set(s) for s in domaines]
    unaires, binaires, comptes, tables = compilation
    for i, positions in unaires:
        d[i] &= positions
    while True:
        avant = tuple(frozenset(s) for s in d)
        for i,j,table in binaires:
            valides = [(p,q) for p,q in table if p in d[i] and q in d[j]]
            d[i] &= {p for p,q in valides}
            d[j] &= {q for p,q in valides}
        for groupe, region, k in comptes:
            dedans = {i for i in groupe if d[i] and d[i] <= region}
            possibles = {i for i in groupe if d[i] & region}
            if len(dedans) > k or len(possibles) < k:
                return None
            if len(dedans) == k:
                for i in groupe - dedans:
                    d[i] -= region
            if len(possibles) == k:
                for i in possibles:
                    d[i] &= region
            # Vue par case, complémentaire à la vue par pion.
            occupants = {p: {i for i in range(n*n) if p in d[i]} for p in region}
            certaines = {p for p, inds in occupants.items() if inds and inds <= groupe}
            candidates = {p for p, inds in occupants.items() if inds & groupe}
            if len(certaines) > k or len(candidates) < k:
                return None
            if len(certaines) == k:
                for i in groupe:
                    d[i] -= region - certaines
            if len(candidates) == k:
                for i in set(range(n*n)) - groupe:
                    d[i] -= candidates
        for table in tables:
            valides = [row for row in table if all(p in d[i] for i,p in row)]
            if not valides:
                return None
            scope = {i for row in table for i,p in row}
            supports = {i: set() for i in scope}
            for row in valides:
                places = dict(row)
                utilisees = set(places.values())
                for i in scope:
                    supports[i].update({places[i]} if i in places else d[i] - utilisees)
            for i in scope:
                d[i] &= supports[i]
        for i in range(n*n):
            if len(d[i]) == 1:
                for j in range(n*n):
                    if i != j:
                        d[j] -= d[i]
        for p in range(n*n):
            candidats = [i for i in range(n*n) if p in d[i]]
            if not candidats:
                return None
            if len(candidats) == 1:
                d[candidats[0]] &= {p}
        if any(not s for s in d):
            return None
        if avant == tuple(frozenset(s) for s in d):
            return d


def propager_riche(indices, n, figures, couleurs):
    d = reduire(compiler(indices,n,figures,couleurs), n)
    return None if d is None else [{divmod(i,n) for i in range(n*n) if p in d[i]} for p in range(n*n)]


def vrai_riche(a, paire, n, figures, couleurs):
    comp = compiler([a], n, figures, couleurs)
    d = [set() for _ in range(n*n)]
    for p,(f,c) in enumerate(zip(*paire)):
        d[f*n+c].add(p)
    return reduire(comp,n,d) is not None


def forcees_riche(a, n, figures, couleurs):
    """Preuve exacte pour UNE phrase riche autonome, pas une heuristique.

    Un compte/diversité est invariant par permutation des pions d'une même
    catégorie : aucun pion individuel ne peut être fixé (n>=3). Pour entre,
    énumération de tous les triples autorisés ; les autres pions se permutent
    librement sur les cases restantes. Les composés riches sont interdits.
    """
    comp = compiler([a],n,figures,couleurs)
    if a['type'] != 'entre':
        # La propagation détecte les comptes immédiatement impossibles.
        if reduire(comp,n) is None:
            raise ValueError('Phrase collective contradictoire')
        return {}
    possibles = [set() for _ in range(n*n)]
    for row in comp[3][0]:
        places = dict(row)
        autres = set(range(n*n)) - set(places.values())
        for i in range(n*n):
            possibles[i].update({places[i]} if i in places else autres)
    return {(figures[i//n], couleurs[i%n]): next(iter(s)) for i,s in enumerate(possibles) if len(s)==1}
