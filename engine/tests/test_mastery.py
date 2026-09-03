from engine.mastery.criteria import palier_maitrise


def test_pas_assez_de_sessions():
    assert not palier_maitrise([0.95, 0.92])


def test_maitrise_3_sessions():
    assert palier_maitrise([0.95, 0.91, 0.93])


def test_echec_si_une_session_sous_seuil():
    assert not palier_maitrise([0.95, 0.85, 0.95])
