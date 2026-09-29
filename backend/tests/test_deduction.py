"""Tests du thème « Déduction » — grille logique 3×3 et 4×4 (figures × couleurs)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from deduction_commun import (  # noqa: E402
    PALIERS_RECOUPMENT_BLOQUANT,
    TYPES_BINAIRES,
    TYPES_UNAIRES,
    _vrai_binaire,
    _vrai_unaire,
    informations_autonomes,
    phrases_qui_fixent_seules,
    positions_forcees_phrase,
    pred_indice,
    propager,
    rang_premiere_certitude,
    resoudre_par_deduction,
)
import mesurer_difficulte  # noqa: E402

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


PAIRES_POSITIVE_NEGATIVE = (
    # Appariement déclaré explicitement : chaque type négatif est le complément
    # exact de CE type positif-là — jamais déduit du libellé français.
    (("voisin-gauche", "pas-voisin-gauche"),
     "le sujet est immédiatement à gauche de la cible"),
    (("voisin-droite", "pas-voisin-droite"),
     "le sujet est immédiatement à droite de la cible"),
    (("voisin-dessus", "pas-voisin-dessus"),
     "le sujet est immédiatement au-dessus de la cible"),
    (("voisin-dessous", "pas-voisin-dessous"),
     "le sujet est immédiatement en dessous de la cible"),
    (("a-droite-de", "pas-a-droite-de"),
     "le sujet est plus à droite que la cible"),
    (("a-gauche-de", "pas-a-gauche-de"),
     "le sujet est plus à gauche que la cible"),
    (("au-dessus-de", "pas-au-dessus-de"),
     "le sujet est plus haut que la cible"),
    (("en-dessous-de", "pas-en-dessous-de"),
     "le sujet est plus bas que la cible"),
)


def test_negations_complements_exactes_des_positives():
    """Chaque négation binaire est le complément EXACT de sa positive : pour toute
    paire de cases distinctes, la négation vaut vrai si et seulement si la positive
    vaut faux. Appariement déclaré explicitement (indépendant des libellés).
    Régression : « pas-voisin-dessus/dessous » étaient croisées — chacune niait
    l'autre, et une phrase pouvait être vraie et fausse en même temps.
    """
    for n in (3, 4):
        for (positive, negative), sens in PAIRES_POSITIVE_NEGATIVE:
            for i1 in range(n * n):
                for i2 in range(n * n):
                    if i1 == i2:
                        continue
                    v_pos = _vrai_binaire({"type": positive}, i1, i2, n)
                    v_neg = _vrai_binaire({"type": negative}, i1, i2, n)
                    assert v_neg == (not v_pos), (
                        f"n={n} « {negative} » ({sens}) : cases {i1}->{i2} donne "
                        f"positive={v_pos}, négative={v_neg} — la négation doit être "
                        "le complément exact de sa positive"
                    )


def test_repro_pas_voisin_dessus_dessous_inverses():
    """Cas de reproduction du défaut : n=3, sujet case 0, cible case 3 — la cible
    est juste en dessous du sujet, donc « voisin-dessus » est vrai ET
    « pas-voisin-dessus » doit être faux (avant correction : les deux vrais).
    """
    n = 3
    assert _vrai_binaire({"type": "voisin-dessus"}, 0, 3, n) is True
    assert _vrai_binaire({"type": "pas-voisin-dessus"}, 0, 3, n) is False
    # Symétrique : sujet case 3, cible case 0 — la cible est juste au-dessus.
    assert _vrai_binaire({"type": "voisin-dessous"}, 3, 0, n) is True
    assert _vrai_binaire({"type": "pas-voisin-dessous"}, 3, 0, n) is False


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


def test_recoupement_paliers_avances():
    """Critères de recoupement (défaut C) : aux paliers 2-4, aucune phrase prise
    seule ne fixe de position, et la première certitude exige au moins deux
    phrases. Au palier 1 (initiation séquentielle), l'exigence est mesurée sans
    être bloquante (décision documentée) : on la signale seulement.
    """
    for item in CONTENU.items("deduction"):
        contenu = item["contenu"]
        n = len(contenu["figures"])
        enonces = contenu["enonces"]
        if item["palier"] in PALIERS_RECOUPMENT_BLOQUANT:
            solos = phrases_qui_fixent_seules(enonces, n, contenu["figures"], contenu["couleurs"])
            assert not solos, \
                f"{item['id']} : phrase(s) {[(s + 1) for s in solos]} fixe(nt) seule(s) une position"
            premiere = rang_premiere_certitude(enonces, n, contenu["figures"], contenu["couleurs"])
            assert premiere != 1, \
                f"{item['id']} : la première certitude vient d'une seule phrase"


def test_validateur_refuse_phrase_solo_et_certitude_immediate():
    """Le validateur du dépôt refuse une grille qui viole les critères C : une
    phrase qui fixe seule une position (ni-ni sur 3×3 = centre) et une première
    certitude obtenue avec une seule phrase. On construit deux grilles fautives
    mais VERIDIQUES (chaque phrase reste vraie pour la solution) à partir d'une
    grille valide de palier 3, puis on passe le validateur dessus.
    """
    import validate_items as vi

    item = next(i for i in CONTENU.items("deduction") if i["palier"] == 3)
    contenu = json.loads(json.dumps(item["contenu"]))  # copie profonde
    n = len(contenu["figures"])
    cellules = item["reponse"]["grille"]

    # (1) Phrase solo véridique : « ni-ni » portée par la figure du CENTRE
    # (3×3, case 4 : ni coin ni bord) — elle fixe seule une position.
    centre_f, centre_c = cellules[4]
    sauvegarde = contenu["enonces"][0]
    contenu["enonces"][0] = {"type": "ni-ni", "figure": centre_f, "couleur": centre_c}
    faux = dict(item)
    faux["contenu"] = contenu
    erreurs = vi._erreurs_grille_deduction(faux, "", contenu)
    assert any("fixe seule" in e for e in erreurs), erreurs

    # (2) Certitude immédiate véridique : ligne + colonne (dans une même phrase)
    # de la case RÉELLE d'une figure — une seule phrase présentée suffit à fixer
    # une position, ce que les critères C interdisent aux paliers avancés.
    cible_f, cible_c = cellules[8]  # n'importe quelle figure : sa ligne+colonne la fixe
    ligne = next(i for i, (f, _) in enumerate(cellules) if (f, _) == (cible_f, cible_c)) // n
    colonne = next(i for i, (f, _) in enumerate(cellules) if (f, _) == (cible_f, cible_c)) % n
    contenu["enonces"][0] = {
        "type": "ligne", "ligne": ligne, "figure": cible_f, "couleur": cible_c,
        "et": [{"figure": cible_f, "couleur": cible_c, "type": "colonne", "colonne": colonne}],
    }
    erreurs = vi._erreurs_grille_deduction(faux, "", contenu)
    assert any("première certitude" in e for e in erreurs), erreurs
    contenu["enonces"][0] = sauvegarde


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

# --------------------------------------------------------------------------- #
# Preuve exacte du « fixe seule » et réparation par scission — correction du
# défaut C, 2026-09-29. Tests INDÉPENDANTS : reproduction du cas df-3-03,
# propagation inverse et unicité, retrait réel des informations (ancre comprise)
# sans mutation, distinction rang de lecture / support, et contrôle par
# énumération brute de TOUT le contenu des paliers 2 à 4.
# --------------------------------------------------------------------------- #

FIGURES3 = ["cercle", "carre", "triangle"]
COULEURS3 = ["rouge", "bleu", "vert"]


def _phrase_solo_df_3_03() -> dict:
    """Première phrase de l'ex-df-3-03, reconstruite indépendamment du contenu."""
    return {
        "type": "diagonale", "figure": "triangle", "couleur": "rouge",
        "et": [
            {"figure": "triangle", "couleur": "rouge", "type": "oppose",
             "figure2": "cercle", "couleur2": "bleu"},
            {"figure": "cercle", "couleur": "bleu", "type": "comparaison",
             "figure2": "cercle", "couleur2": "rouge"},
        ],
    }


def test_reproduction_df_3_03_la_phrase_seule_fixe_les_cases_0_et_8():
    """Reproduction du faux « zéro solo » : cette phrase, prise SEULE, fixe deux
    positions — le triangle rouge en case 8 et le cercle bleu en case 0 (le
    centre est exclu : deux jetons ne partagent pas une case). La propagation à
    sens unique de l'ancienne détection ne le voyait pas."""
    phrase = _phrase_solo_df_3_03()
    assert positions_forcees_phrase(phrase, 3) == {
        ("triangle", "rouge"): 8, ("cercle", "bleu"): 0}
    assert phrases_qui_fixent_seules([phrase], 3, FIGURES3, COULEURS3) == [0]


def test_la_scission_rend_chaque_chaine_inoffensive_seule():
    """La réparation scinde la phrase solo en deux chaînes de deux informations,
    [ancre + oppose] et [oppose + comparaison] : aucune ne fixe seule une
    position — c'est leur croisement qui retrouve les cases 0 et 8."""
    infos = informations_autonomes(_phrase_solo_df_3_03())
    assert [a["type"] for a in infos] == ["diagonale", "oppose", "comparaison"]
    premiere = {**infos[0], "et": [dict(infos[1])]}
    seconde = {**infos[1], "et": [dict(infos[2])]}
    assert phrases_qui_fixent_seules([premiere], 3, FIGURES3, COULEURS3) == []
    assert phrases_qui_fixent_seules([seconde], 3, FIGURES3, COULEURS3) == []


def test_propagation_inverse_et_unicite_des_cases():
    """La propagation binaire réduit les DEUX extrémités de la relation ;
    deux jetons ne partagent jamais une case."""
    phrases = [
        {"type": "coin", "figure": "cercle", "couleur": "rouge"},
        {"type": "voisin-gauche", "figure": "cercle", "couleur": "rouge",
         "figure2": "carre", "couleur2": "rouge"},
    ]
    domaines = propager(phrases, 3, FIGURES3, COULEURS3)
    assert domaines is not None
    cr = (FIGURES3.index("cercle"), COULEURS3.index("rouge"))
    kr = (FIGURES3.index("carre"), COULEURS3.index("rouge"))
    assert {c for c, d in enumerate(domaines) if cr in d} == {0, 6}
    assert {c for c, d in enumerate(domaines) if kr in d} == {1, 7}

    # Unicité : deux jetons ne peuvent pas occuper la même case.
    assert propager([
        {"type": "case", "figure": "cercle", "couleur": "rouge", "case": 4},
        {"type": "case", "figure": "carre", "couleur": "rouge", "case": 4},
    ], 3, FIGURES3, COULEURS3) is None

    # Le centre est exclu d'un « à l'opposé » : il faudrait y mettre les deux.
    domaines = propager([
        {"type": "oppose", "figure": "cercle", "couleur": "rouge",
         "figure2": "carre", "couleur2": "rouge"},
    ], 3, FIGURES3, COULEURS3)
    assert 4 not in {c for c, d in enumerate(domaines) if cr in d}
    assert 4 not in {c for c, d in enumerate(domaines) if kr in d}


def test_retrait_reel_derniere_sous_info_et_ancre_sans_mutation():
    """La mesure retire VRAIMENT chaque information — la dernière sous-information
    comprise (l'ancienne copie gardait le champ « et » et ne retirait rien) — et
    l'ancre est testée comme les autres. Aucune mutation des phrases au passage."""
    # (1) Tout est retirable un à un : chaque retrait laisse la grille déterminée
    # (le jeton libéré retrouve la seule case restante) — 9 retraits comptés,
    # l'ancre de la première phrase comprise : elle n'était jamais testée avant.
    toutes_retirables = [
        {"type": "case", "figure": "cercle", "couleur": "rouge", "case": 0,
         "et": [{"figure": "carre", "couleur": "rouge", "type": "case", "case": 1}]},
        {"type": "case", "figure": "carre", "couleur": "bleu", "case": 2},
        {"type": "case", "figure": "carre", "couleur": "vert", "case": 3},
        {"type": "case", "figure": "triangle", "couleur": "rouge", "case": 4},
        {"type": "case", "figure": "triangle", "couleur": "bleu", "case": 5},
        {"type": "case", "figure": "triangle", "couleur": "vert", "case": 6},
        {"type": "case", "figure": "cercle", "couleur": "bleu", "case": 7},
        {"type": "case", "figure": "cercle", "couleur": "vert", "case": 8},
    ]
    assert resoudre_par_deduction(toutes_retirables, 3, FIGURES3, COULEURS3)
    assert mesurer_difficulte._retirables_internes(
        toutes_retirables, 3, FIGURES3, COULEURS3) == 9

    # (2) Une relation essentielle (deux jetons se partagent les dernières cases,
    # départagés par « plus à droite que ») : la retirer casse réellement la
    # détermination — elle n'est donc pas comptée. L'ancien faux retrait (copie
    # gardant « et ») l'aurait comptée à tort sans rien retirer.
    essentielle = [
        {"type": "case", "figure": "cercle", "couleur": "rouge", "case": 0,
         "et": [{"figure": "carre", "couleur": "rouge", "type": "a-droite-de",
                 "figure2": "cercle", "couleur2": "vert"}]},
        {"type": "case", "figure": "carre", "couleur": "bleu", "case": 2},
        {"type": "case", "figure": "carre", "couleur": "vert", "case": 3},
        {"type": "case", "figure": "triangle", "couleur": "rouge", "case": 4},
        {"type": "case", "figure": "triangle", "couleur": "bleu", "case": 5},
        {"type": "case", "figure": "triangle", "couleur": "vert", "case": 6},
        {"type": "case", "figure": "cercle", "couleur": "bleu", "case": 7},
    ]
    assert resoudre_par_deduction(essentielle, 3, FIGURES3, COULEURS3)
    sans_relation = [
        {"type": "case", "figure": "cercle", "couleur": "rouge", "case": 0},
    ] + essentielle[1:]
    assert not resoudre_par_deduction(sans_relation, 3, FIGURES3, COULEURS3)
    assert mesurer_difficulte._retirables_internes(
        essentielle, 3, FIGURES3, COULEURS3) == 0

    # (3) Aucune mutation des phrases mesurées ni des atomes décomposés.
    instantane = json.dumps(toutes_retirables, sort_keys=True)
    mesurer_difficulte._retirables_internes(toutes_retirables, 3, FIGURES3, COULEURS3)
    assert json.dumps(toutes_retirables, sort_keys=True) == instantane
    phrase = {"type": "ligne", "ligne": 1, "figure": "cercle", "couleur": "bleu",
              "et": [{"type": "colonne", "colonne": 2}]}
    avant = json.dumps(phrase, sort_keys=True)
    atomes = informations_autonomes(phrase)
    assert json.dumps(phrase, sort_keys=True) == avant
    assert [a["type"] for a in atomes] == ["ligne", "colonne"]
    assert all("et" not in a for a in atomes)
    assert (atomes[1]["figure"], atomes[1]["couleur"]) == ("cercle", "bleu")


def test_rang_de_lecture_et_support_disent_des_choses_differentes():
    """Le rang de lecture suit l'ordre présenté (il change au mélange) ; le
    support propagé cherche des lots de 1 à 3 phrases sans ordre — borne."""
    neutre = {"type": "autre-ligne", "figure": "cercle", "couleur": "rouge",
              "figure2": "carre", "couleur2": "bleu"}
    directe = {"type": "case", "figure": "cercle", "couleur": "rouge", "case": 0}
    assert mesurer_difficulte._k_premier_placement(
        [neutre, directe], 3, FIGURES3, COULEURS3) == 2
    assert mesurer_difficulte._support_propage(
        [neutre, directe], 3, FIGURES3, COULEURS3) == 1
    assert mesurer_difficulte._k_premier_placement(
        [directe, neutre], 3, FIGURES3, COULEURS3) == 1
    assert mesurer_difficulte._support_propage(
        [directe, neutre], 3, FIGURES3, COULEURS3) == 1


def test_paliers_2_4_zero_phrase_solo_par_enumeration_independante():
    """Contrôle indépendant sur TOUT le contenu des paliers 2 à 4 : pour chaque
    phrase, énumération brute (permutations, sans cache ni élagage) de toutes
    les affectations injectives des seuls jetons cités — aucun jeton cité ne
    doit avoir une position certaine."""
    from itertools import permutations

    for item in CONTENU.items("deduction"):
        if item["palier"] not in PALIERS_RECOUPMENT_BLOQUANT:
            continue
        contenu = item["contenu"]
        n = len(contenu["figures"])
        for phrase in contenu["enonces"]:
            infos = informations_autonomes(phrase)
            variables: list[tuple[str, str]] = []
            for a in infos:
                jetons = [(a["figure"], a["couleur"])]
                if a["type"] in TYPES_BINAIRES:
                    jetons.append((a["figure2"], a["couleur2"]))
                for v in jetons:
                    if v not in variables:
                        variables.append(v)
            assert len(variables) <= 3, f"{item['id']} : phrase à plus de 3 jetons cités"
            possibles = {v: set() for v in variables}
            for cases in permutations(range(n * n), len(variables)):
                affectation = dict(zip(variables, cases))
                verifie = True
                for a in infos:
                    c1 = affectation[(a["figure"], a["couleur"])]
                    if a["type"] in TYPES_UNAIRES:
                        if not _vrai_unaire(a, c1, n):
                            verifie = False
                            break
                    elif a["type"] in TYPES_BINAIRES:
                        if not _vrai_binaire(a, c1, affectation[(a["figure2"], a["couleur2"])], n):
                            verifie = False
                            break
                    else:
                        raise AssertionError("type inconnu : " + str(a["type"]))
                if verifie:
                    for v, c in affectation.items():
                        possibles[v].add(c)
            for v, cases in possibles.items():
                assert len(cases) != 1, \
                    f"{item['id']} : {v} fixé seul (énumération indépendante)"

