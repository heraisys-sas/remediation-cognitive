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
    assert client.post('/api/memoires-immediates/sessions', json={'parcours':'objets','parametres':{'longueur':7}}).status_code == 422


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

@pytest.mark.parametrize('parcours', ['code', 'chemin', 'changement', 'objets'])
def test_progression_deux_blocs_complets_puis_palier_suivant(client, parcours):
    def ouvrir():
        r = client.post('/api/memoires-immediates/sessions', json={'parcours': parcours, 'progression': True, 'sans_limite_sessions': True})
        assert r.status_code == 201
        return r.json()
    for _ in range(2):
        session = ouvrir()
        assert session['progression']['palier'] == (3 if parcours == 'code' else 2)
        trial = session['essai']
        for _ in range(4):
            s = trial['stimulus']
            if parcours == 'code':
                response = ''.join(s['chiffres'])
            elif parcours == 'chemin':
                response = s['trajet']
            elif parcours == 'objets':
                response = s['modele']
            else:
                changed = [a['position'] for a, b in zip(s['avant'], s['apres']) if a != b]
                response = {'decision': 'different' if changed else 'identique', 'localisation': changed}
            r = client.post(f"/api/memoires-immediates/sessions/{session['session_id']}/reponses", json={'essai_id': trial['id'], 'reponse': response})
            assert r.status_code == 200
            trial = r.json()['essai_suivant']
        client.post(f"/api/memoires-immediates/sessions/{session['session_id']}/fin")
        client.post(f"/api/memoires-immediates/sessions/{session['session_id']}/fin")
    assert ouvrir()['progression']['palier'] == (4 if parcours == 'code' else 3)


def test_paliers_avances_stimuli_et_correction():
    from backend.app.api.memoires_immediates.progression import PALIERS
    for parcours, levels in PALIERS.items():
        for level in levels:
            params = parameters(parcours, level)
            if parcours == 'chemin':
                params['plateau_etendu'] = True
            for seed in range(30):
                s = stimulus(parcours, params, str(seed), True)
                if parcours == 'code':
                    assert len(s['chiffres']) == params['longueur']
                    assert correction(parcours, s, ''.join(s['chiffres']))['exacte']
                elif parcours == 'chemin':
                    assert len(s['positions']) == 9
                    assert correction(parcours, s, s['trajet'])['exacte']
                elif parcours == 'objets':
                    assert len(s['objets']) == params['longueur']
                    assert correction(parcours, s, s['modele'])['exacte']
                else:
                    assert len(s['avant']) == params['longueur']
                    assert sum(a != b for a, b in zip(s['avant'], s['apres'])) == 1


def test_progression_ignore_aides_incomplets_et_separe_modalites():
    from backend.app.api.memoires_immediates.progression import etat
    def bloc(i, palier=3, correct=4, **extras):
        return {'session_id': str(i), 'cree': f'2026-10-10T12:00:{i:02}', 'terminee': True, 'parcours': 'code',
                'progression': {'version': 'paliers-mi-v1', 'palier': palier, 'condition': 'visuelle', 'revision': 0 if palier == 3 else 1},
                'essais': [{'premiere': {'correction': {'exacte': j < correct}}} for j in range(4)], **extras}
    a, b = bloc(1), bloc(2)
    b['essais'][0]['aide'] = {'reponse': '1234'}
    assert etat([a,b], 'code', 'visuelle')['palier'] == 3
    assert etat([a,bloc(3)], 'code', 'auditive')['palier'] == 3
    interrupted = bloc(4)
    interrupted['essais'][0]['interruption'] = {}
    interrupted['essais'][0]['premiere'] = None
    assert etat([a,interrupted], 'code', 'visuelle')['palier'] == 3
    sessions = [a,bloc(3),bloc(5,4,0),bloc(6,4,1)]
    assert etat(sessions, 'code', 'visuelle')['palier'] == 3
    assert etat([a,bloc(3)], 'code', 'visuelle')['palier'] == 4


def test_progression_clotures_desordonnees_et_revision_ancienne():
    from backend.app.api.memoires_immediates.progression import etat
    def bloc(i, fin, palier=3, revision=0, correct=4):
        return {'session_id': str(i), 'cree': str(i), 'fin': str(fin), 'terminee': True, 'parcours': 'code',
                'progression': {'version': 'paliers-mi-v1', 'palier': palier, 'condition': 'visuelle', 'revision': revision},
                'essais': [{'premiere': {'correction': {'exacte': j < correct}}} for j in range(4)]}
    sessions = [bloc(1,1), bloc(3,2)]
    assert etat(sessions, 'code', 'visuelle')['palier'] == 4
    sessions.append(bloc(2,3,correct=2))
    assert etat(sessions, 'code', 'visuelle')['palier'] == 4
    sessions += [bloc(4,4,4,1,0), bloc(5,5,4,1,1)]
    result = etat(sessions, 'code', 'visuelle')
    assert (result['palier'], result['revision']) == (3,2)
    sessions += [bloc(6,6), bloc(7,7)]
    assert etat(sessions, 'code', 'visuelle') == result
    sessions += [bloc(8,8,revision=2), bloc(9,9,revision=2)]
    assert etat(sessions, 'code', 'visuelle')['palier'] == 4


@pytest.mark.parametrize('condition', ['forme', 'couleur', 'association'])
def test_paliers_changement_toutes_conditions(condition):
    from backend.app.api.memoires_immediates.progression import PALIERS
    for level in PALIERS['changement']:
        params = parameters('changement', {**level, 'condition': condition})
        for seed in range(30):
            for changed in (False, True):
                sample = stimulus('changement', params, str(seed), changed)
                positions = [a['position'] for a,b in zip(sample['avant'],sample['apres']) if a != b]
                assert len(positions) == (2 if condition == 'association' else 1) * changed
                response = {'decision': 'different' if changed else 'identique', 'localisation': positions}
                result = correction('changement', sample, response)
                assert result['exacte']
                if changed:
                    assert result['localisation_exacte']


def test_ancien_bloc_garde_version_et_stimulus_apres_mise_a_jour(client):
    session = create(client)
    storage = client.app.state.blocs_memoires
    stored = storage.read(session['session_id'])
    stored['version'] = 'memoires-immediates-v1'
    stored['essais'][0].pop('version')
    original = stored['essais'][0]['stimulus']
    storage.save(stored)
    answer(client, session, ''.join(original['chiffres']))
    result = client.post(f"/api/memoires-immediates/sessions/{session['session_id']}/fin").json()
    assert result['version'] == 'memoires-immediates-v1'
    assert result['observations'][0]['version'] == 'memoires-immediates-v1'
    assert result['observations'][1]['version'] == 'memoires-immediates-v2'
    assert storage.read(session['session_id'])['essais'][0]['stimulus'] == original
