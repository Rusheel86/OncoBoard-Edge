from __future__ import annotations

from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class PatientIntake(BaseModel):
    patient_id: str = Field(min_length=1, description="Local identifier (no PHI).")
    age: Optional[int] = Field(default=None, ge=0, le=130)
    sex: Optional[Literal["female", "male", "intersex", "unknown"]] = None
    primary_site: Optional[str] = Field(default=None, description="Tumor primary site.")
    known_diagnosis: Optional[str] = None
    clinician_question: str = Field(
        min_length=1,
        description="What the clinician wants the system to answer.",
    )
    encounter_date: Optional[date] = None


class ArtifactIndex(BaseModel):
    images: list[str] = Field(default_factory=list, description="Paths to image files.")
    pdfs: list[str] = Field(default_factory=list, description="Paths to PDF files.")
    audios: list[str] = Field(default_factory=list, description="Paths to audio files.")


class ExtractionBundle(BaseModel):
    pathology_text: Optional[str] = None
    pathology_entities: dict[str, Any] = Field(default_factory=dict)
    audio_transcript: Optional[str] = None
    audio_entities: dict[str, Any] = Field(default_factory=dict)
    radiology_summary: Optional[str] = None
    radiology_entities: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(
        default_factory=dict,
        description="Entity-level provenance (page/time/image references).",
    )
    warnings: list[str] = Field(default_factory=list)


class RetrievedChunk(BaseModel):
    doc_id: str
    chunk_id: str
    source_title: str
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceReference(BaseModel):
    chunk_id: str
    source_title: str
    section: Optional[str] = None
    page: Optional[int] = None
    score: Optional[float] = None
    quote: str = Field(default="", description="Short evidence excerpt.")


class RetrievalBundle(BaseModel):
    query: str
    k: int = Field(default=6, ge=1, le=50)
    chunks: list[RetrievedChunk] = Field(default_factory=list)


class OncologyReport(BaseModel):
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    assessment: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
    treatment_considerations: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
    citations: list[str] = Field(
        default_factory=list,
        description="List of chunk_id values used to support claims.",
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence after evidence and modality checks.",
    )
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    evidence_vs_inference: dict[str, list[str]] = Field(
        default_factory=lambda: {"evidence": [], "inference": []}
    )


class OncoState(BaseModel):
    case: PatientIntake
    artifacts: ArtifactIndex = Field(default_factory=ArtifactIndex)
    extractions: ExtractionBundle = Field(default_factory=ExtractionBundle)
    retrieval: Optional[RetrievalBundle] = None
    report: Optional[OncologyReport] = None
    telemetry: dict[str, Any] = Field(default_factory=dict)
