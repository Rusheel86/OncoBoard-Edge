from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_analyze_endpoint_offline() -> None:
    client = TestClient(app)
    res = client.post(
        "/analyze",
        json={
            "intake": {
                "patient_id": "API_001",
                "primary_site": "colorectal",
                "known_diagnosis": "MSI high colon cancer",
                "clinician_question": "What biomarker evidence is relevant?",
            },
            "artifacts": {"images": [], "pdfs": [], "audios": []},
        },
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["report"]["citations"]
    assert payload["retrieval"]["chunks"]


def test_upload_rejects_wrong_extension() -> None:
    client = TestClient(app)
    res = client.post("/upload/pdf", files={"file": ("bad.exe", b"hello", "application/octet-stream")})
    assert res.status_code == 400
