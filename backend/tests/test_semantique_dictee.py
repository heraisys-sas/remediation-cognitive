"""Le texte dicté suit le même correcteur ; sens libre et cibles strictes séparés."""
from backend.app.domain import correction


def item(type_, cible, **contenu):
    return {'type': type_, 'contenu': contenu, 'reponse': {'valeur': cible}}


def test_phrase_libre_utilise_comparaison_locale(monkeypatch):
    appels = []
    def proche(reponse, cibles):
        appels.append((reponse, cibles))
        return True
    monkeypatch.setattr(correction.capacites, 'proche', proche)
    assert correction.corriger('methodes', item('production', 'je vais chez le médecin'), 'je consulte le docteur')
    assert appels == [('je consulte le docteur', ['je vais chez le médecin'])]


def test_cibles_strictes_ne_consultent_pas_semantique(monkeypatch):
    def interdit(*args):
        raise AssertionError('Pas de similarité pour une cible stricte')
    monkeypatch.setattr(correction.capacites, 'proche', interdit)
    assert not correction.corriger('calcul-mental', item('production', 42), '43')
    assert not correction.corriger('memoire', item('empan', '549'), '594')
    assert not correction.corriger('evocation', item('rappel-indice', 'gare'), 'station')
    assert correction.corriger('evocation', item('rappel-indice', 'gare'), 'on attend devant la gare')
    assert not correction.corriger('methodes', item('pqrst', 'je vérifie le plan', options=['je vérifie le plan','je change le plan']), 'je change le plan')


def test_nombre_et_negation_ne_passent_pas_par_similarite(monkeypatch):
    monkeypatch.setattr(correction.capacites, 'proche', lambda *args: True)
    assert not correction.corriger('quotidien', item('prise-message', 'jeudi soir'), 'vendredi soir')
    assert not correction.corriger('methodes', item('production', 'je vérifie le plan'), 'je ne vérifie pas le plan')
