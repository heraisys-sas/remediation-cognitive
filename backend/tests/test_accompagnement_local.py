"""Contrat portable du coaching : modèle facultatif, relances bornées, sans score."""

import asyncio
import json
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.app.domain import accompagnement_local as coaching
from backend.app.domain.messages import texte


def fake_sdk(monkeypatch, category="contrainte", available=True):
    model = SimpleNamespace(is_available=lambda: (available, None))
    seen = {}

    class Session:
        def __init__(self, **kwargs):
            seen.update(kwargs)

        async def respond(self, **kwargs):
            seen.update(kwargs)
            return SimpleNamespace(categorie=category)

    def guide(description, anyOf):
        seen["categories"] = anyOf
    sdk = SimpleNamespace(SystemLanguageModel=lambda: model, LanguageModelSession=Session,
                          generable=lambda cls: cls, guide=guide)
    monkeypatch.setattr(coaching.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(coaching.importlib, "import_module", lambda name: sdk)
    return model, seen


def test_modele_optionnel_sur_autre_plateforme(client, monkeypatch):
    monkeypatch.setattr(coaching.platform, "system", lambda: "Linux")
    def interdit(name):
        raise AssertionError("Aucun SDK sur cette plateforme")
    monkeypatch.setattr(coaching.importlib, "import_module", interdit)
    assert client.get("/api/capacites/accompagnement").json() == {
        "disponible": False, "local": True, "raison": "mac_requis",
    }


def test_sdk_absent(client, monkeypatch):
    monkeypatch.setattr(coaching.platform, "system", lambda: "Darwin")
    def absent(name):
        raise ImportError("absent")
    monkeypatch.setattr(coaching.importlib, "import_module", absent)
    response = client.post("/api/capacites/accompagnement", json={"texte": "Un texte", "reformulation": "Un essai"})
    assert response.status_code == 200
    assert response.json() == {"disponible": False, "relance": None, "raison": "sdk_absent"}


def test_relance_fermee_et_session_locale(client, monkeypatch):
    model, seen = fake_sdk(monkeypatch)
    payload = {"texte": "Le colis attend au guichet.", "reformulation": "Je retire un colis."}
    assert client.get("/api/capacites/accompagnement").json()["disponible"] is True
    response = client.post("/api/capacites/accompagnement", json=payload).json()
    assert response == {"disponible": True, "categorie": "contrainte", "relance": texte("entrainement", "accompagnement_contrainte")}
    assert seen["model"] is model
    assert seen["tools"] == []
    assert json.loads(seen["prompt"]) == {**payload, "question": ""}
    assert seen["categories"] == [c for c in coaching.CATEGORIES if c != "question"]
    assert seen["generating"].__name__ == "Selection"


def test_deuxieme_relance_exclut_categorie_precedente(client, monkeypatch):
    _, seen = fake_sdk(monkeypatch, category="verification")
    response = client.post("/api/capacites/accompagnement", json={
        "texte": "Texte", "reformulation": "Essai", "categories_deja_vues": ["contrainte"],
    }).json()
    assert response["categorie"] == "verification"
    assert "contrainte" not in seen["categories"]


@pytest.mark.parametrize("category", ["Voici le corrigé complet", "", None])
def test_texte_modele_inattendu_jamais_affiche(client, monkeypatch, category):
    fake_sdk(monkeypatch, category=category)
    response = client.post("/api/capacites/accompagnement", json={"texte": "Texte", "reformulation": "Essai"}).json()
    assert response == {"disponible": False, "relance": None, "raison": "generation_indisponible"}


@pytest.mark.parametrize("payload", [
    {"texte": " ", "reformulation": "Essai"},
    {"texte": "Texte", "reformulation": " "},
    {"texte": "a" * 6001, "reformulation": "Essai"},
    {"texte": "Texte", "reformulation": "a" * 2001},
    {"texte": "Texte", "reformulation": "Essai", "categories_deja_vues": ["autre"]},
])
def test_entrees_bornees(client, payload):
    assert client.post("/api/capacites/accompagnement", json=payload).status_code == 422


def test_timeout_annule_generation(monkeypatch):
    fake_sdk(monkeypatch)
    monkeypatch.setattr(coaching, "TIMEOUT_SECONDS", 0.001)
    cancelled = []
    async def long_call(**kwargs):
        try:
            await asyncio.sleep(10)
        finally:
            cancelled.append(True)
    sdk, model, _ = coaching._charger_modele()
    sdk.LanguageModelSession = lambda **kwargs: SimpleNamespace(respond=long_call)
    result = asyncio.run(coaching.accompagner("Texte", "Essai"))
    assert result["raison"] == "delai_depasse"
    assert cancelled == [True]


def test_exception_et_indisponibilite_ne_sortent_pas_du_module(monkeypatch):
    fake_sdk(monkeypatch, available=False)
    assert asyncio.run(coaching.accompagner("Texte", "Essai"))["disponible"] is False
    fake_sdk(monkeypatch)
    sdk, model, _ = coaching._charger_modele()
    sdk.LanguageModelSession = lambda **kwargs: SimpleNamespace(respond=AsyncMock(side_effect=RuntimeError("texte confidentiel")))
    assert asyncio.run(coaching.accompagner("Texte", "Essai")) == {
        "disponible": False, "relance": None, "raison": "generation_indisponible",
    }


@pytest.mark.skipif(os.environ.get("TEST_APPLE_FM_LOCAL") != "1", reason="Inférence locale explicite uniquement")
def test_inference_reelle_locale():
    assert coaching.etat()["disponible"] is True
    result = asyncio.run(coaching.accompagner(
        "Le colis doit être retiré jeudi au guichet avec une pièce d'identité.",
        "Je dois retirer mon colis.",
    ))
    assert result["disponible"] is True
    assert result["categorie"] in coaching.CATEGORIES
    assert result["relance"] == texte("entrainement", "accompagnement_" + result["categorie"])


def test_question_personnelle_transmise_sans_notation(client, monkeypatch):
    _, seen = fake_sdk(monkeypatch, category="question")
    response = client.post("/api/capacites/accompagnement", json={
        "texte": "Le colis attend au guichet.", "reformulation": "Je retire le colis.",
        "question": "Où aller ?",
    }).json()
    assert json.loads(seen["prompt"])["question"] == "Où aller ?"
    assert response["categorie"] == "question"
    assert "score" not in response
    assert response["relance"] == texte("entrainement", "accompagnement_question")
