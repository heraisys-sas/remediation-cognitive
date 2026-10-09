from fastapi.testclient import TestClient
import pytest

from backend.app.main import creer_app
from backend.app.api.memoires_immediates.protocoles import correction, parameters, stimulus


@pytest.fixture
def client(tmp_path):
    return TestClient(creer_app(racine_donnees=tmp_path / 'entrainement'))


def create(client, parcours='code', **params):
    response = client.post('/api/memoires-immediates/sessions', json={'parcours': parcours, 'parametres': params, 'sans_limite_sessions': True})
    assert response.status_code == 201
    return response.json()


def answer(client, session, response, **extras):
    return client.post(f"/api/memoires-immediates/sessions/{session['session_id']}/reponses", json={'essai_id': session['essai']['id'], 'reponse': response, **extras})


def test_codes_preserve_zero_and_serial_order():
    sample = {'chiffres': list('047')}
    assert correction('code', sample, '0 4-7')['exacte']
    r = correction('code', {'chiffres': list('472')}, '742')
    assert r['positions_exactes'] == 1 and r['elements_retrouves'] == 3 and not r['exacte']
    assert correction('code', {'chiffres': list('112')}, '111')['elements_retrouves'] == 2


def test_objects_permutation_and_invalid_duplicates():
    sample = stimulus('objets', parameters('objets', {}), 'test', False)
    expected = sample['modele']
    ids = list(expected)
    answer = dict(expected)
    answer[ids[0]], answer[ids[1]] = answer[ids[1]], answer[ids[0]]
    result = correction('objets', sample, answer)
    assert result['associations_erronees'] == 2 and result['permutation']
    with pytest.raises(ValueError):
        correction('objets', sample, {ids[0]: '0', ids[1]: '0'})


def test_changes_balanced_and_transformation_isolated():
    for condition in ('forme', 'couleur', 'association'):
        for seed in range(30):
            sample = stimulus('changement', parameters('changement', {'condition': condition}), seed, True)
            before, after = sample['avant'], sample['apres']
            if condition == 'association':
                assert sorted(e['couleur'] for e in before) == sorted(e['couleur'] for e in after)
                assert sum(a != b for a,b in zip(before, after)) == 2
            else:
                assert sum(a != b for a,b in zip(before, after)) == 1
                invariant = 'couleur' if condition == 'forme' else 'forme'
                assert [e[invariant] for e in before] == [e[invariant] for e in after]


@pytest.mark.parametrize('parcours,condition', [('code','forme'), ('chemin','forme'), ('objets','forme'), ('changement','forme'), ('changement','couleur'), ('changement','association')])
def test_four_trials_server_correction_and_durable_records(client, parcours, condition):
    s = create(client, parcours, condition=condition)
    changes = []
    for i in range(4):
        sample = s['essai']['stimulus']
        if parcours == 'code':
            value = ''.join(sample['chiffres'])
        elif parcours == 'chemin':
            value = sample['trajet']
        elif parcours == 'objets':
            value = sample['modele']
        else:
            changed = sample['avant'] != sample['apres']
            changes.append(changed)
            positions = [a['position'] for a,b in zip(sample['avant'], sample['apres']) if a != b]
            value = {'decision': 'different' if changed else 'identique', 'localisation': positions}
        response = answer(client, s, value)
        assert response.status_code == 200
        assert response.json()['correction']['exacte']
        s['essai'] = response.json()['essai_suivant']
    if parcours == 'changement':
        assert sum(changes) == 2
    final = client.post(f"/api/memoires-immediates/sessions/{s['session_id']}/fin").json()
    assert len(final['observations']) == 4 and final['terminee']
    assert all(row['premiere']['correction']['exacte'] for row in final['observations'])


def test_invalid_response_and_observations_do_not_mutate(client):
    s = create(client)
    assert answer(client, s, 'abc').status_code == 422
    assert answer(client, s, '123', observations={'correcte': True}).status_code == 422
    assert answer(client, s, '123', observations={'exposition_ms': -1}).status_code == 422
    assert answer(client, s, '123').status_code == 200
    assert answer(client, s, '123').status_code == 200


def test_interruption_replaces_without_scoring(client):
    s = create(client)
    response = client.post(f"/api/memoires-immediates/sessions/{s['session_id']}/interruption", json={'essai_id': s['essai']['id'], 'phase': 'exposition'})
    replacement = response.json()['essai']
    assert replacement['index'] == 1 and replacement['id'] != s['essai']['id']
    assert answer(client, s, '123').status_code == 409
    result = client.post(f"/api/memoires-immediates/sessions/{s['session_id']}/fin").json()['observations']
    assert result[0]['premiere'] is None and result[1]['remplace'] == result[0]['essai_id']


def test_assistance_keeps_first_response(client):
    s = create(client)
    assert answer(client, s, None).status_code == 200
    base = f"/api/memoires-immediates/sessions/{s['session_id']}"
    assert client.post(base+'/aide', json={'essai_id': s['essai']['id']}).status_code == 200
    assert answer(client, s, ''.join(s['essai']['stimulus']['chiffres']), assistee=True).status_code == 200
    records = client.post(base+'/fin').json()['observations']
    assert records[0]['premiere']['reponse'] is None and records[0]['aide']['correction']['exacte']


def test_limits_and_unknown_ids(client):
    for _ in range(3):
        assert client.post('/api/memoires-immediates/sessions', json={'parcours':'code'}).status_code == 201
    assert client.post('/api/memoires-immediates/sessions', json={'parcours':'code'}).status_code == 429
    assert client.post('/api/memoires-immediates/sessions', json={'parcours':'code','sans_limite_sessions':'true'}).status_code == 422
    assert client.post('/api/memoires-immediates/sessions/../../fin').status_code == 404
    assert client.post('/api/memoires-immediates/sessions', json={'parcours':'objets','parametres':{'longueur':5}}).status_code == 422


def test_retry_and_restart_preserve_first_and_replacement(tmp_path):
    root = tmp_path / 'entrainement'
    client = TestClient(creer_app(racine_donnees=root))
    s = create(client)
    first = answer(client, s, '012')
    assert answer(client, s, '012').json() == first.json()
    assert answer(client, s, '210').status_code == 409
    next_trial = first.json()['essai_suivant']
    base = f"/api/memoires-immediates/sessions/{s['session_id']}"
    body = {'essai_id':next_trial['id'], 'phase':'masque'}
    replacement = client.post(base+'/interruption', json=body).json()
    assert client.post(base+'/interruption', json=body).json() == replacement
    other = TestClient(creer_app(racine_donnees=root))
    final = other.post(base+'/fin').json()
    assert final['observations'][0]['premiere']['reponse'] == '012'
    assert final['observations'][1]['premiere'] is None
    assert other.post(base+'/fin').json() == final


def test_reserve_independence_and_changed_positions():
    layouts = set()
    reserve_matches = []
    for seed in range(100):
        p = parameters('changement', {'condition':'association'})
        s = stimulus('changement', p, seed, True)
        layouts.add(tuple(a['position'] for a,b in zip(s['avant'],s['apres']) if a != b))
        o = stimulus('objets', parameters('objets', {}), seed, False)
        model_order = sorted(o['modele'], key=o['modele'].get)
        reserve_matches.append(o['reserve'] == model_order)
    assert len(layouts) == 3 and any(reserve_matches) and not all(reserve_matches)


def test_assisted_interruption_keeps_first_and_cannot_be_answered(client):
    s = create(client)
    first = answer(client, s, None).json()
    base = f"/api/memoires-immediates/sessions/{s['session_id']}"
    client.post(base+'/aide', json={'essai_id':s['essai']['id']})
    body = {'essai_id':s['essai']['id'], 'phase':'exposition', 'assistee':True}
    result = client.post(base+'/interruption', json=body)
    assert result.status_code == 200
    assert result.json()['assistee_interrompue']
    assert result.json()['essai'] == first['essai_suivant']
    assert client.post(base+'/interruption', json=body).json() == result.json()
    assert answer(client, s, '012', assistee=True).status_code == 409
    final = client.post(base+'/fin').json()['observations']
    assert len(final) == 2 and final[0]['premiere']['reponse'] is None
    assert final[0]['aide']['interruption']['phase'] == 'exposition'
    assert 'reponse' not in final[0]['aide']


def test_untrusted_nested_localisation_is_rejected(client):
    s = create(client, 'changement')
    assert answer(client, s, {'decision':'different','localisation':[{}]}).status_code == 422
    assert answer(client, s, {'decision':'different','localisation':[['0']]}).status_code == 422


def test_chemin_vide_sauvegarde_et_retry_identique(client):
    session = client.post('/api/memoires-immediates/sessions', json={'parcours': 'chemin'}).json()
    payload = {'essai_id': session['essai']['id'], 'reponse': []}
    url = f"/api/memoires-immediates/sessions/{session['session_id']}/reponses"
    response = client.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['correction']['positions_exactes'] == 0
    assert data['correction']['elements_retrouves'] == 0
    assert data['essai_suivant'] is not None
    assert client.post(url, json=payload).json() == data
