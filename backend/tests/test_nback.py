import random
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.memoires_immediates import Blocs
from backend.app.api.nback import router
from backend.app.api.nback.protocoles import advance, public, sequence


def client_at(root):
    app = FastAPI()
    app.state.blocs_nback = Blocs(root)
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def client(tmp_path):
    return client_at(tmp_path)


def create(client, **data):
    response = client.post('/api/nback/sessions', json={'sans_limite_sessions': True, **data})
    assert response.status_code == 201
    return response.json()['session_id']


def step(client, sid, action, data=None, key=None):
    return client.post(f'/api/nback/sessions/{sid}/etapes', json={'etape_id': key or str(uuid4()), 'action': action, 'donnees': data or {}})


def assert_hidden(data):
    if isinstance(data, dict):
        assert not set(data).intersection({'sequence', 'decisions', 'correspondance_attendue', 'resultat'})
        for value in data.values(): assert_hidden(value)
    elif isinstance(data, list):
        for value in data: assert_hidden(value)


def test_generator_exact_matches_and_variety():
    generated = [sequence(random.Random(seed)) for seed in range(100)]
    assert len({tuple(s) for s in generated}) > 90
    for values in generated:
        assert len(values) == 16
        assert sum(a == b for a, b in zip(values, values[1:])) == 5
        assert set(values) <= {'cercle', 'carre', 'triangle', 'etoile'}


def test_true_online_comparison_abbc():
    s = dict(session_id='example', version='test', condition='observation-sans-feedback', n=1, total=16, position=0, phase='ready', terminee=False, sequence=['cercle', 'carre', 'carre', 'triangle'] + ['etoile'] * 12, decisions=[])
    advance(s, 'commencer', {})
    advance(s, 'suivant', {})
    for decision in ('different', 'identique', 'different'):
        advance(s, 'repondre', {'decision': decision})
        assert 'symbole' not in public(s)
        advance(s, 'suivant', {})
    assert [r['position'] for r in s['decisions']] == [2, 3, 4]
    assert s['position'] == 5 and s['phase'] == 'decision'


def test_full_block_no_feedback_or_history(client, tmp_path):
    sid = create(client)
    values = Blocs(tmp_path).read(sid)['sequence']
    assert step(client, sid, 'repondre', {'decision': 'different'}).status_code == 409
    first = step(client, sid, 'commencer').json()
    assert first['position'] == 1 and first['phase'] == 'initialisation'
    assert_hidden(first)
    assert step(client, sid, 'repondre', {'decision': 'different'}).status_code == 409
    state = step(client, sid, 'suivant').json()
    for position in range(2, 17):
        assert state['position'] == position and state['symbole'] == values[position - 1]
        assert_hidden(state)
        answer = 'identique' if values[position - 1] == values[position - 2] else 'different'
        neutral = step(client, sid, 'repondre', {'decision': answer, 'exposition_secondes': 2.5}).json()
        assert neutral['phase'] == 'neutre' and 'symbole' not in neutral
        assert_hidden(neutral)
        assert step(client, sid, 'repondre', {'decision': answer}).status_code == 409
        state = step(client, sid, 'suivant').json()
    r = state['resultat']
    assert state['terminee'] and state['phase'] == 'resultat'
    assert r['correspondances_detectees'] == 5 and r['non_correspondances_rejetees'] == 10
    assert r['decisions_observees'] == 15 and r['absences_declarees'] == 0
    assert len(r['decisions']) == 15 and r['decisions'][0]['position'] == 2
    assert client.post(f'/api/nback/sessions/{sid}/fin').json() == state
    assert step(client, sid, 'suivant').status_code == 409


def test_retry_restart_same_payload_and_conflict(tmp_path):
    c = client_at(tmp_path); sid = create(c); key = str(uuid4())
    original = step(c, sid, 'commencer', key=key)
    restarted = client_at(tmp_path)
    assert step(restarted, sid, 'commencer', key=key).json() == original.json()
    assert step(restarted, sid, 'suivant', key=key).status_code == 409
    step(restarted, sid, 'suivant')
    answerkey = str(uuid4())
    response = step(restarted, sid, 'repondre', {'decision': 'absence'}, answerkey)
    assert step(c, sid, 'repondre', {'decision': 'absence'}, answerkey).json() == response.json()
    result = c.post(f'/api/nback/sessions/{sid}/fin').json()['resultat']
    assert result['decisions_observees'] == 1 and result['absences_declarees'] == 1
    assert sum(result[k] for k in ('correspondances_detectees', 'correspondances_manquees', 'non_correspondances_rejetees', 'fausses_alertes')) == 0


@pytest.mark.parametrize('reason', ['pause', 'masquage', 'fatigue'])
def test_interruption_excludes_unseen_future_decisions(client, reason):
    sid = create(client); step(client, sid, 'commencer'); step(client, sid, 'suivant')
    r = step(client, sid, 'interrompre', {'raison': reason}).json()
    assert r['terminee'] and r['phase'] == 'interrompu'
    assert r['resultat']['statut'] == 'interrompu'
    assert r['resultat']['decisions_observees'] == 0 and r['resultat']['absences_declarees'] == 0
    assert len(r['resultat']['sequence']) == 2
    assert r['resultat']['interruption']['raison'] == reason
    assert step(client, sid, 'repondre', {'decision': 'absence'}).status_code == 409
    assert client.post(f'/api/nback/sessions/{sid}/fin').json() == r


@pytest.mark.parametrize('data', [{'decision': True}, {'decision': 'yes'}, {'decision': 'identique', 'extra': 1}, {'decision': 'different', 'exposition_secondes': True}, {'decision': 'different', 'exposition_secondes': -1}, {'decision': 'different', 'exposition_secondes': '2'}, {'decision': 'different', 'exposition_secondes': 86401}])
def test_strict_decision_payload(client, data):
    sid = create(client); step(client, sid, 'commencer'); step(client, sid, 'suivant')
    assert step(client, sid, 'repondre', data).status_code == 422


def test_creation_quota_and_strict_contract(client):
    for _ in range(3): create(client, sans_limite_sessions=False)
    assert client.post('/api/nback/sessions', json={}).status_code == 429
    create(client)
    for data in ({'n': True}, {'sans_limite_sessions': 'true'}, {'sequence': ['secret']}):
        assert client.post('/api/nback/sessions', json=data).status_code == 422
    assert client.post('/api/nback/sessions/not-a-uuid/fin').status_code == 404
    sid = create(client)
    assert step(client, sid, 'commencer', {'unexpected': 1}).status_code == 422
    assert step(client, sid, 'interrompre', {'raison': 'resume'}).status_code == 422
    assert step(client, sid, 'suivant').status_code == 409


def test_errors_and_absences_remain_distinct(client, tmp_path):
    sid = create(client)
    values = Blocs(tmp_path).read(sid)['sequence']
    step(client, sid, 'commencer'); step(client, sid, 'suivant')
    omitted = 0
    for position in range(2, 17):
        match = values[position - 1] == values[position - 2]
        decision = 'absence' if position == 2 else ('different' if match else 'identique')
        omitted += position == 2 and match
        step(client, sid, 'repondre', {'decision': decision})
        response = step(client, sid, 'suivant').json()
    r = response['resultat']
    assert r['correspondances_manquees'] == 5 - omitted
    assert r['fausses_alertes'] == 10 - (1 - omitted)
    assert r['absences_declarees'] == 1
    assert r['correspondances_detectees'] == r['non_correspondances_rejetees'] == 0


def test_partial_abbc_observed_denominators_include_absences():
    s = dict(session_id='example', version='test', condition='observation-sans-feedback', n=1, total=16, position=0, phase='ready', terminee=False, sequence=['cercle', 'carre', 'carre', 'triangle'] + ['etoile'] * 12, decisions=[])
    advance(s, 'commencer', {})
    advance(s, 'suivant', {})
    for _ in range(2):
        advance(s, 'repondre', {'decision': 'absence'})
        advance(s, 'suivant', {})
    advance(s, 'interrompre', {'raison': 'pause'})
    r = public(s)['resultat']
    assert r['statut'] == 'interrompu' and r['decisions_observees'] == 2
    assert r['correspondances_observees'] == r['non_correspondances_observees'] == 1
    assert r['absences_correspondances'] == r['absences_non_correspondances'] == 1
    assert r['absences_declarees'] == 2
    assert r['correspondances_manquees'] == r['fausses_alertes'] == 0


def test_fin_records_exit_without_attributing_fatigue(client):
    sid = create(client)
    step(client, sid, 'commencer')
    response = client.post(f'/api/nback/sessions/{sid}/fin').json()
    assert response['resultat']['interruption']['raison'] == 'sortie'
    assert response['resultat']['decisions_observees'] == 0
    assert client.post(f'/api/nback/sessions/{sid}/fin').json() == response


@pytest.mark.parametrize('n', [1, 2, 3])
def test_generator_each_lag_exact_and_canonical_uniqueness(tmp_path, n):
    from backend.app.api.nback.protocoles import canonical
    for seed in range(100):
        values = sequence(random.Random(seed), n=n)
        assert len(values) == n + 15
        assert sum(values[i] == values[i - n] for i in range(n, len(values))) == 5
    client = client_at(tmp_path)
    seen = set()
    for index in range(65):
        if index == 30:
            client = client_at(tmp_path)
        sid = create(client, n=n)
        archived = Blocs(tmp_path).read(sid)
        identity = canonical(archived['sequence'])
        assert identity not in seen
        seen.add(identity)
        assert archived['total'] == n + 15 and archived['version'] == 'nback-visuel-v2'


@pytest.mark.parametrize('n', [2, 3])
def test_advanced_initialization_excluded_and_wrong_answers(client, tmp_path, n):
    sid = create(client, n=n)
    values = Blocs(tmp_path).read(sid)['sequence']
    state = step(client, sid, 'commencer').json()
    for position in range(1, n + 1):
        assert state['position'] == position and state['phase'] == 'initialisation'
        assert step(client, sid, 'repondre', {'decision': 'identique'}).status_code == 409
        state = step(client, sid, 'suivant').json()
    for position in range(n + 1, n + 16):
        assert state['position'] == position and state['phase'] == 'decision'
        assert_hidden(state)
        answer = 'different' if values[position - 1] == values[position - 1 - n] else 'identique'
        assert_hidden(step(client, sid, 'repondre', {'decision': answer}).json())
        state = step(client, sid, 'suivant').json()
    r = state['resultat']
    assert r['n'] == n and r['decisions_observees'] == r['decisions_prevues'] == 15
    assert r['correspondances_manquees'] == 5 and r['fausses_alertes'] == 10
    assert r['decisions'][0]['position'] == n + 1
    assert all(not row['leurre_proximite'] for row in r['decisions'] if row['correspondance_attendue'])
    assert r['fausses_alertes_leurres'] == r['leurres_proximite_observes']


@pytest.mark.parametrize('n', [True, False, 0, 4, '2', 2.0, None])
def test_n_parameter_strict(client, n):
    assert client.post('/api/nback/sessions', json={'n': n}).status_code == 422


def test_duplicate_canonical_legacy_and_exhaustion_no_write(tmp_path, monkeypatch):
    import backend.app.api.nback as api
    from backend.app.api.nback.protocoles import canonical
    storage = Blocs(tmp_path)
    client = client_at(tmp_path)
    sid = create(client)
    session = storage.read(sid)
    session['version'] = 'nback-visuel-v1'
    storage.save(session)
    mapping = {'cercle': 'carre', 'carre': 'triangle', 'triangle': 'etoile', 'etoile': 'cercle'}
    permuted = [mapping[value] for value in session['sequence']]
    assert canonical(permuted) == canonical(session['sequence'])
    monkeypatch.setattr(api, 'sequence', lambda **kwargs: permuted)
    assert client.post('/api/nback/sessions', json={'sans_limite_sessions': True}).status_code == 503
    assert len(list(tmp_path.glob('*.json'))) == 1
    assert storage.read(sid) == session


def test_v1_result_and_stimulus_unchanged_after_restart(tmp_path):
    client = client_at(tmp_path)
    sid = create(client)
    storage = Blocs(tmp_path)
    old = storage.read(sid)
    old.update(version='nback-visuel-v1', phase='decision', position=2)
    storage.save(old)
    state = step(client_at(tmp_path), sid, 'repondre', {'decision': 'absence'}).json()
    assert state['version'] == 'nback-visuel-v1' and state['n'] == 1 and state['total'] == 16
    r = client_at(tmp_path).post(f'/api/nback/sessions/{sid}/fin').json()['resultat']
    assert r['sequence'] == old['sequence'][:2]
    assert r['decisions'][0]['correspondance_attendue'] == (old['sequence'][1] == old['sequence'][0])
    assert 'leurres_proximite_observes' not in r and 'leurre_proximite' not in r['decisions'][0]
