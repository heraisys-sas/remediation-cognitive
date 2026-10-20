"""Filtrage de présentation : contrat DOM et stockage synthétique, sans historique."""
import shutil
import subprocess
from pathlib import Path


def test_filtre_accueil_javascript():
    node = shutil.which('node')
    assert node, 'Node requis pour les tests du filtre d’accueil'
    subprocess.run(
        [node, '--test', 'tools/test_accueil_difficultes.cjs'],
        cwd=Path(__file__).resolve().parents[2], check=True, capture_output=True, text=True,
    )
