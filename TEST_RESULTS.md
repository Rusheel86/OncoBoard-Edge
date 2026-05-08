# Test Results

Date: 2026-05-08

Command:

```bash
python -m pytest tests -q -p no:cacheprovider
```

Result:

```text
10 passed in 0.93s
```

Notes:

- The default Windows temp directory in this sandbox denied pytest fixture creation, so tests were run directly against the `tests/` tree with pytest cache disabled.
- Coverage includes offline full-pipeline execution, citation grounding, entity extraction, sidecar PDF extraction, API health/analyze/upload behavior, and evaluation metrics.
- Pytest created several unreadable temporary cache directories during the initial denied-temp run. They are ignored by `.gitignore`; deletion was not performed because escalated cleanup approval was unavailable.

Additional checks:

```bash
python eval/retrieval_quality.py --results paper/figures/retrieval_eval.json
```

```json
{
  "recall_at_k": 1.0,
  "mrr": 0.6666666666666666
}
```

```bash
python scripts/kaggle_setup.py
```

Result: passed in offline/local provider mode. The local Windows environment reported a broken Torch DLL import, so GPU availability could not be validated here.
