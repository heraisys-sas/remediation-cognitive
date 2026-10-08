from tools.generation import arguments_generation, ecrire_json


def test_dry_run_ne_cree_aucun_fichier_et_json_reproductible(tmp_path):
    cible = tmp_path / 'contenu/palier.json'
    donnees = [{'id': 'test-1', 'texte': 'Réponse'}]
    assert arguments_generation('Test', ['--dry-run']).dry_run
    ecrire_json(cible, donnees, dry_run=True)
    assert not cible.parent.exists()
    ecrire_json(cible, donnees)
    premiere = cible.read_bytes()
    ecrire_json(cible, donnees)
    assert cible.read_bytes() == premiere
    assert b'\\u00' not in premiere and premiere.endswith(b'\n')
