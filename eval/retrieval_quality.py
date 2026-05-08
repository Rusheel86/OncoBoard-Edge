from __future__ import annotations

import argparse
import json
from typing import Any


def retrieval_metrics(results: list[dict[str, Any]]) -> dict[str, float]:
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    for item in results:
        expected = set(item.get("expected_chunk_ids") or [])
        retrieved = [c.get("chunk_id") for c in item.get("retrieved_chunks") or []]
        if not expected:
            continue
        hits = [chunk_id for chunk_id in retrieved if chunk_id in expected]
        recalls.append(len(set(hits)) / len(expected))
        rank = next((idx + 1 for idx, chunk_id in enumerate(retrieved) if chunk_id in expected), None)
        reciprocal_ranks.append(1.0 / rank if rank else 0.0)
    if not recalls:
        return {"recall_at_k": 0.0, "mrr": 0.0}
    return {
        "recall_at_k": sum(recalls) / len(recalls),
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="JSON list with expected_chunk_ids and retrieved_chunks")
    args = ap.parse_args()
    with open(args.results, "r", encoding="utf-8") as f:
        results = json.load(f)
    print(json.dumps(retrieval_metrics(results), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
