"""Tests de la séparation évaluation / entraînement.

L'évaluation regroupe les thèmes qui *mesurent* (empans, n-back, attention
soutenue, rappel de listes) : ils restent jouables pour se situer, mais sont
plafonnés à une séance par jour pour que la répétition ne fausse pas la mesure.
L'entraînement de remédiation garde son dosage normal (3 séances/jour).
"""

from backend.app.domain.contenu import ChargeurContenu

CONTENU = ChargeurContenu()

THEMES_EVALUATION = {"memoire", "concentration", "rappel-series"}


def test_categories_des_themes(client):
    """Chaque thème expose sa catégorie (entraînement ou évaluation)."""
    themes = {t["id"]: t for t in client.get("/api/entrainement/themes").json()["themes"]}
    for identifiant in THEMES_EVALUATION:
        assert themes[identifiant]["categorie"] == "evaluation", identifiant
    for identifiant in ("evocation", "social", "quotidien", "deduction", "calcul-mental"):
        assert themes[identifiant]["categorie"] == "entrainement", identifiant


def test_evaluation_limitee_a_une_seance_par_jour(client):
    """Une mesure ne se répète pas dans la journée : 2e séance refusée (429)."""
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
