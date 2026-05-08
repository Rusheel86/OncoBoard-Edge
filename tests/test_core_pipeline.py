from __future__ import annotations

from pathlib import Path

from core.extractors import build_query, extract_entities, parse_pathology_pdfs
from core.graph import build_onco_graph
from core.state import OncoState, PatientIntake


def test_entity_extraction_finds_common_biomarkers() -> None:
    entities = extract_entities("Adenocarcinoma. EGFR exon 19 mutated. PD-L1 TPS 20%. Stage IV.")
    assert "adenocarcinoma" in entities["histology"]
    assert "EGFR" in entities["biomarkers"]
    assert "PD-L1" in entities["biomarkers"]
    assert entities["stage"].lower() == "stage iv"


def test_full_pipeline_runs_offline_with_grounded_citations() -> None:
    run = build_onco_graph()
    state = OncoState(
        case=PatientIntake(
            patient_id="T_PIPE",
            primary_site="lung",
            known_diagnosis="Adenocarcinoma PD-L1 20%",
            clinician_question="What biomarker data are required before therapy?",
        )
    )
    out = run(state)
    assert out["report"]["citations"]
    assert out["report"]["confidence_score"] > 0
    available = {c["chunk_id"] for c in out["retrieval"]["chunks"]}
    assert set(out["report"]["citations"]).issubset(available)
    assert out["telemetry"]["graph_backend"] == "sequential_phase1"


def test_query_uses_extracted_entities() -> None:
    run = build_onco_graph()
    state = OncoState(
        case=PatientIntake(
            patient_id="T_QUERY",
            primary_site="breast",
            known_diagnosis="ER positive HER2 equivocal",
            clinician_question="What next?",
        )
    )
    out = run(state)
    query = out["telemetry"]["retrieval_query"]
    assert "breast" in query
    assert "HER2" in query or "her2" in query.lower()


def test_pdf_sidecar_pathology_extraction() -> None:
    tmp_path = Path(".oncoedge") / "test_artifacts"
    tmp_path.mkdir(parents=True, exist_ok=True)
    pdf = tmp_path / "pathology.pdf"
    pdf.write_bytes(b"not a real pdf")
    sidecar = tmp_path / "pathology.pdf.txt"
    sidecar.write_text("Invasive ductal carcinoma. ER positive. HER2 2+ equivocal.", encoding="utf-8")
    text, entities, provenance, warnings = parse_pathology_pdfs([str(pdf)])
    assert "ductal carcinoma" in text.lower()
    assert "ER" in entities["biomarkers"]
    assert provenance["pathology"]
