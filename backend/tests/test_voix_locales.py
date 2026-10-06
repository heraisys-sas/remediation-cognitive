from backend.app.domain import voix_locales


def test_liste_limitee_aux_voix_francaises_de_qualite(monkeypatch):
    monkeypatch.setattr(voix_locales.platform, 'system', lambda: 'Darwin')
    class Sortie:
        stdout = 'Audrey (Premium)    fr_FR # Bonjour\nThomas fr_FR # Bonjour\nSamantha en_US # Hello\n'
    monkeypatch.setattr(voix_locales.subprocess, 'run', lambda *a, **k: Sortie())
    assert voix_locales.voix_disponibles() == [{'id':'Audrey (Premium)', 'nom':'Audrey (haute qualité)'}]


def test_api_voix_et_selection_explicite(client, monkeypatch):
    monkeypatch.setattr(voix_locales, 'voix_disponibles', lambda: [{'id':'Audrey (Premium)', 'nom':'Audrey (haute qualité)'}])
    appels = []
    def produire(texte, voix):
        appels.append((texte, voix))
        return b'audio', 'audio/wav'
    monkeypatch.setattr(voix_locales, 'synthetiser', produire)
    assert client.get('/api/capacites/voix').json()['voix'][0]['id'] == 'Audrey (Premium)'
    r = client.post('/api/capacites/synthese', json={'texte':'Bonjour', 'voix':'Audrey (Premium)'})
    assert r.status_code == 200
    assert appels == [('Bonjour','Audrey (Premium)')]


def test_voix_arbitraire_non_executee(monkeypatch):
    monkeypatch.setattr(voix_locales, 'voix_disponibles', lambda: [])
    assert voix_locales.synthetiser('Bonjour', 'inconnue') is None
