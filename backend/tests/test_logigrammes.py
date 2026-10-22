"""Corpus et correction : unicité indépendante, preuve sans supposition."""
import copy
import json
from pathlib import Path

import pytest

from backend.app.domain.logigramme import corriger_logigramme, compter_solutions, propager
from tools.generer_logigrammes import generer

ROOT = Path(__file__).resolve().parents[2]
ITEMS = [item for path in sorted((ROOT / 'content/entrainement/logigrammes/paliers').glob('*.json')) for item in json.loads(path.read_text())]


@pytest.mark.parametrize('item', ITEMS, ids=lambda item: item['id'])
def test_corpus_unique_et_deductif(item):
    content = item['contenu']
    proof = propager(content)
    assert proof['resolu']
    assert proof['solution'] == item['reponse']['associations']
    assert proof == item['reponse']['preuve_deductive']
    assert compter_solutions(content) == 1
    assert proof['trace']
    assert all(set(step['apres']) < set(step['avant']) for step in proof['trace'])
    assert {'association', 'exclusion', 'avant'} <= {c['type'] for c in content['contraintes']}
    assert 'solution' not in content
    assert len(content['categories']) == (4 if item['palier'] == 3 else 3)
    assert len(content['categories'][0]['valeurs']) == (3 if item['palier'] == 1 else 4)


@pytest.mark.parametrize('item', ITEMS, ids=lambda item: item['id'])
def test_correction_exige_toutes_les_associations(item):
    answer = item['reponse']['associations']
    assert corriger_logigramme(item, answer)
    assert corriger_logigramme(item, json.dumps(answer))
    assert not corriger_logigramme(item, None)
    assert not corriger_logigramme(item, 'pas un JSON')
    missing = copy.deepcopy(answer)
    first, second = list(missing)[:2]
    del missing[first]['dossier']
    assert not corriger_logigramme(item, missing)
    wrong = copy.deepcopy(answer)
    wrong[first]['personne'], wrong[second]['personne'] = wrong[second]['personne'], wrong[first]['personne']
    assert not corriger_logigramme(item, wrong)
    duplicate = copy.deepcopy(answer)
    duplicate[first]['personne'] = duplicate[second]['personne']
    assert not corriger_logigramme(item, duplicate)
    extra = copy.deepcopy(answer)
    extra[first]['intrus'] = 'extra'
    assert not corriger_logigramme(item, extra)


def test_sans_indices_pas_de_resolution_par_supposition():
    content = copy.deepcopy(ITEMS[0]['contenu'])
    content['contraintes'] = []
    assert not propager(content)['resolu']
    assert compter_solutions(content) == 2


def test_contradiction_sans_fausse_solution():
    content = copy.deepcopy(ITEMS[0]['contenu'])
    positive = next(c for c in content['contraintes'] if c['type'] == 'association')
    conflict = copy.deepcopy(positive)
    conflict['type'] = 'exclusion'
    content['contraintes'].append(conflict)
    assert not propager(content)['resolu']
    assert compter_solutions(content) == 0


def test_generation_identique_au_corpus_versionne():
    generated = generer()
    assert len(ITEMS) == 12
    assert len({item['id'] for item in ITEMS}) == 12
    assert [item for palier in generated.values() for item in palier] == ITEMS


def test_structures_variees_independamment_des_intitules():
    # Signature sur catégories/types, sans noms, sujets ou supports : les
    # variantes ne sont pas de simples renommages d'un même graphe d'indices.
    for palier in (1, 2, 3):
        signatures = set()
        for item in ITEMS:
            if item['palier'] != palier:
                continue
            constraints = item['contenu']['contraintes']
            signatures.add(tuple(sorted((c['type'], c['gauche']['categorie'], c['droite']['categorie']) for c in constraints)))
            assert all(c['gauche']['categorie'] != c['droite']['categorie'] for c in constraints)
            assert all('horaire' not in (c['gauche']['categorie'], c['droite']['categorie']) for c in constraints if c['type'] == 'avant')
        assert len(signatures) >= 2


@pytest.mark.parametrize('item', ITEMS, ids=lambda item: item['id'])
def test_chaque_indice_utile_au_recoupement(item):
    content = item['contenu']
    constraints = content['contraintes']
    for i in range(len(constraints)):
        reduced = {**content, 'contraintes': constraints[:i] + constraints[i + 1:]}
        assert not propager(reduced)['resolu']
