"""Séparation des données et du code PowerShell ; repli vocal préservé."""
import base64
from pathlib import Path
import platform
import subprocess
from backend.app.domain import capacites


def test_windows_texte_hors_du_script(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(capacites.shutil, 'which', lambda outil: outil)
    texte = "' ; $(commande) `id` \"\ntexte"
    def lancer(args, **options):
        script = base64.b64decode(args[-1]).decode('utf-16-le')
        assert texte not in script
        assert options['env']['TTS_TEXT'] == texte
        assert not options.get('shell', False)
        Path(options['env']['TTS_OUT']).write_bytes(b'RIFF-test')
    monkeypatch.setattr(capacites.subprocess, 'run', lancer)
    assert capacites.synthese(texte) == (b'RIFF-test', 'audio/wav')


def test_macos_exige_les_deux_outils(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Darwin')
    monkeypatch.setattr(capacites.shutil, 'which', lambda outil: outil if outil == 'say' else None)
    assert not capacites.synthese_disponible()


def test_retentative_voix_conservee(monkeypatch):
    monkeypatch.setattr(platform, 'system', lambda: 'Darwin')
    appels = []
    def lancer(args, **options):
        appels.append(args)
        if len(appels) == 1:
            raise subprocess.TimeoutExpired('say', 40)
        if args[0] == 'afconvert':
            Path(args[-1]).write_bytes(b'RIFF-test')
    monkeypatch.setattr(capacites.subprocess, 'run', lancer)
    assert capacites.synthese('gare') == (b'RIFF-test', 'audio/wav')
    assert len(appels) == 3
