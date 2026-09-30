"""Scripted comparison controls at the evidence/context/review/disk seams.

These exercise real task guardrails and context aggregation, not native model
reasoning. Prescribed findings, drafts and correction plans cannot establish
that a provider will interpret comparisons correctly or choose these edits.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from crewai import Agent
from crewai.llms.base_llm import BaseLLM

from academic_agent import crew as crew_module
from academic_agent.evidence import EvidenceReport, EvidenceSource
from academic_agent.pipeline_worker import _select_report_and_scores
from academic_agent.run_output import save_report
from academic_agent.source_pipeline import SourceCollection


@dataclass(frozen=True)
class _ComparisonCase:
    name: str
    summary: str
    finding: str
    draft_claim: str
    final_claim: str
    draft_action: str
    final_action: str


_CASES = (
    _ComparisonCase(
        name="physical_difference",
        summary=(
            "During steady flow, the inlet air was 6 degrees C warmer than the "
            "outlet air. This was a spatial temperature difference; no comparison "
            "with a reference thermometer or sensor accuracy limit was reported."
        ),
        finding="The sensor showed a calibration error of 6 degrees C during steady flow.",
        draft_claim="The sensor calibration error was 6 degrees C during steady flow [A2].",
        final_claim=(
            "During steady flow, inlet air was 6 degrees C warmer than outlet air; "
            "sensor calibration error was not established [A2]."
        ),
        draft_action=(
            "Analyst inference: the reported calibration error requires a "
            "0.6 degrees C acceptance threshold before deployment [A2]."
        ),
        final_action=(
            "The accuracy acceptance threshold is not established; a same-quantity "
            "instrument-versus-reference measurement is needed before setting it [A2]."
        ),
    ),
    _ComparisonCase(
        name="true_calibration_error",
        summary=(
            "In a stable bath, the probe read 6 degrees C above a reference "
            "thermometer measuring the same bath temperature. This is a measured "
            "calibration error for that condition, not an acceptance threshold."
        ),
        finding="The probe had a 6 degrees C calibration error against the bath reference.",
        draft_claim=(
            "The probe's calibration error was 6 degrees C against the reference "
            "thermometer in the same stable bath [A2]."
        ),
        final_claim=(
            "The probe's calibration error was 6 degrees C against the reference "
            "thermometer in the same stable bath [A2]."
        ),
        draft_action=(
            "Analyst experiment proposal requiring owner confirmation: test a "
            "0.6 degrees C target, not a threshold derived from the reported "
            "calibration error or an established release requirement [A2]."
        ),
        final_action=(
            "Analyst experiment proposal requiring owner confirmation: test a "
            "0.6 degrees C target, not a threshold derived from the reported "
            "calibration error or an established release requirement [A2]."
        ),
    ),
    _ComparisonCase(
        name="mixed_quantities",
        summary=(
            "Under steady flow, inlet air was 6 degrees C warmer than outlet air. "
            "Separately, in a stable bath the probe read 0.6 degrees C above a "
            "reference thermometer measuring that same bath temperature. No "
            "deployment acceptance threshold was reported."
        ),
        finding="A temperature comparison found a difference of 6 degrees C and another of 0.6 degrees C.",
        draft_claim=(
            "The probe calibration error was 6 degrees C and the inlet-to-outlet "
            "air difference was 0.6 degrees C under steady flow [A2]."
        ),
        final_claim=(
            "The inlet-to-outlet air difference was 6 degrees C under steady flow; "
            "separately, the probe calibration error was 0.6 degrees C against "
            "the reference thermometer in the same stable bath [A2]."
        ),
        draft_action=(
            "Analyst inference: these comparisons establish a 6 degrees C "
            "maximum calibration error for deployment [A2]."
        ),
        final_action=(
            "The deployment threshold is not established; the spatial difference "
            "and bath calibration do not supply acceptance criteria [A2]."
        ),
    ),
    _ComparisonCase(
        name="negative_caveat",
        summary=(
            "During steady flow, inlet air was 6 degrees C warmer than outlet air. "
            "No same-quantity comparison with a reference instrument was made; "
            "the result does not establish calibration error or an accuracy threshold."
        ),
        finding="The spatial air-temperature difference does not establish calibration error.",
        draft_claim=(
            "The 6 degrees C inlet-to-outlet air difference under steady flow "
            "does not establish sensor calibration error [A2]."
        ),
        final_claim=(
            "The 6 degrees C inlet-to-outlet air difference under steady flow "
            "does not establish sensor calibration error [A2]."
        ),
        draft_action=(
            "The accuracy threshold is not established; absence of calibration "
            "evidence is not proof that the sensor has no error [A2]."
        ),
        final_action=(
            "The accuracy threshold is not established; absence of calibration "
            "evidence is not proof that the sensor has no error [A2]."
        ),
    ),
)


class _NoProviderLLM(BaseLLM):
    def call(self, *args, **kwargs):
        raise AssertionError("scripted controls must not invoke a provider")


def _make_crew(monkeypatch, summary):
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    monkeypatch.setenv("CREWAI_TRACING_ENABLED", "false")
    monkeypatch.setenv("CREWAI_TELEMETRY_ENABLED", "false")
    monkeypatch.setattr(
        crew_module, "create_llm", lambda **_: _NoProviderLLM(model="offline-control")
    )

    def source(prefix, source_type, text):
        return EvidenceSource(
            source_id=f"{prefix}2",
            title=f"Synthetic comparison source {prefix}2",
            url=f"https://records.test-domain.org/comparison/{prefix.lower()}2",
            publisher="Synthetic Publisher",
            accessed_date=date(2026, 1, 1),
            source_type=source_type,
            evidence_summary=text,
        )

    collection = SourceCollection(
        topic="Synthetic comparison contract",
        collected_at=datetime(2026, 1, 1, tzinfo=UTC),
        academic_sources=[source("A", "academic_paper", summary)],
        patent_sources=[source(
            "P", "patent",
            "The synthetic patent describes a probe housing; it does not establish measurement accuracy.",
        )],
        market_sources=[source(
            "M", "company_disclosure",
            "The synthetic company describes a monitoring application without specifying an acceptance limit.",
        )],
        academic_queries=["offline academic control"],
        patent_queries=["offline patent control"],
        market_queries=["offline market control"],
    )
    return crew_module.AcademicAgent(collection).crew(), collection


def _analysis(prefix, claim):
    # The model contributes findings, not sources. The real guardrail binds the
    # immutable summary even when a model finding has the wrong interpretation.
    return json.dumps({
        "scope_summary": "Scripted evidence analysis for a comparison delivery control.",
        "findings": [{
            "finding_id": f"{prefix}F{index}",
            "category": "comparison control",
            "claim": statement,
            "claim_type": "observed_fact",
            "source_ids": [f"{prefix}2"],
            "confidence": "medium",
            "commercial_implication": "Acceptance criteria require separate evidence.",
        } for index, statement in enumerate((
            claim,
            "The source provides bounded evidence for this synthetic comparison control.",
            "The source does not establish an owner-approved deployment threshold.",
        ), start=1)],
        "limitations": ["Synthetic scripted control; no native semantic judgment."],
    })


def _draft(case):
    return f"""# Academic Commercialization Assessment: Synthetic comparison

## Executive Summary
The assessment is limited to the supplied comparison evidence [A2].

## 1. Technology Overview & Maturity
{case.draft_claim}

## 2. Patent Landscape & White Spaces
The patent describes a probe housing [P2].
Patent analysis is preliminary research, not legal advice or a freedom-to-operate opinion.

## 3. Target Industries & Use Cases
The company describes a monitoring application [M2].

## 4. Competitive Landscape
The company disclosure does not establish an acceptance limit [M2].

## 5. Commercialization Opportunities & Recommendations
{case.draft_action}

## Evidence Limitations
This is a scripted offline control, not native reasoning or deployment evidence.

## References
[A2] Synthetic comparison source A2.
[P2] Synthetic comparison source P2.
[M2] Synthetic comparison source M2.
"""


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.name)
def test_comparison_context_and_prescribed_replacements_reach_saved_report(
    monkeypatch, tmp_path: Path, case: _ComparisonCase,
):
    """Catch raw-summary loss or lost edits, including dependent gate corrections.

    Scripted true-error and negative-caveat controls also prevent this test
    harness from demanding blanket removal of every mention of sensor error.
    """
    crew, collection = _make_crew(monkeypatch, case.summary)
    evidence_tasks = crew.tasks[:3]
    writer, reviewer = crew.tasks[3:5]
    edits = [
        {"find": old, "replace": new, "reason": "Preserve the comparison and its evidence limits."}
        for old, new in (
            (case.draft_claim, case.final_claim),
            (case.draft_action, case.final_action),
        )
        if old != new
    ]
    scripts = {
        evidence_tasks[0].id: _analysis("A", case.finding),
        evidence_tasks[1].id: _analysis("P", collection.patent_sources[0].evidence_summary),
        evidence_tasks[2].id: _analysis("M", collection.market_sources[0].evidence_summary),
        writer.id: _draft(case),
        reviewer.id: json.dumps({"corrections": edits}),
    }
    received = {}

    def scripted_execute(_agent, task, context=None, tools=None):
        assert task.id not in received, "unexpected retry in scripted seam control"
        received[task.id] = context
        return scripts[task.id]

    monkeypatch.setattr(Agent, "execute_task", scripted_execute)
    outputs = []
    # Serial invocation intentionally excludes parallel scheduling and scoring.
    # Task execution, guardrails and Crew context aggregation remain real.
    for task in crew.tasks[:5]:
        outputs.append(task.execute_sync(context=crew._get_context(task, outputs)))

    assert len(received) == 5
    for prefix, task in zip(("A", "P", "M"), evidence_tasks, strict=True):
        assert isinstance(task.output.pydantic, EvidenceReport)
        payload = json.loads(task.output.raw)
        source = collection.sources_for_prefix(prefix)[0]
        assert payload["sources"][0]["evidence_summary"] == source.evidence_summary
        for target in (writer, reviewer):
            assert task.output.raw in received[target.id], "evidence raw context was lost"
    assert json.loads(evidence_tasks[0].output.raw)["findings"][0]["claim"] == case.finding
    assert writer.output.raw in received[reviewer.id]

    report, scores = _select_report_and_scores(outputs, "wrong fallback")
    assert report == reviewer.output.raw
    assert scores is None  # The scorer is outside this test's scope.
    body, marker, notes = report.partition("\n## Reviewer Notes\n")
    assert marker
    assert notes.count("- Applied:") == len(edits)
    assert "Not applied" not in notes
    if not edits:
        assert notes.strip() == "No corrections required."

    _, path = save_report(body.rstrip(), run_id=case.name, output_root=tmp_path)
    delivered = path.read_text(encoding="utf-8")
    assert case.final_claim in delivered
    assert case.final_action in delivered
    expected = writer.output.raw
    for edit in edits:
        assert edit["find"] not in delivered, "a dependent or primary false claim survived"
        expected = expected.replace(edit["find"], edit["replace"], 1)
    assert delivered == expected.rstrip()  # Unrelated prose/references are preserved too.


@pytest.mark.parametrize("index", (3, 4), ids=("writer", "reviewer"))
def test_loaded_comparison_prompt_contract(monkeypatch, index):
    """Supplementary prompt check: findings alone must not define a comparison."""
    crew, _ = _make_crew(monkeypatch, _CASES[0].summary)
    task = crew.tasks[index]
    for text in (task.prompt(), task.agent.backstory):
        normalized = " ".join(text.lower().split())
        for clause in (
            "sources[].evidence_summary", "measured subject", "reference",
            "comparison conditions", "negative caveats", "physical difference",
            "calibration error", "false premise", "not established",
        ):
            assert clause in normalized
    if index == 4:
        assert "every dependent" in task.description
        assert '"find"' in task.prompt() and '"replace"' in task.prompt()
        assert "at most 20 corrections" in task.description
