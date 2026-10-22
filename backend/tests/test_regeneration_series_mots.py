"""Les compléments éditoriaux survivent à la régénération des banques."""
import json
import random
from pathlib import Path

from tools import generer_evocation, generer_rappel_series, generer_series_entendues

ROOT = Path(__file__).resolve().parents[2]


def test_series_regeneration_identique_et_manifest():
    banques = [
        ('rappel-series', generer_rappel_series.construire_paliers(random.Random(generer_rappel_series.GRAINE))),
        ('series-entendues', generer_series_entendues.construire()),
    ]
    for theme, paliers in banques:
        for numero, items in enumerate(paliers, 1):
            fichier = ROOT / f'content/entrainement/{theme}/paliers/palier-{numero:02d}.json'
            assert items == json.loads(fichier.read_text(encoding='utf-8'))
        assert len(paliers[3]) == 24
        for portee in ('toutes-series', 'premiere-serie'):
            assert sum(e['contenu']['portee'] == portee for e in paliers[3]) == 12
        manifeste = json.loads((ROOT / f'content/entrainement/{theme}/paliers.json').read_text())
        assert [e['nb_items'] for e in manifeste['paliers']] == [len(p) for p in paliers]


def test_sfa_pca_regeneration_identique():
    items = generer_evocation.items_evocation()
    for numero in (6, 7):
        fichier = ROOT / f'content/entrainement/evocation/paliers/palier-{numero:02d}.json'
        banque = [e for e in items if e['palier'] == numero]
        assert banque == json.loads(fichier.read_text(encoding='utf-8'))
        assert len(banque) == 18
