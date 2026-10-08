"""Tests du programme d'entraînement : endpoint, avancement du jour, stabilité.

Le programme propose un rythme ; il ne décide jamais de la progression des paliers
(celle-ci appartient au moteur de maîtrise). Ces tests vérifient donc :
- la structure servie par `GET /api/programme` ;
- le repérage du jour, qui avance avec le calendrier (horloge injectée) ;
- la stabilité de la date de début (relire le programme ne décale rien) ;
- la logique pure de `jour_du_programme` (avant, pendant, après).
"""

import json
from datetime import date, datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.domain.programme import jour_du_programme, resume_programme
from backend.app.main import creer_app


def _app_a_la_date(racine, jour: date):
    """Application avec horloge figée (déterminisme des tests de calendrier)."""
    return creer_app(
        racine_donnees=racine,
        dossier_frontend=racine / "frontend-inexistant",
        horloge=lambda: datetime(jour.year, jour.month, jour.day, 12, 0, tzinfo=timezone.utc),
    )


def test_programme_servi_avec_plan_du_jour(tmp_path):
    client = TestClient(_app_a_la_date(tmp_path / "data", date(2026, 9, 22)))
    reponse = client.get("/api/programme")
    assert reponse.status_code == 200
    corps = reponse.json()

    programme = corps["programme"]
    assert programme["duree_semaines"] == 8
    assert len(programme["semaines"]) == 8
    assert corps["date_debut"] == "2026-09-22"
    assert corps["regles"] and "progression" in corps["regles"]

    jour = corps["aujourd_hui"]
    assert jour["semaine"] == 1 and jour["jour"] == 1
    assert jour["type"] == "seance"
    assert jour["themes"] and jour["themes"][0] != "au-choix"
    assert jour["jour_depuis_debut"] == 1
    assert jour["plafond_palier"]

    # L'état du programme vit dans son propre dossier, à côté de l'entraînement.
    assert (tmp_path / "programme" / "programme.json").is_file()


def test_programme_avance_avec_le_calendrier(tmp_path):
    racine = tmp_path / "data"
    client = TestClient(_app_a_la_date(racine, date(2026, 9, 22)))
    client.get("/api/programme")          # pose la date de début

    # Sept jours plus tard : semaine 2, jour 1 (même date de début).
    client_suivant = TestClient(_app_a_la_date(racine, date(2026, 9, 29)))
    jour = client_suivant.get("/api/programme").json()["aujourd_hui"]
    assert (jour["semaine"], jour["jour"]) == (2, 1)
    assert jour["jour_depuis_debut"] == 8

    # Jour 6 d'une semaine : journée légère, « au choix ».
    client_leger = TestClient(_app_a_la_date(racine, date(2026, 9, 27)))
    jour = client_leger.get("/api/programme").json()["aujourd_hui"]
    assert jour["type"] == "legere"
    assert jour["themes"] == ["au-choix"] and jour["themes_extra"]

    # Jour 7 : repos, sans thème.
    client_repos = TestClient(_app_a_la_date(racine, date(2026, 9, 28)))
    jour = client_repos.get("/api/programme").json()["aujourd_hui"]
    assert jour["type"] == "repos" and jour["themes"] == []


def test_programme_date_debut_stable_et_fin_de_programme(tmp_path):
    racine = tmp_path / "data"
    client = TestClient(_app_a_la_date(racine, date(2026, 9, 22)))
    premiere = client.get("/api/programme").json()["date_debut"]
    # Relire le programme, même des jours plus tard, ne décale pas le calendrier.
    client_plus_tard = TestClient(_app_a_la_date(racine, date(2026, 10, 1)))
    assert client_plus_tard.get("/api/programme").json()["date_debut"] == premiere
    assert json.loads((tmp_path / "programme" / "programme.json").read_text())["date_debut"] == premiere

    # Au-delà des 8 semaines : programme terminé (jamais prolongé d'office).
    apres = date(2026, 9, 22) + timedelta(days=8 * 7 + 1)
    client_apres = TestClient(_app_a_la_date(racine, apres))
    jour = client_apres.get("/api/programme").json()["aujourd_hui"]
    assert jour["type"] == "termine" and jour["jours_restants"] == 0


def test_jour_du_programme_logique_pure():
    programme = {
        "semaines": [
            {"semaine": 1, "duree_min": 6, "plafond_palier": {"memoire": 2},
             "jours": [{"jour": n, "type": "seance" if n < 6 else "repos",
                        "duree_min": 6, "themes": ["memoire"] if n < 6 else []} for n in range(1, 8)]}
        ]
    }
    debut = date(2026, 9, 22)
    # Avant le début : rien à proposer.
    assert jour_du_programme(programme, debut, date(2026, 9, 21)) is None
    assert resume_programme(programme, debut, date(2026, 9, 21))["type"] == "a_venir"
    # Pendant : jour 3 → séance.
    jour = jour_du_programme(programme, debut, date(2026, 9, 24))
    assert (jour["semaine"], jour["jour"], jour["type"]) == (1, 3, "seance")
    # Après la dernière semaine : terminé.
    assert resume_programme(programme, debut, date(2026, 10, 1))["type"] == "termine"
