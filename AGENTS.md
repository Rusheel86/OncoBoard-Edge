# LangGraph Agents & Nodes (OncoBoard-Edge)

This document defines the Phase 1 LangGraph nodes and their responsibilities. The guiding principle is **grounded oncology reasoning**: the model must never produce recommendations without a preceding **source retrieval** step.

## Shared State

All nodes operate on a single shared state object (`OncoState`) containing:

- **`case`**: structured patient inputs and normalized artifacts (image/pdf/audio paths).
- **`extractions`**: extracted findings from each modality with provenance.
- **`retrieval`**: top-k evidence snippets + metadata from ChromaDB.
- **`report`**: the final structured oncology report (validated).
- **`telemetry`**: timings, warnings, and resource usage hints (no PHI logging by default).

## Nodes

### `PatientIntakeNode`

- Validates the intake schema (Pydantic v2).
- Normalizes free text into canonical fields (chief complaint, known diagnosis, site).

### `PathologyParser`

- Input: `pdf_paths`
- Tooling: PyMuPDF
- Output:
  - full extracted text
  - page-indexed text map
  - key entities (tumor site, histology, grade, markers)
  - provenance for each entity (page + span)

### `RadiologyAgent`

- Phase 1 (edge-friendly): captures user-entered imaging findings and stores image paths.
- Phase 2: adds image embedding + summary extraction (SigLIP/ViT).

### `AudioTranscriber`

- Input: `wav_paths`
- Tooling: Whisper
- Output:
  - transcript
  - timestamps
  - extracted symptoms and clinician intent

### `SourceRetrievalNode` (Mandatory)

- Input: extracted entities + clinician question
- Tooling: ChromaDB
- Output: top-k chunks with metadata:
  - `doc_id`, `chunk_id`, `source_title`, `section`, `page`, `score`, `text`

### `OncoReasoningNode`

- Calls Gemma 4 (Google AI Studio via `google-generativeai`).
- Prompt contract:
  - must cite `chunk_id`s
  - must label uncertainty
  - must separate evidence vs inference
- Output: structured JSON report parsed into schemas.

### `SafetyGate`

- Ensures:
  - citations present for claims
  - unsafe/unsupported recommendations are flagged
  - missing evidence triggers a “needs more data” response

## Graph Topology (Phase 1)

`PatientIntakeNode` → parallel(`PathologyParser`, `AudioTranscriber`, `RadiologyAgent`) → `SourceRetrievalNode` → `OncoReasoningNode` → `SafetyGate`

## Determinism & Auditability

- Each node stores its inputs/outputs (paths + hashes, not raw bytes).
- Each reasoning output is accompanied by evidence payloads used to produce it.
