from __future__ import annotations

import argparse
import json
from typing import Any


def citation_coverage(report: dict[str, Any], retrieval: dict[str, Any]) -> dict[str, Any]:
    cited = set(report.get("citations") or [])
    chunks = retrieval.get("chunks") or []
    available = {c.get("chunk_id") for c in chunks if isinstance(c, dict)}
    available.discard(None)

    if not available:
        return {"citation_rate": 0.0, "missing_citations": list(cited)}

    matched = cited.intersection(available)
    return {
        "citation_rate": (len(matched) / max(len(cited), 1)) if cited else 0.0,
        "cited": sorted(cited),
        "matched": sorted(matched),
        "available": sorted(available),
        "unmatched": sorted(cited - available),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, help="Path to report JSON")
    ap.add_argument("--retrieval", required=True, help="Path to retrieval JSON")
    args = ap.parse_args()

    report = json.loads(open(args.report, "r", encoding="utf-8").read())
    retrieval = json.loads(open(args.retrieval, "r", encoding="utf-8").read())

    metrics = citation_coverage(report, retrieval)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
