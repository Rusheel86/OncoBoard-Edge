from __future__ import annotations

"""Gradio UI for the OncoBoard-Edge oncology demo."""
import json
import os
from typing import Any, Optional

import gradio as gr

from core.graph import build_onco_graph
from core.state import ArtifactIndex, OncoState, PatientIntake


def _ensure_local_path(x: Any) -> Optional[str]:
    if x is None:
        return None
    if isinstance(x, str):
        return x
    p = getattr(x, "name", None)
    return str(p) if p else None


def run_analysis(
    patient_id: str,
    age: Optional[int],
    sex: str,
    primary_site: str,
    known_diagnosis: str,
    clinician_question: str,
    image_files: list[Any],
    pdf_files: list[Any],
    audio_files: list[Any],
) -> tuple[str, str, str]:
    intake = PatientIntake(
        patient_id=patient_id.strip(),
        age=age,
        sex=sex if sex else None,
        primary_site=primary_site.strip() or None,
        known_diagnosis=known_diagnosis.strip() or None,
        clinician_question=clinician_question.strip(),
    )

    artifacts = ArtifactIndex(
        images=[p for p in (_ensure_local_path(f) for f in (image_files or [])) if p],
        pdfs=[p for p in (_ensure_local_path(f) for f in (pdf_files or [])) if p],
        audios=[p for p in (_ensure_local_path(f) for f in (audio_files or [])) if p],
    )

    run = build_onco_graph()
    state = OncoState(case=intake, artifacts=artifacts)
    final_state = OncoState.model_validate(run(state))

    report_json = json.dumps(
        final_state.report.model_dump() if final_state.report else {},
        indent=2,
        ensure_ascii=False,
    )
    retrieval_json = json.dumps(
        final_state.retrieval.model_dump() if final_state.retrieval else {},
        indent=2,
        ensure_ascii=False,
    )
    return _format_report(final_state), retrieval_json, report_json


def _format_report(state: OncoState) -> str:
    """Format OncoState report into beautiful Markdown with confidence badges and styled cards."""
    report = state.report
    if not report:
        return "❌ No report generated. Please check inputs and try again."

    def get_confidence_badge(score: float) -> str:
        """Convert confidence score (0-1) to visual badge."""
        if score >= 0.7:
            return f'<span class="badge badge-high">🟢 HIGH ({score:.2f})</span>'
        elif score >= 0.5:
            return f'<span class="badge badge-medium">🟡 MEDIUM ({score:.2f})</span>'
        else:
            return f'<span class="badge badge-low">🔴 LOW ({score:.2f})</span>'

    def section(title: str, emoji: str, items: list[str]) -> str:
        """Format a section with emoji and title."""
        if not items:
            return f"### {emoji} {title}\n- Not available."
        formatted_items = "\n".join(f"- {item}" for item in items)
        return f"### {emoji} {title}\n{formatted_items}"

    # Evidence cards with styled formatting
    evidence_html = []
    if report.evidence_references:
        for i, ref in enumerate(report.evidence_references, 1):
            loc = f", **p. {ref.page}**" if ref.page else ""
            score_badge = get_confidence_badge(ref.score) if ref.score is not None else ""
            evidence_html.append(
                f'<div class="evidence-card">'
                f'<div class="evidence-source">📄 [{ref.chunk_id}] {ref.source_title}{loc}</div>'
                f'{score_badge}'
                f'<div class="evidence-quote">"{ref.quote}"</div>'
                f"</div>"
            )
    evidence_section = (
        "\n".join(evidence_html) if evidence_html else '<div class="alert-card">No evidence references retrieved.</div>'
    )

    # Red flags with visual styling
    red_flags_html = []
    if report.red_flags:
        for flag in report.red_flags:
            red_flags_html.append(f'<div class="red-flag">{flag}</div>')
    red_flags_section = (
        "\n".join(red_flags_html) if red_flags_html else '<div class="clinical-note">No critical red flags identified.</div>'
    )

    # Uncertainty notes with visual styling
    uncertainty_html = []
    if report.uncertainty_notes:
        for note in report.uncertainty_notes:
            uncertainty_html.append(f'<div class="alert-card">{note}</div>')
    uncertainty_section = "\n".join(uncertainty_html) if uncertainty_html else ""

    # Warnings from extractions
    warnings = "\n".join(f"⚠️ {w}" for w in state.extractions.warnings) or "✓ No extraction warnings."
    telemetry = ", ".join(f"{k}: {v}ms" for k, v in state.telemetry.items() if "ms" in str(k))

    return "\n\n".join(
        [
            f'<div class="header-section">'
            f'<div class="header-title">📋 Oncology Report</div>'
            f'<div class="header-subtitle">Confidence: {get_confidence_badge(report.confidence_score)}</div>'
            f"</div>",
            f"{report.summary}",
            section("Key Findings", "🔬", report.key_findings or []),
            section("Assessment", "📊", report.assessment or []),
            section("Recommended Next Steps", "✓", report.recommended_next_steps or []),
            section("Treatment Considerations", "💊", report.treatment_considerations or []),
            f'<div class="section-divider"></div>\n### 🚨 Red Flags\n{red_flags_section}',
            (f'<div class="section-divider"></div>\n### ⚠️ Uncertainty & Gaps\n{uncertainty_section}' if uncertainty_section else ""),
            f'<div class="section-divider"></div>\n### 📚 Evidence & Citations\n{evidence_section}',
            f"### 📝 Extraction Metadata\n{warnings}",
            f"### ⏱️ Runtime\n{telemetry or 'No telemetry captured.'}",
        ]
    )



def build_ui() -> gr.Blocks:
    """Build OncoBoard-Edge Gradio UI with medical design polish."""
    
    # Load custom CSS
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    custom_css = ""
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            custom_css = f.read()

    # Load demo cases
    demo_cases = []
    demo_json_path = os.path.join(os.path.dirname(__file__), "..", "demo", "cases.json")
    if os.path.exists(demo_json_path):
        with open(demo_json_path, "r") as f:
            demo_data = json.load(f)
            for case in demo_data.get("demo_cases", [])[:3]:
                intake = case.get("patient_intake", {})
                demo_cases.append(
                    [
                        intake.get("patient_id", "CASE_001"),
                        intake.get("age"),
                        intake.get("sex", ""),
                        intake.get("primary_site", ""),
                        intake.get("known_diagnosis", ""),
                        intake.get("clinician_question", ""),
                        None,
                        None,
                        None,
                    ]
                )

    with gr.Blocks(title="OncoBoard-Edge", css=custom_css, theme=gr.themes.Soft()) as demo:
        # Header Section
        gr.Markdown(
            """
            # 🏥 OncoBoard-Edge
            
            **Offline Multimodal Oncology Decision Support Using Quantized Frontier Models**
            
            Evidence-grounded AI for low-resource cancer clinics
            """
        )
        
        gr.Markdown(
            """
            <div class="disclaimer">
            <strong>⚠️ Clinical Decision Support Only</strong><br/>
            Outputs require clinician review and are grounded in retrieved local guidelines. 
            Not intended for autonomous clinical decisions. Always consult with oncology specialists.
            </div>
            """
        )

        # Main Input Section
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown("### 📋 Patient Information")
                patient_id = gr.Textbox(
                    label="Patient ID (no PHI)",
                    value="CASE_001",
                    placeholder="e.g., CASE_001",
                )
                with gr.Row():
                    age = gr.Number(
                        label="Age",
                        value=None,
                        precision=0,
                        minimum=0,
                        maximum=120,
                    )
                    sex = gr.Dropdown(
                        ["", "female", "male", "intersex", "unknown"],
                        label="Sex",
                        value="",
                    )
                with gr.Row():
                    primary_site = gr.Textbox(
                        label="Primary Site",
                        value="lung",
                        placeholder="e.g., lung, breast, colon",
                    )
                    known_diagnosis = gr.Textbox(
                        label="Known Diagnosis",
                        value="Non-small cell lung cancer",
                        placeholder="e.g., adenocarcinoma",
                    )
                
                gr.Markdown("### ❓ Clinical Question")
                clinician_question = gr.Textbox(
                    label="What would you like to know?",
                    value="Summarize key considerations and next steps grounded in local guidelines.",
                    lines=3,
                    placeholder="Describe your clinical question here...",
                )

            with gr.Column(scale=3):
                gr.Markdown("### 📁 Evidence & Media")
                image_files = gr.Files(
                    label="📷 Images",
                    file_types=["image"],
                    file_count="multiple",
                )
                pdf_files = gr.Files(
                    label="📄 Pathology / Genomics PDFs",
                    file_types=[".pdf"],
                    file_count="multiple",
                )
                audio_files = gr.Files(
                    label="🔊 Voice Notes",
                    file_types=["audio"],
                    file_count="multiple",
                )
                
                gr.Markdown("### 🚀 Run Analysis")
                run_btn = gr.Button(
                    "▶️ Run Grounded Analysis",
                    variant="primary",
                    size="lg",
                    scale=1,
                )

        # Output Tabs
        gr.Markdown("---")
        gr.Markdown("## 📊 Analysis Results")
        
        with gr.Tabs():
            with gr.Tab("📋 Clinical Report", id="report"):
                report_view = gr.Markdown()
            
            with gr.Tab("🔬 Evidence & Citations", id="evidence"):
                retrieval_out = gr.Code(
                    label="Retrieved Evidence with Metadata",
                    language="json",
                )
            
            with gr.Tab("📑 Structured Report (JSON)", id="json"):
                report_out = gr.Code(
                    label="Machine-Readable Report Schema",
                    language="json",
                )

        # Demo Cases
        if demo_cases:
            gr.Markdown("---")
            gr.Markdown("## 📚 Demo Cases")
            gr.Markdown(
                "**Try these realistic oncology scenarios to explore the system:**"
            )
            gr.Examples(
                examples=demo_cases,
                inputs=[
                    patient_id,
                    age,
                    sex,
                    primary_site,
                    known_diagnosis,
                    clinician_question,
                    image_files,
                    pdf_files,
                    audio_files,
                ],
                cache_examples=False,
                label="Pre-loaded Demo Cases",
            )
        else:
            # Fallback demo cases if JSON not available
            gr.Markdown("---")
            gr.Markdown("## 📚 Example Cases")
            gr.Examples(
                examples=[
                    [
                        "CASE_NSCLC_001",
                        68,
                        "male",
                        "lung",
                        "Adenocarcinoma, KRAS G12C+, PD-L1 18%",
                        "What is the evidence-based recommendation for adjuvant therapy?",
                        None,
                        None,
                        None,
                    ],
                    [
                        "CASE_BREAST_001",
                        52,
                        "female",
                        "breast",
                        "HER2+ invasive ductal carcinoma, Grade 3",
                        "Is trastuzumab-based neoadjuvant therapy appropriate for this stage?",
                        None,
                        None,
                        None,
                    ],
                    [
                        "CASE_CRC_001",
                        61,
                        "male",
                        "colon",
                        "Adenocarcinoma, MSI-H, Stage IIA",
                        "Do I need adjuvant chemotherapy or can we just watch and wait?",
                        None,
                        None,
                        None,
                    ],
                ],
                inputs=[
                    patient_id,
                    age,
                    sex,
                    primary_site,
                    known_diagnosis,
                    clinician_question,
                    image_files,
                    pdf_files,
                    audio_files,
                ],
                cache_examples=False,
                label="Pre-loaded Demo Cases",
            )

        # Footer
        gr.Markdown(
            """
            ---
            **About OncoBoard-Edge**
            
            • Offline-first: Works without internet or API subscriptions  
            • Grounded reasoning: Every recommendation cites retrieved evidence  
            • Multimodal: Handles pathology PDFs, imaging summaries, clinician voice notes  
            • Transparent: Confidence scores and uncertainty clearly labeled  
            
            [📖 Documentation](https://github.com/) | 
            [📄 Paper](https://github.com/) | 
            [⚠️ Limitations](#)
            """
        )

        # Button Click Handler
        run_btn.click(
            fn=run_analysis,
            inputs=[
                patient_id,
                age,
                sex,
                primary_site,
                known_diagnosis,
                clinician_question,
                image_files,
                pdf_files,
                audio_files,
            ],
            outputs=[report_view, retrieval_out, report_out],
        )

    return demo



if __name__ == "__main__":
    app = build_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False,
        quiet=False,
    )
