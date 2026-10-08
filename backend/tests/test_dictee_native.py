"""WAV borné, nettoyage et absence de repli réseau de la dictée Apple."""
import base64
import io
from pathlib import Path
from types import SimpleNamespace
import subprocess
import wave
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.domain import dictee_locale as d


def audio(channels=1, width=2, rate=16000, seconds=0.1):
    f = io.BytesIO()
    with wave.open(f, 'wb') as w:
        w.setnchannels(channels); w.setsampwidth(width); w.setframerate(rate)
        w.writeframes(b'\0' * int(rate * seconds) * width * channels)
    return base64.b64encode(f.getvalue()).decode()


@pytest.mark.parametrize('value', ['???', base64.b64encode(b'not wav').decode(), audio(channels=2), audio(width=1), audio(seconds=61)])
def test_audio_invalide_ne_lance_pas_moteur(value, monkeypatch):
    monkeypatch.setattr(d, '_installation', lambda: pytest.fail('pas de moteur sur audio invalide'))
    with pytest.raises(ValueError):
        d.transcrire(value)


def test_transcription_fichier_temporaire_et_nettoyage(monkeypatch):
    paths = []
    monkeypatch.setattr(d, '_installation', lambda: {'disponible': True})
    def execute(path, timeout):
        paths.append(Path(path))
        assert paths[-1].read_bytes() == d.decoder_wav(audio())
        assert timeout == d.TRANSCRIPTION_TIMEOUT_SECONDS
        return {'disponible': True, 'texte': 'On attend devant la gare.'}
    monkeypatch.setattr(d, '_executer', execute)
    assert d.transcrire(audio())['texte'] == 'On attend devant la gare.'
    assert not paths[0].exists()


def test_indisponibilite_sans_repli(monkeypatch):
    monkeypatch.setattr(d, '_installation', lambda: {'disponible': False, 'raison': 'francais_non_installe'})
    monkeypatch.setattr(d, '_executer', lambda *a: pytest.fail('aucun repli'))
    assert d.transcrire(audio())['raison'] == 'francais_non_installe'


def test_timeout_et_sortie_invalide(monkeypatch):
    def timeout(*a, **kw): raise subprocess.TimeoutExpired('helper', 60)
    monkeypatch.setattr(subprocess, 'run', timeout)
    assert not d._executer('file', 60)['disponible']
    monkeypatch.setattr(subprocess, 'run', lambda *a, **kw: SimpleNamespace(stdout='[]'))
    assert not d._executer('file', 60)['disponible']


def test_api_dictee(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr(d, '_installation', lambda: {'disponible': True})
    monkeypatch.setattr(d, '_executer', lambda *a: {'disponible': True, 'texte': 'La gare'})
    monkeypatch.setattr(d, 'etat', lambda: {'disponible': True})
    assert client.get('/api/capacites/dictee').json()['disponible']
    assert client.post('/api/capacites/dictee', json={'audio_base64': audio()}).json()['texte'] == 'La gare'
    assert client.post('/api/capacites/dictee', json={'audio_base64': '???'}).status_code == 422
    monkeypatch.setattr(d, '_installation', lambda: {'disponible': False})
    assert client.post('/api/capacites/dictee', json={'audio_base64': audio()}).status_code == 503


def test_un_seul_appel_et_pas_de_succes_silencieux(monkeypatch):
    monkeypatch.setattr(d, '_installation', lambda: {'disponible': True})
    appels = []
    def execute(path, timeout):
        assert path != '--status'
        appels.append(path)
        return {'disponible': True, 'texte': '  \n  '}
    monkeypatch.setattr(d, '_executer', execute)
    assert d.transcrire(audio()) == {'disponible': False, 'raison': 'parole_non_detectee'}
    assert len(appels) == 1


def test_timeout_explicite(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired('helper', d.TRANSCRIPTION_TIMEOUT_SECONDS)
    monkeypatch.setattr(subprocess, 'run', timeout)
    assert d._executer('file', d.TRANSCRIPTION_TIMEOUT_SECONDS)['raison'] == 'transcription_trop_longue'
