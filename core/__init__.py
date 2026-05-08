"""
Core primitives for OncoBoard-Edge.

This package contains:
- LangGraph state definitions and graph construction
- Gemma 4 client wrapper (Google AI Studio via `google-generativeai`)
- Local retrieval utilities (ChromaDB)
"""

from .chroma_store import ChromaStore
from .graph import build_onco_graph
from .llm_manager import GemmaManager
from .state import OncologyReport, OncoState, PatientIntake

__all__ = [
    "ChromaStore",
    "GemmaManager",
    "OncologyReport",
    "OncoState",
    "PatientIntake",
    "build_onco_graph",
]
