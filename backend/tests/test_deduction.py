"""Tests du thème « Déduction » — grille logique 3×3 et 4×4 (figures × couleurs)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from deduction_commun import TYPES_BINAIRES, pred_indice, resoudre_par_deduction  # noqa: E402

from backend.app.domain.contenu import ChargeurContenu  # noqa: E402

CONTENU = ChargeurContenu()


def _demarrer(client):
    reponse = client.post("/api/entrainement/deduction/sessions")
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def _repondre(client, session_id, item_id, reponse):
    return client.post(
        f"/api/entrainement/deduction/sessions/{session_id}/reponses",
        json={"item_id": item_id, "reponse": reponse, "temps_ms": 1500},
    )


def test_grille_deduction_structure_et_correction(client):
    payload = _demarrer(client)
    item = payload["items"][0]
    assert item["type"] == "grille-deduction"
    assert len(item["contenu"]["figures"]) == 3
    assert len(item["contenu"]["couleurs"]) == 3
    assert 4 <= len(item["contenu"]["enonces"]) <= 20   # assez de phrases pour déduire, pas de remplissage
    assert "reponse" not in item                    # la solution ne fuit jamais

    solution = CONTENU.item("deduction", item["id"])["reponse"]["valeur"]

    # Grille exacte : acceptée.
    assert _repondre(client, payload["session_id"], item["id"], solution).json()["correcte"] is True

    # Grille fausse (deux cases échangées) : refusée.
    cellules = solution.split(";")
    cellules[0], cellules[1] = cellules[1], cellules[0]
    autre = payload["items"][1]
    assert _repondre(client, payload["session_id"], autre["id"], ";".join(cellules)).json()["correcte"] is False


def test_grille_deduction_indices_vrais_pour_la_solution():
    """Chaque phrase — les deux informations d'une phrase composée comprises — est vraie."""
    for item in CONTENU.items("deduction"):
        contenu = item["contenu"]
        figures, couleurs = contenu["figures"], contenu["couleurs"]
        n = len(figures)
        ifigure = {f: i for i, f in enumerate(figures)}
        icouleur = {c: i for i, c in enumerate(couleurs)}
        cellules = item["reponse"]["grille"]
        # Chaque figure colorée est unique dans la grille.
        assert len({(f, c) for f, c in cellules}) == n * n, item["id"]
        fig = tuple(ifigure[f] for f, _ in cellules)
        coul = tuple(icouleur[c] for _, c in cellules)
        for indice in contenu["enonces"] + contenu.get("indices", []):
            if not isinstance(indice, dict) or indice.get("type") == "regle":
                continue
            assert pred_indice(indice, (fig, coul), n, figures, couleurs), \
                f"{item['id']} : indice faux {indice}"


def test_grille_deduction_provoque_une_deduction():
    """Le cœur du thème : chaque phrase enchaîne plusieurs informations et relie deux
    figures ; aucun placement direct, aucune règle cachée — les phrases suffisent.
    """
    binaires = TYPES_BINAIRES
    for item in CONTENU.items("deduction"):
        enonces = item["contenu"]["enonces"]
        for position, phrase in enumerate(enonces, start=1):
            atomes = [phrase] + list(phrase.get("et") or [])
            assert len(atomes) >= 2, \
                f"{item['id']} phrase {position} : une seule information"
            assert not any(a.get("type") == "case" for a in atomes), \
                f"{item['id']} phrase {position} : placement direct interdit"
            assert any(a.get("type") in binaires for a in atomes), \
                f"{item['id']} phrase {position} : ne relie aucune figure"
        if item["palier"] == 1:
            assert all(len([p] + list(p.get("et") or [])) >= 3 for p in enonces), \
                f"{item['id']} : le palier 1 commence par des phrases denses (trois informations)"


def test_grilles_solubles_par_deduction_et_solutions_distinctes():
    """La garantie du thème : chaque grille se reconstruit par raisonnement pur
    (propagation des phrases, aucune hypothèse), et une même solution n'est
    jamais resservie — le stock tient l'entraînement long terme."""
    solutions = set()
    items = list(CONTENU.items("deduction"))
    for item in items:
        contenu = item["contenu"]
        n = len(contenu["figures"])
        assert resoudre_par_deduction(
            contenu["enonces"], n, contenu["figures"], contenu["couleurs"]
        ), f"{item['id']} : grille non résoluble par déduction"
        solutions.add(item["reponse"]["valeur"])

    assert len(solutions) == len(items), "deux grilles partagent la même solution"
    assert len(items) >= 80, "stock insuffisant pour un entraînement de trois mois"
