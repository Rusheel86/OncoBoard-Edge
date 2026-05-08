# W&B Media Gallery Plan

This document organizes the media assets that should appear in a Weights & Biases report or media gallery for the OncoBoard-Edge submission.

## Purpose

The gallery should show that the project is not just a model demo, but a reproducible system with measurable grounding, retrieval quality, and low-latency behavior.

## Suggested W&B Sections

### 1. Project Overview
- Short description of the system.
- One-line summary: offline-first multimodal oncology decision support with grounded citations.
- Link to the live demo and repository.

### 2. Benchmark Graphs
Use the existing figures in `paper/figures/` as the canonical sources:

- `paper/figures/latency_benchmark.svg`
- `paper/figures/grounding_matrix.svg`
- `paper/figures/retrieval_eval.json`
- `paper/figures/benchmark_table.csv`
- `paper/figures/benchmark_summary.md`

Recommended captions:
- Latency benchmark: show the end-to-end latency for the three demo cases.
- Grounding matrix: show whether the expected source chunk was retrieved.
- Retrieval eval: show the ranking and retrieval quality summary.
- Benchmark table: show the compact metric view for judges.

### 3. UI Screenshots
Add screenshots of the polished Gradio interface:
- Clinical report tab.
- Evidence and citations tab.
- Structured JSON tab.
- Mobile width screenshot for responsiveness.

### 4. Demo Case Cards
Add a media panel for each synthetic case:
- NSCLC_01
- BREAST_01
- CRC_01

Each card should include:
- Patient summary
- Clinical question
- Confidence badge snapshot
- A representative evidence card

### 5. Architecture Graphic
Use the architecture diagram from the paper folder or export a W&B-friendly version of the same flow:
- Intake
- Extraction
- Retrieval
- Reasoning
- Safety gate
- Final report

## W&B Logging Notes

If W&B logging is enabled, the media should be attached as artifacts or report panels with stable names so updates are easy to compare across runs. A practical naming pattern is:

- `oncoboard/latency_benchmark`
- `oncoboard/grounding_matrix`
- `oncoboard/retrieval_eval`
- `oncoboard/ui_clinical_report`
- `oncoboard/ui_evidence_tab`
- `oncoboard/ui_json_tab`
- `oncoboard/architecture`

## Copy for the Report Header

**OncoBoard-Edge** is an offline-first multimodal oncology assistant that retrieves local evidence before reasoning, then generates cited and confidence-labeled reports for clinicians working in constrained environments.

## Supporting Links

- Repository: [README.md](../README.md)
- Paper: [paper/paper.md](../paper/paper.md)
- Benchmarks: [paper/figures/](../paper/figures/)
- Deployment: [DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md)
- Positioning: [HACKATHON_POSITIONING.md](../HACKATHON_POSITIONING.md)
