"""Vérifications du contenu réellement servi, indépendantes de ses formules de génération."""
import json
from decimal import Decimal
from pathlib import Path
from tools.calcul_adulte import construire
from tools.verifier_calcul_adulte import recalculer
from tools.validate_items import erreurs_coherence_calcul

ROOT = Path(__file__).resolve().parents[2]


def test_corpus_servi_recalculable_sans_reponse_et_deterministe():
    corpus = construire()
    for palier, items in corpus.items():
        assert items == json.loads((ROOT / f'content/entrainement/calcul-mental/paliers/palier-{palier:02d}.json').read_text())
        assert len({i['contenu']['enonce'] for i in items}) == len(items)
        for item in items:
            assert recalculer(item['contenu']['enonce']) == Decimal(str(item['reponse']['valeur']))
            faux = {**item, 'reponse': {'valeur': item['reponse']['valeur'] + 1}}
            assert erreurs_coherence_calcul(faux, '', {'calcul-mental': {palier: {}}})
        assert all(i['id'].startswith('cm4-') for i in items)


def test_calcul_pur_et_variete_a_tous_les_paliers_adultes():
    for palier, items in construire().items():
        assert len({i['contenu']['famille_calcul'] for i in items[:12]}) >= 4
        purs = [i for i in items if i['contenu']['enonce'].startswith('Combien font ') or '= ?' in i['contenu']['enonce'] or i['contenu']['enonce'].startswith('Un nombre est multiplié ')]
        assert len(purs) >= len(items) / 3
    assert recalculer('Combien font (77,5 + 18,75) × 8 ?') == 770
    assert recalculer('Combien font 15 % de 240 ?') == 36


def test_seuil_livraison_inclus_et_variations_successives():
    assert recalculer('4 articles à 17 €. Livraison de 8 €, gratuite dès 68 € d’achats (seuil inclus). Quel total payer en euros ?') == 68
    assert recalculer('3 articles à 17 €. Livraison de 8 €, gratuite dès 60 € d’achats (seuil inclus). Quel total payer en euros ?') == 59
    assert recalculer('5 articles à 17 €. Livraison de 8 €, gratuite dès 80 € d’achats (seuil inclus). Quel total payer en euros ?') == 85
    assert recalculer('Un prix de 200 € augmente de 20 %, puis baisse de 10 % sur le nouveau prix. Quel est le prix final en euros ?') == 216
