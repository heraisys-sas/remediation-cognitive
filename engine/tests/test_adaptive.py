from engine.adaptive.rule import ajuster_palier


def test_progres_si_reussite_haute():
    assert ajuster_palier(3, 0.95) == 4


def test_recule_si_reussite_basse():
    assert ajuster_palier(3, 0.4) == 2


def test_stable_si_zone_neutre():
    assert ajuster_palier(3, 0.75) == 3


def test_ne_descend_pas_sous_palier_1():
    assert ajuster_palier(1, 0.1) == 1
