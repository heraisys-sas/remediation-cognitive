"""Exerce les trois chemins de synthèse sans voix installée ni shell réel."""
import base64
from pathlib import Path
import subprocess
import pytest
from backend.app.domain import tts, capacites, probe


@pytest.mark.parametrize('systeme', ['Darwin', 'Linux', 'Windows'])
@pytest.mark.parametrize('texte', ["Bonjour.", "' ; $(touch interdit) `id` \"\ntexte", '--help'])
def test_commandes_et_audio(systeme, texte, monkeypatch):
    monkeypatch.setattr(tts.platform, 'system', lambda: systeme)
    monkeypatch.setattr(tts.shutil, 'which', lambda outil: outil)
    appels = []
    def lancer(args, **options):
        appels.append(args)
        assert isinstance(args, list) and not options.get('shell', False)
        if systeme == 'Windows':
            script = base64.b64decode(args[-1]).decode('utf-16-le')
            assert texte not in script
            assert options['env']['TTS_TEXT'] == texte
            sortie = options['env']['TTS_OUT']
        elif args[0] == 'afconvert':
            sortie = args[-1]
        else:
            assert args[-1] == texte
            sortie = args[args.index('-o' if systeme == 'Darwin' else '-w')+1]
        Path(sortie).write_bytes(b'RIFF-test-wave')
        return subprocess.CompletedProcess(args, 0)
    monkeypatch.setattr(tts.subprocess, 'run', lancer)
    assert tts.synthese(texte) == (b'RIFF-test-wave', 'audio/wav')
    assert len(appels) == (2 if systeme == 'Darwin' else 1)


def test_disponibilite_reexportee_et_honnete(monkeypatch):
    monkeypatch.setattr(tts.platform, 'system', lambda: 'Darwin')
    monkeypatch.setattr(tts.shutil, 'which', lambda outil: outil if outil == 'say' else None)
    assert capacites.synthese_disponible is tts.synthese_disponible
    assert not capacites.synthese_disponible()
    assert probe.capacites()['synthese']['disponible'] is False


def test_echec_moteur(monkeypatch):
    monkeypatch.setattr(tts.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(tts.shutil, 'which', lambda outil: outil)
    def echouer(*args, **kwargs):
        raise subprocess.TimeoutExpired('tts', 40)
    monkeypatch.setattr(tts.subprocess, 'run', echouer)
    assert tts.synthese('Bonjour') is None
