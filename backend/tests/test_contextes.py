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
