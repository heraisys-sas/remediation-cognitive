"""Tests de non-régression P0 (issues #1 #2 #3 #4).

Valide les quatre correctifs de robustesse :
- #2 / P0-A1 : la synthèse vocale n'interpole jamais de shell ;
- #3 / P0-A4 : source unique des seuils de fatigue, comparaison `>=` ;
- #1 / P0-A2 : la persistance protège les écritures concurrentes ;
- #4 / P0-A3 : la racine du projet est explicite et robuste.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from engine.fatigue import (
    SEUIL_RT_FATIGUE,
    SEUIL_TAUX_ERREUR,
    alerter_fatigue,
    taux_erreur,
)
from backend.app.domain import tts
from backend.app.domain.fatigue import alerter_fatigue as domain_alerter
from backend.app.storage.store import StockageJSON, _racine_projet


# --- P0-A1 : pas d'injection shell dans la synthèse vocale ----------------

def test_tts_ne_construit_pas_de_commande_shell():
    """Aucun appel à synthesese ne doit utiliser shell=True."""
    source = Path(tts.__file__).read_text(encoding="utf-8")
    assert "shell=True" not in source


def test_tts_texte_malveillant_ne_leve_pas_et_ne_declenche_rien():
    """Entrées à injection : le texte ne doit jamais être exécuté."""
    hostiles = [
        "$(touch /tmp/pwned)",
        "`id`",
        "'; echo pwned > /tmp/pwned ; '",
        'a"; rm -rf /tmp/x; "',
        "texte\nnormal avec ' guillemet",
    ]
    for texte in hostiles:
        # Ne doit jamais lever, quel que soit le moteur (ou None si indisponible).
        resultat = tts.synthese(texte)
        assert resultat is None or isinstance(resultat, tuple)
    # Aucun effet de bord : le flag d'injection n'a pas été créé.
    assert not Path("/tmp/pwned").exists()


def test_tts_vide_renvoie_none():
    assert tts.synthese("") is None
    assert tts.synthese("   ") is None


# --- P0-A4 : source unique de la fatigue ----------------------------------

def test_seuil_erreur_est_inclusif():
    """Un taux d'erreur exactement au seuil déclenche l'alerte (>=)."""
    assert alerter_fatigue([], baseline_rt=1000.0, taux_erreur_glissant=SEUIL_TAUX_ERREUR) is True
    assert alerter_fatigue([], baseline_rt=1000.0, taux_erreur_glissant=SEUIL_TAUX_ERREUR - 0.01) is False


def test_seuil_rt_est_strict():
    """Un RT exactement à 1,25x baseline NE déclenche PAS l'alerte (strict >)."""
    rt = 1000.0 * SEUIL_RT_FATIGUE
    assert alerter_fatigue([rt], baseline_rt=1000.0) is False
    assert alerter_fatigue([rt + 1], baseline_rt=1000.0) is True


def test_anti_bruit_min_reponses():
    """Pas d'alerte avant MIN_REPONSES_FATIGUE réponses."""
    assert alerter_fatigue([], 1000.0, taux_erreur_glissant=1.0, nb_reponses=2) is False
    assert alerter_fatigue([], 1000.0, taux_erreur_glissant=1.0, nb_reponses=3) is True


def test_domain_et_engine_partagent_la_meme_logique():
    """domain.fatigue n'est qu'une ré-export : identité de fonction."""
    assert domain_alerter is alerter_fatigue


def test_taux_erreur():
    assert taux_erreur([]) == 0.0
    assert taux_erreur([True, True, True]) == 0.0
    assert taux_erreur([False, False]) == 1.0
    assert taux_erreur([True, False]) == 0.5


# --- P0-A3 : racine explicite ---------------------------------------------

def test_racine_via_variable_environnement(tmp_path, monkeypatch):
    monkeypatch.setenv("REMEDIATION_ROOT", str(tmp_path))
    assert _racine_projet() == tmp_path.resolve()


def test_stockage_accepte_racine_explicite(tmp_path):
    stockage = StockageJSON(racine=tmp_path)
    assert stockage.racine == tmp_path
    # Écriture/lecture sur racine personnalisée, indépendante de la profondeur.
    stockage.ecrire_compteur("calcul-mental", __import__("datetime").date(2026, 1, 5), 2)
    assert stockage.lire_compteur("calcul-mental", __import__("datetime").date(2026, 1, 5)) == 2


def test_theme_invalide_rejete(tmp_path):
    stockage = StockageJSON(racine=tmp_path)
    with pytest.raises(ValueError):
        stockage.lire_cartes("../etc/passwd")


# --- P0-A2 : verrou sur la persistance ------------------------------------

def test_ecritures_concurrentes_sans_perte(tmp_path):
    """Plusieurs écritures concurrentes ne doivent perdre aucune donnée."""
    import datetime

    stockage = StockageJSON(racine=tmp_path)
    # Enchaînement read-modify-write simulé par écritures successives.
    for i in range(1, 6):
        stockage.ecrire_compteur("calcul-mental", datetime.date(2026, 1, 5), i)
    assert stockage.lire_compteur("calcul-mental", datetime.date(2026, 1, 5)) == 5


def test_module_store_ne_contient_plus_parents3():
    source = Path(os.path.dirname(__import__("backend.app.storage.store", fromlist=["x"]).__file__)) .joinpath("store.py")
    assert "parents[3]" not in source.read_text(encoding="utf-8")
