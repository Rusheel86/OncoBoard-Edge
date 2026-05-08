# Bugs and Gaps

Date: 2026-05-08

## Post-Repair Resolution Summary

The critical implementation bugs below were repaired in the current pass: the graph now includes all required Phase 1 nodes, optional dependencies are lazy/fallback-safe, offline/local inference is supported, the safety gate validates citation IDs, and uploaded artifacts flow into extraction state. Remaining gaps are mostly research/production hardening items rather than demo-breaking failures.

## Critical Bugs

1. **Graph does not implement required topology**
   - Broken: `core/graph.py` starts at `SourceRetrievalNode`.
   - Why it matters: patient PDFs, audio, and images never influence retrieval or reasoning.
   - Fix: add intake normalization, pathology, audio, radiology, retrieval, reasoning, and safety functions in order.
   - Tradeoff: deterministic Phase 1 extraction will be less capable than full medical NER but much more reliable offline.

2. **Repository cannot import without optional ML dependencies**
   - Broken: `langgraph` and `chromadb` are imported at module import time.
   - Why it matters: UI/API fail in clean demo environments.
   - Fix: lazy imports and fallback execution paths.
   - Tradeoff: fallback graph lacks LangGraph visualization but preserves behavior.

3. **No offline/local inference path**
   - Broken: `GemmaManager()` raises if `GOOGLE_API_KEY` is absent.
   - Why it matters: contradicts offline-first and Kaggle demo goals.
   - Fix: modular providers with hosted, local endpoint, and deterministic offline report provider.
   - Tradeoff: deterministic offline provider is a clinical report generator, not an LLM.

4. **Safety gate only checks that any citation exists**
   - Broken: hallucinated citation IDs pass.
   - Why it matters: unsupported medical recommendations may appear grounded.
   - Fix: verify citations against retrieved chunk IDs and downgrade unsupported sections.
   - Tradeoff: stricter safety may produce more “needs more data” outputs.

5. **Uploaded files are not processed**
   - Broken: UI and API collect file paths but graph ignores them.
   - Why it matters: multimodal requirement is not met.
   - Fix: add PDF extraction, image summary/path provenance, and audio transcript metadata.
   - Tradeoff: Phase 1 audio fallback may use sidecar transcripts if Whisper is unavailable.

## Major Gaps

- No README.
- No tests.
- No Dockerfile or compose file.
- No Hugging Face Spaces entrypoint.
- No paper directory.
- No benchmark figures.
- No sample evidence corpus.
- No section-aware guideline ingestion.
- No PubMed-style metadata.
- No confidence scoring.
- No claim-level evidence support.
- No robust error handling in API/UI.
- No upload size/type controls.
- No model provider abstraction.
- No retry/backoff logic.
- No token budgeting.
- No local quantized inference documentation.

## Dependency Gaps

- `python-multipart` is needed for FastAPI uploads but not explicitly listed.
- `pytest` and `httpx` are needed for tests but not listed.
- `psutil`, `matplotlib`, and `scikit-learn` are needed for benchmark/report figures if used.
- `google-genai` should be considered for current Gemini/Gemma API examples.
- Python 3.13 may be too new for some ML wheels; deployment docs should recommend Python 3.11.

## Documentation Gaps

- No setup quickstart.
- No sample workflow.
- No limitations statement.
- No clinical safety disclaimer in README/UI.
- No RAG corpus ingestion guidance beyond one script.
- No deployment instructions.
- No evaluation methodology.

## Evaluation Gaps

- No retrieval gold set.
- No benchmark data generator.
- No hallucination evaluator.
- No latency/memory measurement.
- No repeatability/consistency test.
- No figures under `paper/figures/`.

## UX Gaps

- Raw JSON remains available for structured inspection, but the polished report tab is now the primary demo view.
- Live demo validation on Hugging Face Spaces is still pending.
- Final screenshots and judge-facing media assets are not yet packaged in one place.
