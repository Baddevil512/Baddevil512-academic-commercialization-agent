# Reviewer comparison v3: transmitted reason bound violated

Date: 2026-10-10 (Australia/Sydney). Disposition: closed mechanical failure.
One response was received, no report was delivered, and the paired semantic
comparison remains unmeasured.

## Frozen preparation and execution scope

The [v3 protocol](https://github.com/shuxiachai/academic-commercialization-agent/blob/7def0808225dfaeedc9d01ff333e24e0006360dc/docs/prereg-2026-10-01-reviewer-comparison-v3.md) appended the same
complete output contract to both instruction arms, retaining the three inspected
synthetic development cases and six-request order. This is dependent development
evidence, not a fresh held-out evaluation or a comparison of production runs.

The immutable preparation remains outside main at
[`7def0808225dfaeedc9d01ff333e24e0006360dc`](https://github.com/shuxiachai/academic-commercialization-agent/tree/7def0808225dfaeedc9d01ff333e24e0006360dc/evals/reviewer_comparison_v3).
Its manifest SHA-256 is
`9c87ac569a4d0a57dd8b1bb4e7ca1fad2b8b8cd9f334ab77218ddddf0fb8ec01`;
the Windows CPython 3.12.9 execution identity is
`1d2a22ee0d920a29a857f25a826679ac251615839510533dacf09a2c0ab5c70d`.
The fixture remains byte-identical to the frozen v2 preparation.

All eight [ordinary checks](https://github.com/shuxiachai/academic-commercialization-agent/actions/runs/37930376066)
and four [preparation cells](https://github.com/shuxiachai/academic-commercialization-agent/actions/runs/37930376059)
passed before execution. Each preparation cell ran 529 checks with no retained
refusals and status zero. GitHub actually checked out PR merge commit
`2b64fb660481a333e6b9f8a0a3dfa54e8c572001`; its tree exactly matched the reviewed
head. The user explicitly accepted this different-commit/same-tree CI evidence
for this one batch. It was not a merge to main or direct CI checkout of the head.
The [earlier preparation failures](https://github.com/shuxiachai/academic-commercialization-agent/blob/7def0808225dfaeedc9d01ff333e24e0006360dc/docs/results-2026-10-09-reviewer-v3-first-preparation-ci.md)
and [ordinary fixture failures](https://github.com/shuxiachai/academic-commercialization-agent/blob/7def0808225dfaeedc9d01ff333e24e0006360dc/docs/results-2026-10-09-reviewer-v3-linux-preparation-ci.md)
retain their original failed outcomes.

The user authorized one native invocation, using only the frozen synthetic
requests and the fixed `qwen3.5-plus` endpoint, at most six sequential requests
and USD 0.10 soft stop. The runner performed its own local credential syntax
admission before claiming the output; no additional standalone preflight ran.
The native invocation used uv and stopped with exit 1. No retry or repair followed.

## Observed failure

The first request, RC01's before arm, received HTTP 200 with `finish_reason=stop`.
Its JSON has the expected envelope and one correction. Strict local validation
rejected `corrections[0].reason`: 378 Unicode code points exceed the inclusive
maximum of 300. All characters in that field are ASCII, so this is not a
UTF-8/Unicode counting disagreement. The find/replace lengths, 125/176, were valid.

The actual 18,519-byte request included the 1,390-byte common-contract suffix.
Its complete schema matched the source-locked model and explicitly supplied
`reason.minLength=3` and `reason.maxLength=300`. The schema was in system-message
text; the HTTP `response_format` was still `json_object`.
Unlike [v2](results-2026-10-01-reviewer-comparison-v2.md), this observation is not
an omitted-bound failure: the supplied bound was violated. It does not explain
the model's internal cause or establish how any unrun arm would behave.

| Observed fact | Result |
| --- | --- |
| Reserved attempts / response-backed requests | 1 / 1 |
| Input / output tokens | 3,628 / 160 |
| Consumed reservation | USD 0.014548032 |
| Usage estimate at frozen conservative rates | USD 0.002629244; invoice not observed |
| Applied corrections / delivered reports | 0 / 0 |
| Remaining requests | 5 unrun |
| Semantic review / paired gain | `not_run` / unassessed |

The observed and stopped usage rows refer to the same ordinal and count once.
The strict validator stopped before patch application; no final report or blind
packet exists. A proposed edit is not a delivered report and supplies no semantic
rating. Adding the complete schema to the prompt did not ensure compliance in
this observed response. This is not evidence of general incapability or a
semantic comparison between the two instruction arms.

## Closure and next boundary

The fixed native output remains occupied and closed, with its seven original
files unchanged. No reason was clipped, no bound or warning policy relaxed, and
no remaining allowance was reused. Raw requests, responses and review notes stay
private; this document publishes qualified aggregate facts only.

A separate read-only failure diagnosis confirmed the single Pydantic violation.
Its first uv launch failed on cache access; the analyst then used the existing
CPython interpreter directly. That diagnostic launch deviated from the uv
convention and is recorded as such. It did not rerun the native batch or modify
its evidence. There was no deliverable eligible for blind semantic review.

The [offline output-constraint review](reviewer-output-constraint-feasibility.md)
separates documented API features, local validation and unobserved provider
enforcement. It grants no new call, model change, production integration or
permission to reopen this batch. The reviewed preparation remains outside main.
