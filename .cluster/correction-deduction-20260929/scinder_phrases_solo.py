#!/usr/bin/env python3
"""Scinde les phrases « solo » du palier 3 en chaînes de deux informations.

Correction du défaut C (preuve exacte, 2026-09-29) : une phrase composée qui,
prise SEULE, fixe une position est un placement direct déguisé. Ici, chaque
phrase fautive est une chaîne [ancre, relation, comparaison] : on la scinde en
deux chaînes de deux informations qui partagent le maillon central —

    [ancre + oppose + comparaison]  ->  [ancre + oppose]  et  [oppose + comparaison]

Aucune des deux ne fixe seule une position (vérifié par énumération exhaustive) ;
la déduction qu'imposait la phrase d'un bloc exige désormais le croisement ENTRE
les deux phrases. Le verrou pédagogique du dépôt est respecté : au palier 3,
chaque phrase porte au moins deux informations et relie deux figures. Les
doublons exacts laissés par la scission (grilles à chaînes jumelles) sont
retirés, de même que les chaînes scindées devenues redondantes — jamais le
vocabulaire requis (oppose, comparaison), jamais sous le plancher de phrases.
Les items modifiés reçoivent de nouveaux identifiants (df-3-XX -> dc-3-XX) ;
les items inchangés gardent les leurs.

Usage (depuis la racine du dépôt) :
    python3 .cluster/correction-deduction-20260929/scinder_phrases_solo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "tools"))

from deduction_commun import (  # noqa: E402
    TYPES_BINAIRES,
    informations_autonomes,
    phrases_qui_fixent_seules,
    pred_indice,
    rang_premiere_certitude,
    resoudre_par_deduction,
)

CHEMIN = RACINE / "content" / "entrainement" / "deduction" / "paliers" / "palier-03.json"
DATE = "2026-09-29"
VOCABULAIRE_REQUIS = ("oppose", "comparaison")
PLANCHER_PHRASES = 4          # minimum du validateur : len(enonces) >= 4
AIDE = ("Aucune phrase ne suffit seule : recoupe les phrases entre elles, "
        "barre ce qui devient impossible — les cases certaines apparaissent au croisement.")
META_AUTEUR = ("generation-automatique (tools/generer_deduction.py) ; correction 2026-09-29 "
               "(scission des phrases qui fixent seules une position — preuve exacte)")


def types_de(phrase: dict) -> set[str]:
    return {atome.get("type") for atome in [phrase] + list(phrase.get("et") or [])}


def scinder(phrase: dict) -> list[dict]:
    """[ancre + oppose + comparaison] -> [ancre + oppose] et [oppose + comparaison]."""
    informations = informations_autonomes(phrase)
    assert len(informations) == 3, f"chaîne solo inattendue ({len(informations)} informations)"
    premiere = {**informations[0], "et": [dict(informations[1])]}
    seconde = {**informations[1], "et": [dict(informations[2])]}
    return [premiere, seconde]


def main() -> int:
    items = json.loads(CHEMIN.read_text(encoding="utf-8"))
    remplaces = []
    for item in items:
        contenu = item["contenu"]
        n = len(contenu["figures"])
        figures, couleurs = contenu["figures"], contenu["couleurs"]
        enonces = contenu["enonces"]
        solos = set(phrases_qui_fixent_seules(enonces, n, figures, couleurs))
        if not solos:
            continue

        # Scission : chaque phrase solo devient deux chaînes de deux informations.
        nouvelles, ids_scindees = [], set()
        for rang, phrase in enumerate(enonces):
            if rang in solos:
                for nouvelle in scinder(phrase):
                    ids_scindees.add(id(nouvelle))
                    nouvelles.append(nouvelle)
            else:
                nouvelles.append(phrase)

        # Doublons exacts : une répétition n'apporte aucune information.
        vues, uniques = set(), []
        for phrase in nouvelles:
            cle = json.dumps(phrase, sort_keys=True)
            if cle in vues:
                continue
            vues.add(cle)
            uniques.append(phrase)
        nouvelles = uniques

        # Chaînes scindées devenues redondantes : retirées si la grille reste
        # déterminée, le vocabulaire requis reste présent et le plancher tient.
        change = True
        while change:
            change = False
            for rang in range(len(nouvelles) - 1, -1, -1):
                phrase = nouvelles[rang]
                if id(phrase) not in ids_scindees or len(nouvelles) - 1 < PLANCHER_PHRASES:
                    continue
                essai = nouvelles[:rang] + nouvelles[rang + 1:]
                types_restants: set[str] = set()
                for autre in essai:
                    types_restants |= types_de(autre)
                if not all(t in types_restants for t in VOCABULAIRE_REQUIS):
                    continue
                if not resoudre_par_deduction(essai, n, figures, couleurs):
                    continue
                nouvelles = essai
                change = True
                break

        # Contrôles : plus aucun solo ; grille déterminée par déduction ; phrases
        # vraies pour la solution ; verrou pédagogique (>= 2 informations, une
        # relation binaire par phrase) ; première certitude au rang >= 2.
        assert not phrases_qui_fixent_seules(nouvelles, n, figures, couleurs), item["id"]
        assert resoudre_par_deduction(nouvelles, n, figures, couleurs), item["id"]
        grille = item["reponse"]["grille"]
        index_f = {f: i for i, f in enumerate(figures)}
        index_c = {c: i for i, c in enumerate(couleurs)}
        fig = tuple(index_f[f] for f, _ in grille)
        coul = tuple(index_c[c] for _, c in grille)
        for phrase in nouvelles:
            assert pred_indice(phrase, (fig, coul), n, figures, couleurs), (item["id"], phrase)
            assert 1 + len(phrase.get("et") or []) >= 2, (item["id"], phrase)
            assert types_de(phrase) & TYPES_BINAIRES, (item["id"], phrase)
        rang = rang_premiere_certitude(nouvelles, n, figures, couleurs)
        assert rang is not None and rang >= 2, (item["id"], rang)

        ancienne = item["id"]
        item["id"] = "dc-3-" + ancienne.rsplit("-", 1)[-1]
        contenu["enonces"] = nouvelles
        contenu["aide"] = AIDE
        item["meta"]["auteur"] = META_AUTEUR
        item["meta"]["date_creation"] = DATE
        remplaces.append((ancienne, item["id"], len(solos), len(nouvelles)))

    CHEMIN.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for ancienne, nouvelle, nb_solos, nb_total in remplaces:
        print(f"{ancienne} -> {nouvelle} : {nb_solos} phrase(s) scindée(s), "
              f"{nb_total} phrases au total")
    print(f"{len(remplaces)} grilles réparées")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
