"""Fresh synthetic controls only; archiveable as sibling checks.py.

The rejected version computed the frozen cohort in a self-test. This version
never evaluates it. Mutation reinjection and final cohort measurement belong
to the parent; assertions here are not claims that reinjection already ran.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from academic_agent import saved_source_candidate_search as old
from academic_agent.report_evidence_snapshot import ReportEvidenceSnapshot, SnapshotSource

# File-relative loading also works when this file is archived/renamed checks.py
# and invoked outside its directory; it cannot import another study's prototype.
SPEC = importlib.util.spec_from_file_location("conjunction_eval_prototype", Path(__file__).with_name("prototype.py"))
prototype = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prototype)


def source(identifier="A1", title="alpha x beta", summary=None):
    return {"source_id": identifier, "title": title, "summary": summary}


def case(query="alpha beta", sources=None, acceptable=(), uncertain=(), case_id="T1"):
    return {"case_id": case_id, "information_need": "fresh fictional engineering control",
            "query": query, "sources": [source()] if sources is None else sources,
            "acceptable_ids": list(acceptable), "uncertain_ids": list(uncertain)}


def fixture():
    cases = [case(acceptable=["A1"], case_id=f"T{i + 1}",
                  sources=[source(), source("A2", "unrelated token")]) for i in range(12)]
    cases[1]["sources"][0] = source(title="different title", summary="alpha x beta")
    cases[-1]["acceptable_ids"], cases[-1]["uncertain_ids"] = [], ["A1"]
    return {"schema_version": 1, "cohort_id": "fresh_synthetic_selftests",
            "origin": "engineering_control", "reference_scope": "not_semantic_validation", "cases": cases}


def delivered(item):
    return json.loads(prototype.render_comparison(prototype._case_comparison(item)))


@pytest.mark.parametrize(("text", "query", "match"), [
    ("alpha x beta", "alpha beta", True),
    ("alpha MW beta", "alpha beta", True),  # MW is legal, not interpreted as a unit.
    ("alpha  beta", "alpha beta", True),
    ("alpha-beta x gamma", "alpha-beta gamma", True),
    ("alpha beta alpha gamma", "alpha alpha gamma", True),
    ("alpha alpha", "alpha alpha", True),
    ("alpha gamma alpha", "alpha alpha", True),
    ("alpha", "alpha alpha", False),
    ("alpha gamma", "gamma alpha", False),
    ("Alpha x beta", "alpha beta", False),
    ("alphas x beta", "alpha beta", False),
    ("alpha-beta x gamma", "beta gamma", False),
    ("alpha beta gamma", "alpha-beta gamma", False),
    ("alpha x mW", "alpha MW", False),
    ("alpha " + "x" * 140 + " alpha alpha beta", "alpha alpha beta", True),
])
def test_order_complete_compound_case_units_and_repeated_starts(text, query, match):
    """No suffix, casefold, plural, unit or reused-position match is admitted."""
    assert prototype.ordered_window_match(text, query)[0] is match


def test_exact_128_and_129_original_codepoint_span_at_delivery():
    """The rejected test used 126/130; these inputs really have length 128/129."""
    within = "alpha " + "x" * 117 + " beta"
    outside = "alpha " + "x" * 118 + " beta"
    assert len(within) == 128 and len(outside) == 129
    assert prototype.ordered_window_match(within, "alpha beta") == (True, "matched")
    assert prototype.ordered_window_match(outside, "alpha beta") == (False, "eligible_no_match")
    assert delivered(case(sources=[source(title=within)]))["addition_full_ids"] == ["A1"]
    assert delivered(case(sources=[source(title=outside)]))["addition_full_ids"] == []
    assert prototype.ordered_window_match("alpha" + " " * 119 + "beta", "alpha beta")[0]
    assert not prototype.ordered_window_match("alpha" + " " * 120 + "beta", "alpha beta")[0]


@pytest.mark.parametrize("boundary", list(".,;:!?()[]{}\"'") + ["\n", "\r", "\v", "\f", "\u00a0", "\u2003"])
def test_hard_segment_boundaries(boundary):
    """A legal word on each side of a boundary cannot create one window."""
    text = "alpha" + boundary + "beta"
    assert prototype.ordered_window_match(text, "alpha beta") == (False, "eligible_no_match")
    assert delivered(case(sources=[source(title=text)]))["addition_full_ids"] == []


@pytest.mark.parametrize("poison", ["10mW", "beta2", "+beta", "-beta", "beta+", "beta/word", "beta\\word",
                                      "βeta", "béta", "βalpha", "alpha_", "alpha--word", "°C", "m²", "a\u0301"])
def test_whole_segment_rejection_does_not_salvage_ascii_suffix(poison):
    """An invalid atom anywhere poisons its segment, even outside the window."""
    text = f"alpha x beta {poison}"
    assert prototype.ordered_window_match(text, "alpha beta") == (False, "no_eligible_segments")
    row = delivered(case(sources=[source(title=text)]))
    assert row["addition_full_ids"] == []
    assert row["ordered_window_additions"]["state"] == "no_eligible_segments"


@pytest.mark.parametrize("query", [" alpha beta", "alpha beta ", "alpha 1 beta", "alpha βeta", "alpha",
                                   "alpha\nbeta", "a b c d e f g h i", "alpha--beta gamma"])
def test_unsupported_grammar_retains_real_old_observation_and_null_counts(query):
    """Unsupported normalization is neither unavailable literal data nor zero additions."""
    item = case(query, [source(title=query)])
    row = delivered(item)
    assert row["baseline"] == old.search_saved_candidates(prototype.snapshot_for_case(item), query)
    assert row["ordered_window_additions"]["state"] == "unsupported_query"
    assert row["ordered_window_additions"]["total_count"] is None
    assert row["addition_full_ids"] is None and row["field_scan_states"] is None
    assert row["mechanics_valid"] is True


@pytest.mark.parametrize("query", [None, 1, True, "", " \t", "a" * 257, "alpha\ud800 beta"])
def test_invalid_plain_scalar_query_is_distinct_and_never_scans(query, monkeypatch):
    """Invalid query values cannot silently fall through to another search grammar."""
    monkeypatch.setattr(old, "search_saved_candidates", lambda *_: pytest.fail("invalid query reached baseline"))
    row = prototype.compare_snapshot(prototype.snapshot_for_case(case()), query)
    assert row["ordered_window_additions"]["state"] == "invalid_query"
    assert row["baseline"] is None and row["addition_full_ids"] is None
    assert row["mechanics_valid"] is False


def test_supported_two_to_eight_atoms_and_query_length_limit():
    """A supported long query can run the new lane even when the old lane abstains."""
    for query in ("a b", "a b c d e f g h", "a" * 254 + " b"):
        assert prototype.ordered_window_match(query, query)[1] in {"matched", "eligible_no_match"}
    row = delivered(case("a b c d e", [source(title="a x b x c x d x e")]))
    assert row["baseline"]["normalized_additions"]["state"] == "unsupported_query"
    assert row["baseline_audit"]["separator_full_ids"] is None
    assert row["addition_full_ids"] == ["A1"]


def test_field_and_source_join_mutations_would_fail_delivered_membership():
    """Assert actual result membership, not just explanatory field names."""
    item = case(sources=[source("A1", "alpha", "beta"), source("A2", "alpha"), source("A3", "beta")])
    row = delivered(item)
    assert row["addition_full_ids"] == []
    assert row["ordered_window_additions"]["hits"] == []
    assert row["ordered_window_additions"]["state"] == "eligible_no_match"


def test_casefold_mutation_would_fail_at_new_lane_delivery_not_only_helper():
    """The baseline has no contiguous hit that could mask an erroneous new hit."""
    row = delivered(case(sources=[source(title="Alpha x beta")]))
    assert row["baseline_audit"]["full_ids"] == []
    assert row["addition_full_ids"] == []
    assert row["ordered_window_additions"]["hits"] == []


def test_actual_baseline_call_unchanged_bytes_and_metadata(monkeypatch):
    """Real baseline metadata and flags survive the JSON boundary unchanged."""
    item = case(sources=[source("A1", "alpha beta", None), source("A2", "alpha beta", ""),
                         source("A3", "alpha beta", " \t"), source("A4", "alpha-beta", "saved")])
    # Rebuild the original measure_baseline.py projection independently. Using
    # snapshot_for_case here would hide hash drift from changed metadata defaults.
    snapshot = ReportEvidenceSnapshot(report_ref=item["case_id"], sources=tuple(
        SnapshotSource(**s, group="academic", publisher="Fictional offline controls",
                       source_type="synthetic_control", accessed_date="2026-09-27")
        for s in item["sources"]
    ))
    expected = old.search_saved_candidates(snapshot, item["query"])
    real_search, entries = old.search_saved_candidates, []

    def record(snapshot, query):
        entries.append((snapshot, query))
        return real_search(snapshot, query)

    monkeypatch.setattr(old, "search_saved_candidates", record)
    row = delivered(item)
    assert len(entries) == 1 and type(entries[0][0]) is ReportEvidenceSnapshot
    assert entries[0][1] == item["query"]
    assert old.render_candidate_result(row["baseline"]) == old.render_candidate_result(expected)
    assert row["baseline"]["source_observation"] == {
        "source_count": 4, "missing_summary_count": 1, "empty_summary_count": 1,
        "whitespace_only_summary_count": 1,
    }
    hits = row["baseline"]["literal_result"]["hits"]
    assert [h["stored_length"] for h in hits] == [0, 0, 2]
    assert [h["text_status"] for h in hits] == ["missing_text", "missing_text", "available"]


@pytest.mark.parametrize("lane", ["literal_result", "normalized_additions"])
@pytest.mark.parametrize("mutation", ["total", "prefix", "metadata", "truncated", "state", "bool_total"])
def test_real_old_response_drift_is_unavailable_not_zero_or_mechanical_pass(lane, mutation, monkeypatch):
    """Both old lanes' totals, exact visible metadata and states are checked."""
    real_search = old.search_saved_candidates

    def drift(snapshot, query):
        result = real_search(snapshot, query)
        target = result[lane]
        if mutation == "total":
            target["total_count"] += 1
        elif mutation == "prefix":
            target["hits"][0]["source_id"] = "A99"
        elif mutation == "metadata":
            target["hits"][0]["stored_length"] += 1
        elif mutation == "truncated":
            target["truncated"] = True
        elif mutation == "state":
            target["status" if lane == "literal_result" else "state"] = "unavailable"
        else:
            target["total_count"] = True  # True == 1 must not conceal type drift.
        return result

    monkeypatch.setattr(old, "search_saved_candidates", drift)
    row = delivered(case(sources=[source("A1", "alpha beta"), source("A2", "alpha-beta")]))
    assert row["baseline"] is not None
    assert row["baseline_equal"] is False and row["mechanics_valid"] is False
    assert row["ordered_window_additions"]["state"] == "unavailable"
    assert row["ordered_window_additions"]["total_count"] is None
    assert row["baseline_audit"] is None and row["addition_full_ids"] is None


def test_hidden_both_old_lanes_really_match_new_lane_but_are_all_masked():
    """Legal A IDs include genuine candidate matches beyond BOTH five-hit caps."""
    sources = [source(f"A{i}", "alpha beta", "alpha x beta") for i in range(1, 8)]
    sources += [source(f"A{i}", "alpha-beta", "alpha x beta") for i in range(8, 15)]
    assert all(prototype.ordered_window_match(s["summary"], "alpha beta")[0] for s in sources)
    row = delivered(case(sources=sources))
    assert row["baseline_audit"]["literal_full_ids"] == [f"A{i}" for i in range(1, 8)]
    assert row["baseline_audit"]["separator_full_ids"] == [f"A{i}" for i in range(8, 15)]
    for lane in ("literal_result", "normalized_additions"):
        assert row["baseline"][lane]["total_count"] == 7
        assert row["baseline"][lane]["truncated"] is True
        assert len(row["baseline"][lane]["hits"]) == 5
    assert row["addition_full_ids"] == [] and row["addition_match_fields"] == {}
    assert row["ordered_window_additions"]["state"] == "matches_masked_by_baseline"


def test_full_additions_metadata_and_hidden_false_candidate_survive_cap():
    """A sixth distractor must fail gate 3 even though the visible five are positive."""
    sources = [source(f"A{i}", summary="private summary bytes") for i in range(1, 8)]
    row = delivered(case(sources=sources, acceptable=[f"A{i}" for i in range(1, 6)], uncertain=["A7"]))
    lane = row["ordered_window_additions"]
    assert lane["total_count"] == 7 and lane["truncated"] is True
    assert lane["hits"] == [old._hit(s) for s in prototype.snapshot_for_case(case(sources=sources)).sources[:5]]
    assert row["addition_full_ids"] == [f"A{i}" for i in range(1, 8)]
    assert "private summary bytes" not in prototype.render_comparison(row).decode()
    summary = prototype.summarize([row])
    assert summary["gates"]["3_zero_definite_added_nonreferences"] == "failed"
    assert summary["returned_ids"]["addition_nonreference"] == [{"case_id": "T1", "source_id": "A6"}]
    assert summary["returned_ids"]["addition_uncertain"] == [{"case_id": "T1", "source_id": "A7"}]
    assert summary["visible_returned_ids"]["addition_nonreference"] == []
    assert summary["visible_returned_ids"]["addition_uncertain"] == []


def test_full_visible_question_and_per_reference_coverage_include_old_false_uncertain():
    """Hidden old positives affect baseline coverage; hidden additions affect new coverage."""
    old_row = delivered(case(sources=[source(f"A{i}", "alpha beta") for i in range(1, 8)],
                             acceptable=["A6"], uncertain=["A7"], case_id="OLD"))
    new_row = delivered(case(sources=[source(f"A{i}") for i in range(1, 8)],
                             acceptable=["A6"], uncertain=["A7"], case_id="NEW"))
    summary = prototype.summarize([old_row, new_row])
    assert summary["question_coverage"]["full"]["baseline"] == {"covered": 1, "unknown": 0, "denominator": 2}
    assert summary["question_coverage"]["visible"]["baseline"]["covered"] == 0
    assert summary["question_coverage"]["full"]["combined"]["covered"] == 2
    assert summary["question_coverage"]["visible"]["combined"]["covered"] == 0
    assert summary["reference_coverage"]["full"]["combined"] == {"covered": 2, "unknown": 0, "denominator": 2}
    assert summary["newly_covered_positive_cases"] == ["NEW"]
    assert len(summary["returned_ids"]["baseline_nonreference"]) == 5
    assert summary["returned_ids"]["baseline_uncertain"] == [{"case_id": "OLD", "source_id": "A7"}]
    assert summary["visible_returned_ids"]["baseline_uncertain"] == []


def test_no_eligible_no_match_masked_and_missing_saved_fields_stay_distinct():
    """No-eligible is not a substring-based eligible-negative observation."""
    rows = [delivered(case(sources=[source(title=t, summary=s)], case_id=str(i)))
            for i, (t, s) in enumerate([("123", None), ("unrelated", ""), ("alpha beta", " \t"), ("123", " ")])]
    assert [r["ordered_window_additions"]["state"] for r in rows] == [
        "no_eligible_segments", "eligible_no_match", "matches_masked_by_baseline", "no_eligible_segments",
    ]
    assert [r["field_scan_states"][0]["summary"] for r in rows] == [
        "missing_field", "empty_field", "whitespace_only_field", "whitespace_only_field",
    ]
    summary = prototype.summarize([rows[0], rows[3]])
    assert summary["eligible_definite_distractors"] == []
    assert summary["gates"]["4_eligible_definite_distractor"] == "unproven"
    assert prototype.summarize([rows[1]])["gates"]["4_eligible_definite_distractor"] == "passed"
    assert prototype.summarize([rows[2]])["gates"]["4_eligible_definite_distractor"] == "passed"


def test_snapshot_is_detached_before_actual_baseline_call(monkeypatch):
    """Changing the caller's frozen-model internals cannot change admitted data."""
    snapshot = prototype.snapshot_for_case(case())
    real_search = old.search_saved_candidates

    def mutate_original(trusted, query):
        assert trusted is not snapshot and trusted.sources[0] is not snapshot.sources[0]
        snapshot.sources[0].__dict__["title"] = "replaced"
        return real_search(trusted, query)

    monkeypatch.setattr(old, "search_saved_candidates", mutate_original)
    row = json.loads(prototype.render_comparison(prototype.compare_snapshot(snapshot, "alpha beta")))
    assert snapshot.sources[0].title == "replaced"
    assert row["addition_full_ids"] == ["A1"]
    assert row["ordered_window_additions"]["hits"][0]["title"] == "alpha x beta"


@pytest.mark.parametrize("defect", ["type", "source_id", "title", "summary", "duplicate", "count", "total_summary"])
def test_constructed_snapshot_bypasses_are_revalidated_against_current_capacity(defect, monkeypatch):
    """model_copy/model_construct cannot bypass original bounded snapshot validation."""
    snapshot = prototype.snapshot_for_case(case())
    valid = snapshot.sources[0]
    if defect == "type":
        snapshot = snapshot.model_dump()
    elif defect in {"source_id", "title", "summary"}:
        value = {"source_id": "A0", "title": "x" * 1025, "summary": "x" * 100001}[defect]
        snapshot = snapshot.model_copy(update={"sources": (valid.model_copy(update={defect: value}),)})
    elif defect == "duplicate":
        snapshot = snapshot.model_copy(update={"sources": (valid, valid)})
    else:
        count = 257 if defect == "count" else 11
        sources = tuple(valid.model_copy(update={"source_id": f"A{i + 1}",
                                                 "summary": "x" * 100000 if defect == "total_summary" else None})
                        for i in range(count))
        snapshot = ReportEvidenceSnapshot.model_construct(report_ref="bad", sources=sources)
    monkeypatch.setattr(old, "search_saved_candidates", lambda *_: pytest.fail("invalid snapshot reached baseline"))
    row = prototype.compare_snapshot(snapshot, "alpha beta")
    assert row["ordered_window_additions"]["state"] == "unavailable"
    assert row["addition_full_ids"] is None and row["baseline"] is None
    assert row["mechanics_valid"] is False


def test_actual_bounded_renderer_and_failure_preserve_full_payload(monkeypatch):
    """The real renderer rejects full bytes; no lane or audit is shortened to pass."""
    result = prototype.compare_fixture(fixture(), delivery_limit=1)
    assert result["delivery"]["state"] == "unavailable"
    assert result["summary"]["mechanics_valid"] is False
    assert result["cases"][0]["addition_full_ids"] == ["A1"]
    assert result["summary"]["gates"]["1_baseline_boundaries_accounting"] == "failed"
    with pytest.raises(ValueError, match="delivery bound"):
        prototype.render_comparison(result)
    big = {"metadata": "x" * old.RESULT_MAX_BYTES}
    with pytest.raises(ValueError, match="delivery bound"):
        prototype.render_comparison(big)
    real_render, entries = old.render_candidate_result, []

    def renderer(value):
        entries.append(value)
        return real_render(value)

    monkeypatch.setattr(old, "render_candidate_result", renderer)
    assert json.loads(prototype.render_comparison({"selection": None})) == {"selection": None}
    assert entries == [{"selection": None}]


def test_aggregate_renderer_overflow_is_explicit_without_trimming_cases():
    """Bounded individual lanes can still overflow the full twelve-row delivery."""
    data = fixture()
    for item in data["cases"]:
        item["sources"] = [source(f"A{i + 1}", "\u4e00" * 1000, "alpha beta") for i in range(7)]
        item["acceptable_ids"], item["uncertain_ids"] = ["A1"], []
    result = prototype.compare_fixture(data)
    assert result["delivery"]["state"] == "unavailable" and len(result["cases"]) == 12
    assert all(r["baseline"]["literal_result"]["total_count"] == 7 for r in result["cases"])
    with pytest.raises(ValueError, match="delivery bound"):
        prototype.render_comparison(result)


def test_null_unsupported_and_unavailable_aggregation_never_crashes_or_claims_zero():
    """Keep every positive in the denominator when its addition observation is null."""
    data = fixture()
    data["cases"][0]["query"] = "one"
    data["cases"][1]["sources"][0]["title"] = "x" * 1025
    result = json.loads(prototype.render_comparison(prototype.compare_fixture(data)))
    summary = result["summary"]
    assert summary["positive_denominator"] == 11 and summary["positive_reference_denominator"] == 11
    assert summary["unobserved_addition_cases"] == ["T1", "T2"]
    assert summary["full_addition_count"] is None and summary["full_nonreference_count"] is None
    assert summary["observed_addition_count"] == 10
    assert summary["question_coverage"]["full"]["combined"]["unknown"] == 2
    assert summary["gates"]["1_baseline_boundaries_accounting"] == "failed"
    assert summary["gates"]["3_zero_definite_added_nonreferences"] == "unproven"


def test_new_question_gains_exclude_already_covered_and_do_not_borrow_masked_fields():
    """More references in an already covered question are not new-question coverage."""
    rows = [delivered(case(sources=[source("A1", "alpha beta"), source("A2", summary="alpha x beta")],
                           acceptable=["A1", "A2"], case_id="COVERED")),
            delivered(case(sources=[source("A1", "alpha beta", "alpha x beta"), source("A2")],
                           acceptable=["A2"], case_id="GAIN"))]
    summary = prototype.summarize(rows)
    assert summary["newly_covered_positive_cases"] == ["GAIN"]
    assert summary["new_gain_fields"] == ["title"]
    assert summary["gates"]["2_new_positive_questions"] == "failed"
    assert rows[1]["addition_match_fields"] == {"A2": ["title"]}


def test_computed_gates_references_uncertainty_and_control_provenance():
    """Positive controls meet only measured gates; no fabricated boundary attestation."""
    data = fixture()
    result = json.loads(prototype.render_comparison(prototype.compare_fixture(data)))
    summary = result["summary"]
    assert summary["newly_covered_positive_cases"] == [f"T{i + 1}" for i in range(11)]
    assert summary["new_gain_fields"] == ["summary", "title"]
    assert summary["gates"] == {
        "1_baseline_boundaries_accounting": "unproven", "2_new_positive_questions": "passed",
        "3_zero_definite_added_nonreferences": "passed", "4_eligible_definite_distractor": "passed",
    }
    assert summary["boundary_control_evidence"] == "not_run_here"
    assert summary["returned_ids"]["addition_uncertain"] == [{"case_id": "T12", "source_id": "A1"}]
    assert summary["positive_denominator"] == 11 and summary["uncertain_case_count"] == 1
    assert result["selection"] is None and result["semantic_support"] == result["unit_equivalence"] == "not_assessed"
    changed = deepcopy(data["cases"][0])
    changed["acceptable_ids"], changed["uncertain_ids"] = [], ["A2"]
    left, right = delivered(data["cases"][0]), delivered(changed)
    left.pop("reference")
    right.pop("reference")
    assert left == right


def test_empty_snapshot_and_malformed_fixture_identity():
    """An empty valid snapshot is observed, but cannot prove an eligible negative."""
    row = delivered(case(sources=[]))
    assert row["baseline"]["normalized_additions"]["state"] == "empty_snapshot"
    assert row["ordered_window_additions"]["state"] == "no_eligible_segments"
    assert row["addition_full_ids"] == []
    data = fixture()
    data["cases"][1]["case_id"] = data["cases"][0]["case_id"]
    with pytest.raises(ValueError, match="duplicate case"):
        prototype.validate_fixture(data)


def test_default_cli_is_identity_only_and_cannot_execute_frozen_cohort(monkeypatch, capfdbinary):
    """Hash checking is permitted; frozen matching from self-tests is forbidden."""
    monkeypatch.setattr(prototype, "compare_fixture", lambda *_args, **_kwargs: pytest.fail("cohort evaluated"))
    monkeypatch.setattr(prototype, "_case_comparison", lambda *_: pytest.fail("case evaluated"))
    monkeypatch.setattr(sys, "argv", ["prototype.py"])
    assert prototype.main() == 0
    result = json.loads(capfdbinary.readouterr().out)
    assert result["state"] == "identity_only" and result["fixture_sha256"] == prototype.FIXTURE_SHA256
    assert "cases" not in result
