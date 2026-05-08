from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.graph import build_onco_graph
from core.state import OncoState, PatientIntake


OUT_DIR = Path("paper/figures")


CASES = [
    {
        "patient_id": "BENCH_NSCLC",
        "primary_site": "lung",
        "known_diagnosis": "Adenocarcinoma PD-L1 20%",
        "clinician_question": "What biomarker data are required before systemic therapy?",
        "expected": "demo_lung_biomarker_001",
    },
    {
        "patient_id": "BENCH_BREAST",
        "primary_site": "breast",
        "known_diagnosis": "ER positive HER2 equivocal invasive ductal carcinoma",
        "clinician_question": "What biomarker-dependent next steps should be confirmed?",
        "expected": "demo_breast_er_001",
    },
    {
        "patient_id": "BENCH_CRC",
        "primary_site": "colorectal",
        "known_diagnosis": "Colon cancer MSI high KRAS pending",
        "clinician_question": "What biomarker grounding is relevant?",
        "expected": "demo_colorectal_msi_001",
    },
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    retrieval_eval = []
    run = build_onco_graph()

    for case in CASES:
        latencies = []
        for _ in range(3):
            state = OncoState(case=PatientIntake(**{k: v for k, v in case.items() if k != "expected"}))
            started = time.perf_counter()
            out = run(state)
            latencies.append((time.perf_counter() - started) * 1000)
        chunks = out["retrieval"]["chunks"]
        retrieved_ids = [c["chunk_id"] for c in chunks]
        rows.append(
            {
                "case_id": case["patient_id"],
                "latency_ms_mean": round(statistics.mean(latencies), 2),
                "latency_ms_p95": round(sorted(latencies)[-1], 2),
                "confidence": out["report"]["confidence_score"],
                "expected_retrieved": case["expected"] in retrieved_ids,
                "top_chunk": retrieved_ids[0] if retrieved_ids else "",
            }
        )
        retrieval_eval.append({"expected_chunk_ids": [case["expected"]], "retrieved_chunks": chunks})

    with open(OUT_DIR / "benchmark_table.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with open(OUT_DIR / "retrieval_eval.json", "w", encoding="utf-8") as f:
        json.dump(retrieval_eval, f, indent=2)

    _write_latency_svg(rows, OUT_DIR / "latency_benchmark.svg")
    _write_grounding_svg(rows, OUT_DIR / "grounding_matrix.svg")
    _write_summary_md(rows)
    return 0


def _write_latency_svg(rows: list[dict[str, object]], path: Path) -> None:
    width, height = 760, 420
    max_latency = max(float(r["latency_ms_mean"]) for r in rows) or 1.0
    bars = []
    for idx, row in enumerate(rows):
        x = 90 + idx * 190
        bar_h = 260 * float(row["latency_ms_mean"]) / max_latency
        y = 330 - bar_h
        bars.append(f"<rect x='{x}' y='{y:.1f}' width='110' height='{bar_h:.1f}' fill='#2b7a78'/>")
        bars.append(f"<text x='{x + 55}' y='360' text-anchor='middle' font-size='13'>{row['case_id']}</text>")
        bars.append(f"<text x='{x + 55}' y='{y - 8:.1f}' text-anchor='middle' font-size='13'>{row['latency_ms_mean']} ms</text>")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
<rect width='100%' height='100%' fill='#ffffff'/>
<text x='40' y='42' font-size='24' font-family='Arial' fill='#17252a'>Offline Pipeline Latency</text>
<line x1='70' y1='330' x2='700' y2='330' stroke='#334' stroke-width='1'/>
{''.join(bars)}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def _write_grounding_svg(rows: list[dict[str, object]], path: Path) -> None:
    cells = []
    for idx, row in enumerate(rows):
        x = 90 + idx * 170
        fill = "#3aafa9" if row["expected_retrieved"] else "#d95d39"
        label = "hit" if row["expected_retrieved"] else "miss"
        cells.append(f"<rect x='{x}' y='120' width='120' height='120' fill='{fill}'/>")
        cells.append(f"<text x='{x + 60}' y='188' text-anchor='middle' font-size='20' fill='white'>{label}</text>")
        cells.append(f"<text x='{x + 60}' y='270' text-anchor='middle' font-size='13'>{row['case_id']}</text>")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='700' height='340' viewBox='0 0 700 340'>
<rect width='100%' height='100%' fill='#ffffff'/>
<text x='40' y='48' font-size='24' font-family='Arial' fill='#17252a'>Retrieval Grounding Matrix</text>
{''.join(cells)}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def _write_summary_md(rows: list[dict[str, object]]) -> None:
    lines = [
        "# Benchmark Summary",
        "",
        "| Case | Mean latency ms | Expected chunk retrieved | Top chunk |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case_id']} | {row['latency_ms_mean']} | {row['expected_retrieved']} | {row['top_chunk']} |"
        )
    (OUT_DIR / "benchmark_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
