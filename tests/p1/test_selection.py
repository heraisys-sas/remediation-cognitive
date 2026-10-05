"""Tests ciblés de la sélection d'items (P1-B5) — unitaires isolés.

Hors de `backend/tests/` pour ne pas hériter du conftest FastAPI.
Couvre le fork `etape_progression` et l'allocation révisions/nouveaux.
Cas limites : palier vide, quota impair, tous nouveaux, tous dus.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.domain.selection import selectionner_items
from engine.srs.fsrs import CarteFSRS, planifier

MAINT = datetime(2026, 1, 5, 8, 0, 0, tzinfo=timezone.utc)


def _item(item_id: str, palier: int = 1, etape: int | None = None) -> dict:
    contenu = {}
    if etape is not None:
        contenu["etape_progression"] = etape
    return {"id": item_id, "palier": palier, "contenu": contenu}


def _carte_due(item_id: str) -> CarteFSRS:
    carte = CarteFSRS(item_id)
    carte, _ = planifier(carte, 3, datetime(2026, 1, 1, tzinfo=timezone.utc))
    return carte


def _carte_future(item_id: str) -> CarteFSRS:
    return CarteFSRS(item_id)


def test_quota_max_respecte():
    items = [_item(f"i{n}") for n in range(30)]
    sel = selectionner_items(items, {}, 1, MAINT, max_items=12)
    assert len(sel) == 12


def test_palier_vide_renvoie_vide():
    items = [_item("a", palier=2)]
    assert selectionner_items(items, {}, 1, MAINT) == []


def test_tous_nouveaux_sans_fork():
    items = [_item(f"n{n}") for n in range(4)]
    sel = selectionner_items(items, {}, 1, MAINT, max_items=4)
    assert [i["id"] for i in sel] == ["n0", "n1", "n2", "n3"]


def test_fork_dus_avant_nouveaux():
    items = [
        _item("n0", etape=1),
        _item("d0", etape=2),
        _item("n1", etape=1),
        _item("d1", etape=2),
    ]
    cartes = {"d0": _carte_due("d0"), "d1": _carte_due("d1")}
    sel = selectionner_items(items, cartes, 1, MAINT, max_items=4)
    ids = [i["id"] for i in sel]
    assert set(ids[:2]) == {"d0", "d1"}
    assert set(ids[2:]) == {"n0", "n1"}


def test_fork_nouveaux_classes_par_etape():
    items = [_item("b", etape=3), _item("a", etape=1), _item("c", etape=2)]
    sel = selectionner_items(items, {}, 1, MAINT, max_items=3)
    assert [i["id"] for i in sel] == ["a", "c", "b"]


def test_fork_dus_classes_par_etape_decroissante():
    items = [_item("r1", etape=1), _item("r3", etape=3), _item("r2", etape=2)]
    cartes = {r["id"]: _carte_due(r["id"]) for r in items}
    sel = selectionner_items(items, cartes, 1, MAINT, max_items=3)
    assert [i["id"] for i in sel] == ["r3", "r2", "r1"]


def test_quota_impair_reserve_majorite_aux_revisions():
    items = [_item(f"r{n}", etape=2) for n in range(6)] + [_item(f"n{n}", etape=1) for n in range(6)]
    cartes = {f"r{n}": _carte_due(f"r{n}") for n in range(6)}
    sel = selectionner_items(items, cartes, 1, MAINT, max_items=5)
    ids = [i["id"] for i in sel]
    assert sum(1 for i in ids if i.startswith("r")) == 3
    assert len(sel) == 5


def test_tous_dus_sans_nouveaux():
    items = [_item(f"r{n}", etape=1) for n in range(5)]
    cartes = {f"r{n}": _carte_due(f"r{n}") for n in range(5)}
    sel = selectionner_items(items, cartes, 1, MAINT, max_items=3)
    assert len(sel) == 3
    assert all(i["id"].startswith("r") for i in sel)


def test_carte_non_due_comptee_comme_nouveau():
    items = [_item("x", etape=1)]
    cartes = {"x": _carte_future("x")}
    assert [i["id"] for i in selectionner_items(items, cartes, 1, MAINT, max_items=3)] == ["x"]


def test_include_non_dus_complete_si_quota_non_atteint():
    items = [_item(f"r{n}", etape=1) for n in range(2)] + [_item("z", etape=1)]
    cartes = {"r0": _carte_due("r0"), "r1": _carte_due("r1")}
    sel = selectionner_items(items, cartes, 1, MAINT, max_items=3, include_non_dus=True)
    assert len(sel) == 3
    assert "z" in [i["id"] for i in sel]


def test_include_non_dus_ne_deborde_pas():
    items = [_item(f"n{n}") for n in range(10)]
    sel = selectionner_items(items, {}, 1, MAINT, max_items=4, include_non_dus=True)
    assert len(sel) == 4
