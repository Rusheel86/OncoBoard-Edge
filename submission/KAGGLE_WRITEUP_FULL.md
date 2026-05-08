Title: OncoBoard-Edge — Gemma 4–Powered Evidence-Grounded Oncology Assistant

Subtitle: Deployable, transparent oncology decision support for low-resource clinics, powered by Gemma 4.

Overview

OncoBoard-Edge is an offline-first, evidence-grounded oncology decision support platform that accepts multimodal inputs (pathology/genomic PDFs, radiology images/metadata, clinician voice notes) and produces explainable, structured oncology reports with citations, confidence scores, and uncertainty labels. For the Gemma 4 Good Hackathon this project demonstrates how frontier models can be responsibly deployed to improve clinical decision support while remaining auditable and reproducible.

Demo & Live Link

Live demo: https://rusheel86-oncoboard-edge.hf.space

(Include this live URL in your Kaggle writeup's Project Links and the submission's demo section.)

Problem Statement

Cancer care access is unequal worldwide. Many regional hospitals lack oncology subspecialists and suffer from unreliable connectivity. Clinicians in these settings need tools that provide evidence-backed recommendations without requiring internet access or opaque black-box models.

Our Solution

- Ingest multimodal inputs: DICOM/PNG radiology screenshots, pathology/genomic PDFs, DICOM metadata JSON, and clinician voice notes.
- Extract structured findings from each modality (histology, biomarker panel, TNM staging, symptoms) with provenance (page, timestamp, image id).
- Retrieve top-k evidence chunks from a local ChromaDB (or keyword fallback) containing guidelines, trials, and curated PubMed-style snippets.
- Use Gemma 4 as the primary reasoning engine to correlate radiology + genomics + pathology, generate a structured, explainable report, propose trial suggestions, and label uncertainty and confidence for each claim.
- Present results in a polished Gradio UI with evidence cards and longitudinal comparison.

Key Features

- Evidence grounding: every claim cites source chunk id, source title, page, and a quoted snippet.
- Confidence badges: 🟢 HIGH / 🟡 MEDIUM / 🔴 LOW mapped to calibrated scores.
- Safety gate: flags missing critical inputs (stage, biomarkers, performance status) and prevents unsupported high-confidence recommendations.
- Offline fallback: deterministic generator for reproducible demos when API keys are not available.
- Rapid demos: designed to run on HF Spaces (Gradio) and offline on commodity hardware.

Architecture

- Ingestion: `PathologyParser` (PyMuPDF), `RadiologyAgent` (metadata + optional image embeddings), `AudioTranscriber` (Whisper)
- Retrieval: `ChromaStore` (ChromaDB if available; local keyword fallback otherwise)
- Reasoning: `GemmaManager` (Gemma 4 via Google SDK || Ollama local || offline deterministic fallback)
- Orchestration: LangGraph nodes with explicit provenance and state
- UI: Gradio app (tabs for Clinical Report, Evidence, JSON) with custom CSS and design tokens

Demo Cases

1) NSCLC adjuvant decision — KRAS G12C, PD-L1 18%, Stage IIIA
2) HER2+ neoadjuvant planning — HER2 3+, ER/PR+, Grade 3
3) MSI-H colorectal surveillance vs adjuvant — MSI-H, dMMR

How to Run (Judges)

1. Visit the live demo: https://rusheel86-oncoboard-edge.hf.space
2. Choose a demo case and click Run Analysis
3. Inspect the Clinical Report and Evidence tabs; click evidence cards to view quoted sources
4. Optionally upload a pathology PDF or a voice note and re-run

Files & Reproducibility

- Source code: GitHub repo (linked in Project Links)
- Demo cases: `demo/cases.json`
- Deployment: HF Spaces (Gradio); Dockerfile & docker-compose included for local reproducibility
- Requirements: `requirements.txt`

Ethical Considerations

- Not a medical device; for clinician decision support only
- All recommendations have provenance and confidence; uncertain or unsupported claims are flagged
- No PHI is logged in telemetry by default; secrets are kept out of source (see `.gitignore` and `.env.example`)

Evaluation & Results

- Retrieval quality: top-k retrieval precision measured on synthetic evaluation set (see `eval/retrieval_quality.py`)
- Grounding: groundedness metrics and examples included in `eval/groundedness.py`
- Latency: end-to-end demo runs under 5s on HF Spaces for demo cases with hosted Gemma 4

Attachments & Links

- Repo: https://github.com/Rusheel86/OncoBoard-Edge
- Live demo: https://rusheel86-oncoboard-edge.hf.space
- Paper: `paper/paper.md` (architecture & methods)

Submission Checklist

- [ ] Title & Subtitle provided
- [ ] Live demo URL included (above)
- [ ] Project description (this file)
- [ ] Code link included (GitHub)
- [ ] Media gallery: screenshots (UI tabs), architecture figure, latency benchmark

Notes for Judges

We emphasize transparency and auditability: for any recommendation, judges can click the evidence card to see the exact guideline quote that supported it. Gemma 4 is used for high-quality reasoning; an offline fallback ensures reproducibility. For reproducibility, run the demo without secrets to use the deterministic offline generator.
