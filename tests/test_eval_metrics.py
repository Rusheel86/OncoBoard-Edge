from __future__ import annotations

from eval.groundedness import citation_coverage
from eval.medical_accuracy import rubric_basic
from eval.retrieval_quality import retrieval_metrics


def test_citation_coverage_matches_available_chunks() -> None:
    metrics = citation_coverage(
        {"citations": ["a", "missing"]},
        {"chunks": [{"chunk_id": "a"}, {"chunk_id": "b"}]},
    )
    assert metrics["citation_rate"] == 0.5
    assert metrics["unmatched"] == ["missing"]


def test_report_rubric_requires_structure() -> None:
    metrics = rubric_basic({"summary": "x"})
    assert "assessment" in metrics["missing_fields"]
    assert metrics["passes_structure"] is False


def test_retrieval_metrics() -> None:
    metrics = retrieval_metrics(
        [
            {
                "expected_chunk_ids": ["b"],
                "retrieved_chunks": [{"chunk_id": "a"}, {"chunk_id": "b"}],
            }
        ]
    )
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 0.5
