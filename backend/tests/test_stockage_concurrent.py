"""Tests de concurrence de la persistance (P0-A2) — vrais accès parallèles.

Contrairement à `test_ecritures_successives_sans_perte` (qui enchaîne les
écritures séquentiellement), ces tests lancent de **véritables** accès
concurrents (threads et processus) pour prouver la propriété revendiquée
par l'issue #1 : aucune mise à jour n'est perdue.

Isolés de `backend/tests/` pour ne pas hériter du `conftest.py` FastAPI.
"""

from __future__ import annotations

import datetime
import multiprocessing as mp
import sys
import threading

import pytest

from backend.app.storage.store import StockageJSON
from engine.srs.fsrs import CarteFSRS

THEME = "calcul-mental"
JOUR = datetime.date(2026, 1, 5)


def _travailleur(racine: str, iterations: int) -> None:
    """Incrémente le compteur `iterations` fois (exécuté dans un process)."""
    stockage = StockageJSON(racine=racine)
    for _ in range(iterations):
        stockage.incrementer_compteur(THEME, JOUR)


# --- threads : incréments atomiques ---------------------------------------


def test_increments_threads_sans_perte(tmp_path):
    """N threads × M incréments ⇒ exactement N×M (verrou processus)."""
    stockage = StockageJSON(racine=tmp_path)
    n_threads, par_thread = 8, 50
    erreurs: list[str] = []

    def tache() -> None:
        try:
            for _ in range(par_thread):
                stockage.incrementer_compteur(THEME, JOUR)
        except Exception as exc:  # noqa: BLE001
            erreurs.append(repr(exc))

    threads = [threading.Thread(target=tache) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
        assert not t.is_alive()

    assert not erreurs, erreurs
    assert stockage.lire_compteur(THEME, JOUR) == n_threads * par_thread


# --- processus : incréments atomiques -------------------------------------


def test_increments_processus_sans_perte(tmp_path):
    """Plusieurs processus concurrents ⇒ total exact (verrou inter-processus)."""
    n_proc, par_proc = 6, 40
    ctx = mp.get_context("spawn")
    procs = [
        ctx.Process(target=_travailleur, args=(str(tmp_path), par_proc))
        for _ in range(n_proc)
    ]
    try:
        for p in procs:
            p.start()
        for p in procs:
            p.join(timeout=20)
            assert p.exitcode == 0
    finally:
        for p in procs:
            if p.is_alive():
                p.terminate(); p.join(timeout=5)

    assert stockage_final(tmp_path) == n_proc * par_proc


def stockage_final(racine) -> int:
    return StockageJSON(racine=racine).lire_compteur(THEME, JOUR)


# --- lectures concurrentes : jamais d'état tronqué ------------------------


def test_lectures_concurrentes_ne_voient_que_des_etats_complets(tmp_path):
    """Pendant des écritures répétées, chaque lecture reste un JSON complet."""
    stockage = StockageJSON(racine=tmp_path)
    cartes = {f"i{n:02d}": CarteFSRS(f"i{n:02d}") for n in range(20)}
    stockage.ecrire_cartes(THEME, cartes)  # état initial complet

    erreurs: list[str] = []

    def ecrivain() -> None:
        for k in range(40):
            sous = dict(list(cartes.items())[: 1 + (k % 20)])
            stockage.ecrire_cartes(THEME, sous)

    def lecteur() -> None:
        for _ in range(80):
            lu = stockage.lire_cartes(THEME)
            if not set(lu) <= set(cartes):
                erreurs.append(f"clés inattendues : {set(lu) - set(cartes)}")

    threads = [
        threading.Thread(target=ecrivain),
        threading.Thread(target=ecrivain),
        threading.Thread(target=lecteur),
        threading.Thread(target=lecteur),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
        assert not t.is_alive()

    assert not erreurs, erreurs
