"""Inventaire reproductible sans données personnelles : python tools/auditer_couverture.py."""
import argparse
from collections import Counter
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.domain.catalog import CATALOGUE  # noqa: E402
from backend.app.domain.contenu import ChargeurContenu  # noqa: E402


def inventaire(seances_semaine=5, semaines=13):
    chargeur = ChargeurContenu()
    themes = []
    for theme in chargeur.themes():
        identifiant = theme['id']
        if identifiant in ('anglais', 'python'):
            continue
        spec = CATALOGUE[identifiant]
        parcours = theme['parcours'] or [{'id': None, 'nom': theme['nom']}]
        detail = []
        for parcours_def in parcours:
            pid = parcours_def['id']
            items = chargeur.items(identifiant, pid)
            paliers = Counter(item['palier'] for item in items)
            quota = spec.session_parameters.get('max_items', 12)
            detail.append({
                'id': pid, 'nom': parcours_def['nom'],
                'items_uniques': len({item['id'] for item in items}),
                'types': dict(sorted(Counter(item['type'] for item in items).items())),
                'palier_depart': chargeur.palier_depart(identifiant, pid),
                'paliers': [{'palier': p, 'items': nombre,
                             'quota_max': chargeur.max_items_parcours(identifiant, pid, p) or quota,
                             'seances_uniques_completes': nombre // (chargeur.max_items_parcours(identifiant, pid, p) or quota)}
                            for p, nombre in sorted(paliers.items())],
            })
        themes.append({'id': identifiant, 'nom': theme['nom'],
                       'carte': 'rappel-series' if identifiant == 'series-entendues' else identifiant,
                       'items_source': len(chargeur.items(identifiant)), 'parcours': detail})
    cartes = len({t['carte'] for t in themes}) + 3
    scenes = json.loads((ROOT / 'frontend/images/contextes/manifest.json').read_text())['scenes']
    return {'hypothese': {'semaines': semaines, 'seances_semaine': seances_semaine,
                         'seances_totales': semaines * seances_semaine,
                         'cartes': cartes,
                         'moyenne_seances_par_carte': round(semaines * seances_semaine / cartes, 2),
                         'stress_seances_par_carte': semaines * seances_semaine,
                         'stress_items_carte_quota12': semaines * seances_semaine * 12},
            'themes': themes, 'contextes_images_distinctes': len(scenes),
            'programme_semaines': len(chargeur.programme().get('semaines', [])),
            'nback_v2': {'paliers': [{'n': n, 'presentations': n + 15, 'decisions': 15, 'correspondances': 5, 'sequences_etiquetees_theoriques': 4 ** n * comb(15, 5) * 3 ** 10} for n in (1, 2, 3)], 'anti_repetition': 'canonique persistante, y compris archives V1 équivalentes', 'couverture_verifiee_par_palier': 65, 'progression': 'choix explicite persistant, aucune montée calendaire'},
            'avertissements': [
                'Capacité brute, pas simulation FSRS ni garantie d’absence de répétition.',
                'Items source hors parcours exposé inclus dans items_source, pas dans le stock jouable du parcours.',
                'Plusieurs parcours peuvent partager des items : ne pas additionner leurs stocks sans dédupliquer.',
                'Les générateurs ne sont pas des banques infinies ; codes/chemins ne garantissent pas l’exclusion interséance. N-back V2 dispose de son propre registre canonique.',
            ]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seances-semaine', type=int, default=5)
    parser.add_argument('--semaines', type=int, default=13)
    args = parser.parse_args()
    if args.seances_semaine < 1 or args.semaines < 1:
        parser.error('Les durées et fréquences doivent être positives.')
    print(json.dumps(inventaire(args.seances_semaine, args.semaines), ensure_ascii=False, indent=2))
