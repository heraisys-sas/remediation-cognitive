"""Frontières publiques et branchements des deux nouvelles cartes."""
from backend.app.api.entrainement.service import _item_sans_reponse
from backend.app.domain.correction import corriger
from backend.app.domain.feedback import essai_supplementaire


def test_segment_public_ne_revele_pas_les_mots_et_ne_mute_pas_la_banque():
    item = {"id": "dc-test", "type": "rappel-indice", "palier": 1,
            "contenu": {"debut_commun": {"mots": ["porte", "portail"], "terminaisons": ["e", "ail"]}},
            "reponse": {"valeur": "port", "variantes": []}}
    public = _item_sans_reponse(item)
    assert "reponse" not in public
    assert "mots" not in public["contenu"]["debut_commun"]
    assert item["contenu"]["debut_commun"]["mots"] == ["porte", "portail"]
    assert corriger("debut-commun", item, " PORT ")
    assert not corriger("debut-commun", item, "porte")
    assert not corriger("debut-commun", item, "je propose port")


def test_logigramme_raisonne_avant_revelation():
    assert essai_supplementaire("logigramme")


def test_cartes_exposees_et_seances_isolees(client):
    themes = {t["id"]: t for t in client.get('/api/entrainement/themes').json()['themes']}
    assert themes['debut-commun']['nom'] == 'Débuts de mots communs'
    assert themes['logigrammes']['nom'] == 'Croiser les indices'
    assert themes['logigrammes']['interface']['dictee'] is False
    assert themes['debut-commun']['palier_depart'] == 2
    for theme in ('debut-commun', 'logigrammes'):
        seance = client.post(f'/api/entrainement/{theme}/sessions').json()
        assert seance['items']
        for item in seance['items']:
            assert 'reponse' not in item
            assert 'preuve_deductive' not in item['contenu']


def test_correction_de_bout_en_bout_et_second_essai_prive(client):
    from backend.app.domain.contenu import ChargeurContenu
    banque = ChargeurContenu()
    for theme in ('debut-commun', 'logigrammes'):
        seance = client.post(f'/api/entrainement/{theme}/sessions').json()
        item_public = seance['items'][0]
        item = next(i for i in banque.items(theme) if i['id'] == item_public['id'])
        url = f"/api/entrainement/{theme}/sessions/{seance['session_id']}/reponses"
        if theme == 'logigrammes':
            essai = client.post(url, json={'item_id': item['id'], 'reponse': {}, 'temps_ms': 1000}).json()
            assert essai['essai_supplementaire'] is True
            assert essai.get('attendue') is None
        retour = client.post(url, json={'item_id': item['id'], 'reponse': item['reponse']['valeur'], 'temps_ms': 2000}).json()
        assert retour['correcte'] is True
        assert 'attendue' in retour


def test_validation_indices_segments_sans_faux_positif_et_sans_reponse():
    from tools.validation.items import erreurs_contenu
    item = {'theme': 'debut-commun', 'type': 'rappel-indice', 'reponse': {'valeur': 'ca'},
            'contenu': {'enonce': 'Chercher le début.', 'debut_commun': {'mots': ['cabane', 'cabine']},
                        'indices': [{'type': 'semantique', 'texte': 'Un abri de campagne.'},
                                    {'type': 'orthographique', 'texte': 'Commence par c.'}]}}
    assert not any('contient la réponse' in e for e in erreurs_contenu(item, ''))
    for divulgue in ('Le début est ca.', 'Une cabane.'):
        item['contenu']['indices'][0]['texte'] = divulgue
        assert any('contient la réponse' in e for e in erreurs_contenu(item, ''))
