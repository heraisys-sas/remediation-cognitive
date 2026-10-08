from backend.app.domain.catalog import CATALOGUE, THEMES, proprietes_interface
from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.dosage import parametres_seance
from tools.validation.common import THEMES_CONNUS


def test_api_et_validation_utilisent_le_catalogue(client):
    exposes = client.get('/api/entrainement/themes').json()['themes']
    assert {theme['id'] for theme in exposes} == set(THEMES) == THEMES_CONNUS
    for theme in exposes:
        spec = CATALOGUE[theme['id']]
        assert theme['categorie'] == spec.category
        assert theme['interface'] == proprietes_interface(theme['id'])
        assert ChargeurContenu().palier_depart(theme['id'], None) == spec.start_level
        for cle, valeur in spec.session_parameters.items():
            assert parametres_seance(theme['id'])[cle] == valeur
