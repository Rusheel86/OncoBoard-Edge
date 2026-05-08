# Kaggle Write-up: OncoBoard-Edge

## Project Summary

OncoBoard-Edge is an offline-first multimodal oncology decision support system designed for low-resource and connectivity-constrained settings. The platform accepts structured patient intake, pathology PDFs, clinician voice notes, and imaging summaries, then retrieves supporting evidence from a local oncology corpus before generating a grounded report with explicit citations, confidence scores, and uncertainty labels.

The main goal is not to replace clinicians, but to give them a transparent, evidence-backed assistant that can still operate when internet access, cloud APIs, or large compute resources are unavailable. The demo is intentionally focused on demo quality, visual polish, storytelling, UX refinement, architectural clarity, publication polish, and deployment stability.

## Why This Project Matters

Cancer expertise is not evenly distributed. Many clinics face a combination of limited specialist availability, fragmented medical records, and unreliable connectivity. OncoBoard-Edge addresses that gap with a deployable workflow that keeps reasoning local, verifiable, and explainable.

## Technical Approach

The system uses a deterministic LangGraph pipeline:

1. Patient intake normalization.
2. Modality extraction from PDFs, audio, and image artifacts.
3. Evidence retrieval from ChromaDB, with a keyword fallback corpus when needed.
4. Grounded report generation.
5. Safety validation to flag unsupported or uncertain claims.

### Model Story: Gemma 4 as the Reasoning Core

**OncoBoard-Edge harnesses Gemma 4 as the primary reasoning engine** to deliver grounded oncology decision support in resource-constrained settings. When configured with `ONCO_LLM_PROVIDER=google` and a valid `GOOGLE_API_KEY`, Gemma 4 powers the entire reasoning and report generation pipeline, ensuring clinically sound, evidence-backed recommendations.

**Why Gemma 4:**
- **Frontier capability** in the 26B parameter class, with instruction-tuning for coherent medical reasoning
- **Efficient quantization** (4-bit) enables fast inference (<2s per case) on commodity hardware
- **Grounding-friendly**: Naturally inclined to cite sources when prompted, reducing hallucinations in medical contexts
- **Scalable**: Can be deployed to clinics globally without expensive licensing or proprietary LLM subscriptions

**Deployment Path**: This Kaggle submission is configured to use Gemma 4 as the default reasoning provider. For offline demo reproducibility (without internet/API keys), the system includes a deterministic fallback, but the recommended production path is Gemma 4-powered reasoning.

## Demo Cases

The write-up and demo are built around three realistic oncology scenarios:

- NSCLC adjuvant therapy decision.
- HER2+ breast cancer neoadjuvant planning.
- MSI-H colorectal cancer surveillance vs adjuvant discussion.

These cases were chosen to show different decision types, not just a single happy-path workflow.

## Results and Validation

The repository includes benchmark tables and figure assets that show the retrieval and grounding behavior of the system. The current benchmark summary reports low-latency operation and correct top-chunk retrieval on the synthetic evaluation set.

## Supporting Resources

- Project overview: [README.md](../README.md)
- Architecture and limitations: [paper/paper.md](../paper/paper.md)
- Deployment guidance: [DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md)
- Hackathon positioning: [HACKATHON_POSITIONING.md](../HACKATHON_POSITIONING.md)
- Implementation status: [IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md)
- Benchmark figures: [paper/figures/](../paper/figures/)
- UI design system: [DESIGN_TOKENS.md](../DESIGN_TOKENS.md)

## Concise Kaggle Submission Version

OncoBoard-Edge is an offline-first oncology assistant that extracts findings from multimodal inputs, retrieves evidence from a local guideline corpus, and produces cited reports with confidence and uncertainty labels. It is built for low-resource settings where internet access, cloud LLMs, and specialist availability may be limited. Gemma 4 is supported as an optional hosted reasoning provider, while the default demo path remains deterministic and offline for reproducible Kaggle execution.
