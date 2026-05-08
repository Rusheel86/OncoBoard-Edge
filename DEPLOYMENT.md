# Deployment Guide

## Hugging Face Spaces

1. Create a Gradio Space.
2. Upload the repository.
3. Ensure `app.py`, `requirements.txt`, and `runtime.txt` are at the repository root.
4. Add secrets in Space settings only when hosted Gemma is required:
   - `GOOGLE_API_KEY`
   - `ONCO_LLM_PROVIDER=google`
   - `ONCO_GEMMA_MODEL=gemma-4-26b-a4b-it`

Offline demo mode requires no secrets.

## Kaggle

Recommended runtime:

- Python 3.11
- GPU: T4 optional
- Internet: off for offline demo, on only for hosted Gemma/API installs

```bash
python scripts/kaggle_setup.py
python ui/app.py
```

For low-VRAM local inference, prefer a small Gemma 4 variant exposed through Ollama or another local HTTP server and set:

```bash
ONCO_LLM_PROVIDER=ollama
ONCO_LOCAL_LLM_MODEL=gemma4:e4b
```

## Docker

```bash
docker compose up --build
```

Gradio is available on `http://localhost:7860`.

## Production Hardening Checklist

- Replace demo evidence corpus with institution-approved guideline and literature sources.
- Add authentication and role-based access.
- Configure PHI-safe logging and retention.
- Enforce upload size, file type, and malware scanning controls.
- Validate local regulatory requirements before clinical deployment.
