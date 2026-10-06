"""Contrat de l'approfondissement facultatif : contenu serveur et aucun score."""
import asyncio
import json
import os
from types import SimpleNamespace

import pytest
from backend.app.domain import accompagnement_documents as module

PAYLOAD = {"item_id": "comparer-documents-v2-1-01", "reponses": {"jour": "ecart", "debut": "conforme"},
           "justification": "La demande est jeudi et la confirmation vendredi, mais l'heure est correcte."}
QUESTION = "Pour Jour (Demande : « jeudi » ; Confirmation : « vendredi »), quelle vérification ferais-tu avant d’agir ?"


def fake(monkeypatch, criterion="jour", angle="verification"):
    seen = {}
    class Session:
        def __init__(self, **kwargs):
            seen.update(kwargs)
        async def respond(self, **kwargs):
            seen.update(kwargs)
            return SimpleNamespace(critere=criterion, angle=angle)
    sdk = SimpleNamespace(LanguageModelSession=Session, generable=lambda c: c, guide=lambda *a, **k: None)
    monkeypatch.setattr(module, "_charger_modele", lambda: (sdk, object(), None))
    return seen


def test_documents_correction_du_serveur_et_justification(client, monkeypatch):
    seen = fake(monkeypatch)
    result = client.post("/api/capacites/accompagnement-documents", json=PAYLOAD)
    assert result.status_code == 200
    assert result.json() == {"disponible": True, "relance": QUESTION}
    prompt = json.loads(seen["prompt"])
    assert prompt["documents"][0]["lignes"][0]["texte"] == "jeudi"
    assert prompt["correction"] == PAYLOAD["reponses"]
    assert prompt["justification"] == PAYLOAD["justification"]
    assert seen["tools"] == []
    assert "score" not in result.json()


def test_second_echange_et_repetition(client, monkeypatch):
    seen = fake(monkeypatch)
    prior = {"justification": "Le jour diffère.", "relance": QUESTION}
    response = client.post("/api/capacites/accompagnement-documents", json={**PAYLOAD, "echanges": [prior]})
    assert json.loads(seen["prompt"])["echange_precedent"] == [prior]
    assert response.json()["raison"] == "relance_repetee"


@pytest.mark.parametrize("changes", [
    {"justification": " "}, {"justification": "x" * 801},
    {"correction": {"jour": "conforme"}},
    {"reponses": {"jour": "autre"}},
    {"echanges": [{"justification": "x", "relance": "?"}] * 2},
])
def test_entrees_bornees(client, changes):
    assert client.post("/api/capacites/accompagnement-documents", json={**PAYLOAD, **changes}).status_code == 422


@pytest.mark.parametrize("changes,reason", [
    ({"item_id": "inconnu"}, "item_inconnu"),
    ({"reponses": {"jour": "ecart"}}, "reponses_invalides"),
])
def test_item_ou_champs_invalides_sans_inference(client, monkeypatch, changes, reason):
    monkeypatch.setattr(module, "_charger_modele", lambda: pytest.fail("pas d'inférence"))
    assert client.post("/api/capacites/accompagnement-documents", json={**PAYLOAD, **changes}).json()["raison"] == reason


@pytest.mark.parametrize("criterion,angle", [(None, "verification"), ("absent", "preuve"), ("jour", "texte inventé")])
def test_selections_hors_contrat_non_affichees(client, monkeypatch, criterion, angle):
    fake(monkeypatch, criterion, angle)
    assert client.post("/api/capacites/accompagnement-documents", json=PAYLOAD).json()["raison"] == "generation_indisponible"


def test_modele_absent_non_bloquant(client, monkeypatch):
    monkeypatch.setattr(module, "_charger_modele", lambda: (None, None, "sdk_absent"))
    assert client.post("/api/capacites/accompagnement-documents", json=PAYLOAD).json() == {
        "disponible": False, "relance": None, "raison": "sdk_absent"}


def test_delai_et_exception_non_bloquants(client, monkeypatch):
    fake(monkeypatch)
    sdk, _, _ = module._charger_modele()
    async def wait(**kwargs):
        await asyncio.sleep(10)
    sdk.LanguageModelSession = lambda **kwargs: SimpleNamespace(respond=wait)
    monkeypatch.setattr(module, "TIMEOUT_SECONDS", .001)
    assert client.post("/api/capacites/accompagnement-documents", json=PAYLOAD).json()["raison"] == "delai_depasse"
    def broken(**kwargs):
        raise RuntimeError("private")
    sdk.LanguageModelSession = broken
    assert client.post("/api/capacites/accompagnement-documents", json=PAYLOAD).json()["raison"] == "generation_indisponible"


@pytest.mark.skipif(os.environ.get("TEST_APPLE_FM_LOCAL") != "1", reason="Inférence locale explicite uniquement")
def test_inference_reelle():
    result = asyncio.run(module.accompagner(**PAYLOAD))
    assert result["disponible"] is True, result
    assert result["relance"].endswith("?")
    print(result["relance"])


def test_rendu_borne_pour_tout_le_corpus():
    from backend.app.domain.messages import texte
    for item in module._chargeur.items("comparer-documents"):
        for field in item["contenu"]["champs"]:
            values = [f'{doc["titre"]} : « {next(l for l in doc["lignes"] if l["id"] == field["id"])["texte"]} »'
                      for doc in item["contenu"]["documents"]]
            for angle in ("preuve", "consequence", "verification"):
                question = texte("entrainement", "accompagnement_documents_" + angle).format(
                    critere=field["label"], documents=" ; ".join(values))
                assert len(question) <= 350
                assert question.endswith("?")
