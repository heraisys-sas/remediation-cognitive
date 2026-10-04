"""Synthèse vocale — extraction depuis `capacites.py` (issue #2, P0-A1).

Sécurité : aucun texte n'est **jamais** concaténé dans une commande shell.
- POSIX (`say`, `espeak-ng`, `afconvert`) : passage par **liste d'arguments**,
  `shell=False` implicite → insensible aux métacaractères.
- Windows (PowerShell) : le script est envoyé via `-EncodedCommand` (Base64
  UTF-16) et le texte transmis par **variable d'environnement**, jamais par
  interpolation dans le corps de la commande.

Renvoie `(octets_wav, "audio/wav")` ou `None` si la voix du système est
indisponible. Le contrôle d'entrée reste local : aucune donnée ne sort de
la machine (ADR-002).
"""

from __future__ import annotations

import base64
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

# Durées bornées : empêche tout blocage sur un moteur TTS honteux.
_TIMEOUT_S = 40


def _run(args: list[str], timeout: int = _TIMEOUT_S) -> bool:
    """Exécute une commande en **liste d'arguments** (jamais shell=True)."""
    try:
        subprocess.run(args, check=True, capture_output=True, timeout=timeout)
    except (subprocess.SubprocessError, OSError):
        return False
    return True


def _powershell_encoded(script: str) -> str:
    """Encode un script PowerShell en `-EncodedCommand` (UTF-16LE Base64)."""
    return base64.b64encode(script.encode("utf-16-le")).decode("ascii")


def _synthese_darwin(texte: str, brut: Path, final: Path) -> bool:
    if not _run(["say", "-o", str(brut), texte]):
        return False
    return _run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(brut), str(final)])


def _synthese_linux(texte: str, final: Path) -> bool:
    outil = shutil.which("espeak-ng") or shutil.which("espeak")
    if not outil:
        return False
    return _run([outil, "-w", str(final), texte])


def _synthese_windows(texte: str, final: Path) -> bool:
    """PowerShell sans interpolation du texte (env + -EncodedCommand)."""
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.SetOutputToWaveFile($env:TTS_OUT); "
        "$s.Speak([Environment]::GetEnvironmentVariable('TTS_TEXT')); "
        "$s.Dispose()"
    )
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if not exe:
        return False
    import os

    environ = {**os.environ, "TTS_OUT": str(final), "TTS_TEXT": texte}
    args = [exe, "-NoProfile", "-EncodedCommand", _powershell_encoded(script)]
    try:
        subprocess.run(
            args,
            check=True,
            capture_output=True,
            timeout=60,
            env=environ,
        )
    except (subprocess.SubprocessError, OSError):
        return False
    return True


def synthese(texte: str) -> tuple[bytes, str] | None:
    """Synthétise `texte` en WAV (octets, mime) ou `None` si indisponible.

    Entrée normalisée puis traitée sans aucun shell interprétable.
    """
    texte = (texte or "").strip()
    if not texte:
        return None
    systeme = platform.system()
    with tempfile.TemporaryDirectory() as dossier:
        brut = Path(dossier) / "voix.aiff"
        final = Path(dossier) / "voix.wav"
        if systeme == "Darwin":
            ok = _synthese_darwin(texte, brut, final)
        elif systeme == "Linux":
            ok = _synthese_linux(texte, final)
        elif systeme == "Windows":
            ok = _synthese_windows(texte, final)
        else:
            ok = False
        if ok and final.exists() and final.stat().st_size > 0:
            return final.read_bytes(), "audio/wav"
    return None
