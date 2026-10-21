"""Non-régression des garde-fous, sans exiger les empreintes Apple en CI."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.app.domain import capacites
from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.correction import _sens_proche, corriger
from tools.calibrer_correction import measure

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("response", [
    "pas chez la gardienne", "pas, chez la gardienne", "chez la gardienne mais pas chez elle",
    "non : chez la gardienne", "jamais chez la gardienne",
])
def test_containment_never_bypasses_negation(response):
    item = ChargeurContenu().item("quotidien", "qo-1-message-06")
    with patch.object(capacites, "proche", return_value=True):
        assert not corriger("quotidien", item, response)


@pytest.mark.parametrize("response", [
    "Marie appelle Paul pour confirmer le rendez-vous",
    "Marie appelle Paul pour confirmer le rendez-vous !",
])
def test_word_permutation_cannot_prove_same_roles(response):
    with patch.object(capacites, "proche", return_value=True) as approximate:
        assert not _sens_proche(response, ["Paul appelle Marie pour confirmer le rendez-vous"])
        approximate.assert_not_called()


def test_corpus_sources_and_lexical_measurement():
    corpus = json.loads((ROOT / "tools/calibration/reponses.json").read_text())
    report = measure("lexical", corpus)
    assert report["cases"] == 40
    assert report["false_accepts"] == 0
    # Limite documentée du repli lexical, pas un synonyme déclaré ni une norme.
    assert [row["response"] for row in report["rows"] if not row["matches"]] == ["la cave"]


def test_measurement_rejects_stale_content_and_never_fakes_apple():
    with pytest.raises(ValueError, match="Source absente ou modifiée"):
        measure("lexical", {"cases": [{"id": "absent", "theme": "quotidien", "item": "absent"}],
                            "synthetic": []})
    with patch.object(capacites, "_embeddings_apple", return_value=None):
        with pytest.raises(RuntimeError, match="aucun repli"):
            measure("apple", {"cases": [], "synthetic": []})
