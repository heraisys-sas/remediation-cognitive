"""Tests des méthodes (PQRST, GMT, auto-instruction) et de l'analyse du mot (SFA/PCA)."""

from backend.app.domain.contenu import ChargeurContenu

CONTENU = ChargeurContenu()


def _forcer_palier(tmp_path, theme, palier):
    import json
    dossier = tmp_path / "data" / theme
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "maitrise.json").write_text(
        json.dumps({"palier_courant": palier, "historique": []}), encoding="utf-8"
    )


def _demarrer(client, theme):
    reponse = client.post(f"/api/entrainement/{theme}/sessions")
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def _repondre(client, theme, session_id, item_id, reponse):
    return client.post(
        f"/api/entrainement/{theme}/sessions/{session_id}/reponses",
        json={"item_id": item_id, "reponse": reponse, "temps_ms": 1500},
    )


def _attendue(theme, item_id):
    return CONTENU.item(theme, item_id)["reponse"]["valeur"]


# -- Méthodes : PQRST, GMT, auto-instruction -----------------------------------


def test_pqrst_texte_et_question(client, tmp_path):
    """PQRST : le texte est fourni (affiché temporisé), la question est à choix."""
    _forcer_palier(tmp_path, "methodes", 1)
    payload = _demarrer(client, "methodes")
    item = payload["items"][0]
    assert item["type"] == "pqrst"
    assert item["contenu"]["affichage"]["mode"] == "texte"
    assert item["contenu"]["affichage"]["elements"]
    assert "reponse" not in item
    bonne = _attendue("methodes", item["id"])
    assert bonne in item["contenu"]["options"]
    assert _repondre(client, "methodes", payload["session_id"], item["id"], bonne).json()["correcte"] is True


def test_gmt_plan_et_auto_instruction(client, tmp_path):
    """Palier 2 (plan d'étapes) et palier 3 (question à se poser) corrigent par choix."""
    for palier, type_attendu in ((2, "but-etapes"), (3, "auto-instruction")):
        _forcer_palier(tmp_path, "methodes", palier)
        payload = _demarrer(client, "methodes")
        item = payload["items"][0]
        assert item["type"] == type_attendu
        assert len(item["contenu"]["options"]) == 3
        assert _repondre(
            client, "methodes", payload["session_id"], item["id"], _attendue("methodes", item["id"])
        ).json()["correcte"] is True


# -- Analyse du mot : SFA / PCA ------------------------------------------------


# -- Vérification de plan et repérage d'information -----------------------------


def test_plan_a_verifier(client, tmp_path):
    """Palier 4 : le plan est affiché, l'étape mal placée est à identifier."""
    _forcer_palier(tmp_path, "methodes", 4)
    payload = _demarrer(client, "methodes")
    item = payload["items"][0]
    assert item["type"] == "plan-a-verifier"
    assert len(item["contenu"]["plan"]) == 3
    bonne = _attendue("methodes", item["id"])
    assert bonne in item["contenu"]["options"]
    assert _repondre(client, "methodes", payload["session_id"], item["id"], bonne).json()["correcte"] is True
    mauvaise = next(o for o in item["contenu"]["options"] if o != bonne)
    assert _repondre(client, "methodes", payload["session_id"], item["id"], mauvaise).json()["correcte"] is False


def test_reperer_info_dans_un_document(client, tmp_path):
    """Palier 5 : le document est affiché temporisé, l'information est à retrouver."""
    _forcer_palier(tmp_path, "methodes", 5)
    payload = _demarrer(client, "methodes")
    item = payload["items"][0]
    assert item["type"] == "reperer-info"
    assert item["contenu"]["affichage"]["mode"] == "texte"
    assert _repondre(
        client, "methodes", payload["session_id"], item["id"], _attendue("methodes", item["id"])
    ).json()["correcte"] is True


def test_analyse_mot_sfa_et_pca(client, tmp_path):
    """SFA (palier 6) et PCA (palier 7) : l'utilisateur génère des attributs puis nomme."""
    for palier, methode in ((6, "semantique"), (7, "phonologique")):
        _forcer_palier(tmp_path, "evocation", palier)
        payload = _demarrer(client, "evocation")
        item = payload["items"][0]
        assert item["type"] == "analyse-mot"
        assert item["contenu"]["methode"] == methode
        assert item["contenu"]["definition"]
        assert len(item["contenu"]["etapes"]) >= 2
        assert "reponse" not in item
        mot = _attendue("evocation", item["id"])
        assert _repondre(client, "evocation", payload["session_id"], item["id"], mot).json()["correcte"] is True
        # La saisie est tolérante (casse, accents).
        variante = mot.upper()
        assert _repondre(client, "evocation", payload["session_id"], item["id"], variante).json()["correcte"] is True
