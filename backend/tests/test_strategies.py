from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.memoires_immediates import Blocs
from backend.app.api.strategies import router


def client_at(root):
    app = FastAPI()
    app.state.blocs_strategies = Blocs(root)
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def client(tmp_path):
    return client_at(tmp_path)


def create(client, parcours, **extra):
    r = client.post('/api/strategies/sessions', json={'parcours': parcours, 'sans_limite_sessions': True, **extra})
    assert r.status_code == 201
    return r.json()['session_id']


def step(client, sid, action, data=None, key=None):
    return client.post(f'/api/strategies/sessions/{sid}/etapes', json={'etape_id': key or str(uuid4()), 'action': action, 'donnees': data or {}})


@pytest.mark.parametrize('order', [['remplir', 'joindre', 'signer'], ['joindre', 'remplir', 'signer']])
def test_plan_orders_and_locked_transitions(client, order):
    sid = create(client, 'plan')
    assert step(client, sid, 'executer', {'action_id': 'signer'}).status_code == 409
    r = step(client, sid, 'plan_initial', {'ordre': order}).json()
    assert 'Joindre la pièce avant de signer.' in r['scenario']['contraintes']
    assert step(client, sid, 'plan_initial', {'ordre': order}).status_code == 409
    step(client, sid, 'reviser', {'ordre': order})
    for item in order: assert step(client, sid, 'executer', {'action_id': item}).status_code == 200
    assert step(client, sid, 'terminer').status_code == 409
    assert 'resultat' not in step(client, sid, 'verifier').json()
    r = step(client, sid, 'terminer').json()['resultat']
    assert r['correction']['execution_compatible']
    assert r['observations']['actions_executees'] == order


def test_idempotent_restart_and_partial(tmp_path):
    c = client_at(tmp_path); sid = create(c, 'message'); key = str(uuid4())
    first = step(c, sid, 'masquer', {'note_presente': True}, key)
    restarted = client_at(tmp_path)
    assert step(restarted, sid, 'masquer', {'note_presente': True}, key).json() == first.json()
    assert step(restarted, sid, 'masquer', {'note_presente': False}, key).status_code == 409
    assert 'message' not in first.json()['scenario']
    r = restarted.post(f'/api/strategies/sessions/{sid}/fin').json()
    assert r['statut'] == 'interrompu' and 'correction' not in r
    assert step(restarted, sid, 'restituer', {'absence': True}).status_code == 409


def test_message_absence_aid_and_notes_local(client):
    sid = create(client, 'message', condition='sans-note')
    assert step(client, sid, 'masquer', {'note_presente': True}).status_code == 409
    assert step(client, sid, 'masquer', {'note_texte': 'secret'}).status_code == 422
    step(client, sid, 'masquer')
    assert step(client, sid, 'restituer').status_code == 409
    step(client, sid, 'reecouter'); step(client, sid, 'masquer')
    step(client, sid, 'restituer', {'absence': True})
    assert step(client, sid, 'restituer', {'quoi': 'appeler'}).status_code == 409
    r = step(client, sid, 'agir', {'action_id': 'appeler', 'heure': '15 h'}).json()['resultat']
    assert r['correction']['quoi'] == 'absence' and r['observations']['restitution_assistee']


def test_rappel_delivery_consultation_and_absence(client):
    sid = create(client, 'rappel')
    step(client, sid, 'configurer', {'piece_id': 'identite', 'rappel': True})
    for action in ('nom', 'date'): step(client, sid, 'intercaler', {'action_id': action})
    r = step(client, sid, 'consulter_rappel').json()
    assert r['donnees']['rappel_delivre'] and r['donnees']['rappel_consulte']
    r = step(client, sid, 'terminer').json()['resultat']
    assert r['correction']['action'] == 'occasion_terminee_sans_action'
    sid2 = create(client, 'rappel')
    r = client.post(f'/api/strategies/sessions/{sid2}/fin').json()
    assert 'correction' not in r


@pytest.mark.parametrize('duration,expected', [({'duree_active_secondes': 30, 'duree_ecoulee_secondes': 40, 'pauses_secondes': 10}, -30), ({'duree_active_secondes': 30, 'duree_ecoulee_secondes': 20, 'pauses_secondes': 10}, None), ({}, None)])
def test_time_signed_comparison_or_unavailable(client, duration, expected):
    sid = create(client, 'temps'); step(client, sid, 'estimer', {'secondes': 60})
    step(client, sid, 'pause'); step(client, sid, 'reprendre')
    for item, category in [('d4', 'courrier'), ('d2', 'courrier'), ('d3', 'facture'), ('d1', 'facture')]: step(client, sid, 'classer', {'document_id': item, 'categorie': category})
    r = step(client, sid, 'comparer', duration).json()
    assert r['donnees'].get('ecart_secondes') == expected
    assert 'resultat' not in r
    r = step(client, sid, 'marge', {'secondes': 15}).json()['resultat']
    assert all(r['correction']['classement'].values()) and r['pauses'] == 1


def test_quota_separate(client):
    for _ in range(3): assert client.post('/api/strategies/sessions', json={'parcours': 'plan'}).status_code == 201
    assert client.post('/api/strategies/sessions', json={'parcours': 'temps'}).status_code == 429
    assert client.post('/api/strategies/sessions', json={'parcours': 'temps', 'sans_limite_sessions': True}).status_code == 201


def test_rappel_intention_hidden_until_consulted_and_actual_rule(client):
    sid = create(client, 'rappel')
    r = step(client, sid, 'configurer', {'piece_id': 'facture', 'rappel': True}).json()
    assert 'consigne' not in r['scenario'] and 'rappel_texte' not in r['scenario']
    for action in ('nom', 'date'):
        r = step(client, sid, 'intercaler', {'action_id': action}).json()
        assert 'consigne' not in r['scenario'] and 'rappel_texte' not in r['scenario']
    r = step(client, sid, 'consulter_rappel').json()
    assert 'Facture' in r['scenario']['rappel_texte']
    assert 'identité' not in r['scenario']['rappel_texte']


def test_rappel_premature_and_no_signal_not_failure(client):
    sid = create(client, 'rappel')
    step(client, sid, 'configurer', {'piece_id': 'identite', 'rappel': False})
    step(client, sid, 'joindre', {'piece_id': 'identite'})
    for action in ('nom', 'date'): step(client, sid, 'intercaler', {'action_id': action})
    r = step(client, sid, 'terminer').json()['resultat']
    assert r['correction']['action'] == 'prematuree'
    sid = create(client, 'rappel')
    from backend.app.api.strategies.protocoles import stimulus
    piece = stimulus(client.app.state.blocs_strategies.read(sid))['pieces'][0]['id']
    assert step(client, sid, 'configurer', {'piece_id': piece, 'rappel': False}).status_code == 200
    r = client.post(f'/api/strategies/sessions/{sid}/fin').json()
    assert r['statut'] == 'interrompu' and 'correction' not in r


def test_message_uncertain_sentence_never_exact(client):
    sid = create(client, 'message')
    step(client, sid, 'masquer')
    step(client, sid, 'restituer', {'quoi': 'Je ne dois pas appeler le secrétariat', 'quand': '15 heures'})
    r = step(client, sid, 'agir', {'action_id': 'appeler', 'heure': '15 h'}).json()['resultat']
    assert r['correction']['quoi'] == 'a_verifier' and r['correction']['quand'] == 'exact'


def test_time_interface_wait_separate_from_user_pause(client):
    sid = create(client, 'temps')
    step(client, sid, 'estimer', {'secondes': 60})
    for item in ('d1', 'd2', 'd3', 'd4'):
        step(client, sid, 'classer', {'document_id': item, 'categorie': 'facture'})
    r = step(client, sid, 'comparer', {'duree_active_secondes': 30, 'duree_ecoulee_secondes': 40, 'pauses_secondes': 5, 'attente_interface_secondes': 5}).json()['donnees']
    assert r['ecart_secondes'] == -30
    assert r['pauses_secondes'] == 5 and r['attente_interface_secondes'] == 5


@pytest.mark.parametrize('parcours', ['plan', 'rappel', 'message', 'temps'])
def test_twelve_banked_scenarios_rotate_without_repeating(client, parcours):
    from backend.app.api.strategies.protocoles import BANQUES, stimulus

    ids = []
    for index in range(13):
        sid = create(client, parcours)
        session = client.app.state.blocs_strategies.read(sid)
        item = stimulus(session)
        ids.append(session['scenario_id'])
        assert session['version'] == 'strategies-appliquees-v3'
        first = client.app.state.blocs_strategies.read(sid)
        # All public payloads exclude private correction material.
        from backend.app.api.strategies.protocoles import public
        assert not any(k.startswith('attendu') or k == 'formes_quoi' for k in public(first)['scenario'])
        if parcours == 'plan':
            order = ['joindre', 'remplir', 'signer']
            step(client, sid, 'plan_initial', {'ordre': order})
            step(client, sid, 'reviser', {'ordre': order})
            for action in order: step(client, sid, 'executer', {'action_id': action})
            step(client, sid, 'verifier')
            r = step(client, sid, 'terminer').json()['resultat']
            assert r['correction']['execution_compatible']
        elif parcours == 'rappel':
            step(client, sid, 'configurer', {'piece_id': item['attendu_piece'], 'rappel': True})
            for action in item['actions_intercalees']: step(client, sid, 'intercaler', {'action_id': action['id']})
            r = step(client, sid, 'consulter_rappel').json()
            assert item['signal'] in r['scenario']['rappel_texte']
            step(client, sid, 'joindre', {'piece_id': item['attendu_piece']})
            r = step(client, sid, 'terminer').json()['resultat']
            assert r['correction']['action'] == 'exacte'
        elif parcours == 'message':
            step(client, sid, 'masquer')
            step(client, sid, 'restituer', {'quoi': item['attendu_quoi'], 'quand': item['attendu_heure'] + ':00'})
            r = step(client, sid, 'agir', {'action_id': item['attendu_action'], 'heure': item['attendu_heure'] + ' h'}).json()['resultat']
            assert all(r['correction'][key] == 'exact' for key in ('quoi', 'quand'))
            assert r['correction']['action_exacte'] and r['correction']['heure_exacte']
        else:
            step(client, sid, 'estimer', {'secondes': 60})
            for document, category in reversed(list(item['attendu_classement'].items())):
                step(client, sid, 'classer', {'document_id': document, 'categorie': category})
            step(client, sid, 'comparer')
            r = step(client, sid, 'marge', {'secondes': 10}).json()['resultat']
            assert all(r['correction']['classement'].values())
        assert r['scenario_id'] == ids[-1]
    assert ids[:12] == BANQUES[parcours] and len(set(ids[:12])) == 12 and ids[12] == ids[0]


def test_legacy_journal_without_scenario_id_keeps_version_and_correction(tmp_path):
    from backend.app.api.strategies.protocoles import ORIGINAUX, result

    c = client_at(tmp_path)
    sid = create(c, 'message')
    storage = c.app.state.blocs_strategies
    legacy = storage.read(sid)
    legacy.pop('scenario_id')
    legacy['version'] = 'strategies-appliquees-v1'
    storage.save(legacy)
    step(c, sid, 'masquer')
    step(c, sid, 'restituer', {'quoi': 'Appeler le secrétariat', 'quand': '15 h'})
    step(c, sid, 'agir', {'action_id': 'appeler', 'heure': '15 h'})
    before = result(storage.read(sid))
    # Une nouvelle simulation ne doit pas modifier le stimulus archivé.
    create(c, 'message')
    restarted = client_at(tmp_path)
    after = restarted.post(f'/api/strategies/sessions/{sid}/fin').json()
    assert after == before
    assert after['scenario_id'] == ORIGINAUX['message']['id']
    assert after['version'] == 'strategies-appliquees-v1'


@pytest.mark.parametrize('value,expected', [('15 h', '15'), ('15 heures', '15'), ('15:00', '15'), ('15h00', '15'), ('quinze heures', '15'), ('dix heures', '10'), ('dix-huit heures', '18'), ('15:30', '15:30')])
def test_hour_tolerances_are_explicit(value, expected):
    from backend.app.api.strategies.protocoles import hour
    assert hour(value) == expected


def test_all_v1_v2_scenarios_keep_their_exact_archived_content():
    import hashlib
    import json
    from backend.app.api.strategies.protocoles import SCENARIOS

    archived = {key: item for key, item in SCENARIOS.items() if key.endswith(('-v1', '-v2'))}
    serialized = json.dumps(archived, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    assert len(archived) == 16
    # Empreinte relevée avant les ajouts v3, pour interdire toute réécriture.
    assert hashlib.sha256(serialized.encode()).hexdigest() == '4f96c0a2cd3ad2516fc6f213f2d286c89c1bbc877c8cc7829e11561797b03786'


@pytest.mark.parametrize('parcours', ['plan', 'rappel', 'message', 'temps'])
def test_v2_archive_survives_restart_and_rotation_reaches_new_content(tmp_path, parcours):
    from backend.app.api.strategies.protocoles import BANQUES, public, stimulus

    c = client_at(tmp_path)
    sid = create(c, parcours)
    storage = c.app.state.blocs_strategies
    legacy = storage.read(sid)
    legacy.update(version='strategies-appliquees-v2', scenario_id=BANQUES[parcours][2])
    storage.save(legacy)
    original_public = public(legacy)
    original_scenario = stimulus(legacy)
    restarted = client_at(tmp_path)
    assert public(restarted.app.state.blocs_strategies.read(sid)) == original_public
    new_sid = create(restarted, parcours)
    new = storage.read(new_sid)
    assert new['scenario_id'] == f'strategie-{parcours}-simulation-4-v3'
    assert new['version'] == 'strategies-appliquees-v3'
    assert public(storage.read(sid)) == original_public
    assert stimulus(storage.read(sid)) == original_scenario
    response = step(restarted, sid, 'aide').json()
    assert response['version'] == 'strategies-appliquees-v2'
    assert response['scenario']['id'] == legacy['scenario_id']


def test_v3_content_keeps_load_and_unambiguous_correction_choices():
    from backend.app.api.strategies.banque_v3 import AJOUTS
    from backend.app.api.strategies.protocoles import hour, norm

    assert all(len(items) == 9 for items in AJOUTS.values())
    for item in AJOUTS['plan']:
        assert [action['id'] for action in item['actions']] == ['remplir', 'signer', 'joindre']
        assert len(set(action['texte'] for action in item['actions'])) == 3
    for item in AJOUTS['rappel']:
        assert len(item['pieces']) == len(item['actions_intercalees']) == 2
        assert sum(piece['id'] == item['attendu_piece'] for piece in item['pieces']) == 1
        target = next(piece['texte'] for piece in item['pieces'] if piece['id'] == item['attendu_piece'])
        assert target in item['consigne'] and item['signal'] in item['consigne']
    for item in AJOUTS['message']:
        assert len(item['actions']) == len(item['heures']) == 3
        assert sum(action['id'] == item['attendu_action'] for action in item['actions']) == 1
        assert sum(hour(value) == item['attendu_heure'] for value in item['heures']) == 1
        assert norm(item['attendu_quoi']) in item['formes_quoi']
    for item in AJOUTS['temps']:
        assert len(item['documents']) == 4 and len(item['categories']) == 2
        assert set(item['attendu_classement']) == {doc['id'] for doc in item['documents']}
        assert all(list(item['attendu_classement'].values()).count(category) == 2 for category in item['categories'])
