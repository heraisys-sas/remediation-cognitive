"""Vérifications des corrections de contenu ; aucune prétention de validation clinique."""
import copy
import json
import itertools
from pathlib import Path

from tools import generer_methodes as methodes, generer_quotidien as quotidien
from tools.validate_items import erreurs_contenu

ROOT = Path(__file__).resolve().parents[2]


def test_plans_une_seule_etape_deplacable_et_ordre_total():
    items = json.loads((ROOT / 'content/entrainement/methodes/paliers/palier-04.json').read_text())
    for item, (situation, cible) in zip(items, methodes.PLANS_A_VERIFIER, strict=True):
        plan = item['contenu']['plan']
        # Les deux précédences imposent un seul ordre parmi toutes les permutations.
        possibles = [p for p in itertools.permutations(cible)
                     if p.index(cible[0]) < p.index(cible[1]) < p.index(cible[2])]
        assert possibles == [tuple(cible)]
        assert plan != cible
        deplacements = []
        for i, etape in enumerate(plan):
            reste = plan[:i] + plan[i+1:]
            for j in range(3):
                if reste[:j] + [etape] + reste[j:] == cible:
                    deplacements.append(etape)
        assert deplacements == [item['reponse']['valeur']], item['id']
        assert situation in item['contenu']['enonce']


def test_document_permanent_obligatoire():
    item = json.loads((ROOT / 'content/entrainement/methodes/paliers/palier-05.json').read_text())[0]
    assert not erreurs_contenu(item, '')
    ancien = copy.deepcopy(item)
    ancien['contenu']['affichage'] = {'mode': 'texte', 'duree_totale_ms': 20000, 'elements': [ancien['contenu'].pop('document')]}
    erreurs = erreurs_contenu(ancien, '')
    assert any('document permanent' in x for x in erreurs)
    assert any('pas de phase' in x for x in erreurs)


def test_generateurs_reproduisent_le_contenu_livre():
    for theme, module in [('methodes', methodes), ('quotidien', quotidien)]:
        module._RNG_FAMILLES.clear()
        paliers = module.construire_paliers()
        for n, items in enumerate(paliers, 1):
            path = ROOT / f'content/entrainement/{theme}/paliers/palier-{n:02d}.json'
            assert items == json.loads(path.read_text()), path
        assert module._manifest(paliers) == json.loads((ROOT / f'content/entrainement/{theme}/paliers.json').read_text())
