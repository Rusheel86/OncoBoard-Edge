from __future__ import annotations

import json
import re
import time
from typing import Any, Callable, Dict, Optional

from .chroma_store import ChromaStore
from .extractors import (
    build_query,
    normalize_intake,
    parse_pathology_pdfs,
    summarize_radiology,
    transcribe_audio,
)
from .llm_manager import GemmaManager
from .state import (
    EvidenceReference,
    ExtractionBundle,
    OncologyReport,
    OncoState,
    RetrievalBundle,
    RetrievedChunk,
)


def _build_reasoning_prompt(state: OncoState) -> str:
    chunks = state.retrieval.chunks if state.retrieval else []
    evidence = "\n\n".join(
        [
            (
                f"[{c.chunk_id}] source_title={c.source_title} "
                f"section={c.metadata.get('section', '')} page={c.metadata.get('page', '')} "
                f"score={c.score}\n{c.text}"
            )
            for c in chunks
        ]
    )
    case = state.case.model_dump(mode="json")
    extractions = state.extractions.model_dump(mode="json")

    return (
        "You are an oncology assistant for clinical decision support.\n"
        "Constraints:\n"
        "- Source retrieval has already been performed; only use the evidence snippets provided.\n"
        "- If evidence is insufficient, say what information is missing.\n"
        "- Cite evidence using exact chunk ids like [demo_safety_001].\n"
        "- Separate evidence from inference.\n"
        "- Include confidence_score from 0.0 to 1.0.\n"
        "- Produce JSON that matches the OncologyReport schema.\n\n"
        f"PATIENT_CASE_JSON:\n{json.dumps(case, ensure_ascii=False)}\n\n"
        f"EXTRACTIONS_JSON:\n{json.dumps(extractions, ensure_ascii=False)}\n\n"
        f"EVIDENCE_SNIPPETS:\n{evidence}\n\n"
        "Return ONLY valid JSON."
    )


def patient_intake_node(state: OncoState) -> OncoState:
    started = time.perf_counter()
    case = normalize_intake(state.case)
    telemetry = dict(state.telemetry)
    telemetry["PatientIntakeNode_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return state.model_copy(update={"case": case, "telemetry": telemetry})


def pathology_parser_node(state: OncoState) -> OncoState:
    started = time.perf_counter()
    text, entities, provenance, warnings = parse_pathology_pdfs(state.artifacts.pdfs)
    extractions = state.extractions.model_copy(
        update={
            "pathology_text": text or state.extractions.pathology_text,
            "pathology_entities": entities,
            "provenance": {**state.extractions.provenance, **provenance},
            "warnings": [*state.extractions.warnings, *warnings],
        }
    )
    telemetry = dict(state.telemetry)
    telemetry["PathologyParser_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return state.model_copy(update={"extractions": extractions, "telemetry": telemetry})


def audio_transcriber_node(state: OncoState) -> OncoState:
    started = time.perf_counter()
    transcript, entities, provenance, warnings = transcribe_audio(state.artifacts)
    extractions = state.extractions.model_copy(
        update={
            "audio_transcript": transcript or state.extractions.audio_transcript,
            "audio_entities": entities,
            "provenance": {**state.extractions.provenance, **provenance},
            "warnings": [*state.extractions.warnings, *warnings],
        }
    )
    telemetry = dict(state.telemetry)
    telemetry["AudioTranscriber_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return state.model_copy(update={"extractions": extractions, "telemetry": telemetry})


def radiology_agent_node(state: OncoState) -> OncoState:
    started = time.perf_counter()
    summary, entities, provenance, warnings = summarize_radiology(state.artifacts)
    extractions = state.extractions.model_copy(
        update={
            "radiology_summary": summary or state.extractions.radiology_summary,
            "radiology_entities": entities,
            "provenance": {**state.extractions.provenance, **provenance},
            "warnings": [*state.extractions.warnings, *warnings],
        }
    )
    telemetry = dict(state.telemetry)
    telemetry["RadiologyAgent_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return state.model_copy(update={"extractions": extractions, "telemetry": telemetry})


def source_retrieval_node(state: OncoState, *, chroma: ChromaStore, retrieval_k: int) -> OncoState:
    started = time.perf_counter()
    query = build_query(state.case, state.extractions)
    docs, metas, scores = chroma.query(query_text=query, k=retrieval_k)

    chunks: list[RetrievedChunk] = []
    for i, (doc, meta, score) in enumerate(zip(docs, metas, scores, strict=False)):
        meta = meta or {}
        chunks.append(
            RetrievedChunk(
                doc_id=str(meta.get("doc_id", meta.get("source", "unknown"))),
                chunk_id=str(meta.get("chunk_id", f"chunk_{i:03d}")),
                source_title=str(meta.get("source_title", meta.get("source", "local"))),
                text=str(doc),
                score=float(score),
                metadata=dict(meta),
            )
        )

    telemetry = dict(state.telemetry)
    telemetry["SourceRetrievalNode_ms"] = round((time.perf_counter() - started) * 1000, 2)
    telemetry["retrieval_query"] = query
    return state.model_copy(
        update={"retrieval": RetrievalBundle(query=query, k=retrieval_k, chunks=chunks), "telemetry": telemetry}
    )


def onco_reasoning_node(state: OncoState, *, llm: GemmaManager) -> OncoState:
    started = time.perf_counter()
    prompt = _build_reasoning_prompt(state)
    generation = llm.generate(prompt=prompt)
    report = _parse_report(generation.text)
    if report is None:
        fallback = GemmaManager(provider="offline").generate(prompt=prompt)
        report = _parse_report(fallback.text)
        if report is None:
            raise RuntimeError("Reasoning provider returned invalid report JSON.")

    telemetry = dict(state.telemetry)
    telemetry["OncoReasoningNode_ms"] = round((time.perf_counter() - started) * 1000, 2)
    telemetry["llm_provider"] = llm.provider
    telemetry["llm_model"] = llm.model_name
    return state.model_copy(update={"report": report, "telemetry": telemetry})


def safety_gate_node(state: OncoState) -> OncoState:
    started = time.perf_counter()
    if not state.retrieval or not state.retrieval.chunks:
        raise RuntimeError("Retrieval returned no evidence; cannot produce a report.")
    if not state.report:
        raise RuntimeError("Missing report output from reasoning node.")

    available = {c.chunk_id: c for c in state.retrieval.chunks}
    valid_citations = [c for c in state.report.citations if c in available]
    uncertainty = list(state.report.uncertainty_notes)
    confidence = state.report.confidence_score

    if len(valid_citations) < len(state.report.citations):
        dropped = sorted(set(state.report.citations) - set(valid_citations))
        uncertainty.append(f"SafetyGate removed unsupported citation ids: {', '.join(dropped)}.")
        confidence = min(confidence, 0.55)

    if not valid_citations:
        valid_citations = [state.retrieval.chunks[0].chunk_id]
        uncertainty.append("SafetyGate inserted top retrieved evidence citation because report citations were missing or invalid.")
        confidence = min(confidence or 0.4, 0.4)

    refs = []
    for chunk_id in valid_citations:
        chunk = available[chunk_id]
        refs.append(
            EvidenceReference(
                chunk_id=chunk.chunk_id,
                source_title=chunk.source_title,
                section=chunk.metadata.get("section"),
                page=_coerce_int(chunk.metadata.get("page")),
                score=chunk.score,
                quote=chunk.text[:320],
            )
        )

    report = state.report.model_copy(
        update={
            "citations": valid_citations,
            "uncertainty_notes": uncertainty,
            "confidence_score": confidence,
            "evidence_references": refs,
        }
    )
    telemetry = dict(state.telemetry)
    telemetry["SafetyGate_ms"] = round((time.perf_counter() - started) * 1000, 2)
    telemetry["grounded_citation_count"] = len(valid_citations)
    return state.model_copy(update={"report": report, "telemetry": telemetry})


def build_onco_graph(
    *,
    chroma: Optional[ChromaStore] = None,
    llm: Optional[GemmaManager] = None,
    retrieval_k: int = 6,
) -> Callable[[OncoState], Dict[str, Any]]:
    chroma = chroma or ChromaStore()
    llm = llm or GemmaManager()

    def run(state: OncoState) -> Dict[str, Any]:
        current = patient_intake_node(state)
        current = pathology_parser_node(current)
        current = audio_transcriber_node(current)
        current = radiology_agent_node(current)
        current = source_retrieval_node(current, chroma=chroma, retrieval_k=retrieval_k)
        current = onco_reasoning_node(current, llm=llm)
        current = safety_gate_node(current)
        telemetry = dict(current.telemetry)
        telemetry["graph_backend"] = "sequential_phase1"
        current = current.model_copy(update={"telemetry": telemetry})
        return current.model_dump(mode="json")

    return run


def _parse_report(text: str) -> OncologyReport | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    try:
        return OncologyReport.model_validate(data)
    except Exception:
        return None


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except Exception:
        return None
