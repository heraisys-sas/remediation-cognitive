"""Correction exacte et preuve déductive des logigrammes de catégories."""
from __future__ import annotations

import itertools
import json


def corriger_logigramme(item: dict, reponse: object) -> bool:
    """Exige toutes les associations, sans tolérance sémantique."""
    if isinstance(reponse, str):
        try:
            reponse = json.loads(reponse)
        except (ValueError, TypeError):
            return False
    return isinstance(reponse, dict) and reponse == item['reponse']['associations']


def _key(ref):
    return ref['categorie'], ref['valeur']


def _compatible(kind, left, right):
    return left == right if kind == 'association' else left != right if kind == 'exclusion' else left < right


def propager(contenu: dict) -> dict:
    """Arc-consistance + supports all-different exhaustifs, sans hypothèse.

    Les permutations ne sont que les supports d'une seule catégorie ; aucune
    recherche de solution globale n'est utilisée pour cette preuve.
    """
    categories = contenu['categories']
    n = len(categories[0]['valeurs'])
    domains = {(c['id'], v): set(range(n)) for c in categories for v in c['valeurs']}
    for i, value in enumerate(categories[0]['valeurs']):
        domains[categories[0]['id'], value] = {i}
    trace = []
    changed = True
    while changed:
        changed = False
        def narrow(key, supported, reason):
            nonlocal changed
            old = domains[key]
            new = old & supported
            if new != old:
                trace.append({'reference': list(key), 'avant': sorted(old), 'apres': sorted(new), 'regle': reason})
                domains[key] = new
                changed = True
        for index, clue in enumerate(contenu['contraintes']):
            left, right = _key(clue['gauche']), _key(clue['droite'])
            pairs = [(a, b) for a in domains[left] for b in domains[right] if _compatible(clue['type'], a, b)]
            narrow(left, {a for a, b in pairs}, f'indice {index + 1}')
            narrow(right, {b for a, b in pairs}, f'indice {index + 1}')
        for category in categories[1:]:
            keys = [(category['id'], v) for v in category['valeurs']]
            supports = [p for p in itertools.permutations(range(n)) if all(v in domains[k] for k, v in zip(keys, p))]
            for i, key in enumerate(keys):
                narrow(key, {p[i] for p in supports}, 'une valeur par ligne et par catégorie')
    solved = all(len(d) == 1 for d in domains.values())
    response = None
    if solved:
        response = {row: {c['id']: next(v for v in c['valeurs'] if domains[c['id'], v] == {i}) for c in categories[1:]} for i, row in enumerate(categories[0]['valeurs'])}
    return {'resolu': solved, 'solution': response, 'trace': trace}


def compter_solutions(contenu: dict, limite: int = 2) -> int:
    """Vérificateur indépendant par énumération, distinct de la preuve."""
    categories = contenu['categories']
    n = len(categories[0]['valeurs'])
    anchor = {(categories[0]['id'], v): i for i, v in enumerate(categories[0]['valeurs'])}
    total = 0
    for assignments in itertools.product(list(itertools.permutations(range(n))), repeat=len(categories) - 1):
        positions = dict(anchor)
        for category, permutation in zip(categories[1:], assignments):
            positions.update({(category['id'], v): p for v, p in zip(category['valeurs'], permutation)})
        if all(_compatible(c['type'], positions[_key(c['gauche'])], positions[_key(c['droite'])]) for c in contenu['contraintes']):
            total += 1
            if total >= limite:
                break
    return total
