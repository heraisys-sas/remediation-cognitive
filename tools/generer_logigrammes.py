#!/usr/bin/env python3
"""Corpus original adulte : recoupement de catégories, preuve sans supposition."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend.app.domain.logigramme import propager, compter_solutions
from tools.generation import ecrire_json

SCENARIOS = [
    ('atelier', 'Les rendez-vous d’un atelier partagé', ['Aline', 'Boris', 'Céline', 'Dario'], ['lampe', 'chaise', 'étagère', 'table'], ['croquis', 'photo', 'notice', 'plan']),
    ('archives', 'La consultation des archives', ['Élise', 'Farid', 'Gaëlle', 'Hugo'], ['urbanisme', 'presse', 'cadastre', 'patrimoine'], ['registre', 'microfilm', 'classeur', 'carte']),
    ('association', 'Les permanences de l’association', ['Inès', 'Jules', 'Karim', 'Léa'], ['adhésions', 'comptabilité', 'matériel', 'bénévolat'], ['cahier', 'tablette', 'dossier papier', 'ordinateur']),
    ('exposition', 'Les préparatifs de l’exposition', ['Maya', 'Nabil', 'Olivia', 'Paul'], ['affiches', 'éclairage', 'cartels', 'accueil'], ['maquette', 'inventaire', 'fiche', 'schéma']),
]


def construire(palier: int, index: int, tentative: int = 0) -> dict:
    slug, title, names, topics, supports = SCENARIOS[index]
    n = 3 if palier == 1 else 4
    rng = random.Random(f'logigrammes:{palier}:{slug}:20261022' + (f':{tentative}' if tentative else ''))
    rows = ['09 h', '10 h', '11 h', '14 h'][:n]
    categories = [dict(id='horaire', label='Horaire', valeurs=rows), dict(id='personne', label='Personne', valeurs=names[:n]), dict(id='dossier', label='Sujet', valeurs=topics[:n])]
    if palier == 3:
        categories.append(dict(id='support', label='Support', valeurs=supports[:n]))
    solution = {}
    positions = {}
    for category in categories:
        values = category['valeurs'][:]
        if category['id'] != 'horaire':
            rng.shuffle(values)
        for i, value in enumerate(values):
            positions[category['id'], value] = i
            solution.setdefault(rows[i], {})[category['id']] = value
    for row in rows:
        del solution[row]['horaire']
    def ref(category, value):
        return {'categorie': category, 'valeur': value}
    def at(category, position):
        return next(ref(category, v) for (c, v), i in positions.items() if c == category and i == position)
    def clue(kind, left, right):
        a, b = left['valeur'], right['valeur']
        left_label = next(c['label'].lower() for c in categories if c['id'] == left['categorie'])
        right_label = next(c['label'].lower() for c in categories if c['id'] == right['categorie'])
        relation = {'association': 'au même horaire que', 'exclusion': 'à un horaire différent de', 'avant': 'à un horaire strictement antérieur à'}[kind]
        return {'type': kind, 'gauche': left, 'droite': right, 'texte': f'« {a} » ({left_label}) est {relation} « {b} » ({right_label}).'}
    # Les comparaisons croisent les catégories : aucun ordre total de
    # personnes n'est livré. On retire les indices tant que la propagation
    # prouve encore la solution ; chaque indice final devient nécessaire.
    references = [ref(c['id'], v) for c in categories for v in c['valeurs']]
    candidates = []
    for i, left in enumerate(references):
        for right in references[i + 1:]:
            lc, rc = left['categorie'], right['categorie']
            if lc == rc:
                continue
            a, b = positions[lc, left['valeur']], positions[rc, right['valeur']]
            if a == b:
                candidates.append(clue('association', left, right))
            else:
                candidates.append(clue('exclusion', left, right))
                # Comparaisons relationnelles sans horaire explicite ; leur
                # ordre ne se lit donc pas directement dans les intitulés.
                if lc != 'horaire' and rc != 'horaire':
                    candidates.append(clue('avant', left if a < b else right, right if a < b else left))
    rng.shuffle(candidates)
    clues = candidates[:]
    deduction_content = {'categories': categories, 'contraintes': clues}
    for candidate in candidates:
        reduced = [c for c in clues if c is not candidate]
        if {c['type'] for c in reduced} != {'association', 'exclusion', 'avant'}:
            continue
        deduction_content['contraintes'] = reduced
        if propager(deduction_content)['resolu']:
            clues = reduced
    # Ne pas garder un indice décoratif uniquement pour afficher une famille.
    if any(propager({'categories': categories, 'contraintes': clues[:i] + clues[i + 1:]})['resolu'] for i in range(len(clues))):
        assert tentative < 100, 'Aucune structure irréductible trouvée'
        return construire(palier, index, tentative + 1)
    rng.shuffle(clues)
    content = {'titre': title, 'consigne': 'Retrouve les associations de chaque rendez-vous. Chaque horaire accueille exactement une personne et un sujet, et chaque valeur de chaque catégorie est utilisée une seule fois.' + (' Chaque rendez-vous a aussi un support distinct, utilisé une seule fois.' if palier == 3 else '') + ' Les horaires sont classés du plus tôt au plus tard. « Avant » signifie strictement plus tôt, sans imposer de rendez-vous consécutifs. Toutes les informations nécessaires figurent dans les indices. Tu peux utiliser le tableau comme aide externe et modifier tes choix sans limite ; aucun chronomètre.', 'categories': categories, 'contraintes': clues, 'aide': 'Précise le but : une ligne complète par rendez-vous. Relève une contrainte, marque seulement ce qui est certain, puis vérifie avec les autres indices. Le tableau sert à organiser les informations.', 'indices': [{'niveau': 1, 'texte': 'Relis les règles : une valeur ne peut apparaître qu’une fois dans sa catégorie.'}, {'niveau': 2, 'texte': 'Regroupe les comparaisons « avant » pour reconstituer un ordre, puis recoupe cet ordre avec les associations et les exclusions.'}, {'niveau': 3, 'texte': 'Pour chaque valeur, barre les horaires impossibles. S’il ne reste qu’un horaire, vérifie-le dans tous les indices avant de le retenir.'}]}
    proof = propager(content)
    assert proof['resolu'] and proof['solution'] == solution, (palier, index)
    assert compter_solutions(content) == 1
    return {'id': f'lg-{palier}-{slug}-20261022', 'type': 'logigramme', 'module': 'entrainement', 'theme': 'logigrammes', 'fonctions_ciblees': ['fonctions-executives'], 'palier': palier, 'prerequis': [], 'cap_complexite': ['3 rendez-vous, 3 catégories : associations, comparaison et élimination', '4 rendez-vous, 3 catégories : comparaisons partielles et exclusions croisées', '4 rendez-vous, 4 catégories : recoupements successifs entre catégories'][palier - 1], 'contenu': content, 'reponse': {'valeur': json.dumps(solution, ensure_ascii=False, sort_keys=True), 'associations': solution, 'preuve_deductive': proof}, 'meta': {'auteur': 'generation-originale (tools/generer_logigrammes.py)', 'date_creation': '2026-10-22', 'relecture_ortho': {'statut': 'a_revoir'}}}


def generer():
    return {palier: [construire(palier, i) for i in range(4)] for palier in range(1, 4)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    for palier, items in generer().items():
        ecrire_json(ROOT / f'content/entrainement/logigrammes/paliers/palier-{palier:02}.json', items, dry_run=args.dry_run)
        print(f'Palier {palier} : {len(items)} items, solutions uniques et propagation complète vérifiées')

if __name__ == '__main__':
    main()
