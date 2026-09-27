"""Tests d'intégration de l'API entraînement (contrat docs/30-technique/api-contract.md).

Cycle complet via TestClient (httpx), garde-fous serveur (429, arrêt
proposé jamais forcé, réponse attendue jamais envoyée avant soumission),
codes 404/409, absence d'endpoint /api/bilan et montage statique /ui.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app.domain.contenu import ChargeurContenu
from backend.app.main import creer_app

CONTENU = ChargeurContenu()
THEMES_ATTENDUS = {
    "calcul-mental",
    "anglais",
    "python",
    "memoire",
    "concentration",
    "evocation",
    "rappel-series",
    "quotidien",
    "deduction",
    "methodes",
}


# -- utilitaires -----------------------------------------------------------------


def _demarrer(client, theme="calcul-mental"):
    """Démarre une séance et retourne le payload 201."""
    reponse = client.post(f"/api/entrainement/{theme}/sessions")
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def _valeur_attendue(theme, item_id):
    """Réponse attendue lue côté serveur de test (contenu versionné)."""
    return CONTENU.item(theme, item_id)["reponse"]["valeur"]


def _repondre(client, theme, session_id, item_id, reponse, temps_ms=900, indice_utilise=None):
    corps = {"item_id": item_id, "reponse": reponse, "temps_ms": temps_ms}
    if indice_utilise is not None:
        corps["indice_utilise"] = indice_utilise
    return client.post(
        f"/api/entrainement/{theme}/sessions/{session_id}/reponses", json=corps
    )


def _finir(client, theme, session_id):
    return client.post(f"/api/entrainement/{theme}/sessions/{session_id}/fin")


def _contient_cle(objet, cle):
    """True si la clé apparaît n'importe où dans la structure JSON."""
    if isinstance(objet, dict):
        return cle in objet or any(_contient_cle(valeur, cle) for valeur in objet.values())
    if isinstance(objet, list):
        return any(_contient_cle(valeur, cle) for valeur in objet)
    return False


def _repondre_tout(client, theme, payload, reponse_factory, temps_ms=900):
    """Répond à chaque item de la séance avec une réponse fabriquée par item."""
    resultats = []
    for item in payload["items"]:
        resultats.append(
            _repondre(
                client,
                theme,
                payload["session_id"],
                item["id"],
                reponse_factory(item),
                temps_ms=temps_ms,
            )
        )
    return resultats


# -- health, thèmes ---------------------------------------------------------------


def test_health(client):
    reponse = client.get("/health")
    assert reponse.status_code == 200
    assert reponse.json() == {"status": "ok"}


def test_themes(client):
    reponse = client.get("/api/entrainement/themes")
    assert reponse.status_code == 200
    themes = reponse.json()["themes"]
    assert {t["id"] for t in themes} == THEMES_ATTENDUS
    for theme in themes:
        assert set(theme) == {"id", "nom", "description", "categorie"}
        assert theme["categorie"] in {"entrainement", "evaluation"}
        assert theme["nom"] and theme["description"]


# -- démarrage de séance -----------------------------------------------------------


def test_demarrage_payload_conforme(client):
    payload = _demarrer(client, "calcul-mental")
    assert isinstance(payload["session_id"], str) and payload["session_id"]
    assert payload["regles"] == {"max_items": 12, "duree_max_s": 600}
    items = payload["items"]
    assert 1 <= len(items) <= 12
    for item in items:
        # Contrat exact : id, type, palier, contenu — et JAMAIS de réponse.
        assert set(item) == {"id", "type", "palier", "contenu"}
        assert item["palier"] == 1  # thème vierge → palier 1


def test_reponse_attendue_absente_du_payload_tous_themes(client):
    for theme in THEMES_ATTENDUS:
        payload = _demarrer(client, theme)
        assert not _contient_cle(payload, "reponse")
        assert not _contient_cle(payload, "valeur")


def test_theme_inconnu_404(client):
    reponse = client.post("/api/entrainement/thermique/sessions")
    assert reponse.status_code == 404
    assert reponse.json()["erreur"] == "theme_inconnu"


# -- cycle complet -------------------------------------------------------------------


def test_cycle_complet_avec_resume_coherent(client, tmp_path):
    payload = _demarrer(client, "calcul-mental")
    items = payload["items"]
    assert len(items) == 12

    # Item 0 : bonne réponse sous forme de chaîne (coercion numérique).
    bonne = _valeur_attendue("calcul-mental", items[0]["id"])
    reponse = _repondre(client, "calcul-mental", payload["session_id"], items[0]["id"], str(bonne))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert set(corps) == {"correcte", "assistee", "attendue", "feedback"}
    assert corps["correcte"] is True
    assert corps["attendue"] == bonne
    assert corps["feedback"]

    # Item 1 : mauvaise réponse (la réponse attendue est révélée après coup).
    reponse = _repondre(
        client, "calcul-mental", payload["session_id"], items[1]["id"],
        _valeur_attendue("calcul-mental", items[1]["id"]) + 1,
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["correcte"] is False
    assert corps["attendue"] == _valeur_attendue("calcul-mental", items[1]["id"])

    # Items restants : tous corrects.
    for item in items[2:]:
        assert _repondre(
            client, "calcul-mental", payload["session_id"], item["id"],
            _valeur_attendue("calcul-mental", item["id"]),
        ).status_code == 200

    # Fin de séance : résumé cohérent.
    reponse = _finir(client, "calcul-mental", payload["session_id"])
    assert reponse.status_code == 200
    fin = reponse.json()
    assert fin["resume"]["items"] == 12
    assert fin["resume"]["correctes"] == 11
    assert fin["resume"]["duree_s"] >= 0
    assert fin["resume"]["taux_reussite"] == pytest.approx(11 / 12)
    assert fin["arret_propose"] is False
    assert fin["motif_arret"] is None
    assert fin["sessions_restantes_aujourdhui"] == 2

    # Fin idempotente : un second appel renvoie le MÊME résumé, sans conflit
    # (l'interface doit pouvoir afficher le résumé après une clôture déjà faite).
    second = _finir(client, "calcul-mental", payload["session_id"])
    assert second.status_code == 200
    assert second.json() == fin
    # En revanche, une réponse après la fin reste refusée (409).
    reponse = _repondre(client, "calcul-mental", payload["session_id"], items[0]["id"], bonne)
    assert reponse.status_code == 409
    assert reponse.json()["erreur"] == "session_terminee"

    # Persistance : cartes FSRS + maîtrise + compteur sous la racine isolée.
    racine = _racine_donnees(client)
    cartes = json.loads((racine / "calcul-mental" / "cartes-fsrs.json").read_text())
    assert set(cartes["cartes"]) == {item["id"] for item in items}
    maitrise = json.loads((racine / "calcul-mental" / "maitrise.json").read_text())
    assert maitrise["palier_courant"] == 1
    assert maitrise["historique"] == [[1, 11 / 12]]
    compteur = json.loads((racine / "calcul-mental" / "compteur-seances.json").read_text())
    assert compteur["nb_sessions"] == 1


def _racine_donnees(client):
    """Racine de données de l'app under test (tmp_path isolé)."""
    return client.app.state.gestionnaire_entrainement.stockage.racine


# -- régressions revue exécution -------------------------------------------------


def test_resume_seance_partiellement_repondue(client):
    """Régression : le résumé compte les items RÉPONDUS, pas les items servis.

    Une séance abandonnée en cours de route doit produire un résumé sur
    les items réellement répondus — pas sur les 12 items livrés d'un bloc
    au démarrage ; les essais dupliqués ne comptent pas deux fois.
    """
    payload = _demarrer(client, "calcul-mental")
    items = payload["items"]
    assert len(items) == 12

    # 3 items répondus seulement : 2 correctes, 1 fausse.
    for item, ecart in zip(items[:3], (0, 0, 1)):
        reponse = _repondre(
            client, "calcul-mental", payload["session_id"], item["id"],
            _valeur_attendue("calcul-mental", item["id"]) + ecart,
        )
        assert reponse.status_code == 200

    fin = _finir(client, "calcul-mental", payload["session_id"])
    assert fin.status_code == 200
    resume = fin.json()["resume"]
    assert resume["items"] == 3
    assert resume["correctes"] == 2
    assert resume["taux_reussite"] == pytest.approx(2 / 3)
    # La maîtrise n'historise que des séances réellement répondues.
    racine = _racine_donnees(client)
    maitrise = json.loads((racine / "calcul-mental" / "maitrise.json").read_text())
    assert maitrise["historique"] == [[1, 2 / 3]]


def test_baseline_rt_adaptative(client):
    """Régression : la baseline RT suit l'utilisateur.

    Après une séance de réponses correctes lentes (4000 ms), des réponses
    correctes à 3000 ms ne doivent plus déclencher de faux positif de
    fatigue (baseline figée à 1000 ms → 3000 > 1,25 × 1000).
    """
    # Séance 1 : 12 réponses correctes à 4000 ms → baseline ≈ 4000 ms.
    payload = _demarrer(client, "calcul-mental")
    for item in payload["items"]:
        reponse = _repondre(
            client, "calcul-mental", payload["session_id"], item["id"],
            _valeur_attendue("calcul-mental", item["id"]), temps_ms=4000,
        )
        assert reponse.status_code == 200
    _finir(client, "calcul-mental", payload["session_id"])

    # Séance 2 : réponses correctes à 3000 ms — lentes en absolu, normales
    # pour cet utilisateur → aucune alerte de fatigue proposée.
    payload = _demarrer(client, "calcul-mental")
    for item in payload["items"]:
        reponse = _repondre(
            client, "calcul-mental", payload["session_id"], item["id"],
            _valeur_attendue("calcul-mental", item["id"]), temps_ms=3000,
        )
        assert reponse.status_code == 200
    fin = _finir(client, "calcul-mental", payload["session_id"])
    assert fin.status_code == 200
    assert fin.json()["arret_propose"] is False
    assert fin.json()["motif_arret"] is None


# -- correction serveur par thème ------------------------------------------------------


def test_correction_memoire_tolerante(client):
    """Mémoire : espaces et casse ignorés (empan tapé avec espaces, n-back minuscule)."""
    payload = _demarrer(client, "memoire")
    item = payload["items"][0]
    attendue = str(_valeur_attendue("memoire", item["id"]))
    if attendue.isdigit():
        saisie = " ".join(attendue)          # "582" → "5 8 2"
    else:
        saisie = attendue.lower()            # n-back : k pour K
    reponse = _repondre(client, "memoire", payload["session_id"], item["id"], saisie)
    assert reponse.status_code == 200
    assert reponse.json()["correcte"] is True
    # Et une mauvaise réponse reste fausse.
    autre = payload["items"][1]
    reponse = _repondre(
        client, "memoire", payload["session_id"], autre["id"],
        str(_valeur_attendue("memoire", autre["id"])) + "9",
    )
    assert reponse.json()["correcte"] is False


def test_correction_concentration_numerique(client):
    """Concentration : chaînes, double tâches et séries ont des réponses numériques."""
    payload = _demarrer(client, "concentration")
    item = payload["items"][0]
    attendue = _valeur_attendue("concentration", item["id"])
    reponse = _repondre(
        client, "concentration", payload["session_id"], item["id"], str(attendue)
    )
    assert reponse.status_code == 200
    assert reponse.json()["correcte"] is True
    # "43,0" est accepté comme 43 (tolérance numérique du contrat).
    autre = payload["items"][1]
    attendue_autre = _valeur_attendue("concentration", autre["id"])
    reponse = _repondre(
        client, "concentration", payload["session_id"], autre["id"],
        f"{attendue_autre},0",
    )
    assert reponse.json()["correcte"] is True


def test_cycle_complet_memoire(client):
    """Cycle E2E du thème mémoire : affichage temporisé dans le payload,
    réponse attendue jamais exposée comme clé, résumé cohérent."""
    payload = _demarrer(client, "memoire")
    items = payload["items"]
    assert 1 <= len(items) <= 12
    assert not _contient_cle(payload, "reponse")
    assert not _contient_cle(payload, "valeur")
    for item in items:
        # Chaque item de mémoire porte son affichage temporisé (phase de mémorisation).
        assert "affichage" in item["contenu"]
        assert item["contenu"]["affichage"]["mode"] in {"sequence", "liste"}
        reponse = _repondre(
            client, "memoire", payload["session_id"], item["id"],
            str(_valeur_attendue("memoire", item["id"])),
        )
        assert reponse.status_code == 200
        assert reponse.json()["correcte"] is True
    fin = _finir(client, "memoire", payload["session_id"]).json()
    assert fin["resume"]["items"] == len(items)
    assert fin["resume"]["taux_reussite"] == 1.0
    assert fin["arret_propose"] is False


def test_correction_serveur_par_theme(client):
    # Calcul mental : "56" ou 56 acceptés, mauvaise valeur rejetée.
    payload = _demarrer(client, "calcul-mental")
    items = payload["items"]
    bonne = _valeur_attendue("calcul-mental", items[0]["id"])
    assert _repondre(client, "calcul-mental", payload["session_id"], items[0]["id"], bonne).json()["correcte"] is True

    # Anglais : insensible à la casse, espaces trimmés.
    payload = _demarrer(client, "anglais")
    item = payload["items"][0]
    attendue = _valeur_attendue("anglais", item["id"])
    reponse = _repondre(client, "anglais", payload["session_id"], item["id"], f"  {attendue.upper()}  ")
    assert reponse.status_code == 200
    assert reponse.json()["correcte"] is True

    # Python : chaîne exacte trimmée.
    payload = _demarrer(client, "python")
    items = payload["items"]
    attendue = _valeur_attendue("python", items[0]["id"])
    assert _repondre(client, "python", payload["session_id"], items[0]["id"], f" {attendue} ").json()["correcte"] is True
    reponse = _repondre(
        client, "python", payload["session_id"], items[1]["id"],
        str(_valeur_attendue("python", items[1]["id"])).upper(),
    )
    assert reponse.status_code == 200
    assert reponse.json()["correcte"] is False
    assert reponse.json()["attendue"] == _valeur_attendue("python", items[1]["id"])


def test_temps_negatif_422(client):
    payload = _demarrer(client, "calcul-mental")
    item = payload["items"][0]
    reponse = _repondre(
        client, "calcul-mental", payload["session_id"], item["id"],
        _valeur_attendue("calcul-mental", item["id"]), temps_ms=-5,
    )
    assert reponse.status_code == 422
    assert reponse.json()["erreur"] == "reponse_invalide"


# -- garde-fous : sessions inconnues, item hors séance ---------------------------------


def test_reponse_session_inconnue_404(client):
    reponse = _repondre(client, "calcul-mental", "session-inexistante", "cm-2-2x1", "2")
    assert reponse.status_code == 404
    assert reponse.json()["erreur"] == "session_inconnue"


def test_fin_session_inconnue_404(client):
    reponse = _finir(client, "calcul-mental", "session-inexistante")
    assert reponse.status_code == 404
    assert reponse.json()["erreur"] == "session_inconnue"


def test_item_hors_seance_404(client):
    payload = _demarrer(client, "calcul-mental")
    reponse = _repondre(client, "calcul-mental", payload["session_id"], "cm-inexistant", "2")
    assert reponse.status_code == 404
    assert reponse.json()["erreur"] == "item_hors_seance"


# -- garde-fou : 3 séances/jour ----------------------------------------------------


def test_quatrieme_seance_du_jour_429(client):
    for _ in range(3):
        assert client.post("/api/entrainement/calcul-mental/sessions").status_code == 201
    reponse = client.post("/api/entrainement/calcul-mental/sessions")
    assert reponse.status_code == 429
    # Corps exact du contrat.
    assert reponse.json() == {
        "erreur": "limite_sessions_atteinte",
        "sessions_restantes_aujourdhui": 0,
    }
    # La limite est par thème : un autre thème reste utilisable.
    assert client.post("/api/entrainement/anglais/sessions").status_code == 201


# -- garde-fou : arrêt proposé, jamais forcé --------------------------------------------


def test_arret_propose_jamais_force(client):
    payload = _demarrer(client, "calcul-mental")
    items = payload["items"]
    # 12 réponses fausses et très lentes : seuils de fatigue dépassés dès
    # la 3e réponse — chaque réponse reste acceptée (aucune interruption).
    for item in items:
        reponse = _repondre(
            client, "calcul-mental", payload["session_id"], item["id"],
            _valeur_attendue("calcul-mental", item["id"]) + 1000,
            temps_ms=9000,
        )
        assert reponse.status_code == 200
        assert {"correcte", "assistee", "attendue", "feedback"} <= set(reponse.json())

        assert set(reponse.json()) <= {"correcte", "assistee", "attendue", "feedback", "reprise"}

    reponse = _finir(client, "calcul-mental", payload["session_id"])
    assert reponse.status_code == 200  # la séance va à son terme normalement
    fin = reponse.json()
    assert fin["arret_propose"] is True
    assert fin["motif_arret"] == "fatigue"
    assert fin["resume"]["items"] == 12
    assert fin["resume"]["correctes"] == 0
    assert fin["resume"]["taux_reussite"] == 0.0
    assert fin["resume"]["duree_s"] >= 0


# -- progression de palier : 90 % × 3 séances consécutives -------------------------------


def _forcer_echeance_passee(client, theme):
    """Simule l'oubli : rejoue les cartes persistées avec une échéance passée.

    Teste au passage le round-trip de persistance des cartes FSRS
    (engine.srs.fsrs to_dict/from_dict, utilisés tel quel).
    """
    chemin = _racine_donnees(client) / theme / "cartes-fsrs.json"
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    for etat in donnees["cartes"].values():
        etat["due"] = "2020-01-01T00:00:00+00:00"
    chemin.write_text(json.dumps(donnees), encoding="utf-8")


def test_maitrise_trois_seances_parfaites_font_progresser_palier(client):
    ids_session_1 = None
    for numero in range(3):
        payload = _demarrer(client, "calcul-mental")
        if numero == 0:
            ids_session_1 = {item["id"] for item in payload["items"]}
            assert len(ids_session_1) == 12
        else:
            # Les items dus (échéance forcée au passé) sont servis en premier :
            # ce sont exactement les items déjà vus de la 1re séance.
            assert {item["id"] for item in payload["items"]} == ids_session_1
        resultats = _repondre_tout(
            client, "calcul-mental", payload,
            reponse_factory=lambda item: _valeur_attendue("calcul-mental", item["id"]),
        )
        assert all(r.status_code == 200 for r in resultats)
        fin = _finir(client, "calcul-mental", payload["session_id"]).json()
        assert fin["resume"]["taux_reussite"] == 1.0
        assert fin["arret_propose"] is False
        if numero < 2:
            _forcer_echeance_passee(client, "calcul-mental")

    racine = _racine_donnees(client)
    maitrise = json.loads((racine / "calcul-mental" / "maitrise.json").read_text())
    assert maitrise["historique"] == [[1, 1.0], [1, 1.0], [1, 1.0]]
    assert maitrise["palier_courant"] == 2


# -- garde-fou : aucun endpoint /api/bilan ------------------------------------------------


@pytest.mark.parametrize("methode,chemin", [
    ("get", "/api/bilan"),
    ("post", "/api/bilan"),
    ("get", "/api/bilan/epreuves"),
    ("post", "/api/bilan/epreuves"),
    ("get", "/api/bilan/epreuves/empan"),
])
def test_aucun_endpoint_bilan(client, methode, chemin):
    reponse = client.request(methode.upper(), chemin, json={} if methode == "post" else None)
    assert reponse.status_code == 404


# -- interface statique /ui ---------------------------------------------------------------


def test_interface_statique_montee_sur_le_dossier_reel():
    """Le montage par défaut sert frontend/ résolu depuis la racine du projet."""
    client = TestClient(creer_app())
    reponse = client.get("/ui/tests/README.md")
    assert reponse.status_code == 200


def test_interface_statique_dossier_absent_tolere(tmp_path):
    application = creer_app(
        racine_donnees=tmp_path / "data", dossier_frontend=tmp_path / "absent"
    )
    client = TestClient(application)
    assert client.get("/ui/").status_code == 404


def test_interface_statique_sert_index_html(tmp_path):
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "index.html").write_text("<html>entrainement</html>", encoding="utf-8")
    application = creer_app(racine_donnees=tmp_path / "data", dossier_frontend=frontend)
    client = TestClient(application)
    reponse = client.get("/ui/")
    assert reponse.status_code == 200
    assert "entrainement" in reponse.text


# -- garde-fou : durée max appliquée côté serveur -----------------------------------


def test_duree_max_appliquee_serveur(tmp_path):
    """Régression : au-delà de la durée maximale, la séance **propose** l'arrêt.

    Le backend livre les 12 items d'un bloc : sans contrôle du temps, le garde-fou de
    durée serait neutralisé. Désormais, au-delà de la limite, la réponse est enregistrée
    et la séance **propose** de s'arrêter (une fois) — elle ne se ferme pas d'elle-même,
    la personne décide (ADR-010). Le garde-fou reste la limite de séances du jour.
    """
    horloge = {"now": datetime.now(timezone.utc)}
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
        horloge=lambda: horloge["now"],
    )
    client = TestClient(application)

    payload = _demarrer(client, "calcul-mental")
    items = payload["items"]
    # Une première réponse dans les temps : acceptée, sans proposition d'arrêt.
    reponse = _repondre(
        client, "calcul-mental", payload["session_id"], items[0]["id"],
        _valeur_attendue("calcul-mental", items[0]["id"]), temps_ms=900,
    )
    assert reponse.status_code == 200
    assert "seance_terminee" not in reponse.json()
    assert "arret_propose" not in reponse.json()

    # L'horloge saute au-delà de la durée max : la réponse est gardée, l'arrêt est proposé.
    horloge["now"] = horloge["now"] + timedelta(seconds=601)
    reponse = _repondre(
        client, "calcul-mental", payload["session_id"], items[1]["id"],
        _valeur_attendue("calcul-mental", items[1]["id"]), temps_ms=900,
    )
    assert reponse.status_code == 200, reponse.text
    assert reponse.json()["arret_propose"] is True
    assert reponse.json()["motif_arret"] == "duree"
    assert "seance_terminee" not in reponse.json()

    # On peut continuer : la réponse suivante passe, sans redite de la proposition.
    suivante = _repondre(
        client, "calcul-mental", payload["session_id"], items[2]["id"],
        _valeur_attendue("calcul-mental", items[2]["id"]), temps_ms=900,
    )
    assert suivante.status_code == 200, suivante.text
    assert "arret_propose" not in suivante.json()

    # La séance se termine quand la personne le décide — et la fin est rejouable.
    fin = _finir(client, "calcul-mental", payload["session_id"])
    assert fin.status_code == 200
    assert fin.json()["resume"]["items"] == 3
    assert _finir(client, "calcul-mental", payload["session_id"]).json() == fin.json()

    # Une réponse après la fin reste refusée (409).
    apres = _repondre(
        client, "calcul-mental", payload["session_id"], items[3]["id"],
        _valeur_attendue("calcul-mental", items[3]["id"]), temps_ms=900,
    )
    assert apres.status_code == 409

    # Les données de la séance clôturée sont persistées (FSRS + maîtrise).
    racine = _racine_donnees(client)
    cartes = json.loads((racine / "calcul-mental" / "cartes-fsrs.json").read_text())
    assert items[0]["id"] in cartes["cartes"]
    maitrise = json.loads((racine / "calcul-mental" / "maitrise.json").read_text())
    assert maitrise["historique"] == [[1, 1.0]]


def test_deduction_seance_plus_courte(tmp_path):
    """Déduction : six exercices par séance, durée maximale inchangée (10 min).

    Chaque grille demande une chaîne de raisonnement complète : douze grilles ne
    tiendraient pas dans une séance. Le cadre clinique reste « séance courte,
    ≤ 10 min » (docs/10-clinique) — on ajuste le NOMBRE d'exercices, pas la durée.
    """
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
    )
    client = TestClient(application)

    deduction = _demarrer(client, "deduction")
    assert deduction["regles"] == {"max_items": 6, "duree_max_s": 600}
    assert len(deduction["items"]) == 6
    assert all(item["type"] == "grille-deduction" for item in deduction["items"])

    # Les autres thèmes conservent le dosage général.
    calcul = _demarrer(client, "calcul-mental")
    assert calcul["regles"] == {"max_items": 12, "duree_max_s": 600}
    assert len(calcul["items"]) == 12


def test_deduction_duree_proposee_pas_imposee(tmp_path):
    """Déduction : au-delà de dix minutes, la séance **propose** l'arrêt.

    Une grille demande plusieurs minutes de raisonnement : fermer la séance d'office
    serait brutal. La proposition est faite une seule fois, la personne décide de
    continuer ou de terminer.
    """
    horloge = {"now": datetime.now(timezone.utc)}
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
        horloge=lambda: horloge["now"],
    )
    client = TestClient(application)

    payload = _demarrer(client, "deduction")
    items = payload["items"]
    assert len(items) == 6

    reponse = _repondre(
        client, "deduction", payload["session_id"], items[0]["id"],
        _valeur_attendue("deduction", items[0]["id"]), temps_ms=900,
    )
    assert reponse.status_code == 200
    assert "arret_propose" not in reponse.json()

    # On dépasse la durée maximale : proposition d'arrêt, séance toujours ouverte.
    horloge["now"] = horloge["now"] + timedelta(seconds=601)
    reponse = _repondre(
        client, "deduction", payload["session_id"], items[1]["id"],
        _valeur_attendue("deduction", items[1]["id"]), temps_ms=900,
    )
    assert reponse.status_code == 200, reponse.text
    assert reponse.json()["arret_propose"] is True
    assert reponse.json()["motif_arret"] == "duree"
    assert "seance_terminee" not in reponse.json()

    # La personne choisit de continuer : la réponse suivante passe, sans redite.
    suivante = _repondre(
        client, "deduction", payload["session_id"], items[2]["id"],
        _valeur_attendue("deduction", items[2]["id"]), temps_ms=900,
    )
    assert suivante.status_code == 200, suivante.text
    assert "arret_propose" not in suivante.json()
    assert "seance_terminee" not in suivante.json()

    # Et la séance se termine normalement quand elle le souhaite.
    fin = _finir(client, "deduction", payload["session_id"])
    assert fin.status_code == 200
    assert fin.json()["resume"]["items"] == 3


def test_seance_vide_ne_consomme_pas_le_quota(tmp_path):
    """Rien de dû, rien de nouveau : la séance n'a rien proposé, elle ne coûte rien.

    Régression liée au rythme de révision : avec des échéances à l'échelle du jour,
    une deuxième séance du même thème dans la même journée peut ne rien avoir à servir.
    Elle ne doit pas consommer une des trois séances quotidiennes.
    """
    horloge = {"now": datetime.now(timezone.utc)}
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
        horloge=lambda: horloge["now"],
    )
    client = TestClient(application)

    # Première séance : on répond à tout le palier 1 de méthodes (12 items).
    payload = _demarrer(client, "methodes")
    for item in payload["items"]:
        _repondre(client, "methodes", payload["session_id"], item["id"],
                  _valeur_attendue("methodes", item["id"]), temps_ms=900)
    assert _finir(client, "methodes", payload["session_id"]).status_code == 200

    racine = _racine_donnees(client)
    compteur = json.loads((racine / "methodes" / "compteur-seances.json").read_text())
    assert compteur["nb_sessions"] == 1

    # Deuxième séance le même jour : plus rien n'est dû (échéances au jour) ni nouveau.
    seconde = _demarrer(client, "methodes")
    assert seconde["items"] == []
    compteur = json.loads((racine / "methodes" / "compteur-seances.json").read_text())
    assert compteur["nb_sessions"] == 1, "une séance vide ne doit pas consommer le quota"


def test_reprise_errorless_des_exercices_manques(tmp_path):
    """Un exercice manqué revient **une fois**, en fin de séance, avec sa réponse.

    Errorless learning : ré-encoder une erreur la renforce (Baddeley & Wilson). La reprise
    est donc plafonnée (elle ne doit pas doubler la séance) et n'a pas lieu pour un essai
    déjà assisté, où la réponse a été fournie par les indices.
    """
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
    )
    client = TestClient(application)

    payload = _demarrer(client, "calcul-mental")
    items = payload["items"]
    session_id = payload["session_id"]

    # Réponse juste : aucune reprise.
    juste = _repondre(client, "calcul-mental", session_id, items[0]["id"],
                      _valeur_attendue("calcul-mental", items[0]["id"]), temps_ms=900)
    assert juste.status_code == 200
    assert "reprise" not in juste.json()

    # Réponse fausse : l'exercice est marqué pour une reprise unique.
    fausse = _repondre(client, "calcul-mental", session_id, items[1]["id"], "999999", temps_ms=900)
    assert fausse.status_code == 200
    assert fausse.json()["reprise"] is True

    # La reprise elle-même est acceptée (nouvel essai sur un item déjà servi).
    reprise = _repondre(client, "calcul-mental", session_id, items[1]["id"],
                        _valeur_attendue("calcul-mental", items[1]["id"]), temps_ms=900)
    assert reprise.status_code == 200
    # Un second échec sur le même exercice ne reprogramme pas de reprise.
    assert "reprise" not in reprise.json()

    # Plafond : au plus quatre reprises par séance, même si tout est manqué.
    manques = 0
    for item in items[2:]:
        resultat = _repondre(client, "calcul-mental", session_id, item["id"], "999999", temps_ms=900)
        if resultat.json().get("reprise"):
            manques += 1
    assert manques == 3, "le plafond de reprises par séance doit borner la séance"


def test_second_essai_avant_la_reponse_pour_les_exercices_de_strategie(tmp_path):
    """Un exercice où la réponse se **raisonne** donne un second essai avant la réponse.

    Pratique de récupération (Roediger & Karpicke) et hypothèse de guidage (Schmidt) :
    c'est l'essai qui apprend ; révéler trop tôt améliore la séance mais dégrade la
    rétention. Pour une information à **récupérer** au contraire, la réponse est donnée
    tout de suite (errorless learning) : ne pas laisser ré-encoder l'erreur.
    """
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
    )
    client = TestClient(application)

    # Exercice de stratégie : on force le palier « but et étapes » (Goal Management
    # Training — choisir le plan). Le palier 1 de méthodes est PQRST, qui porte sur la
    # mémoire d'un texte : c'est un exercice de récupération, pas de stratégie.
    dossier = tmp_path / "data" / "methodes"
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "maitrise.json").write_text(
        json.dumps({"palier_courant": 2, "historique": []}), encoding="utf-8"
    )
    payload = _demarrer(client, "methodes")
    items = payload["items"]
    session_id = payload["session_id"]
    assert items[0]["type"] in ("but-etapes", "auto-instruction", "plan-a-verifier")

    premiere = _repondre(client, "methodes", session_id, items[0]["id"], "réponse fausse", temps_ms=900)
    assert premiere.status_code == 200
    corps = premiere.json()
    assert corps["essai_supplementaire"] is True
    assert corps["attendue"] is None, "la réponse ne doit pas être révélée au premier essai"
    assert "reprise" not in corps, "la reprise se décide après le second essai"

    seconde = _repondre(client, "methodes", session_id, items[0]["id"],
                        _valeur_attendue("methodes", items[0]["id"]), temps_ms=900)
    assert seconde.status_code == 200
    assert seconde.json()["correcte"] is True
    assert seconde.json()["attendue"] is not None
    assert "essai_supplementaire" not in seconde.json()


def test_reponse_immediate_pour_les_exercices_de_memoire(tmp_path):
    """Un exercice de **récupération** garde la réponse immédiate (errorless learning)."""
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
    )
    client = TestClient(application)
    payload = _demarrer(client, "evocation")
    item = payload["items"][0]
    # Évocation au palier 1 : reconnaissance (choix) — un échec révèle la réponse.
    reponse = _repondre(client, "evocation", payload["session_id"], item["id"], "réponse fausse")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert "essai_supplementaire" not in corps
    assert corps["attendue"] is not None
