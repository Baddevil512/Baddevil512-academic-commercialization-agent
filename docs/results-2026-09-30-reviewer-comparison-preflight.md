# Reviewer comparison: stopped before native dispatch

Date: 2026-09-30. Disposition: closed pre-dispatch failure; native semantic
effectiveness remains unmeasured.

The [registered protocol](prereg-2026-09-30-reviewer-comparison.md) and
[preparation record](results-2026-09-30-reviewer-comparison-preparation.md)
remain unchanged. Three fresh fictional pairs compare old/current Reviewer
instructions using actual correction application/report validation, not the
full production CrewAI workflow.

## Frozen identity and observed attempt

The isolated preparation is retained at
[`aa1c591526db40683413073e3c759ab690e7b013`](https://github.com/shuxiachai/academic-commercialization-agent/tree/aa1c591526db40683413073e3c759ab690e7b013/evals/reviewer_comparison_v1).
Its preparation PR #185 is not merged into main. Runner, fixture, manifest and
tests remain at that immutable revision rather than adding a consumed batch's
shared-source hash pins to the default maintenance suite.

- Fixture SHA-256: `4ee81119c3e680e96c8904ac0946e6d96a91a06fd5a84fd101966809301fef4a`.
- Manifest SHA-256: `175b297c2bad813494c3d8a3a0bf0a553de38b0533614232d93228ed51be13ba`.
- Execution identity: `d3e0a6900e44d836ea9e68214b26780a84af918cffbd6e472009477c69eaaa84`.
- [Preparation CI 36681459415](https://github.com/shuxiachai/academic-commercialization-agent/actions/runs/36681459415): all eight jobs succeeded, including four platform/Python cells, coverage, lint, Chromium and Docker.

The identity-only command reported the exact commit and an unoccupied output.
One authorized live CLI invocation then exited 1 with the safe category
`invalid_key_assignment`. The executor had written its identity, manifest and
one durable `claimed` event before reading the narrowly selected credential.
The journal contains no reservation, observed response or completed delivery.
The native output contains only those three initial files, with no responses
or answer artifacts.

The error category is an operator-observed CLI fact; the frozen journal does
not persist that pre-key termination category. It is not a stored terminal
event or provider rejection. A separate value-free syntax check found one
selected assignment of admissible length with punctuation outside the
executor's accepted grammar. It disclosed no key or other credential and did
not modify `.env`. This does not establish that the credential itself is
invalid at the provider, and does not diagnose production configuration.

## Accounting and review scope

| Observation | Result |
|---|---|
| Authorized native ceiling | Six sequential requests; USD 0.10 soft stop |
| Batch claims | 1 |
| Per-request reservations / native POSTs | 0 / 0 |
| Mechanically delivered reports | 0 |
| Observed input / output tokens | 0 / 0 |
| Known batch engineering estimate | USD 0; no request reached dispatch |
| Provider invoice observation | Not performed |
| Blind semantic judgment | `not_run`; all six planned deliveries are `not_reviewable` |
| Semantic gain or regression | Unmeasured, not a pass or model-quality failure |

A fresh read-only LLM audit checked the frozen identities, persisted artifacts
and key-failure control flow. Credential parsing precedes client creation, the
execution loop and any reservation/POST. That control flow plus the CLI and
artifacts supports zero native calls in this attempt; no packet capture or
provider invoice was obtained. The audit did not read credentials, call a
provider, execute tests or grade nonexistent answers. Requested role was
`route_reviewer` (configured Astra/high); effective backend model metadata was
unavailable. This is a mechanical audit, not blind semantic approval.

An arm-hidden closeout packet records six undelivered items. No semantic judge
was invoked merely to manufacture six ratings. Missing observations are not
successful corrections, source support or paired improvement.

## Closure and next boundary

The fixed output remains occupied and the batch is closed. No retry, directory
replacement, credential rewrite, search, repair, fallback or production
activation followed. Production Reviewer instructions and historical reports,
scoring and closed Tool Calling experiments remain unchanged.

Any successor must first resolve the local selected-variable syntax safely. A
credential accepted by the provider but rejected by this narrow grammar needs
a separately reviewed parser/identity, not relaxation of the consumed batch.
Before another dispatch, freeze a new committed execution identity and output,
verify isolation and applicable budget/data authority, and obtain green CI.
Do not retune consumed controls and call them unseen data. Until actual answers
and the registered blind judgment exist, native prevention of the motivating
factual misinterpretation remains unestablished.
