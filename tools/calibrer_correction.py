"""Mesure locale reproductible ; aucun appel réseau, aucun historique utilisateur."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.domain import capacites  # noqa: E402
from backend.app.domain.contenu import ChargeurContenu  # noqa: E402
from backend.app.domain.correction import corriger, _sens_proche  # noqa: E402


def measure(provider: str, corpus: dict, threshold: float = 0.78) -> dict:
    if provider == "apple" and capacites._embeddings_apple() is None:
        raise RuntimeError("Apple NLEmbedding français indisponible : mesure annulée, aucun repli")
    score = capacites._similarite_apple if provider == "apple" else capacites._similarite_lexicale
    content = ChargeurContenu()
    rows = []
    with patch.object(capacites, "similarite", side_effect=score), patch.object(
        capacites, "SEUIL_SIMILARITE", threshold
    ):
        for case in [*corpus["cases"], *corpus["synthetic"]]:
            item = content.item(case["theme"], case["item"]) if "item" in case else None
            if "item" in case and (item is None or item["reponse"]["valeur"] != case["expected"]):
                raise ValueError(f"Source absente ou modifiée : {case['id']}")
            actual = corriger(case["theme"], item, case["response"]) if item else _sens_proche(
                case["response"], [case["expected"]]
            )
            rows.append({**case, "source": "contenu" if item else "synthetique",
                         "score": round(score(case["response"], case["expected"]), 4),
                         "actual": actual, "matches": actual == case["accepted"]})
    return {"provider": provider, "threshold": threshold,
            "purpose": "regression_exploration", "independent_validation": False,
            "system": platform.platform(), "python": platform.python_version(),
            "cases": len(rows),
            "false_accepts": sum(r["actual"] and not r["accepted"] for r in rows),
            "false_rejects": sum(not r["actual"] and r["accepted"] for r in rows),
            "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["lexical", "apple"], default="lexical")
    parser.add_argument("--threshold", type=float, default=capacites.SEUIL_SIMILARITE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true", help="Échoue dès qu'une étiquette diverge")
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1:
        parser.error("Le seuil doit être compris entre 0 et 1")
    corpus = json.loads((ROOT / "tools/calibration/reponses.json").read_text())
    try:
        report = measure(args.provider, corpus, args.threshold)
    except (RuntimeError, ValueError) as error:
        parser.exit(2, f"{error}\n")
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"{report['provider']} seuil={args.threshold} : {report['cases']} cas, "
          f"{report['false_accepts']} fausses acceptations, {report['false_rejects']} faux refus")
    for row in report["rows"]:
        if not row["matches"]:
            print(f"  {row['id']} ({row['category']}) score={row['score']} : {row['response']}")
    return int(args.strict and any(not row["matches"] for row in report["rows"]))


if __name__ == "__main__":
    raise SystemExit(main())
