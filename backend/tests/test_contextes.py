"""La même série peut être corrigée une fois après les scènes, puis de mémoire."""


import pytest


@pytest.mark.parametrize("erreur_decouverte", [False, True])
def test_deux_passes_de_la_serie_contextes(client, erreur_decouverte):
    demarrage = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'sans_limite_sessions': True,
    })
    assert demarrage.status_code == 201
    seance = demarrage.json()
    items = seance['items']
    assert len(items) == 10 and all(i['type'] == 'rappel-source' for i in items)
    from backend.app.domain.contenu import ChargeurContenu
    attendues = {i["id"]: i["reponse"]["valeur"] for i in ChargeurContenu().items("evocation", "memoire-source")}
    route = f"/api/entrainement/evocation/sessions/{seance['session_id']}"
    for passe in range(2):
        for numero, item in enumerate(items):
            erreur = numero == 0 and (erreur_decouverte if passe == 0 else not erreur_decouverte)
            retour = client.post(route + '/reponses', json={
                'item_id': item['id'],
                'reponse': 'Contexte inconnu' if erreur else attendues[item['id']],
                'temps_ms': 1500,
                'memorisation': passe == 0,
            })
            assert retour.status_code == 200
            assert retour.json()['correcte'] is not erreur
            assert retour.json()['attendue'] == attendues[item['id']]
    fin = client.post(route + '/fin')
    assert fin.status_code == 200
    # Seul le rappel final compte, dans les deux sens de divergence.
    assert fin.json()['resume']['items'] == len(items)
    assert fin.json()['resume']['correctes'] == len(items) - (0 if erreur_decouverte else 1)


def test_decouverte_seule_ne_modifie_pas_fsrs_maitrise_ni_baseline(client):
    g = client.app.state.gestionnaire_entrainement
    seance = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'sans_limite_sessions': True,
    }).json()
    cle = 'evocation--memoire-source'
    cartes = g.stockage.lire_cartes(cle)
    progression = g.stockage.lire_maitrise(cle)
    temps = g.stockage.lire_temps_reference(cle)
    item = seance['items'][0]
    route = f"/api/entrainement/evocation/sessions/{seance['session_id']}"
    retour = client.post(route + '/reponses', json={
        'item_id': item['id'], 'reponse': 'inconnu', 'temps_ms': 2000,
        'memorisation': True,
    })
    assert retour.status_code == 200
    assert retour.json()['memorisation'] is True
    assert retour.json()['attendue']
    assert 'reprise' not in retour.json()
    fin = client.post(route + '/fin').json()
    assert fin['resume']['items'] == 0
    assert g.stockage.lire_cartes(cle) == cartes
    assert g.stockage.lire_maitrise(cle) == progression
    assert g.stockage.lire_temps_reference(cle) == temps


def test_memorisation_refusee_hors_scenes(client):
    seance = client.post('/api/entrainement/calcul-mental/sessions').json()
    route = f"/api/entrainement/calcul-mental/sessions/{seance['session_id']}"
    retour = client.post(route + '/reponses', json={
        'item_id': seance['items'][0]['id'], 'reponse': '0', 'temps_ms': 1000,
        'memorisation': True,
    })
    assert retour.status_code == 422


def test_profils_contextes_et_sources_familieres(client):
    g = client.app.state.gestionnaire_entrainement
    banque = g.contenu.items('evocation', 'memoire-source')
    originales = {i['id']: list(i['contenu']['options']) for i in banque}
    attendues = {i['id']: i['reponse']['valeur'] for i in banque}
    seance = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'profil_contextes': 'sources-vues', 'sans_limite_sessions': True,
    }).json()
    assert seance['protocole_contextes'] == {'version': 'contextes-source-v2', 'profil': 'sources-vues'}
    sources = {attendues[i['id']] for i in seance['items']}
    route = f"/api/entrainement/evocation/sessions/{seance['session_id']}"
    assert client.post(route + '/reponses', json={'item_id': seance['items'][0]['id'],
        'reponse': attendues[seance['items'][0]['id']], 'temps_ms': 1000}).status_code == 422
    for ordre, item in enumerate(seance['items'], 1):
        choix = item['contenu']['options_rappel']
        assert len(choix) == len(set(choix)) == min(4, len(sources))
        assert choix.count(attendues[item['id']]) == 1 and set(choix) <= sources
        assert item['contenu']['options'] == originales[item['id']]
        assert client.post(route + '/reponses', json={'item_id': item['id'],
            'reponse': attendues[item['id']], 'temps_ms': 1000, 'memorisation': True,
            'observation_contextes': {'passe': 'decouverte', 'ordre': ordre, 'presentee': True, 'photo_chargee': True, 'exposition_ms': 1000}}).status_code == 200
    for ordre, item in enumerate(seance['items'], 1):
        faux = next(c for c in item['contenu']['options_rappel'] if c != attendues[item['id']])
        retour = client.post(route + '/reponses', json={'item_id': item['id'],
            'reponse': faux, 'temps_ms': 1000,
            'observation_contextes': {'passe': 'rappel', 'ordre': ordre, 'presentee': True}})
        assert retour.status_code == 200 and not retour.json()['correcte']
    journal = g.stockage.lire_observations(seance['session_id'])
    for ligne, item in zip(journal['contextes']['rappel'], seance['items']):
        assert ligne['choix_proposes'] == item['contenu']['options_rappel']
        assert ligne['protocole'] == seance['protocole_contextes']
    assert {i['id']: i['contenu']['options'] for i in g.contenu.items('evocation', 'memoire-source')} == originales


@pytest.mark.parametrize('theme,corps', [('calcul-mental', {'profil_contextes': 'sources-vues'}),
    ('evocation', {'parcours': 'memoire-source', 'profil_contextes': 'inconnu'})])
def test_profil_invalide_ne_consomme_pas_seance(client, theme, corps):
    assert client.post(f'/api/entrainement/{theme}/sessions', json=corps).status_code == 422


def test_sources_vues_photo_chargee_et_recuperation(client):
    g = client.app.state.gestionnaire_entrainement
    seance = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'profil_contextes': 'sources-vues', 'sans_limite_sessions': True}).json()
    item = seance['items'][0]
    route = f"/api/entrainement/evocation/sessions/{seance['session_id']}/reponses"
    corps = {'item_id': item['id'], 'reponse': 'inconnu', 'temps_ms': 1000, 'memorisation': True,
             'observation_contextes': {'passe': 'decouverte', 'ordre': 1, 'incident_photo': True}}
    assert client.post(route, json=corps).status_code == 422
    assert not g._sessions[seance['session_id']].items_decouverts
    maitrise = g.stockage.lire_maitrise('evocation--memoire-source')
    corps['observation_contextes'].update(photo_chargee=True, exposition_ms=1234)
    assert client.post(route, json=corps).status_code == 200
    assert not g._sessions[seance['session_id']].reponses
    assert g.stockage.lire_cartes('evocation--memoire-source') == {}
    ligne = g.stockage.lire_observations(seance['session_id'])['contextes']['decouverte'][0]
    assert ligne['incident_photo'] and ligne['photo_chargee']
    assert client.post(route, json={**corps, 'memorisation': False,
        'observation_contextes': {'passe': 'rappel', 'ordre': 1}}).status_code == 422
    fin = client.post(route.removesuffix('/reponses') + '/fin').json()
    assert fin['resume']['items'] == 0
    assert g.stockage.lire_maitrise('evocation--memoire-source') == maitrise
    assert g.stockage.lire_temps_reference('evocation--memoire-source') == []


def test_sources_vues_petite_selection_sans_source_inedite(client, monkeypatch):
    from backend.app.api.entrainement import service
    original = service.selectionner_items
    monkeypatch.setattr(service, 'selectionner_items', lambda *args, **kwargs: original(*args, **kwargs)[:2])
    g = client.app.state.gestionnaire_entrainement
    seance = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'profil_contextes': 'sources-vues', 'sans_limite_sessions': True}).json()
    sources = {i['reponse']['valeur'] for i in g._sessions[seance['session_id']].items_par_id.values()}
    assert len(seance['items']) == 2
    for item in seance['items']:
        assert set(item['contenu']['options_rappel']) == sources


def test_origine_par_defaut_et_journal_versionne_sans_reponse(client):
    g = client.app.state.gestionnaire_entrainement
    seance = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'sans_limite_sessions': True}).json()
    assert seance['protocole_contextes']['profil'] == 'origine'
    assert all('options_rappel' not in i['contenu'] for i in seance['items'])
    assert g.stockage.lire_observations(seance['session_id'])['protocole_contextes'] == seance['protocole_contextes']
