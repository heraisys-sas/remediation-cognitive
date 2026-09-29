"""Tests des outils de vérification du dépôt (exécutés en sous-processus).

Ces tests verrouillent les contrôles eux-mêmes : si un garde-fou est affaibli
dans le code ou le contenu, le test échoue. Ils s'exécutent depuis la racine
du dépôt, indépendamment du CWD.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

RACINE_DEPOT = Path(__file__).resolve().parents[2]


def _executer(outil: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", f"tools/{outil}"], cwd=RACINE_DEPOT, capture_output=True, text=True
    )


def test_validateur_contenu_zero_erreur():
    """Le contenu passe le validateur (schéma, manifests, invariantes)."""
    resultat = _executer("validate_items.py")
    assert resultat.returncode == 0, resultat.stdout[-2000:]
    assert "0 erreur(s)" in resultat.stdout


def test_verifier_reponses_zero_anomalie():
    """Les réponses sont recalculables depuis l'énoncé, sans anomalie."""
    resultat = _executer("verifier_reponses.py")
    assert resultat.returncode == 0, resultat.stdout[-2000:]
    assert "Anomalies : 0" in resultat.stdout


def test_verifier_interface_coherence():
    """L'interface et l'HTML restent cohérents (identifiants, remise à zéro)."""
    resultat = _executer("verifier_interface.py")
    assert resultat.returncode == 0, resultat.stdout

def test_verifier_session_transmet_le_palier():
    """La requête JS de démarrage porte le palier choisi (et rien en mode auto) :
    le contrôle exécute le VRAI demarrerSession + apiFetch de frontend/src/app.js
    sous Node, sur un fetch simulé. Node est cherché via NODE_BIN puis le PATH ;
    sans Node, le contrôle est ignoré et signalé."""
    node = os.environ.get("NODE_BIN") or shutil.which("node")
    if not node:
        pytest.skip("node indisponible : contrôle JS non exécuté")
    resultat = subprocess.run(
        [node, "tools/verifier_session.js"],
        cwd=RACINE_DEPOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert resultat.returncode == 0, (resultat.stdout + resultat.stderr)[-2000:]
    assert "palier 2 : POST avec corps" in resultat.stdout

