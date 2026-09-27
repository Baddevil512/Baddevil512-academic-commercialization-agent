"""NQ fake-key physical HTTP seams; no native compatibility or unseen accuracy."""

from copy import deepcopy
from decimal import Decimal
import json
import os
from pathlib import Path
import shutil
import stat
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest

from academic_agent import report_evidence_followup as followup
from academic_agent import report_evidence_snapshot as snapshots
from academic_agent import saved_source_candidate_search as candidate
from academic_agent import saved_source_candidate_query_qwen_transport as native
from academic_agent import saved_source_candidate_query_canary as runner

KEY = "sk-nq-synthetic-only-fake-key"
COMMIT = "a" * 40
USAGE = {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}
QUERIES = ("acoustic emission", "低温再生", "laser-induced breakdown spectroscopy", None)
REAL_ROOT = runner.ROOT
READ_DEDICATED_KEY = runner.read_dedicated_key


def payload(query):
    message = {"role": "assistant", "content": '{"action":"decline"}'}
    if query is not None:
        message = {"role": "assistant", "content": None, "tool_calls": [{
            "id": "synthetic", "type": "function", "function": {
                "name": "search_saved_candidates", "arguments": json.dumps({"query": query}),
            },
        }]}
    return {"model": "qwen3.5-plus", "usage": dict(USAGE), "choices": [{
        "index": 0, "message": message, "finish_reason": "stop" if query is None else "tool_calls",
    }]}


def invoke():
    return runner.run_canary(expected_commit=COMMIT, expected_fixture_sha256=runner.FIXTURE_SHA256,
                             expected_preview_sha256=runner.PREVIEW_SHA256, authorize_paid=runner.PROTOCOL_IDENTITY)


def cli_args():
    return ["--expected-commit", COMMIT, "--expected-fixture-sha256", runner.FIXTURE_SHA256,
            "--expected-preview-sha256", runner.PREVIEW_SHA256]


def published(state, name):
    return json.loads((state.output / name).read_bytes())


def journals(state):
    return b"".join(path.read_bytes() for path in state.output.rglob("*") if path.is_file())


def simulate_indirect_lstat(monkeypatch, target, kind):
    """Inject metadata at one exact path; this is NOT OS-native link evidence."""
    original = Path.lstat
    observations = []

    def lstat(path):
        if path == target:
            observations.append(path)
            return SimpleNamespace(
                st_mode=stat.S_IFLNK if kind == "symlink" else stat.S_IFDIR,
                st_file_attributes=0 if kind == "symlink" else stat.FILE_ATTRIBUTE_REPARSE_POINT,
            )
        return original(path)

    monkeypatch.setattr(Path, "lstat", lstat)
    return observations


@pytest.fixture
def offline(tmp_path, monkeypatch):
    """Mock ONLY identity/key selection and physical HTTP, not the native callback."""
    fixture = tmp_path / runner.FIXTURE
    fixture.parent.mkdir(parents=True)
    shutil.copyfile(REAL_ROOT / runner.FIXTURE, fixture)
    (tmp_path / "outputs").mkdir()
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    state = SimpleNamespace(output=tmp_path / runner.FIXED_OUTPUT, requests=[], searches=[],
                            at_post=[], fsynced=[], responses=[payload(q) for q in QUERIES],
                            exception=None, after_post=None, identity_calls=0, drift_at=None,
                            client_options=[], transport_options=[])
    state.identity = {"commit": COMMIT, "fixture_sha256": runner.FIXTURE_SHA256,
                      "preview_sha256": runner.PREVIEW_SHA256, "test_identity": "explicit_offline_stub"}

    def identity(*args):
        assert args == (COMMIT, runner.FIXTURE_SHA256, runner.PREVIEW_SHA256)
        state.identity_calls += 1
        value = deepcopy(state.identity)
        if state.drift_at is not None and state.identity_calls >= state.drift_at:
            value["test_identity"] = "changed"
        return value

    monkeypatch.setattr(runner, "verify_identity", identity)
    monkeypatch.setattr(runner, "read_dedicated_key", lambda: KEY)
    actual_client, actual_fsync = httpx.AsyncClient, os.fsync
    actual_search = candidate.search_saved_candidates

    def disk():
        return {str(path.relative_to(state.output)): path.read_bytes()
                for path in state.output.rglob("*") if path.is_file()}

    def fsync(fd):
        actual_fsync(fd)
        state.fsynced.append(disk())

    def dispatch(request):
        state.requests.append(request)
        state.at_post.append((disk(), deepcopy(state.fsynced)))
        if state.after_post is not None:
            state.after_post()
        if state.exception is not None:
            raise state.exception
        response = state.responses[len(state.requests) - 1]
        raw = response if type(response) is bytes else runner._encoded(response)
        return httpx.Response(200, stream=httpx.ByteStream(raw))

    def transport(**kwargs):
        state.transport_options.append(kwargs)
        return httpx.MockTransport(dispatch)

    def client(**kwargs):
        assert isinstance(kwargs["transport"], httpx.MockTransport)
        state.client_options.append(kwargs)
        return actual_client(**kwargs)

    def search(*args, **kwargs):
        state.searches.append((args, kwargs))
        return actual_search(*args, **kwargs)

    state.read = Mock(side_effect=AssertionError("NQ never reads saved evidence"))
    monkeypatch.setattr(os, "fsync", fsync)
    monkeypatch.setattr(httpx, "AsyncHTTPTransport", transport)
    monkeypatch.setattr(httpx, "AsyncClient", client)
    monkeypatch.setattr(candidate, "search_saved_candidates", search)
    monkeypatch.setattr(candidate, "propose_saved_candidates", Mock(side_effect=AssertionError("automatic search forbidden")))
    monkeypatch.setattr(snapshots, "read_source", state.read)
    monkeypatch.setattr(followup, "read_source", state.read)
    return state


def test_fixed_fixture_preview_and_identity_closure():
    """A new identity must bind full outbound bytes and all actually coupled local modules."""
    cases = runner.load_cases()
    preview = runner.request_preview(cases)
    assert runner._digest((REAL_ROOT / runner.FIXTURE).read_bytes()) == runner.FIXTURE_SHA256
    assert runner._digest(runner._encoded(preview)) == runner.PREVIEW_SHA256
    assert [len(runner._encoded(body)) for body in preview] == [1415, 1436, 1420, 1448]
    assert tuple(case["case_id"] for case in cases) == runner.CASE_IDS
    assert len(set(runner.IDENTITY_PATHS)) == len(runner.IDENTITY_PATHS)
    assert set(native.FROZEN_DEPENDENCY_COUPLING) <= set(runner.IDENTITY_PATHS)
    assert all((REAL_ROOT / path).is_file() for path in runner.IDENTITY_PATHS)
    assert runner.configuration()["four_request_reservation_usd"] == "0.044597248"
    assert "report_evidence_source_locator_canary" not in (REAL_ROOT / "src/academic_agent/saved_source_candidate_query_canary.py").read_text()


def test_physical_http_full_bytes_durable_slots_native_intents_and_metadata_delivery(offline):
    """Reserve-after-POST, private catalog outbound, or repaired NQ03 cannot pass this seam."""
    cases = runner.load_cases()
    summary = invoke()
    assert len(offline.requests) == 4 and len(offline.searches) == 3
    assert offline.identity_calls == 9
    assert summary["mechanical"] == {"passed": 4, "required": 4}
    assert summary["positive_coverage"] == {"checked": 3, "passed": 2, "required": 3}
    assert summary["explicit_decline"] == {"checked": 1, "passed": True, "required": 1}
    assert summary["batch_passed"] is False and summary["reference_failure"] is True
    assert summary["execution_stop"] is None and summary["unrun_cases"] == []
    assert summary["reserved_slots"] == summary["aggregate_slot_attempts"] == 4
    assert summary["callback_entries"] == summary["native_intents"] == summary["reported_responses"] == 4
    assert summary["local_searches"] == 3 and summary["unknown_usage_requests"] == 0
    assert summary["unresolved_slots"] == []
    assert Decimal(summary["budget_consumed_usd"]) == runner.RESERVATION_USD * 4
    assert Decimal(summary["known_usage_estimated_usd"]) == runner._cost(USAGE) * 4
    assert summary["visible_reference_ids_covered"] == 3 and summary["reference_ids_available_total"] == 4
    offline.read.assert_not_called()
    for index, (case, request) in enumerate(zip(cases, offline.requests, strict=True), 1):
        body = native._request(case["question"])
        assert request.content == runner._encoded(body)
        assert request.url == native.ENDPOINT and request.method == "POST"
        assert request.headers["authorization"] == "Bearer " + KEY
        assert body["messages"] == [{"role": "system", "content": candidate.QUERY_POLICY},
                                    {"role": "system", "content": native.NATIVE_POLICY},
                                    {"role": "user", "content": case["question"]}]
        for private in [case["case_id"], "acceptable_ids", "expected_action", *[row["summary"] for row in case["sources"]],
                        *[row["title"] for row in case["sources"]]]:
            assert private not in request.content.decode("ascii")
            assert private not in json.dumps(body, ensure_ascii=False)
        at_post, fsynced = offline.at_post[index - 1]
        slot_name, events_name = f"slot-{index}.json", case["case_id"] + "/events.jsonl"
        # Windows relative paths use backslashes; assertions still inspect the
        # physical fsynced bytes, not an in-memory or mock-side admission gate.
        at_post = {name.replace("\\", "/"): raw for name, raw in at_post.items()}
        fsynced = [{name.replace("\\", "/"): raw for name, raw in snapshot.items()} for snapshot in fsynced]
        slot = json.loads(at_post[slot_name])
        assert slot["slot"] == index and slot["case_id"] == case["case_id"]
        assert slot["request_sha256"] == runner._digest(request.content)
        assert any(snapshot.get(slot_name) == at_post[slot_name] and events_name not in snapshot for snapshot in fsynced)
        assert any(snapshot.get(events_name) == at_post[events_name] for snapshot in fsynced)
        events = [json.loads(line) for line in at_post[events_name].splitlines()]
        assert [row["event"] for row in events] == ["request_reserved"]
        assert events[0]["request"] == body and events[0]["case_id"] is None
        assert events[0]["request_sha256"] == runner._digest(request.content)
        final_events = [json.loads(line) for line in (offline.output / case["case_id"] / "events.jsonl").read_bytes().splitlines()]
        assert [row["event"] for row in final_events] == ["request_reserved", "request_finished"]
        assert final_events[1]["reported_usage"] == USAGE
        outcome = published(offline, case["case_id"] + ".json")
        if index <= 3:
            args, kwargs = offline.searches[index - 1]
            assert args[1] == QUERIES[index - 1] and kwargs == {}
            assert args[0].model_dump() == runner.snapshot_for(case).model_dump()
            assert outcome["candidate_result"]["snapshot_hash"] == args[0].snapshot_hash
            assert "summary" not in outcome["candidate_result"]
            assert outcome["proposal"] == {"query": QUERIES[index - 1]}
    nq03 = published(offline, "NQ03.json")
    assert nq03["reference"]["visible_ids_by_lane"] == {"literal": ["A2"], "lexical": []}
    assert nq03["reference"]["nonreference_ids_by_lane"] == {"literal": ["A2"], "lexical": []}
    assert nq03["reference"]["deduplicated_nonreference_count"] == 1
    assert KEY.encode() not in journals(offline)
    assert offline.transport_options == [{"retries": 0, "verify": True, "trust_env": False}] * 4
    assert all(not row["follow_redirects"] and not row["trust_env"] for row in offline.client_options)
    disk_summary = published(offline, "summary.json")
    assert disk_summary == {name: value for name, value in summary.items()
                            if name != "elapsed_through_summary_publication_attempt_seconds"}


def test_positive_reference_misses_continue_and_cancellation_wrong_query_never_searches(offline):
    """The reference-failure stop mutant and automatic NQ04 search mutant both go red."""
    offline.responses = [payload("no-match-at-all")] * 4
    summary = invoke()
    assert len(offline.requests) == 4 and len(offline.searches) == 3
    assert summary["mechanical"]["passed"] == 4 and summary["execution_stop"] is None
    assert summary["positive_coverage"]["passed"] == 0
    assert summary["explicit_decline"]["passed"] is False and summary["reference_failure"] is True
    nq04 = published(offline, "NQ04.json")
    assert nq04["proposal"] == {"query": "no-match-at-all"}
    assert nq04["candidate_result"] is None and nq04["local_searches"] == 0
    assert nq04["mechanical_passed"] is True and nq04["reference_failure"] is True


def test_successful_development_gate_and_declines_on_positive_controls(offline):
    """Shortening is a scripted native response, never runner repair of the known failed query."""
    offline.responses[2] = payload("scrap")
    summary = invoke()
    assert summary["batch_passed"] is True
    assert published(offline, "NQ03.json")["proposal"] == {"query": "scrap"}
    assert summary["production_admission"] is False


def test_positive_declines_are_mechanical_but_not_coverage(offline):
    """No-search declines may continue, but zero checked candidates cannot become coverage."""
    offline.responses = [payload(None)] * 4
    summary = invoke()
    assert len(offline.requests) == 4 and offline.searches == []
    assert summary["mechanical"]["passed"] == 4 and summary["positive_coverage"]["passed"] == 0
    assert summary["explicit_decline"]["passed"] is True and summary["batch_passed"] is False


@pytest.mark.parametrize("fault", ["text_query", "wrong_model", "unknown_usage", "contradictory_usage", "raw_refusal", "timeout"])
def test_first_native_mechanical_fault_stops_preserving_accounting(offline, fault):
    """Stop-policy bypass must issue a second physical POST and fail this assertion."""
    response = offline.responses[0]
    if fault == "text_query":
        response["choices"] = [{"message": {"role": "assistant", "content": '{"query":"acoustic emission"}'}, "finish_reason": "stop"}]
    elif fault == "wrong_model":
        response["model"] = "not-authorized"
    elif fault in {"unknown_usage", "contradictory_usage"}:
        response["usage"] = None if fault == "unknown_usage" else {**USAGE, "total_tokens": 121}
    elif fault == "raw_refusal":
        response["choices"] = [{"message": {"role": "assistant", "content": None, "refusal": "PRIVATE_REFUSAL"}, "finish_reason": "stop"}]
    else:
        offline.exception = httpx.ReadTimeout("PRIVATE_EXCEPTION " + KEY)
    summary = invoke()
    assert len(offline.requests) == 1 and offline.searches == []
    assert summary["mechanical"]["passed"] == 0 and summary["unrun_cases"] == ["NQ02", "NQ03", "NQ04"]
    assert summary["cases"][0]["reference"] is None
    assert summary["explicit_decline"]["passed"] is None and summary["positive_coverage"]["checked"] == 0
    assert summary["execution_stop"] is not None
    unknown = fault in {"unknown_usage", "contradictory_usage", "timeout"}
    assert summary["unknown_usage_requests"] == int(unknown)
    assert Decimal(summary["known_usage_estimated_usd"]) == (0 if unknown else runner._cost(USAGE))
    assert Decimal(summary["budget_consumed_usd"]) == runner.RESERVATION_USD
    assert b"PRIVATE" not in journals(offline) and KEY.encode() not in journals(offline)


@pytest.mark.parametrize("drift_at,post_count", [(2, 0), (3, 1), (4, 1)])
def test_identity_rechecked_before_dispatch_and_after_callback(offline, drift_at, post_count):
    """A pre-dispatch identity bypass must physically POST and fail the zero-call assertion."""
    offline.drift_at = drift_at
    summary = invoke()
    assert len(offline.requests) == post_count
    assert summary["execution_stop"] == "runtime_identity_changed"
    assert Decimal(summary["known_usage_estimated_usd"]) == runner._cost(USAGE) * post_count
    assert summary["batch_passed"] is False


def test_post_failure_identity_check_does_not_erase_observed_usage(offline):
    """A rejected reply still needs the post-call identity check and retained billing facts."""
    offline.responses[0]["model"] = "wrong"
    offline.drift_at = 3
    summary = invoke()
    assert offline.identity_calls == 3 and len(offline.requests) == 1
    assert summary["execution_stop"] == "runtime_identity_changed"
    assert Decimal(summary["known_usage_estimated_usd"]) == runner._cost(USAGE)


@pytest.mark.parametrize("fault", ["duplicate", "missing", "partial", "extra_field", "request_byte", "slot"])
def test_exact_event_and_aggregate_slot_reconciliation(offline, monkeypatch, fault):
    """A plausible final counter cannot certify tampered durable intent/finish bytes."""
    original = native.CandidateQueryQwenLedger.finish

    def finish(ledger, *args, **kwargs):
        original(ledger, *args, **kwargs)
        path = ledger.output_dir / "events.jsonl"
        raw = path.read_bytes()
        rows = [json.loads(line) for line in raw.splitlines()]
        if fault == "duplicate":
            raw += raw.splitlines(keepends=True)[-1]
        elif fault == "missing":
            raw = raw.splitlines(keepends=True)[0]
        elif fault == "partial":
            raw = raw[:-1]
        elif fault == "extra_field":
            rows[1]["unexpected"] = True
            raw = b"".join(runner._encoded(row) + b"\n" for row in rows)
        elif fault == "request_byte":
            rows[0]["request"]["temperature"] = 1
            raw = b"".join(runner._encoded(row) + b"\n" for row in rows)
        else:
            path = offline.output / "slot-1.json"
            raw = b"{}\n"
        path.write_bytes(raw)

    monkeypatch.setattr(native.CandidateQueryQwenLedger, "finish", finish)
    summary = invoke()
    assert len(offline.requests) == 1 and summary["execution_stop"] == "accounting_reconciliation_failed"
    assert summary["cases"][0]["reference"] is None and Decimal(summary["known_usage_estimated_usd"]) > 0


@pytest.mark.parametrize("fault", ["render", "hit", "hash", "unavailable"])
def test_local_search_and_rendered_delivery_must_match_trusted_snapshot(offline, monkeypatch, fault):
    """A model/renderer cannot substitute an invented candidate or hide local observation loss."""
    actual = candidate.search_saved_candidates
    if fault == "render":
        monkeypatch.setattr(candidate, "render_candidate_result", lambda _: b'{}')
    else:
        def search(*args):
            result = actual(*args)
            if fault == "hit":
                result["literal_result"]["hits"][0]["title"] = "invented"
            elif fault == "hash":
                result["snapshot_hash"] = "wrong"
            else:
                result["literal_result"] = None
                result["normalized_additions"] = candidate._lane("unavailable")
            return result
        monkeypatch.setattr(candidate, "search_saved_candidates", search)
    summary = invoke()
    assert len(offline.requests) == 1 and summary["execution_stop"] == "invalid_case_observation"
    assert summary["local_searches"] == 1 and summary["mechanical"]["passed"] == 0
    assert Decimal(summary["known_usage_estimated_usd"]) == runner._cost(USAGE)


def test_child_creation_failure_keeps_aggregate_slot_not_native_intent(offline, monkeypatch):
    """An aggregate reservation is not evidence of a native request or a refundable slot."""
    monkeypatch.setattr(native.CandidateQueryQwenLedger, "__init__", Mock(side_effect=OSError("PRIVATE " + KEY)))
    summary = invoke()
    assert offline.requests == []
    assert summary["reserved_slots"] == summary["aggregate_slot_attempts"] == 1
    assert summary["native_intents"] == summary["callback_entries"] == summary["reported_responses"] == 0
    assert summary["unresolved_slots"] == ["NQ01"] and summary["cost_coverage"] == "lower_bound"
    assert summary["unknown_usage_requests"] == 0
    assert Decimal(summary["budget_consumed_usd"]) == runner.RESERVATION_USD
    assert Decimal(summary["known_usage_estimated_usd"]) == 0


def test_fifth_aggregate_slot_and_budget_admission_are_independent(offline, monkeypatch):
    """The cap must reject a fifth slot even when every one-request child finished."""
    batches = []
    original = runner._Batch.__init__

    def capture(batch, *args):
        original(batch, *args)
        batches.append(batch)

    monkeypatch.setattr(runner._Batch, "__init__", capture)
    invoke()
    batch = batches[0]
    with pytest.raises(runner.CanaryStopped, match="^runner_request_limit$"):
        batch.admit()
    assert len(batch.slots) == 4 and len(offline.requests) == 4


def test_engineering_budget_checked_before_next_slot_or_native_post(offline, monkeypatch):
    """A budget-bypass mutant must send the second POST and fail this boundary test."""
    monkeypatch.setattr(runner, "USD_LIMIT", runner.RESERVATION_USD * 2 - Decimal("0.000000001"))
    summary = invoke()
    assert len(offline.requests) == 1 and summary["reserved_slots"] == 1
    assert summary["execution_stop"] == "runner_budget_limit"


def test_budget_uses_larger_observed_estimate_not_only_reservations(offline):
    """Direct admission remains conservative when known estimated cost exceeds a slot reserve."""
    batch = runner._Batch(runner.validate_output(), KEY)
    ledger = SimpleNamespace(records=[{"estimated_usd": "0.045", "usage_status": "complete",
                                      "provider_response_received": True}], pending=None, stop_reason=None)
    batch.slots.append({"case_id": "NQ01", "ledger": ledger, "persisted": True,
                        "callback_entries": 1, "local_searches": 1})
    assert Decimal(batch.totals()["budget_consumed_usd"]) == Decimal("0.045")
    with pytest.raises(runner.CanaryStopped, match="^runner_budget_limit$"):
        batch.admit()


@pytest.mark.parametrize("fault", ["slot", "native_reserve", "native_finish", "case_publish", "summary_publish"])
def test_fsync_failure_stops_and_retains_truthful_counts(offline, monkeypatch, fault):
    """Failed durable publication is not success; finishing failure retains known usage and pending intent."""
    original = os.fsync
    case_publication_faulted = False

    def fsync(fd):
        nonlocal case_publication_faulted
        trigger = False
        if fault in {"slot", "case_publish", "summary_publish"}:
            name = {"slot": ".slot-1.json.pending", "case_publish": ".NQ01.json.pending", "summary_publish": ".summary.json.pending"}[fault]
            trigger = (offline.output / name).exists()
        else:
            path = offline.output / "NQ01/events.jsonl"
            if path.exists():
                raw = path.read_bytes()
                trigger = b"request_reserved" in raw if fault == "native_reserve" else b"request_finished" in raw
        if trigger:
            if fault == "case_publish":
                # Fail only this publication. The summary must still be able
                # to durably report the failed case rather than masking it with
                # a second, unrelated summary-persistence failure.
                if case_publication_faulted:
                    return original(fd)
                case_publication_faulted = True
            raise OSError("PRIVATE_FSYNC " + KEY)
        original(fd)

    monkeypatch.setattr(os, "fsync", fsync)
    summary = invoke()
    assert summary["execution_stop"] == "persistence_failed" and summary["batch_passed"] is False
    expected_posts = 0 if fault in {"slot", "native_reserve"} else 4 if fault == "summary_publish" else 1
    assert len(offline.requests) == expected_posts
    assert summary["native_intents"] == expected_posts
    if fault == "slot":
        assert summary["aggregate_slot_attempts"] == 1 and summary["reserved_slots"] == 0
    if fault in {"slot", "native_reserve", "native_finish"}:
        assert summary["unresolved_slots"] == ["NQ01"]
    assert Decimal(summary["known_usage_estimated_usd"]) == runner._cost(USAGE) * expected_posts
    assert b"PRIVATE_FSYNC" not in journals(offline) and KEY.encode() not in journals(offline)
    if fault == "summary_publish":
        assert summary["summary_persisted"] is False and not (offline.output / "summary.json").exists()
    if fault == "case_publish":
        assert summary["mechanical"] == {"passed": 0, "required": 4}
        first = summary["cases"][0]
        assert first["mechanical_passed"] is False and first["case_record_persisted"] is False
        assert first["reference"]["passed"] is True and first["reference_failure"] is False
        assert first["reference_observation_scope"] == "observed_before_case_publication"
        assert summary["reference_check_scope"] == "observed_before_case_publication_not_mechanical_admission"
        assert summary["positive_coverage"] == {"checked": 1, "passed": 1, "required": 3}
        assert summary["explicit_decline"]["passed"] is None
        assert summary["summary_persisted"] is True
        assert not (offline.output / "NQ01.json").exists()
        assert published(offline, "summary.json")["cases"][0] == first


@pytest.mark.parametrize("encoding", ["plain", "escaped", "nested"])
def test_publication_scans_serialized_values_before_any_file_creation(offline, encoding):
    """Recoverable escaped keys must not hide in an otherwise publishable value."""
    output = runner.validate_output()
    output.mkdir()
    secret = KEY if encoding == "plain" else "".join(f"\\u{ord(char):04x}" for char in KEY)
    if encoding == "nested":
        secret = json.dumps(secret)
    with pytest.raises(runner.CanaryStopped, match="^secret_in_publication$"):
        runner._publish(output, "unsafe.json", {"value": secret}, KEY)
    assert list(output.iterdir()) == []


def test_publication_is_closed_fsynced_atomic_and_never_overwrites(offline, monkeypatch):
    """Atomic linking before close, or replacing a prior artifact, breaks write-once publication."""
    output = runner.validate_output()
    output.mkdir()
    original_link, original_open, original_fsync = os.link, Path.open, os.fsync
    pending = output / ".value.json.pending"
    links, writers, synced_writers = [], [], []

    def track_open(path, mode="r", *args, **kwargs):
        stream = original_open(path, mode, *args, **kwargs)
        if path == pending and mode == "xb":
            writers.append(stream)
        return stream

    def track_fsync(fd):
        original_fsync(fd)
        if writers and not writers[-1].closed and writers[-1].fileno() == fd:
            synced_writers.append(writers[-1])

    def link(source, destination):
        assert source.read_bytes() == runner._encoded({"safe": True}) + b"\n"
        # Inspect the actual publisher's stream and completed fsync at link
        # entry. An r+b reopen would prove neither exclusivity nor writer close.
        assert source == pending and writers
        assert writers[-1].closed and writers[-1] in synced_writers
        links.append((source, destination))
        original_link(source, destination)

    monkeypatch.setattr(Path, "open", track_open)
    monkeypatch.setattr(os, "fsync", track_fsync)
    monkeypatch.setattr(os, "link", link)
    runner._publish(output, "value.json", {"safe": True}, KEY)
    with pytest.raises(runner.CanaryStopped, match="^persistence_failed$"):
        runner._publish(output, "value.json", {"safe": True}, KEY)
    assert len(links) == len(writers) == len(synced_writers) == 2
    assert all(stream.closed for stream in writers)
    assert json.loads((output / "value.json").read_bytes()) == {"safe": True}


@pytest.mark.parametrize("kind", ["directory", "file"])
def test_fixed_output_occupancy_and_indirection_refused_before_key(offline, monkeypatch, kind):
    """Real occupied files/directories must not permit overwrite, resume or key access."""
    if kind == "directory":
        offline.output.mkdir()
    else:
        offline.output.write_bytes(b"occupied")
    key = Mock(side_effect=AssertionError("key read before output admission"))
    monkeypatch.setattr(runner, "read_dedicated_key", key)
    with pytest.raises(runner.CanaryStopped, match="^output_creation_failed_or_occupied$"):
        invoke()
    key.assert_not_called()
    assert offline.requests == []


def test_default_cli_identity_only_has_no_environment_key_http_or_output(offline, monkeypatch, capsys):
    """No-key identity mode must remain executable without credential lookup or output creation."""
    with monkeypatch.context() as scoped:
        forbidden = Mock(side_effect=AssertionError("identity-only side effect"))
        scoped.setattr(runner, "read_dedicated_key", forbidden)
        scoped.setattr(type(os.environ), "__getitem__", forbidden)
        scoped.setattr(os, "getenv", forbidden)
        scoped.setattr(httpx, "AsyncClient", forbidden)
        assert runner.main(cli_args()) == 0
        forbidden.assert_not_called()
    assert not offline.output.exists()
    assert json.loads(capsys.readouterr().out)["mode"] == "identity_only"


def test_process_key_only_and_explicit_acknowledgement(offline, monkeypatch):
    """Only the dedicated process variable is requested; rejected acknowledgement reads nothing."""
    read = Mock(side_effect=AssertionError("no key before acknowledgement"))
    monkeypatch.setattr(runner, "read_dedicated_key", read)
    with pytest.raises(runner.CanaryStopped, match="^fresh_protocol_acknowledgement_required$"):
        runner.run_canary(expected_commit=COMMIT, expected_fixture_sha256=runner.FIXTURE_SHA256,
                          expected_preview_sha256=runner.PREVIEW_SHA256, authorize_paid="old-batch")
    read.assert_not_called()
    assert not offline.output.exists()
    environment = Mock()
    environment.get.return_value = KEY
    with monkeypatch.context() as scoped:
        scoped.setattr(os, "environ", environment)
        assert READ_DEDICATED_KEY() == KEY
    environment.get.assert_called_once_with("DASHSCOPE_API_KEY")


@pytest.mark.parametrize("location", ["missing_output_leaf", "existing_output_parent"])
@pytest.mark.parametrize("kind", ["symlink", "reparse"])
def test_simulated_output_indirection_rejected_before_key_or_dispatch(offline, monkeypatch, location, kind):
    """Simulated lstat metadata exercises real admission, NOT native OS symlink handling."""
    # The absent leaf models a dangling link; the real parent directory models
    # redirected ancestry. No link is created and no OS privilege is requested.
    target = offline.output if location == "missing_output_leaf" else offline.output.parent
    assert runner.validate_output() == offline.output
    key = Mock(side_effect=AssertionError("key read before indirection admission"))
    monkeypatch.setattr(runner, "read_dedicated_key", key)
    with monkeypatch.context() as scoped:
        observations = simulate_indirect_lstat(scoped, target, kind)
        with pytest.raises(runner.CanaryStopped, match="^indirect_path_rejected$"):
            runner.validate_output()
        with pytest.raises(runner.CanaryStopped, match="^indirect_path_rejected$"):
            invoke()
        assert observations == [target, target]
    key.assert_not_called()
    assert offline.requests == [] and offline.searches == []
    assert not offline.output.exists() and list(offline.output.parent.iterdir()) == []
    assert runner.validate_output() == offline.output


@pytest.mark.parametrize("arguments", [[], ["--unknown", KEY], ["--expected-commit"],
    cli_args() + ["--expected-commit", COMMIT], cli_args() + ["--authorize-paid="],
    cli_args() + ["--authorize-paid", "--unknown"]])
def test_fixed_cli_rejects_malformed_options_without_echoing_values(offline, capsys, arguments):
    """Reject unknown/duplicate/empty options without diagnostic echo."""
    assert runner.main(arguments) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and captured.err == "invalid_candidate_query_canary_arguments\n"
    assert KEY not in captured.err and not offline.output.exists()


@pytest.mark.parametrize("fault", ["preview", "fixture"])
def test_runtime_preview_or_fixture_drift_refused_before_key_or_output(offline, monkeypatch, fault):
    """An identity stub cannot make a changed full request or raw fixture acceptable."""
    if fault == "preview":
        original = native._request
        monkeypatch.setattr(native, "_request", lambda question: {**original(question), "temperature": 1})
    else:
        path = runner.ROOT / runner.FIXTURE
        path.write_bytes(path.read_bytes() + b" ")
    key = Mock(side_effect=AssertionError("must not resolve key"))
    monkeypatch.setattr(runner, "read_dedicated_key", key)
    with pytest.raises(runner.CanaryStopped):
        invoke()
    key.assert_not_called()
    assert not offline.output.exists() and offline.requests == []


@pytest.mark.parametrize("kind", ["canary", "runtime", "string_bomb"])
def test_cli_diagnostics_never_stringify_arbitrary_exception(offline, monkeypatch, capsys, kind):
    """Neither a shared exception class nor its __str__ can publish raw diagnostics."""
    class StringBomb(runner.CanaryStopped):
        def __str__(self):
            raise AssertionError("never stringify")
    error = {"canary": runner.CanaryStopped, "runtime": RuntimeError, "string_bomb": StringBomb}[kind]("PRIVATE " + KEY)
    monkeypatch.setattr(runner, "verify_identity", Mock(side_effect=error))
    assert runner.main(cli_args()) == 1
    output = capsys.readouterr()
    assert "PRIVATE" not in output.out + output.err and KEY not in output.out + output.err
    assert json.loads(output.out)["error"] == "candidate_query_canary_admission_or_execution_failed"


@pytest.fixture
def identity_tree(tmp_path, monkeypatch):
    """Real file/version/preview checks; only git's committed-blob responses are simulated."""
    blobs = {}
    for name in runner.IDENTITY_PATHS:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = (REAL_ROOT / name).read_bytes()
        path.write_bytes(raw)
        blobs[name] = raw.replace(b"\r\n", b"\n")
    state = SimpleNamespace(blobs=blobs, dirty=b"", head=COMMIT, queries=[])

    def git(*args):
        state.queries.append(args)
        if args[0] == "rev-parse":
            return state.head.encode() + b"\n"
        if args[0] == "status":
            assert args[4:] == runner.IDENTITY_PATHS
            return state.dirty
        assert args[0] == "show"
        return blobs[args[1].split(":", 1)[1]]

    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "_git", git)
    return state


def verify():
    return runner.verify_identity(COMMIT, runner.FIXTURE_SHA256, runner.PREVIEW_SHA256)


@pytest.mark.parametrize("location", ["bound_file", "bound_parent"])
@pytest.mark.parametrize("kind", ["symlink", "reparse"])
def test_simulated_identity_indirection_rejected_before_bound_file_read(identity_tree, monkeypatch, location, kind):
    """Real identity validation rejects simulated link metadata before reading the bound source."""
    name = "src/academic_agent/__init__.py"
    path = runner.ROOT / name
    target = path if location == "bound_file" else path.parent
    reads = []
    original = Path.read_bytes

    def read_bytes(current):
        reads.append(current)
        return original(current)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    with monkeypatch.context() as scoped:
        observations = simulate_indirect_lstat(scoped, target, kind)
        with pytest.raises(runner.CanaryStopped, match="^indirect_path_rejected$"):
            verify()
        assert observations == [target]
    assert path not in reads
    assert ("show", f"{COMMIT}:{name}") not in identity_tree.queries
    # Restoring the one-path simulation leaves the unchanged identity valid;
    # this does not assert that an OS-native junction/symlink was exercised.
    assert verify()["commit"] == COMMIT


def test_identity_full_bytes_despite_clean_git_and_preserves_raw_hashes(identity_tree):
    """A git-clean cached bit cannot hide changed source bytes; CRLF raw identity is retained."""
    identity = verify()
    name = "src/academic_agent/__init__.py"
    path = runner.ROOT / name
    path.write_bytes(identity_tree.blobs[name].replace(b"\n", b"\r\n"))
    crlf = verify()
    assert crlf["disk_sha256"][name] == runner._digest(path.read_bytes())
    assert crlf["committed_sha256"][name] == identity["committed_sha256"][name]
    path.write_bytes(path.read_bytes() + b"# different\n")
    with pytest.raises(runner.CanaryStopped, match="^committed_content_mismatch$"):
        verify()


@pytest.mark.parametrize("fault", ["head", "dirty", "package", "attributes", "preview", "fixture"])
def test_actual_identity_rejects_wrong_dirty_versions_and_contract_drift(identity_tree, monkeypatch, fault):
    """Version/source/fixture/preview gates fail independently before any execution authority."""
    reason = "source_identity_mismatch"
    if fault == "head":
        identity_tree.head = "b" * 40
    elif fault == "dirty":
        identity_tree.dirty = b" M bound-source\n"
    elif fault == "package":
        monkeypatch.setattr(runner, "version", lambda _: "0.invalid")
        reason = "installed_dependency_mismatch"
    elif fault == "attributes":
        name = ".gitattributes"
        identity_tree.blobs[name] = b"* text=auto\n"
        (runner.ROOT / name).write_bytes(identity_tree.blobs[name])
        reason = "unsupported_text_normalization"
    elif fault == "preview":
        original = native._request
        monkeypatch.setattr(native, "_request", lambda question: {**original(question), "max_tokens": 511})
        reason = "preview_identity_mismatch"
    else:
        identity_tree.blobs[runner.FIXTURE] += b" "
        (runner.ROOT / runner.FIXTURE).write_bytes(identity_tree.blobs[runner.FIXTURE])
        reason = "fixture_identity_mismatch"
    with pytest.raises(runner.CanaryStopped, match="^" + reason + "$"):
        verify()


@pytest.mark.parametrize("field,value", [("commit", "HEAD"), ("fixture", "0" * 64), ("preview", "0" * 64)])
def test_identity_expected_arguments_fail_before_git(monkeypatch, field, value):
    """No implicit HEAD, old fixture or alternate preview is an exact authorization."""
    args = {"commit": COMMIT, "fixture": runner.FIXTURE_SHA256, "preview": runner.PREVIEW_SHA256, field: value}
    git = Mock(side_effect=AssertionError("early rejection before git"))
    monkeypatch.setattr(runner, "_git", git)
    with pytest.raises(runner.CanaryStopped):
        runner.verify_identity(args["commit"], args["fixture"], args["preview"])
    git.assert_not_called()
