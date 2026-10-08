"""Le parcours lexical garde le QCM comme entrée, jamais comme retour au P4."""
from backend.app.domain.contenu import ChargeurContenu


def test_palier_quatre_sans_qcm_et_historiques_preserves():
    chargeur = ChargeurContenu()
    parcours = chargeur.items('evocation', 'acces-lexical')
    assert {i['type'] for i in parcours if i['palier'] == 1} == {'reconnaissance'}
    for palier in (2, 3, 4, 5, 6):
        items = [i for i in parcours if i['palier'] == palier]
        assert items
        assert {i['type'] for i in items} == {'rappel-indice'}
    originaux = chargeur.items('evocation')
    assert any(i['palier'] == 5 and i['type'] == 'reconnaissance' for i in originaux)
    assert chargeur.palier_depart('evocation', 'acces-lexical') == 2
    definition = next(p for p in chargeur.parcours('evocation') if p['id'] == 'acces-lexical')
    assert 'QCM' in definition['libelles_paliers'][1]
    assert 'Point de départ' in definition['libelles_paliers'][2]
    assert 'types_par_source' not in definition


def test_banque_adulte_variee_et_dosee():
    from backend.app.domain.correction import corriger
    c = ChargeurContenu()
    items = c.items('evocation', 'acces-lexical')
    assert len(items) == 144
    for palier in range(1, 7):
        lot = [i for i in items if i['palier'] == palier]
        assert len(lot) == 24
        assert len({i['reponse']['valeur'] for i in lot}) == 24
        assert all(corriger('evocation', i, i['reponse']['valeur']) for i in lot)
        for item in lot:
            for variante in item['reponse'].get('variantes', []):
                # Les variantes sont utiles aux réponses libres, pas aux QCM.
                if item['type'] == 'rappel-indice': assert corriger('evocation', item, variante)
    assert c.max_items_parcours('evocation', 'acces-lexical', 2) == 10
    assert c.max_items_parcours('evocation', 'acces-lexical', 6) == 6
    assert c.max_items_parcours('evocation', 'strategie-semantique', 1) is None


def test_quota_reel_de_seance(client):
    for palier, quota in [(2, 10), (6, 6)]:
        resultat = client.post('/api/entrainement/evocation/sessions', json={
            'parcours': 'acces-lexical', 'palier': palier, 'sans_limite_sessions': True})
        assert resultat.status_code == 201
        assert len(resultat.json()['items']) == quota
