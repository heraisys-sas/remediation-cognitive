"""Tests unitaires : persistance JSON (storage.store).

Couvre le round-trip des cartes FSRS (engine.srs.fsrs tel quel), la
maîtrise par palier, le compteur de séances du jour (remise à zéro au
changement de date) et la création des répertoires à la volée.
"""

from datetime import date, datetime, timezone

import pytest

from backend.app.storage.store import StockageJSON
from engine.srs.fsrs import CarteFSRS, planifier

T0 = datetime(2026, 9, 3, 12, 0, 0, tzinfo=timezone.utc)


def _stockage(tmp_path) -> StockageJSON:
    return StockageJSON(racine=tmp_path / "data" / "entrainement")


# -- cartes FSRS ---------------------------------------------------------------


def test_cartes_vierges_et_round_trip(tmp_path):
    stockage = _stockage(tmp_path)
    assert stockage.lire_cartes("calcul-mental") == {}

    carte, _ = planifier(CarteFSRS("cm-2-2x1"), 3, T0)
    stockage.ecrire_cartes("calcul-mental", {"cm-2-2x1": carte})
    relues = stockage.lire_cartes("calcul-mental")

    assert set(relues) == {"cm-2-2x1"}
    assert relues["cm-2-2x1"].item_id == "cm-2-2x1"
    assert relues["cm-2-2x1"].echeance_iso() == carte.echeance_iso()
    assert relues["cm-2-2x1"].etat == carte.etat


def test_repertoires_crees_a_la_volee(tmp_path):
    stockage = _stockage(tmp_path)
    dossier = stockage.racine / "anglais"
    assert not dossier.exists()
    stockage.ecrire_maitrise("anglais", 1, [])
    assert dossier.is_dir()


# -- maîtrise par palier ---------------------------------------------------------


def test_maitrise_valeurs_par_defaut_puis_round_trip(tmp_path):
    stockage = _stockage(tmp_path)
    etat = stockage.lire_maitrise("calcul-mental")
    assert etat == {"palier_courant": 1, "historique": []}

    stockage.ecrire_maitrise("calcul-mental", 2, [(1, 0.95), (1, 1.0), (1, 0.9)])
    etat = stockage.lire_maitrise("calcul-mental")
    assert etat["palier_courant"] == 2
    assert etat["historique"] == [(1, 0.95), (1, 1.0), (1, 0.9)]


# -- compteur de séances du jour --------------------------------------------------


def test_compteur_jour_et_rollover(tmp_path):
    stockage = _stockage(tmp_path)
    jour = date(2026, 9, 3)
    assert stockage.lire_compteur("python", jour) == 0

    stockage.ecrire_compteur("python", jour, 2)
    assert stockage.lire_compteur("python", jour) == 2
    # Le lendemain, le compteur est remis à zéro (date stockée ≠ date lue).
    assert stockage.lire_compteur("python", date(2026, 9, 4)) == 0


def test_theme_invalide_refuse(tmp_path):
    stockage = _stockage(tmp_path)
    with pytest.raises(ValueError):
        stockage.lire_cartes("../injection")
