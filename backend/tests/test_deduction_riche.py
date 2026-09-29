"""Propriétés logiques des indices riches, avec oracle indépendant sur 3×3."""
from itertools import permutations, product
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from deduction_contraintes import compiler, reduire, forcees_riche

FIGURES = ["cercle", "carre", "triangle"]
COULEURS = ["rouge", "bleu", "vert"]


def compte(categorie, numero, nombre, zone="ligne"):
    return dict(type="compte-categorie", categorie=categorie, zone=zone, numero=numero, nombre=nombre)


def entre(axe="ligne", extremites=None):
    return dict(type="entre", figure="carre", couleur="rouge", axe=axe,
                extremites=extremites or [{"figure": "cercle"}, {"figure": "cercle"}])


def oracle(indice, positions, figures=FIGURES, couleurs=COULEURS):
    """Évalue les phrases directement sur une permutation complète, sans moteur."""
    n = len(figures)
    pions = list(product(figures, couleurs))
    def selection(categorie):
        return [positions[i] for i, (f, c) in enumerate(pions)
                if categorie.get("figure", f) == f and categorie.get("couleur", c) == c]
    t = indice["type"]
    if t in ("compte-categorie", "diversite"):
        for numero in range(n) if indice["numero"] == "chaque" else [indice["numero"]]:
            region = {p for p in range(n*n)
                      if (p // n if indice["zone"] == "ligne" else p % n) == numero}
            if t == "compte-categorie":
                if len(region & set(selection(indice["categorie"]))) != indice["nombre"]:
                    return False
            else:
                valeurs = figures if indice["attribut"] == "figure" else couleurs
                if any(len(region & set(selection({indice["attribut"]: v}))) != 1 for v in valeurs):
                    return False
        return True
    centre = positions[pions.index((indice["figure"], indice["couleur"]))]
    rc, cc = divmod(centre, n)
    for a, b in product(selection(indice["extremites"][0]), selection(indice["extremites"][1])):
        if len({a, b, centre}) < 3:
            continue
        ra, ca = divmod(a, n)
        rb, cb = divmod(b, n)
        if indice["axe"] == "ligne" and ra == rb == rc and min(ca, cb) < cc < max(ca, cb):
            return True
        if indice["axe"] == "colonne" and ca == cb == cc and min(ra, rb) < rc < max(ra, rb):
            return True
        if indice["axe"] == "diagonale":
            for pente in (-1, 1):
                if (ca - pente * ra == cc - pente * rc == cb - pente * rb
                        and min(ra, rb) < rc < max(ra, rb)):
                    return True
    return False


def test_aucune_distribution_collective_implicite():
    # Tous les cercles sur la première ligne est autorisé par les seules règles.
    positions = [{i} for i in range(9)]
    assert reduire(compiler([], 3, FIGURES, COULEURS), 3, positions) == positions
    diversite = dict(type="diversite", attribut="figure", zone="ligne", numero="chaque")
    assert reduire(compiler([diversite], 3, FIGURES, COULEURS), 3, positions) is None
    # La même disposition contient bien toutes les couleurs dans chaque ligne.
    assert reduire(compiler([dict(diversite, attribut="couleur")], 3, FIGURES, COULEURS), 3, positions) == positions


def test_cardinalite_exacte_et_exclusion_ne_sont_pas_des_minima():
    positions = [{i} for i in range(9)]
    assert reduire(compiler([compte({"figure": "cercle"}, 0, 3)], 3, FIGURES, COULEURS), 3, positions)
    assert reduire(compiler([compte({"figure": "cercle"}, 0, 2)], 3, FIGURES, COULEURS), 3, positions) is None
    domaines = reduire(compiler([compte({"couleur": "rouge"}, 1, 0)], 3, FIGURES, COULEURS), 3)
    assert domaines is not None
    for i in (0, 3, 6):
        assert not domaines[i] & {3, 4, 5}
    with pytest.raises(ValueError):
        compiler([compte({"figure": "cercle"}, "chaque", 2)], 3, FIGURES, COULEURS)


def test_entre_partiel_est_existentiel_et_exige_trois_pions_distincts():
    compilation = compiler([entre()], 3, FIGURES, COULEURS)
    # Deux des trois cercles suffisent, le troisième reste libre ailleurs.
    positions = [0, 2, 8, 1, 3, 4, 5, 6, 7]
    assert reduire(compilation, 3, [{p} for p in positions]) is not None
    with pytest.raises(ValueError, match="impossible"):
        compiler([entre(extremites=[{"figure": "cercle", "couleur": "rouge"}] * 2)], 3, FIGURES, COULEURS)
    with pytest.raises(ValueError, match="impossible"):
        compiler([entre(extremites=[{"figure": "carre", "couleur": "rouge"},
                                   {"figure": "cercle", "couleur": "rouge"}])], 3, FIGURES, COULEURS)


def test_entre_4x4_ne_requiert_ni_adjacence_ni_equidistance():
    figures = FIGURES + ["losange"]
    couleurs = COULEURS + ["jaune"]
    a = entre(extremites=[{"figure": "cercle", "couleur": "rouge"},
                         {"figure": "cercle", "couleur": "bleu"}])
    positions = [0, 3, 2, 4, 1, *range(5, 16)]
    assert oracle(a, positions, figures, couleurs)
    assert reduire(compiler([a], 4, figures, couleurs), 4, [{p} for p in positions]) is not None


@pytest.mark.parametrize("indices,fixes", [
    ([compte({"couleur": "rouge"}, 0, 1),
      dict(type="diversite", attribut="figure", zone="colonne", numero=0)], [0, 4, 8]),
    ([entre(), compte({"couleur": "vert"}, 1, 0)], [0, 2, 8]),
    ([entre("diagonale"), compte({"figure": "triangle"}, 0, 1)], [0, 2, 8]),
])
def test_propagation_ne_supprime_aucune_solution_de_enumeration_independante(indices, fixes):
    # Six pions mobiles, 720 affectations complètes. L'oracle ne partage ni
    # compiler, ni les relations géométriques, ni la propagation du moteur.
    libres = set(range(9)) - set(fixes)
    solutions = [fixes + list(suite) for suite in permutations(libres)
                 if all(oracle(a, fixes + list(suite)) for a in indices)]
    assert solutions, "fixture involontairement contradictoire"
    domaines = [{p} for p in fixes] + [set(libres) for _ in range(6)]
    reduits = reduire(compiler(indices, 3, FIGURES, COULEURS), 3, domaines)
    assert reduits is not None
    for solution in solutions:
        assert all(p in reduits[i] for i, p in enumerate(solution))
    # Toute affectation complète est acceptée exactement quand l'oracle le dit.
    for suite in permutations(libres):
        positions = fixes + list(suite)
        accepte = reduire(compiler(indices, 3, FIGURES, COULEURS), 3, [{p} for p in positions]) is not None
        assert accepte == all(oracle(a, positions) for a in indices)


def test_phrase_solo_diagonale3_fixe_centre_mais_pas_ligne_ou_diagonale4():
    assert forcees_riche(entre("diagonale"), 3, FIGURES, COULEURS) == {("carre", "rouge"): 4}
    assert forcees_riche(entre("ligne"), 3, FIGURES, COULEURS) == {}
    assert forcees_riche(entre("diagonale"), 4, FIGURES + ["losange"], COULEURS + ["jaune"]) == {}


@pytest.mark.parametrize("indice", [
    dict(entre(), et=[{"type": "coin"}]),
    {"type": "coin", "figure": "carre", "couleur": "rouge", "et": [entre()]},
])
def test_indice_riche_compose_est_refuse(indice):
    with pytest.raises(ValueError, match="autonome"):
        compiler([indice], 3, FIGURES, COULEURS)


def test_corpus_cinq_paliers_familles_utiles_et_progression():
    from backend.app.domain.contenu import ChargeurContenu
    from deduction_commun import resoudre_par_deduction, informations_autonomes
    from generer_deduction_riche import famille, requis
    from collections import Counter
    items=list(ChargeurContenu().items('deduction'))
    assert Counter(i['palier'] for i in items)=={p:20 for p in range(1,6)}
    for item in items:
        c=item['contenu']; p=item['palier']; n=len(c['figures']); e=c['etape_progression']
        assert n==(4 if p==5 else 3)
        if p>=2:
            assert requis(p,e)<={famille(a) for a in c['enonces']}
        if p==5 and e>=2:
            assert any(a['type']=='entre' and a['axe']=='diagonale' for a in c['enonces'])
        # Une famille n'est pas présente pour décorer : retirer une information
        # retire une étape de la preuve sans hypothèse. Unicité vérifiée à part.
        infos=[a for ph in c['enonces'] for a in informations_autonomes(ph)]
        for k in range(len(infos)):
            assert not resoudre_par_deduction(infos[:k]+infos[k+1:],n,c['figures'],c['couleurs']), item['id']
    for p in range(1,6):
        assert [i['contenu']['etape_progression'] for i in items if i['palier']==p]==[1]*7+[2]*7+[3]*6


def test_recherche_independante_detecte_ambiguite_contradiction_et_budget():
    from verifier_unicite_deduction import solutions_independantes, BudgetDepasse
    import pytest
    contenu={'figures':['cercle','carre','triangle'],'couleurs':['rouge','bleu','vert'],'enonces':[]}
    item={'id':'test','contenu':contenu}
    assert len(solutions_independantes(item)[0])==2
    with pytest.raises(BudgetDepasse):
        solutions_independantes(item,budget=1)
    contenu['enonces']=[{'type':'case','figure':'cercle','couleur':'rouge','case':0},
                        {'type':'case','figure':'carre','couleur':'rouge','case':0}]
    assert solutions_independantes(item)[0]==[]
