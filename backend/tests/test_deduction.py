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
    assert 5 <= len(item["contenu"]["enonces"]) <= 14   # assez d'indices pour déduire, pas de remplissage
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
    """Chaque indice (à deux informations) est cohérent avec la solution."""
    def cellule(fig, coul, i_f, i_c):
        for i in range(len(fig)):
            if fig[i] == i_f and coul[i] == i_c:
                return i
        return -1

    def vrai(indice, fig, coul, n, ifig, icoul):
        if indice["type"] == "regle":
            return True
        case = cellule(fig, coul, ifig[indice["figure"]], icoul[indice["couleur"]])
        if case < 0:
            return False
        coins = {0, n - 1, n * (n - 1), n * n - 1}
        bords = {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}
        t = indice["type"]
        if t == "case": return case == indice["case"]
        if t == "ligne": return case // n == indice["ligne"]
        if t == "colonne": return case % n == indice["colonne"]
        if t == "pas-coin": return case not in coins
        if t == "pas-bord": return case not in bords
        if t == "ni-ni": return case not in coins and case not in bords
        if "figure2" in indice:
            autre = cellule(fig, coul, ifig[indice["figure2"]], icoul[indice["couleur2"]])
            if t == "voisin-gauche": return autre == case + 1 and case % n != n - 1
            if t == "voisin-droite": return autre == case - 1 and case % n != 0
            if t == "voisin-dessous": return autre == case + n
            if t == "voisin-dessus": return autre == case - n
            if t == "autre-ligne": return case // n != autre // n
            if t == "autre-colonne": return case % n != autre % n
            if t == "comparaison": return case // n == autre // n and case < autre
            if t == "si-alors": return case not in coins or autre in bords
        return False

    for item in CONTENU.items("deduction"):
        figures = item["contenu"]["figures"]
        couleurs = item["contenu"]["couleurs"]
        n = len(figures)
        ifig = {f: i for i, f in enumerate(figures)}
        icoul = {c: i for i, c in enumerate(couleurs)}
        cellules = item["reponse"]["grille"]
        # Chaque figure colorée est unique dans la grille.
        assert len({(f, c) for f, c in cellules}) == n * n, item["id"]
        fig = [ifig[f] for f, _ in cellules]
        coul = [icoul[c] for _, c in cellules]
        for indice in item["contenu"]["enonces"] + item["contenu"].get("indices", []):
            assert vrai(indice, fig, coul, n, ifig, icoul), f"{item['id']} : indice incohérent {indice}"


def test_grilles_solubles_par_deduction_et_solutions_distinctes():
    """La garantie du thème : chaque grille se reconstruit par raisonnement pur
    (propagation des indices, aucune hypothèse), et une même solution n'est
    jamais resservie — le stock tient l'entraînement long terme."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
    from deduction_commun import resoudre_par_deduction

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
