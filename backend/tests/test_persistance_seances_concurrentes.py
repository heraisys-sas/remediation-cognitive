"""Intégration : plusieurs gestionnaires de séances partagent le même stockage."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from fastapi.testclient import TestClient
from backend.app.main import creer_app
from backend.app.domain.contenu import ChargeurContenu
from backend.app.storage.store import StockageJSON


def clients(tmp_path, n):
    return [TestClient(creer_app(racine_donnees=tmp_path / 'data',
        dossier_frontend=tmp_path / 'absent',
        horloge=lambda: datetime.now(timezone.utc))) for _ in range(n)]


def test_demarrage_concurrent_respecte_quota_et_increment_atomique(tmp_path, monkeypatch):
    appels = []
    original = StockageJSON.incrementer_compteur
    def incrementer(self, *args, **kwargs):
        appels.append(args)
        return original(self, *args, **kwargs)
    monkeypatch.setattr(StockageJSON, 'incrementer_compteur', incrementer)
    with ThreadPoolExecutor(max_workers=10) as pool:
        resultats = list(pool.map(lambda c: c.post('/api/entrainement/calcul-mental/sessions'), clients(tmp_path, 10)))
    assert sorted(r.status_code for r in resultats) == [201]*6 + [429]*4
    assert len(appels) == 6
    compteur = json.loads((tmp_path/'data/calcul-mental/compteur-seances.json').read_text())
    assert compteur['nb_sessions'] == 6


def test_clotures_concurrentes_conservent_cartes_historique_et_temps(tmp_path):
    cs = clients(tmp_path, 4)
    contenu = ChargeurContenu()
    sessions = []
    ids = set()
    for i,c in enumerate(cs):
        session = c.post('/api/entrainement/calcul-mental/sessions').json()
        item = session['items'][0]
        ids.add(item['id'])
        url = '/api/entrainement/calcul-mental/sessions/' + session['session_id']
        reponse = contenu.item('calcul-mental',item['id'])['reponse']['valeur']
        r = c.post(url+'/reponses', json={'item_id': item['id'], 'reponse': str(reponse), 'temps_ms': 2000+i})
        assert r.status_code == 200, r.text
        sessions.append((c,url))
    with ThreadPoolExecutor(max_workers=4) as pool:
        resultats = list(pool.map(lambda pair: pair[0].post(pair[1]+'/fin'), sessions))
    assert all(r.status_code == 200 for r in resultats), [r.text for r in resultats]
    racine = tmp_path/'data/calcul-mental'
    assert len(json.loads((racine/'maitrise.json').read_text())['historique']) == 4
    assert set(json.loads((racine/'cartes-fsrs.json').read_text())['cartes']) == ids
    assert sorted(json.loads((racine/'temps-reference.json').read_text())['temps']) == [2000,2001,2002,2003]


def test_reference_temps_existante_repli_mediane_et_fenetre(tmp_path):
    client = clients(tmp_path, 1)[0]
    gestionnaire = client.app.state.gestionnaire_entrainement
    stockage = gestionnaire.stockage
    assert gestionnaire._baseline_rt('calcul-mental') == 1000
    stockage.ecrire_temps_reference('calcul-mental', [100, 200, 300, 400])
    assert gestionnaire._baseline_rt('calcul-mental') == 1000
    stockage.ecrire_temps_reference('calcul-mental', [100, 200, 300, 400, 10000])
    assert gestionnaire._baseline_rt('calcul-mental') == 300
    stockage.ecrire_temps_reference('calcul-mental', list(range(1, 121)))
    assert len(stockage.lire_temps_reference('calcul-mental')) == 100
    assert gestionnaire._baseline_rt('calcul-mental') == 70.5
