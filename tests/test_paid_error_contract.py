"""Machine-readable admission reasons must survive the actual HTTP boundary."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from api import main, papers, runs


@pytest.mark.parametrize("operation", ["run", "resume", "paper"])
@pytest.mark.parametrize("exception,code,hint", [
    (runs.ConcurrencyLimitReached, "concurrency_limit", "another paid operation finishes"),
    (runs.DailyCapReached, "daily_quota_exceeded", "00:00 UTC"),
])
def test_admission_reason_reaches_all_paid_endpoints(monkeypatch, tmp_path, operation, exception, code, hint):
    """The same 429 must not cause daily quota to be painted as a full slot."""
    fail = MagicMock(side_effect=exception("offline admission rejection"))
    # Ownership behavior has separate tests. Isolate this response seam before
    # a worker or extraction can ever be constructed, even with a local .env.
    monkeypatch.setattr(main, "_authorize_run_mutation", lambda *_: None)
    monkeypatch.setattr(runs, "start_run", fail)
    monkeypatch.setattr(runs, "resume_run", fail)
    monkeypatch.setattr(main, "_extract_paper_with_paid_reservation", fail)
    # save_upload has always returned a generated capability. The old invalid
    # placeholder never reached the new observation store's strict path check;
    # use the real id grammar without weakening the 429/call/cleanup assertions.
    paper_id = "paper-" + "0" * 32
    monkeypatch.setattr(papers, "PAPERS_ROOT", tmp_path / "_papers")
    monkeypatch.setattr(papers, "save_upload", lambda *_args, **_kw: (paper_id, tmp_path / "stub.pdf"))
    discarded = MagicMock()
    monkeypatch.setattr(papers, "discard", discarded)
    client = TestClient(main.app)
    if operation == "run":
        response = client.post("/api/runs", json={"topic": "Offline admission fixture"})
    elif operation == "resume":
        response = client.post("/api/runs/fixture/resume", json={})
    else:
        response = client.post("/api/papers", files={"file": ("fixture.pdf", b"%PDF-fixture", "application/pdf")})
    client.close()
    assert response.status_code == 429
    assert response.headers["X-Error-Code"] == code
    assert isinstance(response.json()["detail"], str), "Keep legacy clients compatible"
    assert hint in response.json()["detail"]
    fail.assert_called_once()
    if operation == "paper":
        discarded.assert_called_once_with(paper_id)


def test_request_rate_limit_is_not_a_paid_quota_error(monkeypatch):
    """Middleware 429s retain their own reason and existing retry guidance."""
    monkeypatch.setattr(main, "_rate_limit_exceeded", lambda _: True)
    client = TestClient(main.app)
    response = client.get("/api/runs")
    client.close()
    assert response.status_code == 429
    assert response.headers["X-Error-Code"] == "rate_limited"
    assert response.headers["Retry-After"] == "10"
