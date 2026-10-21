"""Simulations originales versionnées ; aucune norme ni programmation FSRS."""
from copy import deepcopy
import re
import time
import unicodedata

from .banque_v3 import AJOUTS

VERSION = 'strategies-appliquees-v3'
SCENARIOS = {
    'plan': {'id': 'strategie-plan-dossier-v1', 'but': 'Préparer un dossier complet et signé.', 'actions': [{'id': 'remplir', 'texte': 'Compléter le formulaire'}, {'id': 'signer', 'texte': 'Signer le formulaire'}, {'id': 'joindre', 'texte': 'Joindre la pièce'}], 'contraintes': ['Compléter avant de signer.', 'Les trois actions sont nécessaires.']},
    'rappel': {'id': 'strategie-rappel-dossier-v1', 'consigne': 'Quand « Dossier prêt » apparaît, joignez la pièce d’identité.', 'pieces': [{'id': 'identite', 'texte': 'Pièce d’identité'}, {'id': 'facture', 'texte': 'Facture'}], 'actions_intercalees': [{'id': 'nom', 'texte': 'Vérifier le nom du dossier'}, {'id': 'date', 'texte': 'Vérifier la date du dossier'}]},
    'message': {'id': 'strategie-message-appel-v1', 'message': 'Appelez le secrétariat à 15 heures.', 'actions': [{'id': 'appeler', 'texte': 'Appeler le secrétariat'}, {'id': 'envoyer', 'texte': 'Envoyer un courrier'}, {'id': 'classer', 'texte': 'Classer le dossier'}], 'heures': ['15 h', '10 h', '18 h']},
    'temps': {'id': 'strategie-temps-documents-v1', 'consigne': 'Classez les quatre documents selon leur titre : factures dans Facture, lettres dans Courrier.', 'categories': ['facture', 'courrier'], 'documents': [{'id': 'd1', 'texte': 'Facture d’électricité'}, {'id': 'd2', 'texte': 'Lettre de confirmation'}, {'id': 'd3', 'texte': 'Facture de téléphone'}, {'id': 'd4', 'texte': 'Lettre d’information'}]},
}
# Archives conservées : les journaux v1 sans ID résolvent ces contenus.
ORIGINAUX = deepcopy(SCENARIOS)
for item in ORIGINAUX.values():
    item['nouvelle_contrainte'] = 'Joindre la pièce avant de signer.' if item is ORIGINAUX['plan'] else None
ORIGINAUX['rappel'].update(signal='Dossier prêt', attendu_piece='identite')
ORIGINAUX['message'].update(attendu_action='appeler', attendu_heure='15', attendu_quoi='Appeler le secrétariat', formes_quoi=['appeler le secretariat', 'appeler secretariat', 'appelez le secretariat', 'telephoner au secretariat', 'je dois appeler le secretariat'])
ORIGINAUX['temps']['attendu_classement'] = {'d1': 'facture', 'd2': 'courrier', 'd3': 'facture', 'd4': 'courrier'}
SCENARIOS = {item['id']: item for item in ORIGINAUX.values()}
BANQUES = {}
for parcours, original in ORIGINAUX.items():
    variants = [deepcopy(original) for _ in range(3)]
    for index, item in enumerate(variants):
        item['id'] = f'strategie-{parcours}-simulation-{index + 1}-v2'
    BANQUES[parcours] = [item['id'] for item in variants]
    SCENARIOS.update({item['id']: item for item in variants})

for index, (but, labels, initial, nouvelle) in enumerate([
    ('Préparer une inscription à un atelier.', ['Compléter le bulletin', 'Signer le bulletin', 'Joindre le justificatif'], 'Compléter le bulletin avant sa signature.', 'Joindre le justificatif avant de signer le bulletin.'),
    ('Préparer une demande de prêt de matériel.', ['Compléter la demande de prêt', 'Signer la demande', 'Joindre la liste du matériel'], 'Compléter la demande avant de la signer.', 'Joindre la liste du matériel avant de signer la demande.'),
], 1):
    item = SCENARIOS[BANQUES['plan'][index]]
    item.update(but=but, actions=[{'id': key, 'texte': label} for key, label in zip(('remplir', 'signer', 'joindre'), labels)], contraintes=[initial, 'Les trois actions sont nécessaires.'], nouvelle_contrainte=nouvelle)

for index, (signal, target, other, actions) in enumerate([
    ('Réservation prête', ('billet', 'Billet de réservation'), ('plan', 'Plan du quartier'), [('destination', 'Vérifier la destination'), ('voyageurs', 'Vérifier le nombre de voyageurs')]),
    ('Matériel prêt', ('liste', 'Liste du matériel'), ('notice', 'Notice d’utilisation'), [('quantite', 'Vérifier la quantité'), ('reference', 'Vérifier la référence du matériel')]),
], 1):
    SCENARIOS[BANQUES['rappel'][index]].update(signal=signal, attendu_piece=target[0], consigne=f'Quand « {signal} » apparaît, joignez : {target[1]}.', pieces=[{'id': key, 'texte': text} for key, text in (target, other)], actions_intercalees=[{'id': key, 'texte': text} for key, text in actions])

for index, (message, target, text, heure, formes, actions) in enumerate([
    ('Envoyez le formulaire à 10 heures.', 'envoyer', 'Envoyer le formulaire', '10', ['envoyer le formulaire', 'envoyez le formulaire', 'je dois envoyer le formulaire'], [('envoyer', 'Envoyer le formulaire'), ('imprimer', 'Imprimer le formulaire'), ('ranger', 'Ranger le formulaire')]),
    ('Imprimez le billet à 18 heures.', 'imprimer', 'Imprimer le billet', '18', ['imprimer le billet', 'imprimez le billet', 'je dois imprimer le billet'], [('imprimer', 'Imprimer le billet'), ('reserver', 'Réserver le billet'), ('annuler', 'Annuler le billet')]),
], 1):
    SCENARIOS[BANQUES['message'][index]].update(message=message, attendu_action=target, attendu_quoi=text, attendu_heure=heure, formes_quoi=formes, actions=[{'id': key, 'texte': label} for key, label in actions], heures=['15 h', '10 h', '18 h'])

for index, (consigne, categories, documents, expected) in enumerate([
    ('Classez les billets dans Voyage et les ordonnances dans Santé.', ['voyage', 'sante'], ['Billet de train', 'Ordonnance de lunettes', 'Ordonnance de pharmacie', 'Billet de bateau'], ['voyage', 'sante', 'sante', 'voyage']),
    ('Classez les recettes dans Cuisine et les fiches de plantes dans Jardin.', ['cuisine', 'jardin'], ['Fiche du rosier', 'Recette de soupe', 'Recette de tarte', 'Fiche du basilic'], ['jardin', 'cuisine', 'cuisine', 'jardin']),
], 1):
    SCENARIOS[BANQUES['temps'][index]].update(consigne=consigne, categories=categories, documents=[{'id': f'd{i + 1}', 'texte': text} for i, text in enumerate(documents)], attendu_classement={f'd{i + 1}': value for i, value in enumerate(expected)})

# Extension seulement : les seize scénarios v1/v2 restent strictement identiques.
for parcours, ajouts in AJOUTS.items():
    BANQUES[parcours].extend(item['id'] for item in ajouts)
    SCENARIOS.update({item['id']: item for item in ajouts})


def stimulus(s):
    return SCENARIOS[s.get('scenario_id', ORIGINAUX[s['parcours']]['id'])]


INITIAL = {'plan': 'plan_initial', 'rappel': 'configuration', 'message': 'encodage', 'temps': 'estimation'}


def public(s):
    scenario = deepcopy(stimulus(s))
    for key in ('attendu_piece', 'attendu_action', 'attendu_heure', 'attendu_quoi', 'formes_quoi', 'attendu_classement'):
        scenario.pop(key, None)
    if s['parcours'] != 'plan' or s['phase'] == 'plan_initial':
        scenario.pop('nouvelle_contrainte', None)
    if s['parcours'] == 'message' and s['phase'] != 'encodage':
        scenario.pop('message')
    if s['parcours'] == 'plan' and s['phase'] != 'plan_initial':
        scenario['contraintes'].append(scenario['nouvelle_contrainte'])
    if s['parcours'] == 'rappel' and s['phase'] != 'configuration':
        scenario.pop('consigne')
        if s['donnees'].get('rappel_consulte'):
            piece = next(item['texte'] for item in scenario['pieces'] if item['id'] == s['donnees']['piece_prevue'])
            scenario['rappel_texte'] = f'Quand « {scenario["signal"]} » apparaît, joindre : {piece}.'
    data = deepcopy(s['donnees'])
    # La restitution n'est jamais renvoyée à l'écran de réponse suivante.
    if s['parcours'] == 'message' and s['phase'] != 'correction':
        data.pop('restitution', None)
    return {'session_id': s['session_id'], 'parcours': s['parcours'], 'version': s['version'], 'condition': s['condition'], 'phase': s['phase'], 'scenario': scenario, 'donnees': data, **({'resultat': result(s)} if s['phase'] == 'correction' else {})}


def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value.lower().strip()) if not unicodedata.combining(c))


def hour(value):
    value = norm(value)
    value = {'quinze heures': '15', 'dix heures': '10', 'dix-huit heures': '18', 'dix huit heures': '18'}.get(value, value)
    match = re.fullmatch(r'(\d{1,2})(?:\s*(?:h|heures?|:)\s*(?:00)?)?', value)
    return str(int(match[1])) if match else value


def result(s):
    d = deepcopy(s['donnees'])
    r = {'session_id': s['session_id'], 'parcours': s['parcours'], 'version': s['version'], 'scenario_id': stimulus(s)['id'], 'condition': s['condition'], 'statut': 'termine' if s['phase'] == 'correction' else 'interrompu', 'observations': d, 'aides': s['aides'], 'pauses': s['pauses']}
    if s['phase'] != 'correction':
        return r
    p = s['parcours']
    item = stimulus(s)
    # Les archives v1 gardent leur tolérance historique.
    normalize_hour = (lambda value: re.sub(r'\s|heures?|h', '', norm(value))) if s['version'] == 'strategies-appliquees-v1' else hour
    if p == 'plan':
        r['correction'] = {'plan_initial_compatible': compatible(d['plan_initial'], False), 'plan_final_compatible': compatible(d['plan_final'], True), 'execution_compatible': compatible(d['actions_executees'], True), 'contraintes': item['contraintes'] + [item['nouvelle_contrainte']]}
    elif p == 'rappel':
        r['correction'] = {'action': 'prematuree' if d.get('action_prematuree') else ('exacte' if d.get('piece_jointe') == item['attendu_piece'] else ('incorrecte' if d.get('piece_jointe') else 'occasion_terminee_sans_action')), 'attendu': item['attendu_piece'], 'signal': item['signal']}
    elif p == 'message':
        rep = d['restitution']
        quoi = norm(rep.get('quoi', ''))
        r['correction'] = {'quoi': 'absence' if rep.get('absence') or not quoi else ('exact' if quoi in item['formes_quoi'] else 'a_verifier'), 'quand': 'absence' if rep.get('absence') or not rep.get('quand') else ('exact' if normalize_hour(rep['quand']) == item['attendu_heure'] else 'confusion'), 'action_exacte': d['action']['action_id'] == item['attendu_action'], 'heure_exacte': normalize_hour(d['action']['heure']) == item['attendu_heure'], 'attendu': {'quoi': item['attendu_quoi'], 'quand': item['attendu_heure'] + ' heures'}}
    else:
        r['correction'] = {'classement': {k: v == item['attendu_classement'][k] for k, v in d['classement'].items()}}
    return r


def compatible(order, revised):
    return set(order) == {'remplir', 'signer', 'joindre'} and len(order) == 3 and order.index('remplir') < order.index('signer') and (not revised or order.index('joindre') < order.index('signer'))


def require(ok, message='Transition indisponible'):
    if not ok:
        raise ValueError(message)


def number(d, key):
    value = d.get(key)
    require(type(value) in (int, float) and 0 <= value <= 86400, 'Durée invalide')
    return value


def advance(s, action, d):
    p, phase, state = s['parcours'], s['phase'], s['donnees']
    item = stimulus(s)
    require(phase != 'correction')
    if action == 'pause':
        require(not s['pause'])
        s['pause'] = time.time(); s['pauses'] += 1
        if p == 'message': s['aides'].append('reprise_apres_interruption')
        return
    if action == 'reprendre':
        require(s['pause'] is not None)
        s['pause_secondes'] += time.time() - s['pause']; s['pause'] = None
        if p == 'message': s['phase'] = 'encodage'
        return
    require(s['pause'] is None, 'Séance en pause')
    if action == 'incident':
        s['temps_fiable'] = False; s['aides'].append('incident')
        return
    if action == 'aide':
        s['aides'].append(phase)
        return
    if p == 'plan':
        if action in ('plan_initial', 'reviser'):
            require(phase == ('plan_initial' if action == 'plan_initial' else 'revision'))
            order = d.get('ordre'); require(isinstance(order, list) and len(order) == 3 and set(order) == {'remplir', 'signer', 'joindre'}, 'Choisissez les trois actions')
            state['plan_initial' if action == 'plan_initial' else 'plan_final'] = order
            s['phase'] = 'revision' if action == 'plan_initial' else 'execution'
            if action == 'reviser': state['actions_executees'] = []
        elif action == 'executer':
            require(phase == 'execution'); item = d.get('action_id'); require(item in ('remplir', 'signer', 'joindre') and item not in state['actions_executees'])
            state['actions_executees'].append(item)
            if len(state['actions_executees']) == 3: s['phase'] = 'verification'
        elif action == 'verifier':
            require(phase == 'verification'); state['verification_realisee'] = True
        elif action == 'terminer':
            require(phase == 'verification' and state.get('verification_realisee')); s['phase'] = 'correction'
        else: require(False)
    elif p == 'rappel':
        if action == 'configurer':
            require(phase == 'configuration' and d.get('piece_id') in [piece['id'] for piece in item['pieces']] and type(d.get('rappel')) is bool)
            state.update(piece_prevue=d['piece_id'], rappel_programme=d['rappel'], rappel_delivre=False, rappel_consulte=False, actions_intercalees=[]); s['phase'] = 'intercale'
            s['condition'] = 'avec-rappel' if d['rappel'] else 'sans-rappel'
        elif action == 'intercaler':
            require(phase == 'intercale' and d.get('action_id') in [entry['id'] for entry in item['actions_intercalees']] and d['action_id'] not in state['actions_intercalees'])
            state['actions_intercalees'].append(d['action_id'])
            if len(state['actions_intercalees']) == 2: s['phase'] = 'signal'; state.update(signal=item['signal'], rappel_delivre=state['rappel_programme'])
        elif action == 'consulter_rappel':
            require(phase == 'signal' and state['rappel_delivre']); state['rappel_consulte'] = True
        elif action == 'joindre':
            require(phase in ('intercale', 'signal') and d.get('piece_id') in [piece['id'] for piece in item['pieces']] and 'piece_jointe' not in state)
            state['piece_jointe'] = d['piece_id']; state['action_prematuree'] = phase != 'signal'
        elif action == 'terminer':
            require(phase == 'signal'); s['phase'] = 'correction'
        else: require(False)
    elif p == 'message':
        if action == 'masquer':
            require(phase == 'encodage' and type(d.get('note_presente', False)) is bool)
            require(s['condition'] == 'avec-note' or not d.get('note_presente'))
            state['note_presente'] = d.get('note_presente', False); s['phase'] = 'action' if 'restitution' in state else 'restitution'
        elif action == 'reecouter':
            require(phase in ('restitution', 'action')); s['aides'].append('reecoute'); s['phase'] = 'encodage'
        elif action == 'consulter_note':
            require(s['condition'] == 'avec-note' and state.get('note_presente') and phase in ('restitution', 'action')); state['note_consultee'] = True
        elif action == 'restituer':
            require(phase == 'restitution' and 'restitution' not in state)
            require(type(d.get('absence', False)) is bool and all(isinstance(d.get(k, ''), str) and len(d.get(k, '')) <= 500 for k in ('quoi', 'quand')))
            require(d.get('absence') or d.get('quoi', '').strip() or d.get('quand', '').strip(), 'Déclarez une absence ou une réponse')
            state['restitution'] = {k: d.get(k, False if k == 'absence' else '') for k in ('quoi', 'quand', 'absence')}; state['restitution_assistee'] = bool(s['aides']); s['phase'] = 'action'
        elif action == 'agir':
            require(phase == 'action' and d.get('action_id') in [entry['id'] for entry in item['actions']] and d.get('heure') in item['heures'])
            state['action'] = {'action_id': d['action_id'], 'heure': d['heure']}; s['phase'] = 'correction'
        else: require(False)
    else:
        if action == 'estimer':
            require(phase == 'estimation'); state['estimation_secondes'] = number(d, 'secondes'); state['classement'] = {}; s['debut_tache'] = time.time(); s['pause_secondes'] = 0; s['phase'] = 'classement'
        elif action == 'classer':
            require(phase == 'classement' and d.get('document_id') in [entry['id'] for entry in item['documents']] and d.get('categorie') in item['categories'] and d['document_id'] not in state['classement'])
            state['classement'][d['document_id']] = d['categorie']
            if len(state['classement']) == 4: s['fin_tache'] = time.time(); s['phase'] = 'comparaison'
        elif action == 'comparer':
            require(phase == 'comparaison' and not state.get('comparaison_realisee'))
            if s['temps_fiable']:
                active, elapsed, pauses = (d.get(k) for k in ('duree_active_secondes', 'duree_ecoulee_secondes', 'pauses_secondes'))
                waiting = d.get('attente_interface_secondes', 0)
                reliable = all(type(v) in (int, float) and 0 <= v <= 86400 for v in (active, elapsed, pauses, waiting))
                if reliable and abs(elapsed - active - pauses - waiting) <= 0.1:
                    state.update(duree_ecoulee_secondes=elapsed, duree_active_secondes=active, pauses_secondes=pauses, attente_interface_secondes=waiting, ecart_secondes=active - state['estimation_secondes'], source_duree='horloge_monotone_locale_declaree')
            state['comparaison_realisee'] = True
        elif action == 'marge':
            require(phase == 'comparaison' and state.get('comparaison_realisee')); state['marge_secondes'] = number(d, 'secondes'); s['phase'] = 'correction'
        else: require(False)
