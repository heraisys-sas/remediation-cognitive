"""Extension lexicale adulte : nouveaux identifiants, ancien corpus conservé."""
from pathlib import Path
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
DESCRIPTIONS = ["QCM de soutien", "Objets familiers", "Mots précis et documents", "Notions en contexte", "Verbes utiles", "Mots en situation"]


def normaliser(texte):
    return ''.join(c for c in unicodedata.normalize('NFD', texte.casefold()) if not unicodedata.combining(c))


def items_lexicaux():
    banque = json.loads((ROOT / 'tools/banque_lexicale_adulte.json').read_text())
    items = []
    for groupe in banque['paliers']:
        niveau = groupe['palier']
        for numero, ligne in enumerate(groupe['items'], 1):
            mot = ligne['mot']
            contenu = {'consigne': 'Choisis le mot qui correspond à la définition.' if niveau == 1 else 'Retrouve le mot à partir de la définition.', 'enonce': ligne['definition'], 'aide': None}
            if niveau == 1:
                contenu['options'] = [mot, *ligne['leurres']]
                # Permutation déterministe propre à chaque item.
                rotation = numero % 3
                contenu['options'] = contenu['options'][rotation:] + contenu['options'][:rotation]
            else:
                assert normaliser(ligne['amorce']) != normaliser(mot)
                contenu['indices'] = [
                    {'type': 'semantique', 'texte': f"Catégorie : {ligne['categorie']}."},
                    {'type': 'phonologique', 'texte': f"Le mot commence par « {ligne['amorce']}… »."},
                    {'type': 'orthographique', 'texte': f"{len(mot)} lettres, première lettre « {mot[0].upper()} »."},
                ]
            reponse = {'valeur': mot}
            if ligne['variantes']: reponse['variantes'] = ligne['variantes']
            items.append({'id': f'ev2-{niveau}-{numero:02d}', 'palier': niveau + 7,
                'type': 'reconnaissance' if niveau == 1 else 'rappel-indice',
                'module': 'entrainement', 'theme': 'evocation', 'fonctions_ciblees': ['acces-lexical', 'recuperation'],
                'contenu': contenu, 'reponse': reponse, 'prerequis': [], 'cap_complexite': None,
                'meta': {'auteur': 'redaction-assistee (banque_lexicale_adulte)', 'date_creation': '2026-10-08', 'relecture_ortho': {'statut': 'a_revoir'}}})
    return items


def ecrire():
    dossier = ROOT / 'content/entrainement/evocation'
    items = items_lexicaux()
    manifeste = json.loads((dossier/'paliers.json').read_text())
    manifeste['paliers'] = [p for p in manifeste['paliers'] if int(p['id'].rsplit('-', 1)[1]) <= 7]
    for niveau, description in enumerate(DESCRIPTIONS, 8):
        lot = [i for i in items if i['palier'] == niveau]
        fichier = f'paliers/palier-{niveau:02d}.json'
        (dossier/fichier).write_text(json.dumps(lot, ensure_ascii=False, indent=2)+'\n')
        manifeste['paliers'].append({'id': f'ev-palier-{niveau}', 'description': description,
            'prerequis': [], 'fichier': fichier, 'nb_items': len(lot)})
    (dossier/'paliers.json').write_text(json.dumps(manifeste, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__': ecrire()
