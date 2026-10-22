"""Paliers de pratique : charge puis rétention, sans norme de capacité."""
PROGRESSION_VERSION = 'paliers-mi-v1'
PALIERS = {
    'code': [{'longueur': n, 'repetitions': False} for n in range(2, 9)] + [{'longueur': n, 'repetitions': True} for n in range(8, 13)],
    'chemin': [{'longueur': n} for n in range(2, 10)],
    'changement': [{'longueur': n, 'masque_ms': 1500} for n in range(2, 6)] + [{'longueur': 5, 'masque_ms': ms} for ms in (2000, 3000, 5000)],
    'objets': [{'longueur': n, 'masque_ms': 1000} for n in range(2, 7)] + [{'longueur': 6, 'masque_ms': ms} for ms in (2000, 3000)],
}


def condition(parcours, params):
    return params.get('modalite', 'visuelle') if parcours == 'code' else params.get('condition', 'forme') if parcours == 'changement' else 'visuelle'


def etat(sessions, parcours, variante):
    index = 2 if parcours == "code" else 1
    reussites = difficultes = revision = 0
    for session in sorted(sessions, key=lambda s: (s.get('fin', s['cree']), s['session_id'])):
        progression = session.get('progression')
        if not session.get('terminee') or not progression or session['parcours'] != parcours or progression['condition'] != variante or progression['version'] != PROGRESSION_VERSION or progression['palier'] != index + 1 or progression.get('revision', 0) != revision:
            continue
        essais = session['essais']
        if len(essais) != 4 or any(e.get('interruption') or not e.get('premiere') or e.get('aide') for e in essais):
            continue
        correct = 0
        for essai in essais:
            c = essai['premiere']['correction']
            exact = c.get('exacte') is True
            if parcours == 'changement' and c.get('type') == 'detection':
                exact = exact and c.get('localisation_exacte') is True
            correct += exact
        reussites = reussites + 1 if correct >= 3 else 0
        difficultes = difficultes + 1 if correct <= 1 else 0
        if reussites == 2:
            index = min(index + 1, len(PALIERS[parcours]) - 1)
            reussites = difficultes = 0
            revision += 1
        elif difficultes == 2:
            index = max(0, index - 1)
            reussites = difficultes = 0
            revision += 1
    return {'version': PROGRESSION_VERSION, 'condition': variante, 'palier': index + 1, 'total': len(PALIERS[parcours]), 'reussites': reussites, 'revision': revision}
