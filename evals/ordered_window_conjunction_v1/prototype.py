"""Eval-only ordered-window comparison; no provider, route or source read.

The rejected self-test executed the twelve frozen cases before formal measurement.
No saved output or manual analysis was reported. Rules/labels are unchanged, but
this cohort must never be described as pristine unseen evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from academic_agent import saved_source_candidate_search as baseline_library
from academic_agent.report_evidence_snapshot import (
    CONTENT_WARNING,
    MAX_HITS,
    MAX_QUERY_CHARS,
    ReportEvidenceSnapshot,
    SnapshotSource,
)

METHOD = "ordered_window_conjunction_v1"
FIXTURE_SHA256 = "3e92ab315981a9cdd4ef2b172428cca2b540e2c63cb7691f945f0210c994a747"
RESULT_MAX_BYTES = baseline_library.RESULT_MAX_BYTES
ATOM = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*")
QUERY = re.compile(r"[A-Za-z]+(?:-[A-Za-z]+)*(?:[ \t]+[A-Za-z]+(?:-[A-Za-z]+)*){1,7}")
BOUNDARIES = frozenset(".,;:!?()[]{}\"'")
ELIGIBLE_STATES = frozenset({"matched", "eligible_no_match"})
OBSERVED_STATES = frozenset({
    "unsupported_query", "no_eligible_segments", "eligible_no_match",
    "matches_masked_by_baseline", "additions_found",
})


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_scalar(value: object, maximum: int) -> bool:
    return (type(value) is str and 1 <= len(value) <= maximum and bool(value.strip())
            and not any(0xD800 <= ord(character) <= 0xDFFF for character in value))


def _segments(text: str) -> list[str]:
    parts, start = [], 0
    for index, character in enumerate(text):
        if character in BOUNDARIES or (character.isspace() and character not in " \t"):
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return parts


def _segment_matches(segment: str, atoms: list[str]) -> bool:
    tokens = list(re.finditer(r"[^ \t]+", segment))
    if not tokens or any(ATOM.fullmatch(token.group()) is None for token in tokens):
        return False
    # Retry every possible start, including overlaps. For a fixed start the
    # earliest ordered completion gives its shortest possible original span.
    for first, token in enumerate(tokens):
        if token.group() != atoms[0]:
            continue
        cursor = first + 1
        for atom in atoms[1:]:
            while cursor < len(tokens) and tokens[cursor].group() != atom:
                cursor += 1
            if cursor == len(tokens):
                break
            cursor += 1
        else:
            if tokens[cursor - 1].end() - token.start() <= 128:
                return True
    return False


def ordered_window_match(text: object, query: object) -> tuple[bool, str]:
    """Apply only the frozen exact-case, complete-atom, 128-code-point rule."""
    if not _valid_scalar(query, MAX_QUERY_CHARS):
        return False, "invalid_query"
    if QUERY.fullmatch(query) is None:
        return False, "unsupported_query"
    if text is None:
        return False, "missing_field"
    if type(text) is not str:
        return False, "invalid_field"
    if not text:
        return False, "empty_field"
    if not text.strip():
        return False, "whitespace_only_field"
    eligible = False
    for segment in _segments(text):
        tokens = re.findall(r"[^ \t]+", segment)
        if tokens and all(ATOM.fullmatch(token) is not None for token in tokens):
            eligible = True
            if _segment_matches(segment, query.split()):
                return True, "matched"
    return False, "eligible_no_match" if eligible else "no_eligible_segments"


def _lane(state: str, sources: list[SnapshotSource] | None = None) -> dict:
    return {
        "state": state, "rule": METHOD,
        "hits": None if sources is None else [baseline_library._hit(s) for s in sources[:MAX_HITS]],
        "total_count": None if sources is None else len(sources),
        "truncated": None if sources is None else len(sources) > MAX_HITS,
    }


def _reconstruct_baseline(trusted: ReportEvidenceSnapshot, query: str, actual: dict) -> dict:
    """Check BOTH complete predicates against the real unmodified response.

    Reuse the frozen separator predicate, not a newly interpreted approximation.
    Full response equality also checks metadata, states and the non-support flags.
    Canonical bytes distinguish bools from integers in totals/truncation fields.
    """
    literal = [s for s in trusted.sources if query.casefold() in s.title.casefold()
               or query.casefold() in (s.summary or "").casefold()]
    literal_ids = [s.source_id for s in literal]
    expected = baseline_library._base_search_result()
    expected.update(snapshot_hash=trusted.snapshot_hash,
                    source_observation=baseline_library._observation(trusted))
    expected["literal_result"] = {
        "status": "ok", "total_count": len(literal), "truncated": len(literal) > MAX_HITS,
        "hits": [baseline_library._hit(s) for s in literal[:MAX_HITS]],
        "content_warning": CONTENT_WARNING,
    }
    separator = None
    if baseline_library._QUERY.fullmatch(query) is None:
        expected["normalized_additions"] = baseline_library._lane("unsupported_query")
    else:
        pattern = baseline_library._search_pattern(query)
        separator = [s for s in trusted.sources if s.source_id not in set(literal_ids)
                     and (baseline_library._matches(pattern, s.title)
                          or baseline_library._matches(pattern, s.summary))]
        state = ("empty_snapshot" if not trusted.sources else
                 "additions_found" if separator else "no_additions")
        expected["normalized_additions"] = baseline_library._lane(
            state, hits=[baseline_library._hit(s) for s in separator[:MAX_HITS]],
            total_count=len(separator),
        )
    if baseline_library.render_candidate_result(actual) != baseline_library.render_candidate_result(expected):
        raise ValueError("baseline response drift")
    separator_ids = None if separator is None else [s.source_id for s in separator]
    # Unsupported old separator grammar has no executable lane; its raw counts
    # remain null. This is not an unavailable baseline observation.
    membership = set(literal_ids) | set(separator_ids or [])
    return {
        "literal_full_ids": literal_ids, "separator_full_ids": separator_ids,
        "full_ids": [s.source_id for s in trusted.sources if s.source_id in membership],
        "visible_ids": [h["source_id"] for h in actual["literal_result"]["hits"]]
        + [h["source_id"] for h in actual["normalized_additions"]["hits"] or []],
    }


def compare_snapshot(snapshot: object, query: object) -> dict:
    """Detach and validate before calling the actual frozen baseline once."""
    result = {
        "baseline": None, "baseline_audit": None, "baseline_equal": None,
        "ordered_window_additions": _lane("unavailable"),
        "addition_full_ids": None, "addition_match_fields": None,
        "field_scan_states": None, "mechanics_valid": False,
        "selection": None, "semantic_support": "not_assessed", "unit_equivalence": "not_assessed",
    }
    if not _valid_scalar(query, MAX_QUERY_CHARS):
        result["ordered_window_additions"] = _lane("invalid_query")
        return result
    try:
        trusted = baseline_library._trusted_snapshot(snapshot)
        actual = baseline_library.search_saved_candidates(trusted, query)
        result["baseline"] = actual
        result["baseline_equal"] = False
        result["baseline_audit"] = _reconstruct_baseline(trusted, query, actual)
        result["baseline_equal"] = True
        if QUERY.fullmatch(query) is None:
            result["ordered_window_additions"] = _lane("unsupported_query")
        else:
            baseline_ids = set(result["baseline_audit"]["full_ids"])
            additions, scans, fields = [], [], {}
            any_match = any_eligible = False
            for source in trusted.sources:
                scans.append({"source_id": source.source_id})
                matched_fields = []
                for field in ("title", "summary"):
                    matched, state = ordered_window_match(getattr(source, field), query)
                    scans[-1][field] = state
                    any_eligible |= state in ELIGIBLE_STATES
                    if matched:
                        matched_fields.append(field)
                any_match |= bool(matched_fields)
                if matched_fields and source.source_id not in baseline_ids:
                    additions.append(source)
                    fields[source.source_id] = matched_fields
            state = ("additions_found" if additions else "matches_masked_by_baseline" if any_match
                     else "eligible_no_match" if any_eligible else "no_eligible_segments")
            result.update(ordered_window_additions=_lane(state, additions),
                          addition_full_ids=[s.source_id for s in additions],
                          addition_match_fields=fields, field_scan_states=scans)
        result["mechanics_valid"] = True
    except (ValueError, TypeError, AttributeError, KeyError, OverflowError):
        # Keep any real old response for diagnosis; never substitute zero hits.
        result["failure"] = "snapshot_or_baseline_unavailable"
    return result


def _validate_case(case: object) -> dict:
    keys = {"case_id", "information_need", "query", "sources", "acceptable_ids", "uncertain_ids"}
    if type(case) is not dict or set(case) != keys:
        raise ValueError("invalid case shape")
    if not all(_valid_scalar(case[k], 4096) for k in ("case_id", "information_need")):
        raise ValueError("invalid case identity")
    if type(case["sources"]) is not list:
        raise ValueError("invalid sources")
    ids = []
    for source in case["sources"]:
        if type(source) is not dict or set(source) != {"source_id", "title", "summary"}:
            raise ValueError("invalid source shape")
        if type(source["source_id"]) is not str:
            raise ValueError("invalid source ID")
        ids.append(source["source_id"])
    for key in ("acceptable_ids", "uncertain_ids"):
        values = case[key]
        if (type(values) is not list or any(type(v) is not str or v not in ids for v in values)
                or len(values) != len(set(values))):
            raise ValueError("invalid references")
    if len(ids) != len(set(ids)) or set(case["acceptable_ids"]) & set(case["uncertain_ids"]):
        raise ValueError("overlapping references or duplicate IDs")
    return case


def validate_fixture(fixture: object) -> dict:
    keys = {"schema_version", "cohort_id", "origin", "reference_scope", "cases"}
    if type(fixture) is not dict or set(fixture) != keys:
        raise ValueError("invalid fixture shape")
    if (type(fixture["schema_version"]) is not int or fixture["schema_version"] != 1
            or type(fixture["cases"]) is not list or len(fixture["cases"]) != 12):
        raise ValueError("invalid fixture cohort")
    cases = [_validate_case(case) for case in fixture["cases"]]
    if len({case["case_id"] for case in cases}) != len(cases):
        raise ValueError("duplicate case ID")
    return fixture


def snapshot_for_case(case: dict) -> ReportEvidenceSnapshot:
    """Project fictional saved fields verbatim using existing capacity limits."""
    return ReportEvidenceSnapshot(report_ref=case["case_id"], sources=tuple(
        SnapshotSource(**s, group="academic",
                       publisher="Fictional offline controls", source_type="synthetic_control",
                       accessed_date="2026-09-27", origin="unknown")
        for s in case["sources"]
    ))


def _case_comparison(case: dict) -> dict:
    case = _validate_case(case)
    try:
        snapshot = snapshot_for_case(case)
    except (ValueError, TypeError, KeyError):
        snapshot = None
    result = compare_snapshot(snapshot, case["query"])
    result.update(case_id=case["case_id"], reference={
        "acceptable_ids": list(case["acceptable_ids"]), "uncertain_ids": list(case["uncertain_ids"]),
    })
    return result


def _coverage(row: dict, ids: list[str], visible: bool) -> dict:
    audit = row["baseline_audit"]
    old = None if audit is None else set(audit["visible_ids" if visible else "full_ids"])
    added = row["addition_full_ids"]
    if added is not None:
        added = set(added[:MAX_HITS] if visible else added)
    references = []
    for source_id in ids:
        baseline_hit = None if old is None else source_id in old
        addition_hit = None if added is None else source_id in added
        combined = True if baseline_hit is True or addition_hit is True else (
            False if baseline_hit is False and addition_hit is False else None)
        references.append({"source_id": source_id, "baseline": baseline_hit,
                           "addition": addition_hit, "combined": combined})

    def question(lane: str) -> bool | None:
        values = [r[lane] for r in references]
        return True if True in values else None if not values or None in values else False

    return {"references": references, "baseline": question("baseline"),
            "combined": question("combined")}


def summarize(rows: list[dict]) -> dict:
    """Labels classify measured memberships only; unknowns never become zeros."""
    positives = [r for r in rows if r["reference"]["acceptable_ids"]]
    classifications = {f"{lane}_{kind}": [] for lane in ("baseline", "addition")
                       for kind in ("nonreference", "uncertain")}
    visible_classifications = {key: [] for key in classifications}
    gains, fields, examined, coverage = [], set(), [], []
    for row in rows:
        positive, uncertain = (row["reference"][k] for k in ("acceptable_ids", "uncertain_ids"))
        full, visible = (_coverage(row, positive, v) for v in (False, True))
        coverage.append({"case_id": row["case_id"], "full": full, "visible": visible})
        if full["baseline"] is False and full["combined"] is True:
            gains.append(row["case_id"])
            for source_id in positive:
                fields.update((row["addition_match_fields"] or {}).get(source_id, []))
        old = None if row["baseline_audit"] is None else row["baseline_audit"]["full_ids"]
        for lane, members in (("baseline", old), ("addition", row["addition_full_ids"])):
            for source_id in members or []:
                kind = "uncertain" if source_id in uncertain else "nonreference" if source_id not in positive else None
                if kind:
                    entry = {"case_id": row["case_id"], "source_id": source_id}
                    classifications[f"{lane}_{kind}"].append(entry)
                    visible_members = (row["baseline_audit"]["visible_ids"] if lane == "baseline"
                                       else row["addition_full_ids"][:MAX_HITS])
                    if source_id in visible_members:
                        visible_classifications[f"{lane}_{kind}"].append(entry)
        for scan in row["field_scan_states"] or []:
            if scan["source_id"] not in positive + uncertain:
                eligible = [f for f in ("title", "summary") if scan[f] in ELIGIBLE_STATES]
                if eligible:
                    examined.append({"case_id": row["case_id"], "source_id": scan["source_id"], "fields": eligible})
    unknown = [r["case_id"] for r in rows if r["addition_full_ids"] is None]
    mechanics = all(r["mechanics_valid"] and r["baseline_equal"] is True
                    and r["ordered_window_additions"]["state"] in OBSERVED_STATES for r in rows)
    has_gain = len(gains) >= 2 and {"title", "summary"} <= fields
    gates = {
        # This library cannot attest tests/reinjection or independent review.
        "1_baseline_boundaries_accounting": "unproven" if mechanics and len(rows) == 12 else "failed",
        "2_new_positive_questions": "passed" if has_gain else "unproven" if unknown else "failed",
        "3_zero_definite_added_nonreferences": ("failed" if classifications["addition_nonreference"]
                                               else "unproven" if unknown else "passed"),
        "4_eligible_definite_distractor": "passed" if examined else "unproven",
    }
    positive_case_ids = {r["case_id"] for r in positives}
    return {
        "case_count": len(rows), "positive_denominator": len(positives),
        "positive_reference_denominator": sum(len(r["reference"]["acceptable_ids"]) for r in rows),
        "uncertain_case_count": sum(bool(r["reference"]["uncertain_ids"]) for r in rows),
        "mechanics_valid": mechanics, "baseline_equal": all(r["baseline_equal"] is True for r in rows),
        "boundary_control_evidence": "not_run_here", "coverage": coverage,
        "question_coverage": {scope: {lane: {
            "covered": sum(c[scope][lane] is True for c in coverage),
            "unknown": sum(c[scope][lane] is None for c in coverage
                           if c["case_id"] in positive_case_ids),
            "denominator": len(positives),
        } for lane in ("baseline", "combined")} for scope in ("full", "visible")},
        "newly_covered_positive_cases": gains, "new_gain_fields": sorted(fields),
        "reference_coverage": {scope: {lane: {
            "covered": sum(ref[lane] is True for c in coverage for ref in c[scope]["references"]),
            "unknown": sum(ref[lane] is None for c in coverage for ref in c[scope]["references"]),
            "denominator": sum(len(r["reference"]["acceptable_ids"]) for r in rows),
        } for lane in ("baseline", "addition", "combined")} for scope in ("full", "visible")},
        "returned_ids": classifications, "visible_returned_ids": visible_classifications,
        "eligible_definite_distractors": examined,
        "unobserved_addition_cases": unknown,
        "observed_addition_count": sum(len(r["addition_full_ids"]) for r in rows if r["addition_full_ids"] is not None),
        "full_addition_count": None if unknown else sum(len(r["addition_full_ids"]) for r in rows),
        "full_nonreference_count": None if unknown else len(classifications["addition_nonreference"]),
        "gates": gates,
    }


def compare_fixture(fixture: object, *, fixture_hash: str | None = None,
                    code_hash: str | None = None, delivery_limit: int = RESULT_MAX_BYTES) -> dict:
    """Explicit evaluation only. Callers, not self-tests, own frozen measurement."""
    trusted = validate_fixture(fixture)
    rows = [_case_comparison(case) for case in trusted["cases"]]
    result = {
        "method": METHOD, "fixture_sha256": fixture_hash, "code_sha256": code_hash,
        "selection": None, "semantic_support": "not_assessed", "unit_equivalence": "not_assessed",
        "provenance": {
            "scope": "offline_development_comparison",
            "supplied_hashes": "caller_supplied; identity-only CLI verifies fixture bytes and hashes its own code",
            "frozen_cohort_history": "previously_computed_by_rejected_selftest_not_pristine_unseen",
        },
        "cases": rows, "summary": summarize(rows),
        "delivery": {"state": "available", "max_bytes": delivery_limit},
    }
    try:
        render_comparison(result)
    except ValueError:
        result["delivery"]["state"] = "unavailable"
        result["delivery"]["reason"] = "result_exceeds_renderer_bound_or_invalid_limit"
        result["summary"]["mechanics_valid"] = False
        result["summary"]["gates"]["1_baseline_boundaries_accounting"] = "failed"
    return result


def render_comparison(result: dict) -> bytes:
    """Use the real old byte cap; never trim old fields or audit IDs to fit."""
    rendered = baseline_library.render_candidate_result(result)
    delivery = result.get("delivery", {"state": "available", "max_bytes": RESULT_MAX_BYTES})
    limit = delivery["max_bytes"]
    if (type(limit) is not int or not 0 < limit <= RESULT_MAX_BYTES
            or delivery["state"] != "available" or len(rendered) > limit):
        raise ValueError("comparison exceeds delivery bound or is unavailable")
    return rendered


def load_fixed_fixture(path: Path | None = None) -> tuple[dict, str]:
    raw = (path or Path(__file__).with_name("fixture.json")).read_bytes()
    digest = _sha256(raw)
    if digest != FIXTURE_SHA256:
        raise ValueError("fixture hash mismatch")
    return validate_fixture(json.loads(raw)), digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluate", action="store_true", help="explicit frozen offline measurement")
    args = parser.parse_args()
    fixture, fixture_hash = load_fixed_fixture()
    code_hash = _sha256(Path(__file__).read_bytes())
    result = (compare_fixture(fixture, fixture_hash=fixture_hash, code_hash=code_hash) if args.evaluate
              else {"state": "identity_only", "fixture_sha256": fixture_hash, "code_sha256": code_hash})
    sys.stdout.buffer.write(render_comparison(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
