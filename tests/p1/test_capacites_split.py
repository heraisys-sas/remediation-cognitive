"""Tests de la séparation capacites -> similarity/probe/tts (P1-B4)."""

from __future__ import annotations

from backend.app.domain import capacites, probe, similarity, tts


def test_modules_sont_separes():
    assert hasattr(similarity, "similarite")
    assert hasattr(probe, "capacites")
    assert hasattr(tts, "synthese")


def test_facade_reexporte_l_api():
    """capacites.py reste une porte d'entrée : mêmes objets, pas de copie."""
    assert capacites.similarite is similarity.similarite
    assert capacites.proche is similarity.proche
    assert capacites.synthese is tts.synthese
    assert capacites.capacites is probe.capacites
    assert capacites.SEUIL_SIMILARITE is similarity.SEUIL_SIMILARITE


def test_similarite_identique_vaut_1():
    assert similarity.similarite("bonjour", "bonjour") == 1.0


def test_proche_avec_seuil():
    assert similarity.proche("le chat", ["le chat"], seuil=0.5) is True
    assert similarity.proche("le chat", ["la lune"], seuil=0.9) is False


def test_probe_rapporte_les_trois_capacites():
    etat = probe.capacites()
    assert "similarite" in etat and "synthese" in etat and "voix" in etat
    assert etat["similarite"]["fournisseur"] in {"nle_embedding", "lexical"}
