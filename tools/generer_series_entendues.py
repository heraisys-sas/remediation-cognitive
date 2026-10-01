#!/usr/bin/env python3
"""Parcours auditif indépendant, mêmes charges mais listes distinctes du parcours lu."""
import json
import random
from pathlib import Path
from generer_rappel_series import construire_paliers, _manifest
from generer_audio_series import PROFIL, nom_fichier

ROOT = Path(__file__).resolve().parents[1]

def construire():
    paliers = construire_paliers(random.Random('series-entendues:20261001'))
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
    return paliers

def main():
    base = ROOT/'content/entrainement/series-entendues'
    (base/'paliers').mkdir(parents=True, exist_ok=True)
    paliers = construire()
    manifest = _manifest(paliers)
    manifest['theme'] = 'series-entendues'
    for p in manifest['paliers']:
        p['id'] = p['id'].replace('rs-', 'rse-')
        p['prerequis'] = [s.replace('rs-', 'rse-') for s in p['prerequis']]
    for n, items in enumerate(paliers, 1):
        (base/f'paliers/palier-{n:02}.json').write_text(json.dumps(items, ensure_ascii=False, indent=2)+'\n')
    (base/'paliers.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
