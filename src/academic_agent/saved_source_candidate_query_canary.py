"""Fixed NQ synthetic batch; identity-only unless explicitly acknowledged.

Only question bytes reach the unchanged native adapter. Aggregate slots are
durable admission facts, NOT POST receipts. No old runner, loader or allowance
is reused. File fsync and atomic links are not directory/power-loss guarantees.
"""

from copy import deepcopy
from decimal import Decimal
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys
from time import monotonic
import tomllib

from academic_agent import saved_source_candidate_search as candidate
from academic_agent import saved_source_candidate_query_qwen_transport as native
from academic_agent.report_evidence_catalog_qwen_transport import _contains_secret
from academic_agent.report_evidence_followup import _strict_json
from academic_agent.report_evidence_qwen_canary import (
    CanaryStopped, INPUT_RATE, INPUT_RESERVATION, MAX_TOKENS, OUTPUT_RATE,
    REQUEST_BYTES, RESERVATION_USD, _encoded,
)
from academic_agent.report_evidence_qwen_transport import _usage, validate_key
from academic_agent.report_evidence_snapshot import (
    CONTENT_WARNING, MAX_HITS, ReportEvidenceSnapshot, SnapshotSource,
)

PROTOCOL_IDENTITY = "saved_source_candidate_query_canary_v1"
ROOT = Path(__file__).resolve().parents[2]
FIXED_OUTPUT = "outputs/saved_source_candidate_query_canary_v1"
FIXTURE = "tests/fixtures/saved_source_candidate_query_qwen.json"
FIXTURE_SHA256 = "e4d4889f0b8e352bd448b6e2618201414408c79c2f274a1b399388db7e144afb"
PREVIEW_SHA256 = "1b1f5ca4042466e4b68be5d62570f78d26449cfee933e41e884b3189b37fa574"
PROTOCOL = "docs/prereg-2026-09-26-candidate-query-synthetic-canary.md"
CASE_IDS = ("NQ01", "NQ02", "NQ03", "NQ04")
REFERENCES = (("A1", "A3"), ("A1",), ("A1",), ())
SOURCE_METADATA = {"group": "academic", "publisher": "Synthetic NQ controls",
                   "source_type": "synthetic_control", "origin": "unknown", "accessed_date": "2026-09-26"}
MAX_REQUESTS = 4
USD_LIMIT = Decimal("0.05")
IDENTITY_PATHS = (
    ".gitattributes", "src/academic_agent/__init__.py", *native.FROZEN_DEPENDENCY_COUPLING,
    "src/academic_agent/saved_source_candidate_query_qwen_transport.py",
    "src/academic_agent/saved_source_candidate_query_canary.py",
    "tests/test_saved_source_candidate_search.py",
    "tests/test_saved_source_candidate_query_qwen_transport.py",
    "tests/test_saved_source_candidate_query_canary.py", FIXTURE, PROTOCOL,
    "docs/saved-source-candidate-search.md",
    "docs/prereg-2026-09-26-candidate-query-qwen-transport.md",
)
DEPENDENCIES = (
    "httpx", "httpcore", "anyio", "certifi", "h11", "idna", "sniffio", "typing-extensions",
    "pydantic", "pydantic-core", "annotated-types", "typing-inspection",
)
_SAFE_REASONS = native._SAFE_ERRORS | frozenset({
    "runner_request_limit", "runner_budget_limit", "runner_unresolved_or_stopped",
    "runtime_identity_changed", "source_identity_mismatch", "committed_content_mismatch",
    "installed_dependency_mismatch", "identity_check_unavailable", "indirect_path_rejected",
    "fixture_identity_mismatch", "fixture_invalid_or_unavailable", "unsupported_text_normalization",
    "preview_identity_mismatch", "case_execution_failed", "accounting_reconciliation_failed",
    "callback_native_audit_failed", "invalid_case_observation", "secret_in_publication",
    "output_creation_failed_or_occupied", "invalid_output_destination",
})


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def configuration():
    return {"protocol_identity": PROTOCOL_IDENTITY, "fixed_output": FIXED_OUTPUT,
            "case_ids": list(CASE_IDS), "max_requests": MAX_REQUESTS, "max_requests_per_case": 1,
            "usd_soft_limit": str(USD_LIMIT), "four_request_reservation_usd": str(RESERVATION_USD * 4),
            "per_case_transport": native.candidate_query_qwen_configuration(),
            "mechanical_fault_stops": True, "reference_miss_stops": False,
            "cancellation_control_searches": 0, "resume": False,
            "credential_source": "process_DASHSCOPE_API_KEY_only",
            "acknowledgement_is_independent_consent_verification": False,
            "elapsed_scope": "monotonic_local_setup_identity_callback_search_checks_publication_attempt",
            "elapsed_exclusions": "not_isolated_provider_latency_or_production_SLO"}


def snapshot_for(case):
    return ReportEvidenceSnapshot(report_ref=case["case_id"], sources=tuple(
        SnapshotSource(**SOURCE_METADATA, **row) for row in case["sources"]))


def load_cases():
    try:
        _plain_path(ROOT / FIXTURE)
        raw = (ROOT / FIXTURE).read_bytes()
        if _digest(raw) != FIXTURE_SHA256:
            raise CanaryStopped("fixture_identity_mismatch")
        data = _strict_json(raw.decode("utf-8"))
        if (type(data) is not dict or set(data) != {
                "schema_version", "cohort_id", "origin", "reference_status", "source_metadata", "cases"}
                or type(data["schema_version"]) is not int or data["schema_version"] != 1
                or data["cohort_id"] != "candidate_query_synthetic_development_v1"
                or data["origin"] != "author_generated_synthetic"
                or data["reference_status"] != "llm_label_blinded_context_limited_reviewed"
                or data["source_metadata"] != SOURCE_METADATA or type(data["cases"]) is not list
                or tuple(row["case_id"] for row in data["cases"]) != CASE_IDS):
            raise ValueError("fixture_contract")
        for index, case in enumerate(data["cases"]):
            if (type(case) is not dict or set(case) != {
                    "case_id", "question", "sources", "expected_action", "acceptable_ids"}
                    or case["expected_action"] != ("decline" if index == 3 else "query")
                    or case["acceptable_ids"] != list(REFERENCES[index])
                    or not candidate._scalars_string(case["question"], candidate.MAX_QUESTION_CHARS)
                    or type(case["sources"]) is not list or len(case["sources"]) != 3
                    or any(type(row) is not dict or set(row) != {"source_id", "title", "summary"}
                           for row in case["sources"])):
                raise ValueError("fixture_contract")
            snapshot = snapshot_for(case)
            if tuple(row.source_id for row in snapshot.sources) != ("A1", "A2", "A3"):
                raise ValueError("fixture_sources")
        return tuple(data["cases"])
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        raise CanaryStopped("fixture_invalid_or_unavailable") from None


def request_preview(cases):
    bodies = [native._request(case["question"]) for case in cases]
    if (_digest(_encoded(bodies)) != PREVIEW_SHA256
            or any(len(_encoded(body)) > REQUEST_BYTES for body in bodies)):
        raise CanaryStopped("preview_identity_mismatch")
    return bodies


def _plain_path(path):
    path.relative_to(ROOT)
    for current in reversed((path, *path.parents)):
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise CanaryStopped("indirect_path_rejected")


def _git(*arguments):
    return subprocess.run(["git", "--no-optional-locks", *arguments], cwd=ROOT,
                          capture_output=True, check=True, timeout=10).stdout


def verify_identity(expected_commit, expected_fixture_sha256, expected_preview_sha256):
    """Compare full bytes, not git's possibly cached clean bit or package attestation."""
    if type(expected_commit) is not str or not re.fullmatch(r"[0-9a-f]{40}", expected_commit):
        raise CanaryStopped("invalid_expected_commit")
    if type(expected_fixture_sha256) is not str or expected_fixture_sha256 != FIXTURE_SHA256:
        raise CanaryStopped("fixture_authorization_mismatch")
    if type(expected_preview_sha256) is not str or expected_preview_sha256 != PREVIEW_SHA256:
        raise CanaryStopped("preview_identity_mismatch")
    try:
        head = _git("rev-parse", "--verify", "HEAD").decode("ascii").strip()
        if head != expected_commit or _git("status", "--porcelain", "--untracked-files=all", "--", *IDENTITY_PATHS).strip():
            raise CanaryStopped("source_identity_mismatch")
        disk, committed = {}, {}
        for name in IDENTITY_PATHS:
            path = ROOT / name
            _plain_path(path)
            raw, blob = path.read_bytes(), _git("show", f"{expected_commit}:{name}")
            if raw.replace(b"\r\n", b"\n") != blob:
                raise CanaryStopped("committed_content_mismatch")
            disk[name], committed[name] = _digest(raw), _digest(blob)
        if (ROOT / ".gitattributes").read_bytes().replace(b"\r\n", b"\n") != b"* text=auto eol=lf\n":
            raise CanaryStopped("unsupported_text_normalization")
        request_preview(load_cases())
        locked = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))["package"]
        installed = {name: version(name) for name in DEPENDENCIES}
        if any(value not in {row["version"] for row in locked if row["name"] == name} for name, value in installed.items()):
            raise CanaryStopped("installed_dependency_mismatch")
        config = configuration()
        return {"protocol_identity": PROTOCOL_IDENTITY, "commit": head, "fixture_sha256": FIXTURE_SHA256,
                "preview_sha256": PREVIEW_SHA256, "disk_sha256": disk, "committed_sha256": committed,
                "comparison": "CRLF_to_LF_for_fixed_text_paths_only",
                "runtime": {"python": platform.python_version(), **installed},
                "package_identity_scope": "installed_versions_not_package_byte_attestation",
                "configuration": config, "configuration_sha256": _digest(_encoded(config))}
    except (OSError, subprocess.SubprocessError, PackageNotFoundError, ValueError, TypeError, KeyError):
        raise CanaryStopped("identity_check_unavailable") from None


def _recheck(identity):
    if verify_identity(identity["commit"], identity["fixture_sha256"], identity["preview_sha256"]) != identity:
        raise CanaryStopped("runtime_identity_changed")


def validate_output():
    try:
        output = ROOT / FIXED_OUTPUT
        _plain_path(output)
        if os.path.lexists(output):
            raise CanaryStopped("output_creation_failed_or_occupied")
        if not output.parent.is_dir():
            raise CanaryStopped("invalid_output_destination")
        return output
    except (OSError, ValueError, TypeError):
        raise CanaryStopped("invalid_output_destination") from None


def read_dedicated_key():
    key = os.environ.get("DASHSCOPE_API_KEY")
    validate_key(key)
    return key


def _safe_reason(exc, fallback):
    # A shared exception class is not permission to stringify provider content.
    if type(exc) is CanaryStopped and len(exc.args) == 1:
        reason = exc.args[0]
        if type(reason) is str and reason in _SAFE_REASONS:
            return reason
    return fallback


def _publication_bytes(value, key):
    raw = _encoded(value) + b"\n"
    # Scan the SERIALIZED value too: custom objects cannot exploit a difference
    # between their in-memory appearance and the bytes we are about to publish.
    if _contains_secret(_strict_json(raw.decode("ascii")), key) or _contains_secret(raw.decode("ascii"), key):
        raise CanaryStopped("secret_in_publication")
    return raw


def _publish(output, name, value, key):
    """Write-once complete write/flush/fsync/close followed by an atomic link."""
    try:
        if Path(name).name != name:
            raise ValueError("publication_name")
        pending, destination = output / ("." + name + ".pending"), output / name
        _plain_path(destination)
        _plain_path(pending)
        raw = _publication_bytes(value, key)
        with pending.open("xb") as stream:
            if stream.write(raw) != len(raw):
                raise OSError("short_write")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(pending, destination)
    except Exception as exc:  # noqa: BLE001 -- only fixed diagnostics, even for hostile filesystem hooks.
        raise CanaryStopped(_safe_reason(exc, "persistence_failed")) from None
    try:
        pending.unlink()
    except OSError:
        pass  # Cleanup cannot revoke an already complete publication.


def _cost(usage):
    return (Decimal(usage["prompt_tokens"]) * INPUT_RATE + Decimal(usage["completion_tokens"]) * OUTPUT_RATE) / 1_000_000


def _accounting(ledger, body):
    """Exact event bytes catch duplicate/partial/extra records, not just a counter."""
    if (type(ledger) is not native.CandidateQueryQwenLedger or ledger.stop_reason is not None
            or ledger.pending is not None or len(ledger.records) != 1 or ledger.case_id is not None):
        return False
    row = ledger.records[0]
    if (type(row["request_id"]) is not int or row["request_id"] != 1 or row["case_id"] is not None
            or row["protocol_accepted"] is not True or row["provider_response_received"] is not True
            or row["response_model_matches_authorized"] is not True or row["usage_status"] != "complete"
            or row["error"] is not None or row["reservation_usd"] != str(RESERVATION_USD)
            or _encoded(row["request"]) != _encoded(body) or row["request_sha256"] != _digest(_encoded(body))):
        return False
    usage = _usage({"usage": row["reported_usage"]})
    if (usage is None or _encoded(usage) != _encoded(row["reported_usage"])
            or usage["prompt_tokens"] > INPUT_RESERVATION or usage["completion_tokens"] > MAX_TOKENS
            or row["estimated_usd"] != str(_cost(usage))):
        return False
    reserved = {name: row[name] for name in ("request_id", "case_id", "request", "request_sha256", "reservation_usd")}
    reserved.update(usage_status="unknown", provider_response_received=False,
                    response_model_matches_authorized=None, protocol_accepted=False)
    expected = [{"event": "request_reserved", **reserved}, {"event": "request_finished", **row}]
    path = ledger.output_dir / "events.jsonl"
    _plain_path(path)
    return (set(row) == set(reserved) | {"reported_usage", "estimated_usd", "error"}
            and path.read_bytes() == b"".join(_encoded(event) + b"\n" for event in expected))


class _Batch:
    """Four durable aggregate slots; child construction failure cannot refund one."""

    def __init__(self, output, key):
        self.output, self.key, self.slots, self.stop_reason = output, key, [], None
        _plain_path(output)
        try:
            output.mkdir(exist_ok=False)
        except OSError:
            raise CanaryStopped("output_creation_failed_or_occupied") from None

    def totals(self):
        records, unresolved, consumed = [], [], Decimal(0)
        for slot in self.slots:
            ledger = slot["ledger"]
            rows = [] if ledger is None else ledger.records
            records.extend(rows)
            consumed += max(RESERVATION_USD, sum((Decimal(row.get("estimated_usd", "0")) for row in rows), Decimal(0)))
            if not slot["persisted"] or not rows or ledger.pending is not None:
                unresolved.append(slot["case_id"])
        unknown = sum(row["usage_status"] != "complete" for row in records)
        known = sum((Decimal(row.get("estimated_usd", "0")) for row in records), Decimal(0))
        return {"aggregate_slot_attempts": len(self.slots),
                "reserved_slots": sum(slot["persisted"] for slot in self.slots),
                "native_intents": len(records), "reported_responses": sum(row["provider_response_received"] for row in records),
                "callback_entries": sum(slot["callback_entries"] for slot in self.slots),
                "local_searches": sum(slot["local_searches"] for slot in self.slots),
                "unknown_usage_requests": unknown, "unresolved_slots": unresolved,
                "known_usage_estimated_usd": str(known), "budget_consumed_usd": str(consumed),
                "cost_coverage": "lower_bound" if unknown or unresolved else "complete_for_reported_requests" if records else "not_observed",
                "price_scope": "frozen_conservative_estimate_not_invoice", "execution_stop": self.stop_reason}

    def admit(self):
        totals = self.totals()
        if (self.stop_reason is not None or totals["unresolved_slots"] or totals["unknown_usage_requests"]
                or any(slot["ledger"].stop_reason is not None for slot in self.slots)):
            raise CanaryStopped("runner_unresolved_or_stopped")
        if len(self.slots) >= MAX_REQUESTS:
            raise CanaryStopped("runner_request_limit")
        if Decimal(totals["budget_consumed_usd"]) + RESERVATION_USD > USD_LIMIT:
            raise CanaryStopped("runner_budget_limit")
        for slot in self.slots:
            self.reconcile(slot)

    def reserve(self, case_id, body):
        self.admit()
        if case_id != CASE_IDS[len(self.slots)]:
            raise CanaryStopped("runner_request_limit")
        record = {"event": "aggregate_slot_reserved", "slot": len(self.slots) + 1,
                  "case_id": case_id, "reservation_usd": str(RESERVATION_USD),
                  "request_sha256": _digest(_encoded(body))}
        slot = {"case_id": case_id, "record": record, "body": deepcopy(body), "persisted": False,
                "ledger": None, "callback_entries": 0, "local_searches": 0}
        self.slots.append(slot)  # A failed publication is unresolved, not a reusable slot.
        _publish(self.output, f"slot-{record['slot']}.json", record, self.key)
        slot["persisted"] = True
        return slot

    def reconcile(self, slot):
        path = self.output / f"slot-{slot['record']['slot']}.json"
        _plain_path(path)
        if (not slot["persisted"] or path.read_bytes() != _encoded(slot["record"]) + b"\n"
                or not _accounting(slot["ledger"], slot["body"])):
            raise CanaryStopped("accounting_reconciliation_failed")


def _validate_search(snapshot, query, result):
    """Validate metadata against trusted sources without executing a second search.

    Reuse only the frozen lexical predicates; do not case-repair NQ03 or derive
    expected candidates from reference labels. Visible hits are not support.
    """
    literal = [source for source in snapshot.sources if query.casefold() in source.title.casefold()
               or query.casefold() in (source.summary or "").casefold()]
    additions = []
    state = "unsupported_query"
    if candidate._QUERY.fullmatch(query) is not None:
        pattern = candidate._search_pattern(query)
        literal_ids = {source.source_id for source in literal}
        additions = [source for source in snapshot.sources if source.source_id not in literal_ids
                     and (candidate._matches(pattern, source.title) or candidate._matches(pattern, source.summary))]
        state = "additions_found" if additions else "no_additions"
    expected = candidate._base_search_result()
    expected.update(snapshot_hash=snapshot.snapshot_hash, source_observation=candidate._observation(snapshot),
                    literal_result={"status": "ok", "total_count": len(literal), "truncated": len(literal) > MAX_HITS,
                                    "hits": [candidate._hit(source) for source in literal[:MAX_HITS]],
                                    "content_warning": CONTENT_WARNING},
                    normalized_additions=candidate._lane(state, hits=None if state == "unsupported_query" else [
                        candidate._hit(source) for source in additions[:MAX_HITS]],
                        total_count=None if state == "unsupported_query" else len(additions)))
    if _encoded(result) != _encoded(expected):
        raise CanaryStopped("invalid_case_observation")
    rendered = candidate.render_candidate_result(result)
    if _encoded(_strict_json(rendered.decode("ascii"))) != _encoded(result):
        raise CanaryStopped("invalid_case_observation")
    return _strict_json(rendered.decode("ascii"))


def _reference(case, action, result):
    lanes = {"literal": [], "lexical": []}
    if result is not None:
        lanes["literal"] = [row["source_id"] for row in result["literal_result"]["hits"]]
        lanes["lexical"] = [row["source_id"] for row in result["normalized_additions"]["hits"] or []]
    acceptable = set(case["acceptable_ids"])
    visible = set(lanes["literal"]) | set(lanes["lexical"])
    covered = sorted(visible & acceptable)
    nonreference = {lane: sorted(set(ids) - acceptable) for lane, ids in lanes.items()}
    passed = action == "decline" if case["case_id"] == "NQ04" else bool(covered)
    return {"passed": passed, "expected_action": case["expected_action"],
            "visible_ids_by_lane": lanes, "visible_reference_ids_covered": covered,
            "reference_ids_available": case["acceptable_ids"],
            "visible_reference_count": len(covered), "available_reference_count": len(acceptable),
            "nonreference_ids_by_lane": nonreference, "deduplicated_nonreference_count": len(visible - acceptable),
            "scope": "visible_candidates_only_not_relevance_or_support"}


def _run_case(batch, case, body, identity):
    started = monotonic()
    slot = result = proposal = reference = None
    reason = None
    try:
        snapshot = candidate._trusted_snapshot(snapshot_for(case))
        try:
            _recheck(identity)  # Must precede aggregate intent, native construction and possible POST.
            if _encoded(native._request(case["question"])) != _encoded(body):
                raise CanaryStopped("callback_native_audit_failed")
            slot = batch.reserve(case["case_id"], body)
            child = batch.output / case["case_id"]
            _plain_path(child)
            ledger = native.CandidateQueryQwenLedger(child)
            slot["ledger"] = ledger
            transport = native.CandidateQueryQwenTransport(batch.key, ledger, question=case["question"])
            slot["callback_entries"] += 1
            admitted = transport(case["question"], candidate.QUERY_POLICY)
        finally:
            # Failure is not an exemption. A post-call mismatch never erases the
            # native ledger's observed usage or creates authority to retry.
            _recheck(identity)
        action, query, _ = candidate._canonical_proposal(admitted)
        if action is None:
            raise CanaryStopped("invalid_case_observation")
        proposal = {"query": query} if action == "query" else {"action": "decline"}
        _publication_bytes(proposal, batch.key)
        batch.reconcile(slot)
        if action == "query" and case["case_id"] != "NQ04":
            slot["local_searches"] += 1
            result = _validate_search(snapshot, query, candidate.search_saved_candidates(snapshot, query))
        batch.reconcile(slot)
        reference = _reference(case, action, result)
    except Exception as exc:  # noqa: BLE001 -- provider/filesystem diagnostics are never publication content.
        reason = _safe_reason(exc, "case_execution_failed")
    outcome = {"case_id": case["case_id"], "mechanical_passed": reason is None,
               "execution_stop": reason, "reference_failure": None if reference is None else not reference["passed"],
               "reference": reference, "proposal": proposal, "candidate_result": result,
               "reference_observation_scope": "not_checked" if reference is None else "observed_before_case_publication",
               "callback_entries": 0 if slot is None else slot["callback_entries"],
               "local_searches": 0 if slot is None else slot["local_searches"],
               "elapsed_before_publication_seconds": monotonic() - started}
    persisted = False
    try:
        _publish(batch.output, case["case_id"] + ".json", outcome, batch.key)
        persisted = True
    except CanaryStopped as exc:
        reason = _safe_reason(exc, "persistence_failed")
    if reason is not None:
        batch.stop_reason = reason
    # Case publication is part of mechanical acceptance, not just the combined
    # gate. Preserve already observed reference/usage facts but do not promote
    # their pre-publication checks to a mechanically admitted case. Summary
    # repeats no provider query/payload, so rejected secrets cannot leak again.
    return {**{name: value for name, value in outcome.items() if name not in {"proposal", "candidate_result"}},
            "mechanical_passed": outcome["mechanical_passed"] and persisted,
            "execution_stop": reason, "case_record_persisted": persisted,
            "elapsed_through_publication_attempt_seconds": monotonic() - started}


def run_canary(*, expected_commit, expected_fixture_sha256, expected_preview_sha256, authorize_paid):
    if type(authorize_paid) is not str or authorize_paid != PROTOCOL_IDENTITY:
        raise CanaryStopped("fresh_protocol_acknowledgement_required")
    started = monotonic()
    identity = verify_identity(expected_commit, expected_fixture_sha256, expected_preview_sha256)
    cases = load_cases()
    preview = request_preview(cases)
    validate_output()
    key = read_dedicated_key()
    batch = _Batch(validate_output(), key)
    for name, value in (
        ("identity.json", identity), ("preview.json", preview), ("configuration.json", configuration()),
        ("authorization.json", {"operator_acknowledgement": authorize_paid, "expected_commit": expected_commit,
                                "expected_fixture_sha256": expected_fixture_sha256,
                                "expected_preview_sha256": expected_preview_sha256,
                                "identity_sha256": _digest(_encoded(identity)), "standing_authorization_source": PROTOCOL,
                                "independent_user_consent_review_ci_verified": False, "old_allowance_reused": False}),
    ):
        _publish(batch.output, name, value, key)
    outcomes = []
    for case, body in zip(cases, preview, strict=True):
        outcomes.append(_run_case(batch, case, body, identity))
        if batch.stop_reason is not None:
            break
    references = [row["reference"] for row in outcomes]
    # These denominators count actual pre-publication observations, including a
    # later publication fault. Mechanical counts independently require durable
    # case publication; discarding an observed reference would erase evidence.
    positive = [row for case, row in zip(cases, references, strict=False) if case["case_id"] != "NQ04" and row is not None]
    decline = references[3] if len(references) == 4 else None
    mechanical = sum(row["mechanical_passed"] for row in outcomes)
    totals = batch.totals()
    summary = {"protocol_identity": PROTOCOL_IDENTITY, "mode": "synthetic_candidate_query_canary",
               "mechanical": {"passed": mechanical, "required": 4},
               "positive_coverage": {"checked": len(positive), "passed": sum(row["passed"] for row in positive), "required": 3},
               "explicit_decline": {"checked": int(decline is not None), "passed": None if decline is None else decline["passed"], "required": 1},
               "visible_reference_ids_covered": sum(row["visible_reference_count"] for row in positive),
               "reference_ids_available_in_checked_cases": sum(row["available_reference_count"] for row in positive),
               "reference_ids_available_total": 4,
               "reference_failure": (True if any(row is not None and not row["passed"] for row in references)
                                     else False if len(references) == 4 and all(row is not None for row in references) else None),
               "cases": outcomes, "unrun_cases": list(CASE_IDS[len(outcomes):]),
               "reference_status": "llm_label_blinded_context_limited_reviewed_not_unseen_or_human_gold",
               "reference_check_scope": "observed_before_case_publication_not_mechanical_admission",
               "semantic_support": "not_assessed", "production_admission": False,
               "summary_persisted": True, "elapsed_scope": configuration()["elapsed_scope"],
               "elapsed_before_summary_publication_seconds": monotonic() - started, **totals}
    summary["batch_passed"] = (mechanical == 4 and len(positive) == 3 and all(row["passed"] for row in positive)
                               and decline is not None and decline["passed"] and totals["execution_stop"] is None
                               and not totals["unresolved_slots"] and totals["unknown_usage_requests"] == 0
                               and all(row["case_record_persisted"] for row in outcomes))
    try:
        _publish(batch.output, "summary.json", summary, key)
    except CanaryStopped as exc:
        summary.update(batch_passed=False, summary_persisted=False, execution_stop=_safe_reason(exc, "persistence_failed"))
    summary["elapsed_through_summary_publication_attempt_seconds"] = monotonic() - started
    return summary


def _arguments(argv):
    # argparse/gettext reads LANGUAGE during construction, even in identity-only
    # mode. This fixed interface cannot consult ambient settings or globally
    # patch gettext, which would change unrelated callers' behavior.
    allowed = {"--expected-commit", "--expected-fixture-sha256", "--expected-preview-sha256", "--authorize-paid"}
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments in (["--help"], ["-h"]):
        print("python -m academic_agent.saved_source_candidate_query_canary "
              "--expected-commit SHA --expected-fixture-sha256 SHA --expected-preview-sha256 SHA "
              "[--authorize-paid saved_source_candidate_query_canary_v1]")
        return None
    parsed = {}
    while arguments:
        option = arguments.pop(0)
        if type(option) is not str:
            raise ValueError("invalid_arguments")
        option, separator, value = option.partition("=")
        if option not in allowed or option in parsed:
            raise ValueError("invalid_arguments")
        if not separator:
            if not arguments:
                raise ValueError("invalid_arguments")
            value = arguments.pop(0)
        if type(value) is not str or not value or value.startswith("--"):
            raise ValueError("invalid_arguments")
        parsed[option] = value
    if not allowed - {"--authorize-paid"} <= parsed.keys():
        raise ValueError("invalid_arguments")
    return parsed


def main(argv=None):
    try:
        args = _arguments(argv)
    except (ValueError, TypeError):
        print("invalid_candidate_query_canary_arguments", file=sys.stderr)
        return 2
    if args is None:
        return 0
    try:
        if "--authorize-paid" not in args:
            identity = verify_identity(args["--expected-commit"], args["--expected-fixture-sha256"], args["--expected-preview-sha256"])
            print(json.dumps({"mode": "identity_only", "identity_verified": True, "live_authorized": False,
                              "identity": identity}, ensure_ascii=True))
            return 0
        result = run_canary(expected_commit=args["--expected-commit"], expected_fixture_sha256=args["--expected-fixture-sha256"],
                            expected_preview_sha256=args["--expected-preview-sha256"], authorize_paid=args["--authorize-paid"])
        print(json.dumps(result, ensure_ascii=True))
        return 0 if result["batch_passed"] and result["summary_persisted"] else 1
    except Exception:  # noqa: BLE001 -- no traceback, raw diagnostics, paths or credential material on CLI.
        print(json.dumps({"batch_passed": False, "error": "candidate_query_canary_admission_or_execution_failed"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
