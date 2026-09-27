# NQ native result: protocol works, candidate coverage fails

Date: 2026-09-27. Execution commit:
`75cb31d8676ba2d84d84be7589b321094e504d6a`.
The [pre-registered NQ batch](prereg-2026-09-26-candidate-query-synthetic-canary.md)
ran once after the frozen implementation passed independent review, full
offline regression and all eight [CI checks](https://github.com/shuxiachai/academic-commercialization-agent/actions/runs/36285818611).
The execution revision was the committed PR HEAD, not a later result-document
commit. The fixed output is occupied and closed; no retry, new directory,
query repair or reuse of this allowance is permitted.

## Result and actual proposals

Four sequential requests completed with reported model `qwen3.5-plus` and
known coherent usage. Three replies contained admitted native query tool calls;
one contained the strict no-call decline. The three proposed queries each
triggered one local saved-title/summary search. No source read, second model
turn, generated answer, supplemental search or production activation occurred.

| Gate | Observed | Pre-registered requirement |
|---|---:|---:|
| Mechanical/identity/accounting/case publication | 4/4 | 4/4 |
| Positive-case visible candidate coverage | 1/3 | 3/3 |
| Explicit no-search decline | 1/1 | 1/1 |
| Combined development gate | **Failed** | All gates pass |

| Case | Unedited admitted proposal | Visible candidates | Reference outcome |
|---|---|---|---|
| NQ01 | `acoustic emission pressurized storage tanks` | none | Missed A1 and A3 |
| NQ02 | `低温再生` | literal A1 | Matched the saved-summary target |
| NQ03 | `laser-induced breakdown spectroscopy scrap metal sorting` | none | Missed A1 |
| NQ04 | `{"action":"decline"}` | no search | Explicit cancellation respected |

NQ01 covered zero of two acceptable IDs; NQ02 one of one; NQ03 zero of one.
There were zero visible nonreference candidates in this native batch, but two
positive searches returned nothing. That is not perfect precision or evidence
that the system detected missing research. No case was unrun, no usage was
unknown and no pending intent remained. Reference misses continued through the
remaining frozen controls as specified; none triggered a retry or repair.

## Why the misses occurred

The English native proposals are keyword combinations rather than contiguous
phrases appearing in the saved records. The unchanged literal lane therefore
has no match. Both proposals also fall outside the deliberately narrow
two-to-four-ASCII-word separator lane, so that lane reports an unsupported
query rather than silently interpreting the proposal as AND search or changing
case. This is a query/search-contract mismatch, not an HTTP or JSON failure.

Keep the pre-live NQ03 observation distinct: the earlier scripted query
`laser-induced breakdown spectroscopy` returned the soil-testing distractor A2
and missed capitalized, space-separated A1. The actual longer native proposal
returned **no candidates**. It would be inaccurate to attribute the actual
empty result solely to the earlier case/separator issue or claim the native
batch returned that distractor.

The Chinese short phrase reached A1 through its saved summary even though its
title did not contain the phrase. That establishes one observed local match,
not semantic support for a scientific claim. The decline control explicitly
asked not to search; it does not establish evidence-insufficiency judgment.

## Usage, limits and data boundary

| Quantity | Observation |
|---|---:|
| Aggregate reserved slots / native intents / reported responses | 4 / 4 / 4 |
| Native query tool calls / no-call declines | 3 / 1 |
| Local candidate searches / source reads | 3 / 0 |
| Reported input tokens | 1,899 |
| Reported output tokens | 97 |
| Reported total tokens | 1,996 |
| Reported-use estimate under frozen rates | USD 0.001421807 |
| Conservative budget consumption | USD 0.044597248 |
| Authorized aggregate soft stopping line | USD 0.05 |

The estimate and reservation are different quantities. The price basis is the
frozen engineering policy, not a current retail-price lookup or provider
invoice; billing remains `not_observed`. Unused reservation is not permission
for another request. Runner elapsed time before summary publication was about
24.67 seconds and includes identity, filesystem and local-search work; it is
not isolated model latency or a production SLO measurement.

Only the current synthetic question and existing fixed controls were prompt
content. The twelve fictional local source records, titles, summaries,
reference labels, case IDs and resulting candidates were not sent as prompt
data. Only the authorized project `DASHSCOPE_API_KEY` assignment was selected
for temporary injection in the one-shot process. Its launcher restored the
environment and left a credential-free used-attempt marker. No key or key hash
was printed or persisted; no other provider setting was resolved.

The operator launcher passed 45 fake-key controls and a separate read-only
review before use. It did not modify the frozen runner or bypass its identity,
budget, publication or first-mechanical-failure stop gates. Neither its scope
label nor a CLI acknowledgement independently verifies consent or remote CI;
those were separately checked by the parent operator.

The pre-run launcher test result was reported by its implementer; the separate
reviewer inspected the helper bytes, and the operator matched their hash before
execution. A post-run read-only audit recomputed journal bindings and arithmetic.
The same 45 fake-key controls were also repeated after the run on unchanged
helper bytes. That saved log is post-run confirmation, not a pre-run artifact or
a replacement for the earlier review.

## Reproducibility and evidence limits

- Fixture SHA-256: `e4d4889f0b8e352bd448b6e2618201414408c79c2f274a1b399388db7e144afb`.
- Ordered request-preview SHA-256: `1b1f5ca4042466e4b68be5d62570f78d26449cfee933e41e884b3189b37fa574`.
- Recorded summary-file SHA-256: `7ab8e3287e699e107fb0cf15b35794510537d7c845871f9f2b668125aed3b4e5`.

Each native journal contains one complete reserve/finish pair with matching
request bytes/hash, accepted reported model identity and complete reported
usage. These are code-owned journal observations, not independent packet
capture, backend-weight attestation or billing-statement verification.
The raw published preview file includes a newline; its file hash is not the
canonical ordered-preview hash above. Do not silently substitute either one.

All source, fixture, reference and protocol bytes stayed unchanged during the
batch. The set-valued references were authored and independently label-blind
reviewed by LLMs before use; they are not human expert gold. NQ03 was already
a known diagnostic challenge. These four dependent synthetic controls are not
an unseen test set, general model accuracy, verified research evidence, user
adoption or demonstrated decision value.

## Decision and next step

Native Tool Calling and bounded accounting were observed. Useful candidate
coverage did not meet the frozen requirement, so this method is **not admitted
to production**. Keep the current report pipeline, source viewer, scoring and
closed production execution switches unchanged.

The next useful work is offline: specify whether a new query contract means
one literal phrase or a bounded conjunction of terms, then compare the chosen
successor with the unchanged literal baseline using fresh positive, negative,
case and unit-sensitive controls. Use this batch for failure diagnosis only.
Do not change both the model proposal and search interpretation at once, tune
these consumed references into a claimed validation pass, or spend on another
batch before that contract and its gates are frozen.
