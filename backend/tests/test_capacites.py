"""Tests de la couche de capacités du poste (similarité, synthèse vocale).

Les tests sont **portables** : ils ne supposent pas le fournisseur d'empreintes
d'Apple. Quand le poste ne sait pas comparer le sens, les assertions sémantiques
sont ignorées (le repli lexical reste vérifié, lui).
"""

import json

from backend.app.domain import capacites as cap
from backend.app.domain.contenu import ChargeurContenu

CONTENU = ChargeurContenu()


def _forcer_palier(tmp_path, theme, palier):
    dossier = tmp_path / "data" / theme
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "maitrise.json").write_text(
        json.dumps({"palier_courant": palier, "historique": []}), encoding="utf-8"
    )


def test_etat_des_capacites(client):
    """Le poste annonce ses capacités et son fournisseur de similarité."""
    corps = client.get("/api/capacites").json()
    assert corps["similarite"]["disponible"] is True
    assert corps["similarite"]["fournisseur"] in {"nle_embedding", "lexical"}
    assert 0 < corps["similarite"]["seuil"] <= 1
    assert "local" in corps["principe"]
    assert corps["voix"]["moyen"].startswith("client")


def test_similarite_bornee_et_ordonnee(client):
    """Le score est borné, et une formulation proche obtient plus qu'une autre."""
    corps = client.post(
        "/api/capacites/similarite",
        json={"texte": "le toubib", "cibles": ["le médecin", "la boulangerie"]},
    ).json()
    scores = {s["cible"]: s["score"] for s in corps["scores"]}
    assert all(0 <= s <= 1 for s in scores.values())
    assert scores["le médecin"] > scores["la boulangerie"]


def test_texte_identique_vaut_un(client):
    corps = client.post(
        "/api/capacites/similarite", json={"texte": "marteau", "cibles": ["marteau"]}
    ).json()
    assert corps["scores"][0]["score"] == 1.0


def test_synthese_par_la_voix_du_systeme(client):
    """La synthèse passe par la voix du système — ou annonce son indisponibilité."""
    reponse = client.post("/api/capacites/synthese", json={"texte": "Bonjour."})
    if cap.synthese_disponible():
        assert reponse.status_code == 200
        corps = reponse.json()
        assert corps["mime"] == "audio/wav"
        assert len(corps["audio_base64"]) > 100
    else:
        assert reponse.status_code == 503
        assert reponse.json()["erreur"] == "synthese_indisponible"


def test_reponse_lointaine_refusee(client, tmp_path):
    """Une réponse qui n'a rien à voir est refusée (quel que soit le fournisseur)."""
    _forcer_palier(tmp_path, "quotidien", 1)
    payload = client.post("/api/entrainement/quotidien/sessions").json()
    item = next(i for i in payload["items"]
                if CONTENU.item("quotidien", i["id"])["reponse"]["valeur"] == "la porte de la cave")
    reponse = client.post(
        f"/api/entrainement/quotidien/sessions/{payload['session_id']}/reponses",
        json={"item_id": item["id"], "reponse": "vendredi", "temps_ms": 1200},
    )
    assert reponse.json()["correcte"] is False


def test_formulation_proche_acceptee_avec_empreintes(client, tmp_path):
    """« la cave » est accepté pour « la porte de la cave » — si le poste sait comparer le sens."""
    if cap.fournisseur_similarite() != "nle_embedding":
        return
    _forcer_palier(tmp_path, "quotidien", 1)
    payload = client.post("/api/entrainement/quotidien/sessions").json()
    item = next(i for i in payload["items"]
                if CONTENU.item("quotidien", i["id"])["reponse"]["valeur"] == "la porte de la cave")
    reponse = client.post(
        f"/api/entrainement/quotidien/sessions/{payload['session_id']}/reponses",
        json={"item_id": item["id"], "reponse": "la cave", "temps_ms": 1200},
    )
    assert reponse.json()["correcte"] is True
