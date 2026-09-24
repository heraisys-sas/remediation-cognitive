"""Tests des outils de vérification du dépôt (exécutés en sous-processus).

Ces tests verrouillent les contrôles eux-mêmes : si un garde-fou est affaibli
dans le code ou le contenu, le test échoue. Ils s'exécutent depuis la racine
du dépôt, indépendamment du CWD.
"""

import subprocess
from pathlib import Path

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
