"""Observations distinctes, durables et indépendantes de la progression historique."""
import pytest
from backend.app.domain.contenu import ChargeurContenu
from backend.app.storage.store import StockageJSON


def contexte(client):
    seance = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'sans_limite_sessions': True,
    }).json()
    item = seance['items'][0]
    attendue = next(i['reponse']['valeur'] for i in ChargeurContenu().items('evocation', 'memoire-source') if i['id'] == item['id'])
    return seance, item, attendue, f"/api/entrainement/evocation/sessions/{seance['session_id']}"


def repondre(client, route, item, reponse, passe='decouverte', **faits):
    return client.post(route + '/reponses', json={
        'item_id': item['id'], 'reponse': reponse, 'temps_ms': 120,
        'memorisation': passe == 'decouverte',
        'observation_contextes': {'passe': passe, 'ordre': 1, 'presentee_ms': 1000, **faits},
    })


def test_erreur_rappel_durable_et_justesse_client_ignoree(client, app):
    seance, item, attendue, route = contexte(client)
    assert repondre(client, route, item, attendue).status_code == 200
    assert repondre(client, route, item, 'inconnu', 'rappel', correcte=True).status_code == 200
    assert repondre(client, route, item, attendue, 'rappel').status_code == 200
    stockage = app.state.gestionnaire_entrainement.stockage
    relu = StockageJSON(stockage.racine).lire_observations(seance['session_id'])
    assert relu['contextes']['rappel'][0]['premiere_reponse']['correcte'] is False
    assert relu['contextes']['decouverte'][0]['premiere_reponse']['correcte'] is True
    faits = {'item_id': item['id'], 'passe': 'rappel', 'ordre': 1,
             'photo_apres_erreur': True, 'photo_revelee_ms': 2000,
             'premiere_reponse': {'correcte': True}}
    fin = client.post(route + '/fin', json={'observations_contextes': {'rappel': [faits]}})
    assert fin.status_code == 200
    rappel = fin.json()['observations_contextes']['rappel'][0]
    assert rappel['photo_apres_erreur'] is True
    assert rappel['premiere_reponse']['correcte'] is False
    assert fin.json()['resume']['items'] == 1
    assert fin.json()['resume']['correctes'] == 0
    assert client.post(route + '/fin', json={'observations_contextes': {'rappel': [faits]}}).json() == fin.json()


@pytest.mark.parametrize('faits', [
    {'passe': 'autre'}, {'ordre': True}, {'ordre': 2}, {'exposition_ms': -1},
    {'incident_photo': 'oui'}, {'photo_apres_erreur': True},
])
def test_metadata_invalide_sans_reponse_enregistree(client, app, faits):
    seance, item, attendue, route = contexte(client)
    assert repondre(client, route, item, attendue, **faits).status_code == 422
    session = app.state.gestionnaire_entrainement._session('evocation', seance['session_id'])
    assert session.reponses == {}


def test_rappel_avant_decouverte_et_revelation_sur_reussite_refuses(client):
    _, item, attendue, route = contexte(client)
    assert repondre(client, route, item, attendue, 'rappel').status_code == 422
    assert repondre(client, route, item, attendue).status_code == 200
    assert repondre(client, route, item, attendue, 'rappel').status_code == 200
    assert client.post(route + '/fin', json={'observations_contextes': {'rappel': [
        {'item_id': item['id'], 'passe': 'rappel', 'ordre': 1, 'photo_apres_erreur': True}
    ]}}).status_code == 422


def test_fin_partielle_conserve_incident_sans_futures_erreurs(client, app):
    seance, item, _, route = contexte(client)
    faits = {'item_id': item['id'], 'passe': 'decouverte', 'ordre': 1, 'incident_photo': True, 'presentee': False}
    fin = client.post(route + '/fin', json={'observations_contextes': {'decouverte': [faits]}})
    assert fin.status_code == 200
    assert fin.json()['resume']['items'] == 0
    assert len(fin.json()['observations_contextes']['decouverte']) == 1
    assert 'premiere_reponse' not in fin.json()['observations_contextes']['decouverte'][0]
    assert StockageJSON(app.state.gestionnaire_entrainement.stockage.racine).lire_observations(seance['session_id'])


def test_fin_invalide_ne_persiste_pas_les_faits_precedents(client, app):
    seance, item, attendue, route = contexte(client)
    repondre(client, route, item, attendue)
    repondre(client, route, item, attendue, 'rappel')
    stockage = app.state.gestionnaire_entrainement.stockage
    avant = stockage.lire_observations(seance['session_id'])
    fin = client.post(route + '/fin', json={'observations_contextes': {
        'decouverte': [{'item_id': item['id'], 'passe': 'decouverte', 'ordre': 1, 'incident_photo': True}],
        'rappel': [{'item_id': item['id'], 'passe': 'rappel', 'ordre': 1, 'photo_apres_erreur': True}],
    }})
    assert fin.status_code == 422
    assert stockage.lire_observations(seance['session_id']) == avant


@pytest.mark.parametrize('identifiant', ['../maitrise', 'abc', '00000000-0000-0000-0000-000000000000/../data'])
def test_journal_refuse_injection_chemin(tmp_path, identifiant):
    with pytest.raises(ValueError):
        StockageJSON(tmp_path).lire_observations(identifiant)
