"""La dérogation rend jouables les items déjà terminés, dans le palier choisi."""
from datetime import datetime, timedelta, timezone
import pytest
from engine.srs.fsrs import CarteFSRS, planifier
from backend.app.domain.selection import selectionner_items


def carte_future(item_id):
    return planifier(CarteFSRS(item_id), 3, datetime.now(timezone.utc) + timedelta(days=10))[0]


def test_api_rejouer_palier_sans_attendre_echeance(client):
    gestionnaire = client.app.state.gestionnaire_entrainement
    items = gestionnaire.contenu.items('evocation', 'memoire-source')
    cle = 'evocation--memoire-source'
    gestionnaire.stockage.ecrire_cartes(cle, {i['id']: carte_future(i['id']) for i in items})
    corps = {'parcours': 'memoire-source', 'sans_limite_sessions': True}
    normal = client.post('/api/entrainement/evocation/sessions', json=corps)
    assert normal.status_code == 201
    assert normal.json()['items'] == []
    replay = client.post('/api/entrainement/evocation/sessions', json={**corps, 'rejouer_palier': True})
    assert replay.status_code == 201
    assert replay.json()['items']
    assert {i['id'] for i in replay.json()['items']} <= {i['id'] for i in items}
    assert gestionnaire.stockage.lire_cartes(cle).keys() == {i['id'] for i in items}


@pytest.mark.parametrize('etapes', [False, True])
def test_rejouer_respecte_palier_quota_et_cartes(etapes):
    items = [{'id': str(i), 'palier': 1, 'contenu': {'etape_progression': 1} if etapes else {}}
             for i in range(5)] + [{'id': 'autre', 'palier': 2}]
    cartes = {i['id']: carte_future(i['id']) for i in items}
    maintenant = datetime.now(timezone.utc)
    assert selectionner_items(items, cartes, 1, maintenant) == []
    selection = selectionner_items(items, cartes, 1, maintenant, max_items=3, inclure_non_dus=True)
    assert len(selection) == 3
    assert all(i['palier'] == 1 for i in selection)
