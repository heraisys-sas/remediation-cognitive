"""Tests du thème « Déduction » — grille logique 3×3 (figures × couleurs)."""

from backend.app.domain.contenu import ChargeurContenu

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
    assert len(item["contenu"]["enonces"]) == 6
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
    """Chaque indice est cohérent avec la solution (garde-fou de validité)."""
    FIGURES = ["cercle", "carre", "triangle"]
    COULEURS = ["rouge", "bleu", "vert"]

    def vrai(indice, fig, coul):
        t = indice["type"]
        if t == "case-couleur":
            return coul[indice["case"]] == COULEURS.index(indice["couleur"])
        if t == "case-figure":
            return fig[indice["case"]] == FIGURES.index(indice["figure"])
        if t == "ligne":
            return FIGURES.index(indice["figure"]) in (fig[indice["ligne"] * 3 + c] for c in range(3))
        if t == "colonne":
            return COULEURS.index(indice["couleur"]) in (coul[r * 3 + indice["colonne"]] for r in range(3))
        if t == "pas-couleur":
            return coul[indice["case"]] != COULEURS.index(indice["couleur"])
        if t == "pas-figure":
            return fig[indice["case"]] != FIGURES.index(indice["figure"])
        if t == "regle":
            return True
        return False

    for item in CONTENU.items("deduction"):
        cellules = item["reponse"]["grille"]
        fig = [FIGURES.index(f) for f, _ in cellules]
        coul = [COULEURS.index(c) for _, c in cellules]
        for indice in item["contenu"]["enonces"]:
            assert vrai(indice, fig, coul), f"{item['id']} : indice incohérent {indice}"
