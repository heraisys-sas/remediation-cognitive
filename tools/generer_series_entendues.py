#!/usr/bin/env python3
"""Parcours auditif indépendant, mêmes charges mais listes distinctes du parcours lu."""

try:
    from tools.generation import ecrire_json, arguments_generation
except ModuleNotFoundError:
    from generation import ecrire_json, arguments_generation
import json
import random
from pathlib import Path
try:
    from tools.generer_rappel_series import construire_paliers, _manifest
    from tools.generer_audio_series import PROFIL, nom_fichier
except ModuleNotFoundError:
    from generer_rappel_series import construire_paliers, _manifest
    from generer_audio_series import PROFIL, nom_fichier

ROOT = Path(__file__).resolve().parents[1]

def construire():
    paliers = construire_paliers(random.Random('series-entendues:20261001'), enrichissement=False)
    for items in paliers:
        for item in items:
            item['id'] = item['id'].replace('rs2-', 'rse1-')
            item['theme'] = 'series-entendues'
            item['prerequis'] = [p.replace('rs-', 'rse-') for p in item['prerequis']]
            item['contenu']['affichage']['modalite'] = 'auditive'
            item['contenu']['affichage']['audio'] = {
                mot: f'/ui/audio/series/{PROFIL}/{nom_fichier(mot)}'
                for serie in item['contenu']['affichage']['series'] for mot in serie
            }
            item['contenu']['consigne'] = item['contenu']['consigne'].replace('les mots affichés', 'les mots entendus')
            item['meta']['auteur'] = 'redaction-assistee (tools/generer_series_entendues.py)'
            item['meta']['date_creation'] = '2026-10-01'
    source = ROOT / "tools/content_sources/series-entendues_04_2026-10-10.json"
    paliers[3].extend(json.loads(source.read_text(encoding="utf-8")))
    return paliers

def main():
    options = arguments_generation(__doc__)
    base = ROOT/'content/entrainement/series-entendues'
    paliers = construire()
    manifest = _manifest(paliers)
    manifest['theme'] = 'series-entendues'
    for p in manifest['paliers']:
        p['id'] = p['id'].replace('rs-', 'rse-')
        p['prerequis'] = [s.replace('rs-', 'rse-') for s in p['prerequis']]
    for n, items in enumerate(paliers, 1):
        ecrire_json(base/f'paliers/palier-{n:02}.json', items, dry_run=options.dry_run)
    ecrire_json(base/'paliers.json', manifest, dry_run=options.dry_run)

if __name__ == '__main__':
    main()
