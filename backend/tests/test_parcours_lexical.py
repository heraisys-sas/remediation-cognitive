"""Le parcours lexical garde le QCM comme entrée, jamais comme retour au P4."""
from backend.app.domain.contenu import ChargeurContenu


def test_palier_quatre_sans_qcm_et_historiques_preserves():
    chargeur = ChargeurContenu()
    parcours = chargeur.items('evocation', 'acces-lexical')
    assert {i['type'] for i in parcours if i['palier'] == 1} == {'reconnaissance'}
    for palier in (2, 3, 4):
        items = [i for i in parcours if i['palier'] == palier]
        assert items
        assert {i['type'] for i in items} == {'rappel-indice'}
    originaux = chargeur.items('evocation')
    assert any(i['palier'] == 5 and i['type'] == 'reconnaissance' for i in originaux)
    assert chargeur.palier_depart('evocation', 'acces-lexical') == 2
    definition = next(p for p in chargeur.parcours('evocation') if p['id'] == 'acces-lexical')
    assert definition['libelles_paliers'][1] == 'QCM'
    assert 'Point de départ' in definition['libelles_paliers'][2]
    assert 'types_par_source' not in definition
