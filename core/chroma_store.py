from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class ChromaConfig:
    persist_dir: str = os.getenv("ONCO_CHROMA_DIR", "chroma_db")
    collection_name: str = os.getenv("ONCO_CHROMA_COLLECTION", "oncoboard_guidelines")


DEFAULT_ONCOLOGY_EVIDENCE: list[dict[str, Any]] = [
    {
        "id": "demo_breast_er_001",
        "text": "For hormone receptor positive breast cancer, endocrine therapy is a core systemic treatment consideration. HER2 status, menopausal status, disease stage, recurrence risk, and patient comorbidities should guide regimen selection.",
        "metadata": {
            "doc_id": "demo_guideline_breast",
            "chunk_id": "demo_breast_er_001",
            "source_title": "Demo Oncology Guideline Corpus",
            "section": "Breast biomarkers",
            "page": 1,
            "source_type": "guideline",
        },
    },
    {
        "id": "demo_breast_her2_001",
        "text": "HER2 positive breast cancer generally requires evaluation for anti-HER2 therapy eligibility. Discordant or equivocal HER2 testing should be resolved with validated repeat or reflex testing before treatment decisions.",
        "metadata": {
            "doc_id": "demo_guideline_breast",
            "chunk_id": "demo_breast_her2_001",
            "source_title": "Demo Oncology Guideline Corpus",
            "section": "HER2 interpretation",
            "page": 2,
            "source_type": "guideline",
        },
    },
    {
        "id": "demo_lung_biomarker_001",
        "text": "For advanced non-small cell lung cancer, actionable biomarker testing commonly includes EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS G12C, and PD-L1 where available. Treatment selection should wait for critical driver results when clinically feasible.",
        "metadata": {
            "doc_id": "demo_guideline_lung",
            "chunk_id": "demo_lung_biomarker_001",
            "source_title": "Demo Oncology Guideline Corpus",
            "section": "NSCLC biomarkers",
            "page": 3,
            "source_type": "guideline",
        },
    },
    {
        "id": "demo_colorectal_msi_001",
        "text": "In colorectal cancer, mismatch repair or MSI testing supports Lynch syndrome screening and may guide immunotherapy decisions in advanced disease. RAS and BRAF status are important for targeted therapy planning.",
        "metadata": {
            "doc_id": "demo_guideline_colorectal",
            "chunk_id": "demo_colorectal_msi_001",
            "source_title": "Demo Oncology Guideline Corpus",
            "section": "Colorectal biomarkers",
            "page": 4,
            "source_type": "guideline",
        },
    },
    {
        "id": "demo_safety_001",
        "text": "When key staging, pathology, performance status, organ function, or biomarker data are missing, an oncology decision-support system should label uncertainty and recommend obtaining the missing data rather than presenting unsupported treatment recommendations.",
        "metadata": {
            "doc_id": "demo_safety",
            "chunk_id": "demo_safety_001",
            "source_title": "Demo Oncology Safety Notes",
            "section": "Grounding and uncertainty",
            "page": 1,
            "source_type": "safety",
        },
    },
    {
        "id": "demo_pubmed_grounding_001",
        "text": "PubMed-style evidence abstracts should be represented with title, year, study type, population, intervention or marker, endpoint, and limitations so downstream reasoning can separate direct evidence from clinical inference.",
        "metadata": {
            "doc_id": "demo_pubmed_style",
            "chunk_id": "demo_pubmed_grounding_001",
            "source_title": "Demo PubMed-style Retrieval Schema",
            "section": "Evidence metadata",
            "page": 1,
            "source_type": "pubmed_style",
        },
    },
]


class ChromaStore:
    """
    Local vector store wrapper.

    In Phase 1 we default to Chroma's built-in embedding function (network-free).
    Phase 2 can swap in domain-specific embedding models (SigLIP/biomed models)
    while keeping the same retrieval contract.
    """

    def __init__(self, config: Optional[ChromaConfig] = None) -> None:
        self.config = config or ChromaConfig()
        os.makedirs(self.config.persist_dir, exist_ok=True)
        self._fallback_records: list[dict[str, Any]] = []
        self._fallback_path = Path(self.config.persist_dir) / "fallback_records.jsonl"
        self._client = None
        self._collection = None

        try:
            import chromadb  # type: ignore

            self._client = chromadb.PersistentClient(path=self.config.persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.config.collection_name
            )
        except Exception:
            self._load_fallback_records()

    @property
    def collection_name(self) -> str:
        return self.config.collection_name

    def add_texts(
        self,
        *,
        ids: list[str],
        texts: list[str],
        metadatas: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        if len(ids) != len(texts):
            raise ValueError("ids and texts must have the same length")
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError("metadatas must match texts length when provided")

        if self._collection is not None:
            self._collection.add(ids=ids, documents=texts, metadatas=metadatas)
            persist = getattr(self._client, "persist", None)
            if callable(persist):
                persist()
            return

        metadatas = metadatas or [{} for _ in texts]
        for item_id, text, meta in zip(ids, texts, metadatas, strict=True):
            record = {"id": item_id, "text": text, "metadata": dict(meta or {})}
            record["metadata"].setdefault("chunk_id", item_id)
            self._fallback_records.append(record)
        self._save_fallback_records()

    def query(
        self, *, query_text: str, k: int = 6
    ) -> tuple[list[str], list[dict[str, Any]], list[float]]:
        if self._collection is not None and self._collection.count() > 0:
            res = self._collection.query(query_texts=[query_text], n_results=k)
            docs = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]
            dists = (res.get("distances") or [[]])[0]
            return docs, metas, dists

        records = self._fallback_records or DEFAULT_ONCOLOGY_EVIDENCE
        ranked = sorted(
            records,
            key=lambda r: self._keyword_score(query_text, str(r.get("text", ""))),
            reverse=True,
        )[:k]
        docs = [str(r["text"]) for r in ranked]
        metas = [dict(r.get("metadata") or {"chunk_id": r.get("id")}) for r in ranked]
        scores = [self._keyword_score(query_text, str(r.get("text", ""))) for r in ranked]
        return docs, metas, scores

    def count(self) -> int:
        if self._collection is not None:
            return int(self._collection.count())
        return len(self._fallback_records)

    def _load_fallback_records(self) -> None:
        if not self._fallback_path.exists():
            self._fallback_records = []
            return
        records: list[dict[str, Any]] = []
        for line in self._fallback_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                import json

                records.append(json.loads(line))
        self._fallback_records = records

    def _save_fallback_records(self) -> None:
        import json

        self._fallback_path.parent.mkdir(parents=True, exist_ok=True)
        self._fallback_path.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in self._fallback_records),
            encoding="utf-8",
        )

    @staticmethod
    def _keyword_score(query: str, text: str) -> float:
        def terms(s: str) -> set[str]:
            import re

            return {t for t in re.findall(r"[a-z0-9][a-z0-9+-]{1,}", s.lower()) if len(t) > 1}

        q = terms(query)
        d = terms(text)
        if not q or not d:
            return 0.0
        overlap = len(q & d)
        return round(overlap / max(len(q), 1), 4)
