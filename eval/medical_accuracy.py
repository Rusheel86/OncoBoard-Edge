from __future__ import annotations

import argparse
import json
from typing import Any


def rubric_basic(report: dict[str, Any]) -> dict[str, Any]:
    """
    Phase 1 lightweight rubric.

    This is not a clinical validator; it checks whether the report is structured,
    includes uncertainty handling, and avoids empty sections.
    """
    required_fields = [
        "summary",
        "key_findings",
        "assessment",
        "recommended_next_steps",
        "treatment_considerations",
        "red_flags",
        "uncertainty_notes",
        "citations",
    ]
    missing = [f for f in required_fields if f not in report]
    empty = []
    for f in required_fields:
        if f in report and (report[f] is None or report[f] == "" or report[f] == []):
            empty.append(f)

    return {
        "missing_fields": missing,
        "empty_fields": empty,
        "passes_structure": (len(missing) == 0),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, help="Path to report JSON")
    args = ap.parse_args()

    report = json.loads(open(args.report, "r", encoding="utf-8").read())
    metrics = rubric_basic(report)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
