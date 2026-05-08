from __future__ import annotations

import gc
import json
import os
import re
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class GemmaGeneration:
    text: str
    raw: dict[str, Any]


class GemmaManager:
    """
    Provider wrapper for Gemma-style report generation.

    Provider selection:
    - `ONCO_LLM_PROVIDER=google`: hosted Gemma 4 via Google API.
    - `ONCO_LLM_PROVIDER=ollama`: local HTTP endpoint compatible with Ollama.
    - `ONCO_LLM_PROVIDER=offline`: deterministic evidence-backed fallback.
    - `auto` chooses Google when an API key and SDK are available, otherwise
      a local endpoint when configured, otherwise offline.
    """

    def __init__(
        self,
        *,
        model_name: Optional[str] = None,
        api_key_env: str = "GOOGLE_API_KEY",
        provider: Optional[str] = None,
    ) -> None:
        load_dotenv(override=False)
        self.provider = (provider or os.getenv("ONCO_LLM_PROVIDER", "auto")).lower()
        self.api_key_env = api_key_env
        self._api_key = os.getenv(api_key_env)
        self._model_name = model_name or os.getenv("ONCO_GEMMA_MODEL", "gemma-4-26b-a4b-it")
        self._genai_client: Any = None
        self._legacy_genai: Any = None

        if self.provider == "auto":
            if self._api_key:
                self.provider = "google"
            elif os.getenv("OLLAMA_BASE_URL") or os.getenv("ONCO_LOCAL_LLM_URL"):
                self.provider = "ollama"
            else:
                self.provider = "offline"

        if self.provider == "google":
            self._configure_google()
        elif self.provider not in {"ollama", "offline"}:
            raise ValueError(f"Unsupported ONCO_LLM_PROVIDER={self.provider!r}")

    @property
    def model_name(self) -> str:
        return self._model_name

    @contextmanager
    def session(self) -> Iterator["GemmaManager"]:
        try:
            yield self
        finally:
            self.cleanup()

    def generate(
        self,
        *,
        prompt: str,
        system_instruction: Optional[str] = None,
        generation_config: Optional[dict[str, Any]] = None,
        safety_settings: Optional[list[dict[str, Any]]] = None,
    ) -> GemmaGeneration:
        cfg: dict[str, Any] = dict(generation_config or {})
        cfg.setdefault("temperature", float(os.getenv("ONCO_TEMPERATURE", "0.2")))
        cfg.setdefault("top_p", 0.9)
        cfg.setdefault("max_output_tokens", int(os.getenv("ONCO_MAX_OUTPUT_TOKENS", "1536")))

        if self.provider == "google" and (self._genai_client or self._legacy_genai):
            return self._generate_google(prompt, system_instruction, cfg, safety_settings)
        if self.provider == "ollama":
            return self._generate_ollama(prompt, system_instruction, cfg)
        return self._generate_offline(prompt)

    def cleanup(self) -> None:
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            return

    def _configure_google(self) -> None:
        if not self._api_key:
            if os.getenv("ONCO_REQUIRE_HOSTED_LLM", "0").lower() in {"1", "true", "yes"}:
                raise RuntimeError(f"Missing {self.api_key_env}. Set it in your environment or `.env`.")
            self.provider = "offline"
            return

        try:
            from google import genai  # type: ignore

            self._genai_client = genai.Client(api_key=self._api_key)
            return
        except Exception:
            pass

        try:
            import google.generativeai as legacy_genai  # type: ignore

            legacy_genai.configure(api_key=self._api_key)
            self._legacy_genai = legacy_genai
            return
        except Exception as e:
            if os.getenv("ONCO_REQUIRE_HOSTED_LLM", "0").lower() in {"1", "true", "yes"}:
                raise RuntimeError(f"Google LLM SDK unavailable: {e}") from e
            self.provider = "offline"

    def _generate_google(
        self,
        prompt: str,
        system_instruction: Optional[str],
        cfg: dict[str, Any],
        safety_settings: Optional[list[dict[str, Any]]],
    ) -> GemmaGeneration:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                if self._genai_client is not None:
                    contents = prompt if not system_instruction else f"{system_instruction}\n\n{prompt}"
                    response = self._genai_client.models.generate_content(
                        model=self._model_name,
                        contents=contents,
                        config={
                            "temperature": cfg["temperature"],
                            "top_p": cfg["top_p"],
                            "max_output_tokens": cfg["max_output_tokens"],
                            "response_mime_type": "application/json",
                        },
                    )
                    text = getattr(response, "text", "") or ""
                    return GemmaGeneration(text=text, raw=self._safe_response_dict(response))

                model = self._legacy_genai.GenerativeModel(
                    self._model_name,
                    system_instruction=system_instruction,
                )
                response = model.generate_content(
                    prompt,
                    generation_config=cfg,
                    safety_settings=safety_settings,
                )
                text = getattr(response, "text", "") or ""
                return GemmaGeneration(text=text, raw=self._safe_response_dict(response))
            except Exception as e:
                last_error = e
                time.sleep(0.4 * (attempt + 1))

        if os.getenv("ONCO_REQUIRE_HOSTED_LLM", "0").lower() in {"1", "true", "yes"}:
            raise RuntimeError(f"Hosted Gemma generation failed: {last_error}") from last_error
        offline = self._generate_offline(prompt)
        return GemmaGeneration(
            text=offline.text,
            raw={"provider": "offline_after_google_failure", "error": str(last_error), "offline": offline.raw},
        )

    def _generate_ollama(
        self,
        prompt: str,
        system_instruction: Optional[str],
        cfg: dict[str, Any],
    ) -> GemmaGeneration:
        base = os.getenv("ONCO_LOCAL_LLM_URL") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        url = base.rstrip("/") + "/api/generate"
        body = {
            "model": os.getenv("ONCO_LOCAL_LLM_MODEL", "gemma4:e4b"),
            "prompt": prompt if not system_instruction else f"{system_instruction}\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": cfg["temperature"],
                "top_p": cfg["top_p"],
                "num_predict": cfg["max_output_tokens"],
            },
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=float(os.getenv("ONCO_LOCAL_LLM_TIMEOUT", "120"))) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            text = str(payload.get("response") or payload.get("text") or "")
            return GemmaGeneration(text=text, raw=payload)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if os.getenv("ONCO_REQUIRE_LOCAL_LLM", "0").lower() in {"1", "true", "yes"}:
                raise RuntimeError(f"Local LLM generation failed: {e}") from e
            offline = self._generate_offline(prompt)
            return GemmaGeneration(
                text=offline.text,
                raw={"provider": "offline_after_local_failure", "error": str(e), "offline": offline.raw},
            )

    def _generate_offline(self, prompt: str) -> GemmaGeneration:
        case = _extract_json_block(prompt, "PATIENT_CASE_JSON") or {}
        extractions = _extract_json_block(prompt, "EXTRACTIONS_JSON") or {}
        evidence = _extract_evidence(prompt)
        citations = [item["chunk_id"] for item in evidence[:4]]
        site = case.get("primary_site") or "unspecified primary site"
        diagnosis = case.get("known_diagnosis") or "oncology case"
        question = case.get("clinician_question") or "clinical question"

        findings: list[str] = []
        for key in ("pathology_entities", "audio_entities", "radiology_entities"):
            block = extractions.get(key) or {}
            if block.get("histology"):
                findings.append(f"Histology signals: {', '.join(block['histology'])}.")
            if block.get("biomarkers"):
                findings.append("Biomarkers: " + "; ".join(f"{k}: {v}" for k, v in block["biomarkers"].items()) + ".")
            if block.get("stage"):
                findings.append(f"Stage mention: {block['stage']}.")
            if block.get("symptoms"):
                findings.append(f"Symptoms noted: {', '.join(block['symptoms'])}.")

        if not findings:
            findings.append("No high-confidence modality-derived oncology entities were extracted.")

        missing = []
        for needed in ("histology", "stage", "biomarker panel", "performance status"):
            if needed not in " ".join(findings).lower():
                missing.append(needed)

        report = {
            "summary": (
                f"Evidence-grounded review for {diagnosis} involving {site}. "
                f"The clinician question was: {question}"
            ),
            "key_findings": findings[:6],
            "assessment": [
                "Available evidence supports a cautious oncology review focused on confirming diagnosis, stage, biomarkers, and treatment fitness.",
                "No treatment recommendation should be finalized without reconciling missing patient-specific data and reviewing the cited evidence.",
            ],
            "recommended_next_steps": [
                "Confirm complete pathology, stage, biomarker status, performance status, organ function, and patient goals.",
                "Use the retrieved guideline and PubMed-style evidence snippets as the starting point for tumor-board review.",
            ],
            "treatment_considerations": [
                "Consider site-specific systemic, surgical, radiation, or supportive care options only after required staging and biomarker data are complete."
            ],
            "red_flags": [
                "Escalate urgently for uncontrolled symptoms, suspected spinal cord compression, severe bleeding, sepsis, or rapidly worsening respiratory status."
            ],
            "uncertainty_notes": [
                "Offline deterministic provider used; hosted Gemma/local model was not required for this run.",
                "Missing or incomplete data: " + ", ".join(missing) + ".",
            ],
            "citations": citations,
            "confidence_score": 0.72 if citations else 0.25,
            "evidence_references": [
                {
                    "chunk_id": item["chunk_id"],
                    "source_title": item.get("source_title", "local evidence"),
                    "section": item.get("section"),
                    "page": item.get("page"),
                    "score": item.get("score"),
                    "quote": item["text"][:280],
                }
                for item in evidence[:4]
            ],
            "evidence_vs_inference": {
                "evidence": [f"[{item['chunk_id']}] {item['text'][:180]}" for item in evidence[:3]],
                "inference": [
                    "The report prioritizes diagnostic completeness because oncology treatment choices depend on site, stage, biomarkers, and patient fitness."
                ],
            },
        }
        return GemmaGeneration(text=json.dumps(report, ensure_ascii=False), raw={"provider": "offline"})

    @staticmethod
    def _safe_response_dict(resp: Any) -> dict[str, Any]:
        for attr in ("to_dict", "model_dump", "dict"):
            fn = getattr(resp, attr, None)
            if callable(fn):
                try:
                    obj = fn()
                    return json.loads(json.dumps(obj, default=str))
                except Exception:
                    pass
        text = getattr(resp, "text", None)
        return {"text": text, "repr": repr(resp)}


def _extract_json_block(prompt: str, label: str) -> dict[str, Any] | None:
    pattern = rf"{re.escape(label)}:\n(.*?)(?:\n\n[A-Z_]+:|\Z)"
    m = re.search(pattern, prompt, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1).strip())
    except json.JSONDecodeError:
        return None


def _extract_evidence(prompt: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    section = prompt.split("EVIDENCE_SNIPPETS:", 1)[-1]
    section = section.split("Return ONLY", 1)[0]
    for match in re.finditer(r"\[(?P<chunk>[^\]]+)\]\s*(?P<text>.*?)(?=\n\n\[|\Z)", section, flags=re.S):
        chunk_id = match.group("chunk").strip()
        text = " ".join(match.group("text").split())
        if chunk_id and text:
            meta: dict[str, Any] = {"chunk_id": chunk_id, "text": text}
            title_match = re.search(r"source_title=([^|]+)", text)
            if title_match:
                meta["source_title"] = title_match.group(1).strip()
            out.append(meta)
    return out
