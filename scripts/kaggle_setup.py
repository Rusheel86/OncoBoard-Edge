from __future__ import annotations

"""Lightweight Kaggle environment check for OncoBoard-Edge."""

import os
import platform
import sys


def main() -> int:
    """Print a concise environment report and return a Kaggle-ready exit code."""
    print("OncoBoard-Edge Kaggle Setup Helper")
    print(f"python={sys.version.split()[0]} platform={platform.platform()}")

    try:
        import torch

        print(f"torch={torch.__version__} cuda_available={torch.cuda.is_available()}")
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            vram_gb = props.total_memory / (1024**3)
            print(f"gpu={props.name} vram_gb={vram_gb:.2f}")
    except Exception as e:
        print(f"torch_check_failed={e}")

    provider = os.getenv("ONCO_LLM_PROVIDER", "auto").lower()
    hosted_required = provider == "google" or os.getenv("ONCO_REQUIRE_HOSTED_LLM", "0").lower() in {"1", "true", "yes"}
    missing = [k for k in ("GOOGLE_API_KEY",) if hosted_required and not os.getenv(k)]
    if missing:
        print("Missing required environment variables:")
        for k in missing:
            print(f"- {k}")
        return 2

    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY not set; offline/local provider mode will be used.")

    print("Environment looks OK for Phase 1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
