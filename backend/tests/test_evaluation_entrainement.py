"""Tests de la séparation évaluation / entraînement.

L'évaluation regroupe les thèmes qui *mesurent* (empans, n-back, attention
soutenue, rappel de listes) : ils restent jouables pour se situer, mais sont
plafonnés à une séance par semaine (fenêtre du lundi au dimanche) pour que la
répétition ne fausse pas la mesure. L'entraînement de remédiation garde son
dosage normal (3 séances/jour). La dérogation d'accueil couvre les deux.
"""

from backend.app.domain.contenu import ChargeurContenu

CONTENU = ChargeurContenu()

THEMES_EVALUATION = {"memoire", "concentration", "rappel-series"}


def test_categories_des_themes(client):
    """Chaque thème expose sa catégorie (entraînement ou évaluation)."""
    themes = {t["id"]: t for t in client.get("/api/entrainement/themes").json()["themes"]}
    for identifiant in THEMES_EVALUATION:
        assert themes[identifiant]["categorie"] == "evaluation", identifiant
    for identifiant in ("evocation", "quotidien", "deduction", "methodes", "calcul-mental"):
        assert themes[identifiant]["categorie"] == "entrainement", identifiant


def test_evaluation_limitee_a_une_seance_par_semaine(client):
    """Une mesure ne se répète pas dans la même semaine : 2e séance refusée (429)."""
    premiere = client.post("/api/entrainement/memoire/sessions")
    assert premiere.status_code == 201
    seconde = client.post("/api/entrainement/memoire/sessions")
    assert seconde.status_code == 429
    assert seconde.json()["sessions_restantes_aujourdhui"] == 0


def test_entrainement_garde_son_dosage(client):
    """L'entraînement de remédiation reste à 3 séances par jour."""
    for _ in range(3):
        assert client.post("/api/entrainement/quotidien/sessions").status_code == 201
    assert client.post("/api/entrainement/quotidien/sessions").status_code == 429


def test_la_categorie_ne_change_pas_le_contenu(client):
    """La catégorie est une étiquette de présentation : le contenu reste servi."""
    assert CONTENU.categorie("memoire") == "evaluation"
    assert CONTENU.categorie("quotidien") == "entrainement"
    assert CONTENU.items("memoire") and CONTENU.items("quotidien")


def test_la_derogation_couvre_aussi_levaluation(client):
    """La dérogation lève aussi le plafond hebdomadaire de l'évaluation ; sans
    elle, le plafond reprend (répéter une mesure la fausse — ADR-021)."""
    assert client.post("/api/entrainement/memoire/sessions").status_code == 201
    seconde = client.post(
        "/api/entrainement/memoire/sessions",
        json={"sans_limite_sessions": True},
    )
    assert seconde.status_code == 201, seconde.text
    assert client.post("/api/entrainement/memoire/sessions").status_code == 429


def test_fenetres_et_plafonds_du_domaine():
    """Plafonds et fenêtres par catégorie ; la semaine commence le lundi."""
    from datetime import date

    from backend.app.domain.dosage import (
        debut_fenetre,
        fenetre_sessions,
        limite_sessions,
    )

    assert limite_sessions("entrainement") == 3
    assert fenetre_sessions("entrainement") == "jour"
    assert limite_sessions("evaluation") == 1
    assert fenetre_sessions("evaluation") == "semaine"
    mercredi = date(2026, 9, 30)
    assert debut_fenetre("jour", mercredi) == mercredi
    assert debut_fenetre("semaine", mercredi) == date(2026, 9, 28)  # lundi
    assert debut_fenetre("semaine", date(2026, 9, 28)) == date(2026, 9, 28)


def test_evaluation_se_reouvre_la_semaine_suivante(tmp_path):
    """Fenêtre hebdomadaire : refusée dans la même semaine, rouverte la suivante."""
    from datetime import datetime, timedelta, timezone

    from fastapi.testclient import TestClient

    from backend.app.main import creer_app

    horloge = {"now": datetime(2026, 9, 30, 10, 0, tzinfo=timezone.utc)}
    application = creer_app(
        racine_donnees=tmp_path / "data",
        dossier_frontend=tmp_path / "front",
        horloge=lambda: horloge["now"],
    )
    client = TestClient(application)

    assert client.post("/api/entrainement/memoire/sessions").status_code == 201
    assert client.post("/api/entrainement/memoire/sessions").status_code == 429
    # La semaine suivante, la mesure redevient possible.
    horloge["now"] = horloge["now"] + timedelta(days=7)
    assert client.post("/api/entrainement/memoire/sessions").status_code == 201
