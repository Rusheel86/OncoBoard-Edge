# Full Repository Audit

Date: 2026-05-08

## Executive Summary

OncoBoard-Edge is currently a promising Phase 1 scaffold, not a complete multimodal oncology decision-support platform. The repository defines the intended architecture in `AGENTS.md` and `SYSTEM_ARCHITECTURE.md`, but the implementation only includes a minimal Chroma wrapper, a retrieval-only LangGraph path, a hosted Gemma wrapper, basic upload endpoints, a simple Gradio interface, and two lightweight evaluation scripts.

The most important issue is architectural drift: the documented graph requires `PatientIntakeNode -> parallel(PathologyParser, AudioTranscriber, RadiologyAgent) -> SourceRetrievalNode -> OncoReasoningNode -> SafetyGate`, but the code starts directly at `SourceRetrievalNode`. Uploaded PDFs, audio, and images are never parsed into state before retrieval or reasoning.

## Repository Inventory

| Area | Files | Status |
|---|---:|---|
| Root docs/config | `AGENTS.md`, `SYSTEM_ARCHITECTURE.md`, `ROADMAP.md`, `.env.example`, `.gitignore`, `requirements.txt`, `LICENSE` | Design intent exists, README/deployment docs missing |
| API | `api/main.py`, `api/__init__.py` | Health/upload/analyze endpoints exist; no modality extraction |
| Core | `core/state.py`, `core/graph.py`, `core/chroma_store.py`, `core/llm_manager.py`, `core/__init__.py` | Schemas and minimal retrieval/reasoning exist; graph incomplete |
| UI | `ui/app.py`, `ui/__init__.py` | Gradio demo exists; basic and JSON-heavy |
| Scripts | `scripts/ingest_guidelines.py`, `scripts/kaggle_setup.py` | Ingestion/setup helpers exist; chunking is simplistic |
| Eval | `eval/groundedness.py`, `eval/medical_accuracy.py` | Very lightweight structure/citation checks only |

## Dependency Audit

`requirements.txt` declares a heavy stack: FastAPI, Gradio, LangGraph, ChromaDB, PyMuPDF, Whisper, Torch, Transformers, bitsandbytes, and Google Generative AI.

Local environment check found:

- Installed: `fastapi`, `pydantic`, `gradio`, `pytest`.
- Missing: `chromadb`, `langgraph`, `google-generativeai`, `google-genai`, `PyMuPDF` package metadata, `openai-whisper`.
- Python runtime: 3.13.11. This is a risk for scientific/ML packages that may lag Python 3.13 wheel support.

Findings:

- `api/main.py` and `ui/app.py` import `core.graph`; `core.graph` imports `langgraph` at module import time. Without LangGraph installed, API/UI import fails.
- `core.chroma_store` imports `chromadb` at module import time. Without ChromaDB installed, any graph import fails.
- `scripts.ingest_guidelines` imports `fitz` at module import time. Without PyMuPDF, ingestion script fails even for TXT/MD files.
- `core.llm_manager` requires `GOOGLE_API_KEY` in `__init__`, which prevents offline/local/demo usage.
- Current hosted Gemma code uses `google-generativeai`; official current Gemma API docs show the newer `google-genai` client style and Gemma 4 model IDs such as `gemma-4-26b-a4b-it`.

## Architecture Consistency

Documented architecture:

`PatientIntakeNode -> parallel(PathologyParser, AudioTranscriber, RadiologyAgent) -> SourceRetrievalNode -> OncoReasoningNode -> SafetyGate`

Implemented architecture:

`SourceRetrievalNode -> OncoReasoningNode -> SafetyGate`

Missing or weak components:

- `PatientIntakeNode`: Pydantic validation exists, but no normalization node.
- `PathologyParser`: absent from graph; no PDF parsing during analysis.
- `RadiologyAgent`: absent from graph; image paths are only stored.
- `AudioTranscriber`: absent from graph; no Whisper or fallback transcription path.
- `SourceRetrievalNode`: exists, but queries only the clinician question and ignores extracted entities.
- `OncoReasoningNode`: exists, but has no retry logic, local fallback, robust JSON repair, streaming, async support, or provider abstraction.
- `SafetyGate`: only checks that at least one citation exists; it does not verify that citations correspond to retrieved chunks or support specific claims.

## Environment Variables and Secrets

Current `.env.example`:

- `GOOGLE_API_KEY`
- `HF_TOKEN`
- `WANDB_API_KEY`

Issues:

- No documented model selection variables.
- No offline mode switch.
- No Chroma persistence path override.
- No local inference endpoint variables.
- No API auth or PHI logging policy controls.
- `.env` is ignored, which is correct.
- No hardcoded keys were found.

## Startup and Deployment Audit

Existing startup paths:

- API: `uvicorn api.main:app`
- UI: `python ui/app.py`
- Guideline ingestion: `python scripts/ingest_guidelines.py --path ...`
- Kaggle helper: `python scripts/kaggle_setup.py`

Missing:

- `README.md`
- `Dockerfile`
- `docker-compose.yml`
- Hugging Face Spaces `app.py` or launch docs
- `runtime.txt`
- Kaggle notebook/script entrypoint
- Health checks for retrieval/inference dependencies
- Sample evidence corpus for offline demo
- End-to-end smoke test script

## Security and Privacy Audit

Strengths:

- Secrets are loaded from environment variables.
- `.env` is ignored.
- Upload filenames are not trusted; stored filenames are hash-based.

Weaknesses:

- Upload validation checks only for empty content and filename suffix.
- No max file-size enforcement.
- No MIME/content sniffing.
- No quarantine or malware scanning note.
- No PHI redaction or warning in logs beyond docs.
- `analyze` returns raw exception strings to API clients.
- No auth, rate limiting, CORS policy, or audit log configuration.

## RAG Audit

Current RAG implementation:

- ChromaDB wrapper uses Chroma default embedding behavior.
- Ingestion chunks by character count with overlap after whitespace normalization.
- Metadata includes `doc_id`, `chunk_id`, `source_title`, `page`, and `path`.
- Query uses only `clinician_question`.

Weaknesses:

- No fallback retrieval when ChromaDB is unavailable.
- Chunking is not section-aware.
- No biomedical synonym expansion.
- No biomarker-aware query construction.
- No oncology guideline schema.
- No PubMed-style metadata support.
- No reranking.
- Score interpretation is not normalized.
- Citations are report-level only, not claim-level.
- Safety gate does not check citation validity against retrieved chunks.
- No latency measurement.

## Model and Inference Audit

Current implementation:

- `GemmaManager` wraps Google AI Studio access with `google-generativeai`.
- Uses default model name `gemma-4`.
- Requires `GOOGLE_API_KEY`.

Weaknesses:

- `gemma-4` is not a sufficiently precise model ID for hosted API usage.
- No `google-genai` support.
- No local inference fallback.
- No deterministic offline report fallback.
- No retry/backoff.
- No JSON schema response config.
- No token budgeting.
- No async generation.
- No graceful API failure handling.
- No model/provider configuration through `.env.example`.

## Frontend and UX Audit

Current UI:

- Gradio tabs for intake, uploads, and report generation.
- Outputs raw JSON for report and retrieval.

Weaknesses:

- UI explicitly states Phase 1 files are only tracked by path.
- No formatted report view.
- No visible confidence scoring.
- No evidence cards.
- No loading/status stages.
- No onboarding sample case.
- Minimal visual hierarchy.
- No medical-style summary layout.
- No robust error display.

## Testing Audit

Current state:

- No `tests/` directory.
- No automated tests for schemas, uploads, ingestion, retrieval, safety, API, UI, or deployment.
- Existing eval scripts are standalone CLIs, not tests.

Required additions:

- Unit tests for Pydantic schemas and extraction helpers.
- RAG tests with deterministic local corpus.
- API tests for upload and analysis smoke paths.
- Inference tests using mock providers.
- Deployment smoke tests.

## Evaluation and Benchmark Audit

Current eval:

- Citation coverage heuristic.
- Basic report-structure rubric.

Missing:

- Latency benchmark.
- Memory benchmark.
- Retrieval recall/MRR/nDCG.
- Grounding support check.
- Hallucination check.
- Output consistency evaluation.
- Benchmark data generation.
- Publication-quality plots in `paper/figures/`.

## Paper Materials Audit

Missing:

- `paper/` directory.
- Abstract, introduction, methods, evaluation, limitations, future work.
- Architecture diagram.
- Benchmark figures.
- Citation/reproducibility notes.

## High-Risk Bugs

- API/UI cannot run in an environment missing LangGraph/Chroma/Gemini packages.
- Analysis fails immediately when `GOOGLE_API_KEY` is not set.
- No report can be generated without an already-populated Chroma store.
- Uploaded PDFs/audio/images do not affect the report.
- Chroma wrapper calls `self._client.persist()`, which is not available in all ChromaDB versions.
- `OncoState.model_validate(out)` may fail depending on LangGraph return shape and typed state handling.
- Safety gate accepts unsupported claims if the model emits any citation string.

## Overall Verdict

The repository is a good concept scaffold but does not yet meet hackathon finalist, deployment, or publication-readiness claims. The next implementation pass should prioritize:

1. Import-safe optional dependencies.
2. Complete deterministic graph nodes for intake, PDF, audio, image, retrieval, reasoning, and safety.
3. Offline/local fallbacks for demo reliability.
4. Stronger RAG chunking, metadata, citation validation, and evaluation.
5. Polished Gradio report and evidence UI.
6. Tests, deployment files, benchmark scripts, and paper materials.
