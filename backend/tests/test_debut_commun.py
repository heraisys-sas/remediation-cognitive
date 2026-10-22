"""Contrat du corpus : reconstruction exacte, correction et stabilité des données."""
import json
from pathlib import Path

from backend.app.domain.debut_commun import est_correct
from tools.generer_debut_commun import items_debut_commun

ROOT = Path(__file__).resolve().parents[2]


def test_corpus_reconstructs_two_distinct_nouns_and_has_progressive_hints():
    items = items_debut_commun()
    assert len(items) == len({item['id'] for item in items}) == 36
    for level in range(1, 4):
        assert sum(item['palier'] == level for item in items) == 12
    for item in items:
        pair = item['contenu']['debut_commun']
        assert pair['mots'] == [item['reponse']['valeur'] + end for end in pair['terminaisons']]
        assert len(set(pair['mots'])) == 2
        assert len(pair['definitions']) == 2
        assert set(pair['genres']) <= {'m', 'f'}
        assert [hint['type'] for hint in item['contenu']['indices']] == ['semantique', 'semantique', 'orthographique']
        assert est_correct(item, item['reponse']['valeur'])


def test_written_correction_preserves_accents_and_rejects_approximation():
    item = next(item for item in items_debut_commun() if item['reponse']['valeur'] == 'pré')
    assert est_correct(item, ' PRÉ ')
    assert est_correct(item, 'pre\u0301')
    for answer in ['pre', 'préavis', 'avant', '', None, 'pré avis']:
        assert not est_correct(item, answer)
    with_variant = {'reponse': {'valeur': 'ab', 'variantes': ['cd']}}
    assert est_correct(with_variant, 'CD')
    assert not est_correct(with_variant, 'ef')


def test_versioned_json_matches_generator():
    items = items_debut_commun()
    for level in range(1, 4):
        stored = json.loads((ROOT / f'content/entrainement/debut-commun/paliers/palier-{level:02d}.json').read_text())
        assert stored == [item for item in items if item['palier'] == level]
