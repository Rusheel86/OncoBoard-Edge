# OncoBoard-Edge — System Architecture

**Tagline:** Offline Multimodal Oncology Intelligence for Low-Resource Cancer Centers

OncoBoard-Edge is an offline-first multimodal oncology assistant that runs in constrained environments (e.g., Kaggle T4 16GB VRAM) while maintaining **clinical explainability** through mandatory **evidence retrieval** from a local guideline store (ChromaDB). The UI layer is implemented with Gradio plus a custom medical design system so the clinician-facing experience stays readable, credible, and demo-ready.

## Design Goals

- **Grounded reasoning**: every model insight must include retrieved evidence snippets and citations (document id + chunk id + page/time range).
- **Edge efficiency**: minimize VRAM/CPU usage, explicitly release memory, and keep data local by default.
- **Modularity**: independent modules for ingestion (image/PDF/audio), retrieval, and reasoning orchestrated by LangGraph.
- **Auditability**: structured outputs suitable for clinical review, with provenance for each claim.

## High-Level Flow

1. **Ingestion**
   - **Images**: DICOM (Phase 2) / PNG/JPEG (Phase 1) → preprocessed → image embeddings.
   - **PDF reports**: pathology/genomic PDFs → text + page mapping via PyMuPDF.
   - **Audio**: voice notes → transcript + timestamps via Whisper.

2. **Normalization**
   - Convert all modalities into a unified `PatientCase` bundle: patient metadata, symptoms, staging elements, extracted findings, and raw artifacts (paths + hashes).
   - Maintain **provenance**: for every extracted element store where it came from (PDF page, audio time range, image filename/series).

3. **Retrieval (Mandatory for Every Answer)**
   - Query a **local ChromaDB** collection containing:
     - NCCN/ESMO-style guidelines (user-provided)
     - local institution protocols
     - curated snippets (tumor boards, pathways)
   - Retrieval returns top-k chunks with metadata (source, section, page).

4. **Multimodal Fusion Strategy**
   - **Late fusion** for robustness on the edge:
     - Image/PDF/audio are processed into **textual summaries** + embeddings.
     - The reasoning model (Gemma 4 when hosted via Google AI Studio, or the deterministic offline fallback by default) receives:
       - the structured `PatientCase` summary
       - retrieved evidence chunks
       - explicit instruction to cite evidence and avoid unsupported claims
   - This avoids needing to keep large multimodal models resident in VRAM during the full session while preserving a reproducible demo path.

5. **Reasoning & Report Generation**
   - Gemma 4 produces a structured report with:
     - differential diagnosis (if applicable)
     - staging hypothesis with uncertainty
     - recommended next tests
     - treatment options (guideline-grounded)
     - red flags / urgent escalations
     - citations (retrieval chunk ids)
   - Output is validated against **Pydantic v2** schemas.

## LangGraph Orchestration (Stateful)

LangGraph orchestrates the workflow as a deterministic state machine:

- **`PathologyParser`**: extracts report text, key entities, and provenance.
- **`RadiologyAgent`**: extracts imaging findings summary (Phase 1: metadata + user-entered findings; Phase 2: image embeddings).
- **`AudioTranscriber`**: transcribes clinician notes, extracts key symptoms, and timestamps.
- **`SourceRetrievalNode`**: queries ChromaDB based on extracted entities and questions.
- **`OncoReasoningNode`**: calls Gemma 4 with evidence + patient context, returns structured report.
- **`SafetyGate`**: enforces grounding, checks missing citations, and flags uncertain outputs.

## Edge Efficiency Tactics (Kaggle T4)

- Use `contextlib.ExitStack()` to ensure files, temp dirs, and GPU resources are released.
- Use explicit `gc.collect()` and (when available) `torch.cuda.empty_cache()` after heavy steps.
- Keep embeddings compact (float16 where possible).
- Prefer **4-bit quantization** for local embedding models when used (bitsandbytes).
- Store artifacts on disk and pass **paths + hashes** through the graph state rather than raw bytes.

## Security Model

- Secrets are loaded via `python-dotenv` and accessed only through `os.getenv(...)`.
- API access is restricted to `GOOGLE_API_KEY` for Gemma 4 calls; no hardcoded secrets.
- `.env` is ignored by git; provide `.env.example` for onboarding.

## Deployment Shapes

- **Offline-first demo**: local ChromaDB + Gradio UI + FastAPI endpoints.
- **Clinical pilot**: same architecture, with stronger audit logs, user auth, and local on-prem sync mechanisms (future phase).
- **Presentation layer**: custom CSS tokens for confidence badges, evidence cards, red-flag alerts, and responsive layouts so the live demo reads like a polished clinical tool rather than a generic app.
