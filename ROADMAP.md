# OncoBoard-Edge — Roadmap

## Stage 1 — Hackathon Demo (Offline-first, publishable baseline)

**Goal:** a polished end-to-end demo that processes PDFs/audio/images and produces a grounded, explainable oncology report with citations from a local ChromaDB store.

- FastAPI endpoints for file upload (PNG/JPG, PDF, WAV).
- Gradio dashboard with:
  - Patient Intake
  - Multimodal Analysis
  - Report Generation
- LangGraph orchestration with mandatory retrieval before reasoning.
- Local ChromaDB ingestion script for guidelines (user-provided PDF/text).
- Evaluation harness for:
  - Groundedness (citation coverage + evidence overlap heuristics)
  - Medical accuracy (expert-annotated subset + rubric)
- Kaggle T4 runtime scripts and memory management patterns.

Deliverable: a runnable repo with a reproducible demo workflow and clear documentation.

## Stage 2 — Research-Grade System (Robust multimodal + quantized edge)

**Goal:** stronger multimodal understanding and efficiency while keeping grounding guarantees.

- Add image embedding pipeline (SigLIP/ViT) with 4-bit quantization (bitsandbytes) where applicable.
- DICOM support (pydicom + basic series handling).
- Better entity extraction for pathology/genomics (regex + lightweight medical NER).
- Automated evidence chaining: multi-hop retrieval and section-aware chunking.
- Improved report schema: staging, biomarkers, contraindications, trial matching hooks.
- Reproducible benchmarks with ablations (retrieval k, chunk sizes, prompt variants).

Deliverable: a manuscript-ready experimental package and model cards.

## Stage 3 — Clinical Pilot (Safety, audit, deployment)

**Goal:** deployable system for low-resource cancer centers with stronger safety and audit features.

- User authentication and role-based access.
- Audit logs (no PHI leakage, configurable retention).
- Local-first storage with optional secure sync.
- Clinical safety guardrails:
  - contraindication checks
  - escalation triggers
  - uncertainty calibration and “needs more information” pathways
- Human-in-the-loop UI for evidence review and editing.

Deliverable: pilot-ready build with operational runbooks and governance documentation.
