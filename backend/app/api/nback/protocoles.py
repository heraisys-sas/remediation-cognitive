"""Observation n-back visuelle auto-rythmée, sans retour pendant le bloc."""
import random

VERSION = 'nback-visuel-v2'
DECISIONS = 15
SYMBOLES = ('cercle', 'carre', 'triangle', 'etoile')
TOTAL = 16
CORRESPONDANCES = 5


def canonical(values):
    symbols = {}
    return tuple(symbols.setdefault(value, len(symbols)) for value in values)


def sequence(rng=None, n=1):
    rng = rng or random.SystemRandom()
    total = n + DECISIONS
    matches = set(rng.sample(range(n, total), CORRESPONDANCES))
    values = [rng.choice(SYMBOLES) for _ in range(n)]
    for position in range(n, total):
        reference = values[position - n]
        values.append(reference if position in matches else rng.choice([x for x in SYMBOLES if x != reference]))
    assert {i for i in range(n, total) if values[i] == values[i - n]} == matches
    return values


def result(session):
    counts = dict(correspondances_detectees=0, correspondances_manquees=0, non_correspondances_rejetees=0, fausses_alertes=0, absences_declarees=0, correspondances_observees=0, non_correspondances_observees=0, absences_correspondances=0, absences_non_correspondances=0)
    rows = []
    n = session['n']
    advanced = session['version'] == VERSION
    if advanced:
        counts.update(leurres_proximite_observes=0, fausses_alertes_leurres=0)
    for item in session['decisions']:
        position = item['position']
        match = session['sequence'][position - 1] == session['sequence'][position - 1 - n]
        decision = item['decision']
        counts['correspondances_observees' if match else 'non_correspondances_observees'] += 1
        if decision == 'absence':
            counts['absences_declarees'] += 1
            counts['absences_correspondances' if match else 'absences_non_correspondances'] += 1
        elif match:
            counts['correspondances_detectees' if decision == 'identique' else 'correspondances_manquees'] += 1
        else:
            counts['non_correspondances_rejetees' if decision == 'different' else 'fausses_alertes'] += 1
        row = {**item, 'correspondance_attendue': match}
        if advanced:
            index = position - 1
            lags = [lag for lag in range(1, n + 2) if lag != n and index >= lag and session['sequence'][index] == session['sequence'][index - lag]]
            lure = bool(lags) and not match
            row.update(lags_proximite=lags, leurre_proximite=lure, coincidence_auxiliaire=bool(lags) and match)
            counts['leurres_proximite_observes'] += lure
            counts['fausses_alertes_leurres'] += lure and decision == 'identique'
        rows.append(row)
    return {'statut': 'termine' if session['phase'] == 'resultat' else 'interrompu', 'n': n, 'presentations': session['position'], 'decisions_observees': len(rows), 'decisions_prevues': session['total'] - n, 'correspondances_prevues': CORRESPONDANCES, **counts, 'interruption': session.get('interruption'), 'sequence': session['sequence'][:session['position']], 'decisions': rows, 'rythme': 'auto-rythme', 'mesure_exposition': 'duree_locale_declaree_sans_temps_de_reaction'}


def public(session):
    data = {key: session[key] for key in ('session_id', 'version', 'condition', 'n', 'total', 'position', 'phase', 'terminee')}
    if session['phase'] in ('initialisation', 'decision'):
        data['symbole'] = session['sequence'][session['position'] - 1]
    if session['phase'] in ('resultat', 'interrompu'):
        data['resultat'] = result(session)
    return data


def advance(session, action, data):
    phase = session['phase']
    if action == 'interrompre' and phase not in ('resultat', 'interrompu'):
        session.update(phase='interrompu', terminee=True, interruption={'raison': data['raison'], 'position': session['position'], 'phase': phase})
    elif action == 'commencer' and phase == 'ready':
        session.update(phase='initialisation', position=1)
    elif action == 'suivant' and phase == 'initialisation':
        session.update(phase='initialisation' if session['position'] < session['n'] else 'decision', position=session['position'] + 1)
    elif action == 'repondre' and phase == 'decision':
        session['decisions'].append({'position': session['position'], **data})
        session['phase'] = 'neutre'
    elif action == 'suivant' and phase == 'neutre':
        if session['position'] == session['total']:
            session.update(phase='resultat', terminee=True)
        else:
            session.update(phase='decision', position=session['position'] + 1)
    else:
        raise ValueError('Cette action ne correspond pas à la phase actuelle')
