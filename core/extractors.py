from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from .state import ArtifactIndex, ExtractionBundle, PatientIntake


BIOMARKER_PATTERNS: dict[str, str] = {
    "ER": r"\bER\b[^.;,\n]*(positive|negative|\d+%)?",
    "PR": r"\bPR\b[^.;,\n]*(positive|negative|\d+%)?",
    "HER2": r"\bHER[- ]?2\b[^.;,\n]*(positive|negative|0|1\+|2\+|3\+|amplified|non[- ]?amplified)?",
    "EGFR": r"\bEGFR\b[^.;,\n]*(mutated|wild[- ]?type|exon\s*\d+)?",
    "ALK": r"\bALK\b[^.;,\n]*(positive|negative|rearranged)?",
    "ROS1": r"\bROS1\b[^.;,\n]*(positive|negative|rearranged)?",
    "KRAS": r"\bKRAS\b[^.;,\n]*(mutated|wild[- ]?type|G12C|G12D)?",
    "BRAF": r"\bBRAF\b[^.;,\n]*(mutated|V600E|wild[- ]?type)?",
    "MSI": r"\bMSI\b[^.;,\n]*(high|stable|low)?",
    "PD-L1": r"\bPD[- ]?L1\b[^.;,\n]*(\d+%|positive|negative|TPS)?",
}

HISTOLOGY_TERMS = [
    "adenocarcinoma",
    "squamous cell carcinoma",
    "ductal carcinoma",
    "lobular carcinoma",
    "small cell carcinoma",
    "melanoma",
    "sarcoma",
    "lymphoma",
]

SYMPTOM_TERMS = [
    "pain",
    "bleeding",
    "weight loss",
    "fever",
    "cough",
    "dyspnea",
    "fatigue",
    "nausea",
    "vomiting",
    "dysphagia",
]


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize_intake(case: PatientIntake) -> PatientIntake:
    data = case.model_dump()
    for key in ("primary_site", "known_diagnosis", "clinician_question"):
        if isinstance(data.get(key), str):
            data[key] = " ".join(data[key].split())
    if isinstance(data.get("patient_id"), str):
        data["patient_id"] = data["patient_id"].strip()
    return PatientIntake.model_validate(data)


def extract_entities(text: str) -> dict[str, Any]:
    lowered = text.lower()
    biomarkers: dict[str, str] = {}
    for name, pattern in BIOMARKER_PATTERNS.items():
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            biomarkers[name] = m.group(0).strip()

    histology = [term for term in HISTOLOGY_TERMS if term in lowered]
    grade = None
    grade_match = re.search(r"\bgrade\s*(1|2|3|I|II|III|low|intermediate|high)\b", text, re.I)
    if grade_match:
        grade = grade_match.group(0)

    stage = None
    stage_match = re.search(r"\bstage\s*(0|I{1,3}|IV|[1-4][A-C]?)\b", text, re.I)
    if stage_match:
        stage = stage_match.group(0)

    symptoms = [term for term in SYMPTOM_TERMS if term in lowered]

    return {
        "biomarkers": biomarkers,
        "histology": histology,
        "grade": grade,
        "stage": stage,
        "symptoms": symptoms,
    }


def _sidecar_text(path: Path) -> str | None:
    for suffix in (".txt", ".md", ".json"):
        candidate = path.with_suffix(path.suffix + suffix)
        if candidate.exists():
            if candidate.suffix == ".json":
                obj = json.loads(candidate.read_text(encoding="utf-8"))
                return str(obj.get("transcript") or obj.get("text") or obj)
            return candidate.read_text(encoding="utf-8", errors="ignore")
    return None


def parse_pathology_pdfs(pdf_paths: list[str]) -> tuple[str, dict[str, Any], dict[str, Any], list[str]]:
    texts: list[str] = []
    page_map: dict[str, dict[int, str]] = {}
    provenance: dict[str, Any] = {"pathology": []}
    warnings: list[str] = []

    try:
        import fitz  # type: ignore
    except Exception as e:
        fitz = None
        warnings.append(f"PyMuPDF unavailable; using sidecar text only for PDFs ({e}).")

    for raw_path in pdf_paths:
        path = Path(raw_path)
        if not path.exists():
            warnings.append(f"PDF not found: {path}")
            continue

        digest = file_sha256(path)
        if fitz is None:
            sidecar = _sidecar_text(path)
            if sidecar:
                texts.append(sidecar)
                page_map[str(path)] = {1: sidecar}
                provenance["pathology"].append({"path": str(path), "sha256": digest, "source": "sidecar"})
            continue

        try:
            doc = fitz.open(path)
            per_page: dict[int, str] = {}
            for page_idx in range(doc.page_count):
                page_text = doc.load_page(page_idx).get_text("text")
                per_page[page_idx + 1] = page_text
                if page_text.strip():
                    texts.append(page_text)
            doc.close()
            page_map[str(path)] = per_page
            provenance["pathology"].append({"path": str(path), "sha256": digest, "pages": len(per_page)})
        except Exception as e:
            sidecar = _sidecar_text(path)
            if sidecar:
                texts.append(sidecar)
                page_map[str(path)] = {1: sidecar}
                provenance["pathology"].append({"path": str(path), "sha256": digest, "source": "sidecar_after_pdf_error"})
                warnings.append(f"Failed to parse PDF {path}; used sidecar transcript instead ({e}).")
            else:
                warnings.append(f"Failed to parse PDF {path}: {e}")

    full_text = "\n\n".join(t.strip() for t in texts if t.strip())
    entities = extract_entities(full_text) if full_text else {}
    entities["page_map"] = page_map
    return full_text, entities, provenance, warnings


def summarize_radiology(artifacts: ArtifactIndex) -> tuple[str, dict[str, Any], dict[str, Any], list[str]]:
    summaries: list[str] = []
    provenance: dict[str, Any] = {"radiology": []}
    warnings: list[str] = []

    for raw_path in artifacts.images:
        path = Path(raw_path)
        if not path.exists():
            warnings.append(f"Image not found: {path}")
            continue
        digest = file_sha256(path)
        sidecar = _sidecar_text(path)
        label = sidecar.strip() if sidecar else f"Image uploaded for clinician review: {path.name}"
        summaries.append(label)
        provenance["radiology"].append({"path": str(path), "sha256": digest, "summary_source": "sidecar" if sidecar else "path"})

    text = "\n".join(summaries)
    return text, extract_entities(text) if text else {}, provenance, warnings


def transcribe_audio(artifacts: ArtifactIndex) -> tuple[str, dict[str, Any], dict[str, Any], list[str]]:
    transcripts: list[str] = []
    provenance: dict[str, Any] = {"audio": []}
    warnings: list[str] = []
    use_whisper = os.getenv("ONCO_USE_WHISPER", "0").lower() in {"1", "true", "yes"}
    whisper_model = None

    if use_whisper:
        try:
            import whisper  # type: ignore

            whisper_model = whisper.load_model(os.getenv("ONCO_WHISPER_MODEL", "base"))
        except Exception as e:
            warnings.append(f"Whisper unavailable; using sidecar transcripts only ({e}).")

    for raw_path in artifacts.audios:
        path = Path(raw_path)
        if not path.exists():
            warnings.append(f"Audio not found: {path}")
            continue
        digest = file_sha256(path)
        transcript = _sidecar_text(path)
        source = "sidecar"
        if transcript is None and whisper_model is not None:
            try:
                result = whisper_model.transcribe(str(path))
                transcript = str(result.get("text", ""))
                source = "whisper"
            except Exception as e:
                warnings.append(f"Whisper transcription failed for {path}: {e}")
        if transcript:
            transcripts.append(transcript)
            provenance["audio"].append({"path": str(path), "sha256": digest, "source": source})
        else:
            warnings.append(f"No transcript available for {path}; add a .txt sidecar or enable Whisper.")

    text = "\n".join(t.strip() for t in transcripts if t.strip())
    return text, extract_entities(text) if text else {}, provenance, warnings


def build_query(case: PatientIntake, extractions: ExtractionBundle) -> str:
    terms: list[str] = [case.clinician_question]
    for value in (case.primary_site, case.known_diagnosis):
        if value:
            terms.append(value)
    for entity_block in (
        extractions.pathology_entities,
        extractions.audio_entities,
        extractions.radiology_entities,
    ):
        if not entity_block:
            continue
        for key in ("histology", "symptoms"):
            values = entity_block.get(key) or []
            if isinstance(values, list):
                terms.extend(str(v) for v in values)
        biomarkers = entity_block.get("biomarkers") or {}
        if isinstance(biomarkers, dict):
            terms.extend(f"{k} {v}" for k, v in biomarkers.items())
        for key in ("grade", "stage"):
            if entity_block.get(key):
                terms.append(str(entity_block[key]))
    return " ".join(dict.fromkeys(t for t in terms if t))
