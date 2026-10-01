"""Les exercices ciblés n'ont ni statut de bilan ni quota censé valider une mesure."""
from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.dosage import debut_fenetre, fenetre_sessions, limite_sessions
from datetime import date


def test_categories_des_themes(client):
    themes = {t['id']:t for t in client.get('/api/entrainement/themes').json()['themes']}
    for t in ('memoire','concentration','rappel-series','series-entendues'):
        assert themes[t]['categorie']=='cible'
    assert not any(t['categorie']=='evaluation' for t in themes.values())


def test_cibles_dosage_et_derogation(client):
    for _ in range(3):
        assert client.post('/api/entrainement/memoire/sessions').status_code==201
    assert client.post('/api/entrainement/memoire/sessions').status_code==429
    assert client.post('/api/entrainement/memoire/sessions',json={'sans_limite_sessions':True}).status_code==201
    assert client.post('/api/entrainement/memoire/sessions').status_code==429


def test_entrainement_garde_son_dosage(client):
    for _ in range(3):
        assert client.post('/api/entrainement/quotidien/sessions').status_code==201
    assert client.post('/api/entrainement/quotidien/sessions').status_code==429


def test_fenetres():
    assert fenetre_sessions('cible')=='jour'
    assert limite_sessions('cible')==3
    assert debut_fenetre('jour',date(2026,10,1))==date(2026,10,1)
    assert debut_fenetre('semaine',date(2026,10,1))==date(2026,9,28)


def test_la_categorie_ne_change_pas_le_contenu():
    contenu=ChargeurContenu()
    assert contenu.items('memoire') and contenu.items('quotidien')
