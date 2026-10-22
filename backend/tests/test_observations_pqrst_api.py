"""Checkpoint PQRST durable sans notation et sans effets sur le moteur."""
from backend.app.storage.store import StockageJSON


def demarrer(client):
    seance = client.post('/api/entrainement/methodes/sessions', json={
        'parcours': 'pqrst-guide', 'sans_limite_sessions': True,
    })
    assert seance.status_code == 201
    donnees = seance.json()
    item = next(i for i in donnees['items'] if i['type'] == 'pqrst-mise-en-oeuvre')
    return donnees, item, f"/api/entrainement/methodes/sessions/{donnees['session_id']}"


def debut():
    return {'5': [], '_pqrst': {'version': 'pqrst-sequence-v1', 'phase': 'pret',
        'etapes_realisees': [], 'statuts': {}, 'tentatives': {}, 'relectures': [],
        'interruptions': {}, 'modele_avant_test': False, 'reprise_apres_correction': False}}


def test_checkpoint_durable_idempotent_sans_reponse(client, app):
    seance, item, route = demarrer(client)
    assert item['contenu']['interface_pqrst']
    corps = {'item_id': item['id'], 'reponse': debut()}
    assert client.post(route + '/observations', json=corps).json() == {'enregistree': True}
    assert client.post(route + '/observations', json=corps).json() == {'enregistree': True}
    gestionnaire = app.state.gestionnaire_entrainement
    assert gestionnaire._session('methodes', seance['session_id']).reponses == {}
    document = StockageJSON(gestionnaire.stockage.racine).lire_observations(seance['session_id'])
    assert document['pqrst'][item['id']]['statut'] == 'partielle'
    assert document['pqrst'][item['id']]['tentatives'] == {}
    fin = client.post(route + '/fin').json()
    assert fin['resume']['items'] == 0
    assert 'observations_contextes' not in fin


def test_checkpoint_invalide_ne_note_pas(client, app):
    seance, item, route = demarrer(client)
    faux = debut()
    faux['_pqrst']['interruptions'] = {'4': -1}
    assert client.post(route + '/observations', json={'item_id': item['id'], 'reponse': faux}).status_code == 422
    assert client.post(route + '/reponses', json={'item_id': item['id'], 'reponse': faux, 'temps_ms': 1}).status_code == 422
    assert app.state.gestionnaire_entrainement._session('methodes', seance['session_id']).reponses == {}
    assert client.post(route + '/observations', json={'item_id': 'inconnu', 'reponse': debut()}).status_code == 404


def test_observation_complete_corrigee_reste_apres_checkpoint(client, app):
    seance, item, route = demarrer(client)
    etapes = {e['etape']: e for e in item['contenu']['etapes']}
    donnees = {'1': etapes[1]['bonne'], '2': 'Que faut-il savoir ?',
               '4': etapes[4]['modele'], '5': [q['bonne'] for q in etapes[5]['questions']]}
    donnees['_pqrst'] = {'version': 'pqrst-sequence-v1', 'phase': 'fin',
        'etapes_realisees': ['P', 'Q', 'R', 'S', 'retour-S', 'T1', 'T2'],
        'statuts': {cle: 'reponse' for cle in ['1', '2', '4', '5.0', '5.1']},
        'tentatives': {cle: [{'reponse': donnees['4'] if cle == '4' else donnees['5'][int(cle[-1])],
                            'condition': 'sans_relecture', 'modalite': 'clavier' if cle == '4' else 'choix'}]
                       for cle in ['4', '5.0', '5.1']},
        'modele_avant_test': True, 'reprise_apres_correction': False, 'relectures': [], 'interruptions': {}}
    resultat = client.post(route + '/reponses', json={'item_id': item['id'], 'reponse': donnees, 'temps_ms': 3000})
    assert resultat.status_code == 200
    complete = resultat.json()['sequence']['observation']
    assert complete['statut'] == 'complete'
    session = app.state.gestionnaire_entrainement._session('methodes', seance['session_id'])
    assert session.temps_reference == []
    assert len(session.reponses) == 1
    assert 'correction' in complete['tentatives']['4'][0]
    assert client.post(route + '/observations', json={'item_id': item['id'], 'reponse': debut()}).status_code == 200
    relu = StockageJSON(app.state.gestionnaire_entrainement.stockage.racine).lire_observations(seance['session_id'])
    assert relu['pqrst'][item['id']] == complete

    assert client.post(route + '/fin').json()['resume']['sans_aide'] == 0
