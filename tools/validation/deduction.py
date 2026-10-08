from __future__ import annotations



from deduction_commun import (  # noqa: E402
    PALIERS_RECOUPMENT_BLOQUANT,
    phrases_qui_fixent_seules,
    pred_indice,
    rang_premiere_certitude,
    resoudre_par_deduction,
)
from generer_deduction import AIDE_CROISEMENT  # noqa: E402



from deduction_contraintes import TYPES_RICHES, compiler as compiler_contraintes

TYPES_INDICE_GRILLE = {
    "case", "ligne", "colonne", "pas-ligne", "pas-colonne",
    "coin", "pas-coin", "pas-bord", "ni-ni",
    "diagonale", "diagonale-inverse", "pas-diagonale", "pas-diagonale-inverse",
    "voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous", "voisin-diagonale",
    "oppose",
    "autre-ligne", "autre-colonne", "comparaison",
    "a-droite-de", "a-gauche-de", "au-dessus-de", "en-dessous-de",
    "pas-voisin-gauche", "pas-voisin-droite", "pas-voisin-dessus", "pas-voisin-dessous",
    "pas-a-droite-de", "pas-a-gauche-de", "pas-au-dessus-de", "pas-en-dessous-de",
    "si-alors", "regle",
} | TYPES_RICHES

def _cellule_grille(fig: list[int], coul: list[int], i_f: int, i_c: int) -> int:
    for i in range(len(fig)):
        if fig[i] == i_f and coul[i] == i_c:
            return i
    return -1

def _predicat_grille(indice: dict, fig: list[int], coul: list[int],
                     index_figure: dict, index_couleur: dict, n: int) -> bool:
    """Un indice (et ses **deux informations**) est-il vrai pour la solution ?

    Le contrôle passe par le solveur commun : une seule définition de la vérité
    des phrases, partagée par le générateur, le dépôt et les tests.
    """
    if indice.get("type") == "regle":
        return True
    noms_f = [nom for nom, _ in sorted(index_figure.items(), key=lambda kv: kv[1])]
    noms_c = [nom for nom, _ in sorted(index_couleur.items(), key=lambda kv: kv[1])]
    return pred_indice(indice, (tuple(fig), tuple(coul)), n, noms_f, noms_c)

def _sens_riche_contredit(indice: dict, fig: list[int], coul: list[int],
                          index_figure: dict, index_couleur: dict, n: int) -> str | None:
    def cases(categorie):
        return [i for i in range(n * n)
                if ("figure" not in categorie or fig[i] == index_figure[categorie["figure"]])
                and ("couleur" not in categorie or coul[i] == index_couleur[categorie["couleur"]])]

    if indice["type"] in {"compte-categorie", "diversite"}:
        numeros = range(n) if indice["numero"] == "chaque" else [indice["numero"]]
        for numero in numeros:
            region = [i for i in range(n * n)
                      if (i // n if indice["zone"] == "ligne" else i % n) == numero]
            if indice["type"] == "compte-categorie":
                compte = len(set(region) & set(cases(indice["categorie"])))
                if compte != indice["nombre"]:
                    return "le nombre de pions de la catégorie dans la zone est différent"
            else:
                valeurs = fig if indice["attribut"] == "figure" else coul
                if len({valeurs[i] for i in region}) != n:
                    return "la zone ne contient pas exactement un pion de chaque valeur annoncée"
        return None
    centre = cases({"figure": indice["figure"], "couleur": indice["couleur"]})[0]
    cr, cc = divmod(centre, n)
    for a in cases(indice["extremites"][0]):
        for b in cases(indice["extremites"][1]):
            if len({a, b, centre}) != 3:
                continue
            ar, ac = divmod(a, n)
            br, bc = divmod(b, n)
            if indice["axe"] == "ligne":
                vrai = ar == cr == br and (ac < cc < bc or bc < cc < ac)
            elif indice["axe"] == "colonne":
                vrai = ac == cc == bc and (ar < cr < br or br < cr < ar)
            else:
                # Les deux segments sont obliques à 45°, de même pente,
                # et le centre se trouve strictement entre les extrémités.
                vrai = (abs(ar-cr) == abs(ac-cc) and abs(br-cr) == abs(bc-cc)
                        and (ar-cr)*(bc-cc) == (br-cr)*(ac-cc)
                        and (ar < cr < br or br < cr < ar))
            if vrai:
                return None
    return "aucune paire de pions des catégories annoncées n'encadre le sujet sur cet axe"

def _sens_contredit(indice: dict, fig: list[int], coul: list[int],
                    index_figure: dict, index_couleur: dict, n: int) -> str | None:
    """Contradiction entre le **sens français** de la phrase et la solution.

    Contrôle écrit indépendamment du solveur, à partir de la signification des
    phrases : « Le carré bleu est juste à gauche du cercle rouge » exige que le
    carré bleu soit dans la colonne immédiatement à gauche. C'est ce contrôle qui
    manquait quand une paire droite/gauche ou dessus/dessous a été inversée -
    l'inversion rendait la grille insoluble sans qu'aucun outil ne s'en aperçoive.
    """
    if indice.get("type") in TYPES_RICHES:
        return _sens_riche_contredit(indice, fig, coul, index_figure, index_couleur, n)

    def case_de(nom_f: str, nom_c: str) -> int:
        return _cellule_grille(fig, coul, index_figure[nom_f], index_couleur[nom_c])

    coins_n = {0, n - 1, n * (n - 1), n * n - 1}
    bords_n = {i for i in range(n * n) if i // n in (0, n - 1) or i % n in (0, n - 1)}
    for atome in [indice] + list(indice.get("et") or []):
        if not isinstance(atome, dict):
            continue
        nom_f = atome.get("figure", indice.get("figure"))
        nom_c = atome.get("couleur", indice.get("couleur"))
        if nom_f not in index_figure or nom_c not in index_couleur:
            continue
        ligne, colonne = divmod(case_de(nom_f, nom_c), n)
        type_indice = atome.get("type")
        if type_indice == "ligne" and ligne != atome["ligne"]:
            return "la phrase annonce une autre ligne"
        if type_indice == "colonne" and colonne != atome["colonne"]:
            return "la phrase annonce une autre colonne"
        if type_indice == "pas-ligne" and ligne == atome["ligne"]:
            return "la phrase exclut la ligne où se trouve la figure"
        if type_indice == "pas-colonne" and colonne == atome["colonne"]:
            return "la phrase exclut la colonne où se trouve la figure"
        if type_indice == "pas-coin" and case_de(nom_f, nom_c) in coins_n:
            return "la figure est dans un coin alors que la phrase l'exclut"
        if type_indice == "coin" and case_de(nom_f, nom_c) not in coins_n:
            return "la phrase annonce un coin, la figure n'y est pas"
        if type_indice == "diagonale" and ligne != colonne:
            return "la phrase annonce la diagonale descendante, la figure n'y est pas"
        if type_indice == "diagonale-inverse" and ligne + colonne != n - 1:
            return "la phrase annonce la diagonale montante, la figure n'y est pas"
        if type_indice == "pas-diagonale" and ligne == colonne:
            return "la phrase exclut la diagonale descendante où se trouve la figure"
        if type_indice == "pas-diagonale-inverse" and ligne + colonne == n - 1:
            return "la phrase exclut la diagonale montante où se trouve la figure"
        if type_indice == "pas-bord" and case_de(nom_f, nom_c) in bords_n:
            return "la figure est sur le bord alors que la phrase l'exclut"
        if type_indice == "ni-ni" and (case_de(nom_f, nom_c) in coins_n or case_de(nom_f, nom_c) in bords_n):
            return "la figure est dans un coin ou sur le bord alors que la phrase l'exclut"
        if type_indice in ("voisin-gauche", "voisin-droite", "voisin-dessus", "voisin-dessous",
                           "voisin-diagonale", "oppose",
                           "comparaison", "a-droite-de", "a-gauche-de", "au-dessus-de",
                           "en-dessous-de", "autre-ligne", "autre-colonne"):
            l2, c2 = divmod(case_de(atome["figure2"], atome["couleur2"]), n)
            attendu = {
                "voisin-gauche": (l2, c2 - 1),      # juste à gauche : une colonne avant
                "voisin-droite": (l2, c2 + 1),
                "voisin-dessus": (l2 - 1, c2),       # juste au-dessus : une ligne avant
                "voisin-dessous": (l2 + 1, c2),
            }.get(type_indice)
            if attendu and (ligne, colonne) != attendu:
                return (f"« {type_indice} » place la figure en ({ligne}, {colonne}) "
                        f"alors que la solution la donne en ({l2}, {c2})")
            if type_indice == "a-droite-de" and colonne <= c2:
                return "la phrase dit « plus à droite » sans que ce soit vrai"
            if type_indice == "a-gauche-de" and colonne >= c2:
                return "la phrase dit « plus à gauche » sans que ce soit vrai"
            if type_indice == "au-dessus-de" and ligne >= l2:
                return "la phrase dit « plus haut » sans que ce soit vrai"
            if type_indice == "en-dessous-de" and ligne <= l2:
                return "la phrase dit « plus bas » sans que ce soit vrai"
            if type_indice == "autre-ligne" and ligne == l2:
                return "la phrase dit « pas la même ligne » alors que c'est la même"
            if type_indice == "autre-colonne" and colonne == c2:
                return "la phrase dit « pas la même colonne » alors que c'est la même"
            if type_indice == "comparaison" and (ligne != l2 or colonne >= c2):
                return "la phrase dit « sur la même ligne, à gauche » sans que ce soit vrai"
            if type_indice == "voisin-diagonale" and not (abs(ligne - l2) == 1 and abs(colonne - c2) == 1):
                return "la phrase dit que les deux figures se touchent en diagonale sans que ce soit vrai"
            if type_indice == "oppose" and case_de(nom_f, nom_c) != n * n - 1 - case_de(atome["figure2"], atome["couleur2"]):
                return "la phrase dit « à l'opposé » sans que les deux figures soient symétriques par le centre"
    return None

def _erreurs_grille_deduction(item: dict, prefixe: str, contenu: dict) -> list[str]:
    erreurs: list[str] = []
    figures = contenu.get("figures")
    couleurs = contenu.get("couleurs")
    if not (isinstance(figures, list) and len(figures) in (3, 4) and len(set(figures)) == len(figures)):
        erreurs.append(prefixe + "grille-deduction : contenu.figures doit être 3 ou 4 figures distinctes")
        return erreurs
    if not (isinstance(couleurs, list) and len(couleurs) == len(figures) and len(set(couleurs)) == len(couleurs)):
        erreurs.append(prefixe + "grille-deduction : contenu.couleurs doit avoir autant de couleurs distinctes que de figures")
        return erreurs
    n = len(figures)

    enonces = contenu.get("enonces")
    if not isinstance(enonces, list) or len(enonces) < 2 or not all(
        isinstance(e, dict) and e.get("type") in TYPES_INDICE_GRILLE for e in enonces
    ):
        erreurs.append(prefixe + "grille-deduction : au moins deux indices structurés attendus")
        return erreurs
    # Valider avant tout prédicat : un indice mal formé doit produire un diagnostic,
    # et non interrompre la validation du dépôt avec une exception.
    secours = contenu.get("indices", [])
    if not isinstance(secours, list):
        return [prefixe + "grille-deduction : indices de secours attendus en liste"]
    try:
        compiler_contraintes(enonces + [i for i in secours if isinstance(i, dict)
                                       and i.get("type") != "regle"], n, figures, couleurs)
    except (ValueError, KeyError, TypeError, IndexError, StopIteration) as exc:
        return [prefixe + f"grille-deduction : structure des indices invalide ({exc})"]

    reponse_bloc = item.get("reponse") if isinstance(item.get("reponse"), dict) else {}
    grille = reponse_bloc.get("grille")
    valeur = reponse_bloc.get("valeur")
    if not isinstance(grille, list) or len(grille) != n * n:
        erreurs.append(prefixe + f"grille-deduction : reponse.grille doit contenir {n * n} cases")
        return erreurs

    cellules = []
    for case in grille:
        if not (isinstance(case, list) and len(case) == 2
                and case[0] in figures and case[1] in couleurs):
            erreurs.append(prefixe + "grille-deduction : case [figure, couleur] attendue")
            return erreurs
        cellules.append(case)

    # Chaque figure colorée (figure × couleur) est posée une seule fois : aucune
    # combinaison ne se répète. C'est la SEULE règle du puzzle - aucune contrainte
    # de ligne ou de colonne n'est supposée : tout doit venir des phrases.
    combinaisons = [(f, c) for f, c in cellules]
    if len(set(combinaisons)) != n * n:
        erreurs.append(prefixe + "grille-deduction : une figure colorée apparaît plusieurs fois (chaque combinaison doit être unique)")

    if valeur != ";".join(f"{f}:{c}" for f, c in cellules):
        erreurs.append(prefixe + "grille-deduction : reponse.valeur ne correspond pas à reponse.grille")

    # Chaque indice (principal et de secours) est vrai pour la solution.
    index_figure = {f: i for i, f in enumerate(figures)}
    index_couleur = {c: i for i, c in enumerate(couleurs)}
    fig = [index_figure[f] for f, _ in cellules]
    coul = [index_couleur[c] for _, c in cellules]
    for position, indice in enumerate(enonces, start=1):
        if not isinstance(indice, dict):
            continue
        if indice.get("type") not in TYPES_INDICE_GRILLE:
            erreurs.append(prefixe + f"grille-deduction : indice {position} de type inconnu")
        elif any(isinstance(a, dict) and a.get("type") not in TYPES_INDICE_GRILLE
                 for a in (indice.get("et") or [])):
            erreurs.append(prefixe + f"grille-deduction : information {position} de type inconnu")
        elif not _predicat_grille(indice, fig, coul, index_figure, index_couleur, n):
            erreurs.append(prefixe + f"grille-deduction : l'indice {position} contredit la solution")

    # Sens des phrases : contrôle INDÉPENDANT du solveur.
    for position, indice in enumerate(enonces, start=1):
        if not isinstance(indice, dict):
            continue
        souci = _sens_contredit(indice, fig, coul, index_figure, index_couleur, n)
        if souci:
            erreurs.append(prefixe + f"grille-deduction : phrase {position} contredit la solution ({souci})")

    # Pédagogie verrouillée : les phrases doivent contenir la résolution.
    palier = item.get("palier")
    if any(a.get("type") == "case" for i in enonces
           for a in [i] + list(i.get("et") or [])):
        erreurs.append(prefixe + "grille-deduction : placement direct interdit "
                                "(toute la résolution doit venir des phrases)")
    secours = contenu.get("indices")
    if isinstance(secours, list):
        for position, indice in enumerate(secours, start=1):
            if isinstance(indice, dict) and indice.get("type") not in TYPES_INDICE_GRILLE:
                erreurs.append(prefixe + f"grille-deduction : indice de secours {position} de type inconnu")
            elif isinstance(indice, dict) and not _predicat_grille(indice, fig, coul, index_figure, index_couleur, n):
                erreurs.append(prefixe + f"grille-deduction : l'indice de secours {position} contredit la solution")

    # Les indices doivent suffire : la grille se reconstruit par déduction, sans deviner.
    if (isinstance(enonces, list) and enonces
            and all(isinstance(i, dict) for i in enonces)
            and not resoudre_par_deduction(enonces, n, figures, couleurs)):
        erreurs.append(prefixe + "grille-deduction : puzzle non résoluble par déduction "
                                "(ajouter des indices jusqu'à ce que le solveur termine)")

    # Recoupement des chaînes (paliers avancés) : aucune phrase seule ne fixe de
    # position ; la première certitude exige au moins deux phrases, quel que soit
    # l'ordre de présentation. Le diagnostic s'applique à TOUTE grille (même non
    # déductible : c'est là qu'il parle le plus). Le palier 1 (initiation
    # séquentielle) est mesuré sans être bloqué.
    if (isinstance(enonces, list) and enonces
            and all(isinstance(i, dict) for i in enonces)
            and isinstance(palier, int)
            and palier in PALIERS_RECOUPMENT_BLOQUANT):
        solos = phrases_qui_fixent_seules(enonces, n, figures, couleurs)
        for rang in solos:
            erreurs.append(prefixe + f"grille-deduction : phrase {rang + 1} fixe seule une "
                                    f"position (placement direct déguisé, palier {palier})")
        premiere = rang_premiere_certitude(enonces, n, figures, couleurs)
        if premiere == 1:
            erreurs.append(prefixe + "grille-deduction : la première certitude vient d'une seule "
                                    "phrase (au moins deux phrases doivent se recouper)")

    aide = contenu.get("aide_raisonnement")
    if aide is not None:
        from deduction_commun import propager
        try:
            refs = aide["phrases"]
            if (aide["mode"] not in ("intersection", "croisement") or not refs
                or any(type(k) is not int or not 1 <= k <= len(enonces) for k in refs)
                or len(set(refs)) != len(refs)
                or type(aide["case"]) is not int or not 0 <= aide["case"] < n*n):
                raise ValueError("références ou case invalides")
            pion = (figures.index(aide["figure"]), couleurs.index(aide["couleur"]))
            support = [enonces[k-1] for k in refs]
            possibles = [[k for k,d in enumerate(propager([ph], n, figures, couleurs)) if pion in d]
                         for ph in support]
            if aide["possibilites"] != possibles:
                raise ValueError("listes de possibilités non fidèles aux phrases")
            if aide["mode"] == "intersection" and set.intersection(*(set(d) for d in possibles)) != {aide["case"]}:
                raise ValueError("intersection annoncée fausse")
            d = propager(support, n, figures, couleurs)
            if [k for k,c in enumerate(d) if pion in c] != [aide["case"]]:
                raise ValueError("conclusion non déductible des phrases citées")
            if aide["mode"] == "croisement":
                from deduction_contraintes import compiler, reduire
                domaines = [set(range(n*n)) for _ in range(n*n)]
                demonstration = aide["demonstration"]
                if not demonstration:
                    raise ValueError("démonstration absente")
                for etape in demonstration:
                    if etape["phrase"] not in refs:
                        raise ValueError("phrase de démonstration non annoncée")
                    apres = reduire(compiler([enonces[etape["phrase"]-1]], n, figures, couleurs), n, domaines)
                    attendu = [dict(figure=figures[i//n], couleur=couleurs[i%n], cases=sorted(apres[i]))
                               for i in range(n*n) if apres[i] != domaines[i]]
                    if etape["reductions"] != attendu:
                        raise ValueError("étape de démonstration incorrecte")
                    domaines = apres
                if domaines[pion[0]*n+pion[1]] != {aide["case"]}:
                    raise ValueError("démonstration inachevée")
            if cellules[aide["case"]] != [aide["figure"], aide["couleur"]]:
                raise ValueError("conclusion différente de la solution")
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            erreurs.append(prefixe + f"grille-deduction : aide de raisonnement invalide ({exc})")

    # Aide harmonisée : les paliers avancés parlent de croisement des phrases —
    # jamais d'une position donnée par une phrase seule (le palier 1 garde son
    # texte d'initiation). Contrôle de cohérence sur tout le corpus avancé.
    if isinstance(palier, int) and palier in PALIERS_RECOUPMENT_BLOQUANT:
        if contenu.get("aide") != AIDE_CROISEMENT:
            erreurs.append(prefixe + "grille-deduction : aide non harmonisée "
                                    "(attendu : texte de croisement des phrases)")
    return erreurs
