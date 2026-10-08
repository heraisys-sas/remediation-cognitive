"""La même série peut être corrigée une fois après les scènes, puis de mémoire."""


def test_deux_passes_de_la_serie_contextes(client):
    demarrage = client.post('/api/entrainement/evocation/sessions', json={
        'parcours': 'memoire-source', 'sans_limite_sessions': True,
    })
    assert demarrage.status_code == 201
    seance = demarrage.json()
    items = seance['items']
    assert items and all(i['type'] == 'rappel-source' for i in items)
    from backend.app.domain.contenu import ChargeurContenu
    attendues = {i["id"]: i["reponse"]["valeur"] for i in ChargeurContenu().items("evocation", "memoire-source")}
    route = f"/api/entrainement/evocation/sessions/{seance['session_id']}"
    for passe in range(2):
        for numero, item in enumerate(items):
            erreur = passe == 1 and numero == 0
            retour = client.post(route + '/reponses', json={
                'item_id': item['id'],
                'reponse': 'Contexte inconnu' if erreur else attendues[item['id']],
                'temps_ms': 1500,
            })
            assert retour.status_code == 200
            assert retour.json()['correcte'] is not erreur
            assert retour.json()['attendue'] == attendues[item['id']]
    assert client.post(route + '/fin').status_code == 200
