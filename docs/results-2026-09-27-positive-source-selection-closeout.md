# Positive saved-source selection: close the completed development batch

Closeout date: 2026-09-27. The existing run used frozen commit
`bfe5ac9711f09015405f1eb8e0a40c9b83abf5df`, not this documentation revision.
Its [protocol and executor remain at that immutable revision](https://github.com/shuxiachai/academic-commercialization-agent/blob/bfe5ac9711f09015405f1eb8e0a40c9b83abf5df/docs/prereg-2026-09-26-saved-source-positive-qwen.md)
and [preparation PR](https://github.com/shuxiachai/academic-commercialization-agent/pull/175).
This closeout does not repeat the experiment or import its dedicated runner
and tests into main. Keep its branch, occupied output and historical evidence;
closing a preparation PR neither erases execution nor authorizes another attempt.

## Recorded observations

Four source-guided positive development questions, including two Chinese ones,
used complete saved catalogs of 19 and 23 entries. The author had inspected
the material before writing the questions. Only the question, ID/title catalog
and derived counts went to exact `qwen3.5-plus`. Saved text, reports, references
and assisted keywords stayed local. No new source retrieval occurred.

| Quantity | Existing recorded result |
|---|---:|
| Native requests / dispatch intents / HTTP entries | 4 / 4 / 4 |
| Mechanical checks | 4/4 |
| Frozen development-reference matches | 3/4 |
| Saved-text deliveries / explicit declines | 3 / 1 |
| Unknown-usage requests / unrun cases | 0 / 0 |
| Reported input / output / total tokens | 5,690 / 87 / 5,777 |
| Frozen-rate reported-use estimate | USD 0.003559650 |
| Conservative aggregate reservation | USD 0.044597248 |
| Authorized soft stopping line | USD 0.05 |
| Combined development gate | **Failed: reference mismatch** |

The first three selections belonged to the frozen acceptable sets and delivered
strings matching saved-text lengths and hashes. Those strings may already be
truncated; this is not full-paper access or verified support. The fourth case
declined with no selected ID and zero local reads. This first mismatch occurred
at the last case, so the stop rule left no cases unrun.

No retry, repair, fallback, recovery, extra search, extra paid judging or
production activation followed. The estimate uses recorded usage and frozen
engineering rates, not an invoice. Unused reservation creates no new allowance.

## Why the last decline remains a failed reference gate

The reference's saved text contains qualifications needed by the last question
that are absent from its visible title. This asymmetry plausibly explains a
title-only decline, but no stored model rationale establishes causality. Do
not claim correct reasoning, replace the reference or count the decline as
successful positive coverage.

References are fallible LLM judgments, not human gold. This closeout adds a
fresh-context, **reference-aware post hoc LLM audit**, not a new blind evaluation.
The original labels and denominator remain unchanged. It establishes neither
general accuracy, semantic support, superiority to free assisted keyword lookup,
measured user savings nor adoption.

## Reconciliation and limits

The read-only audit recomputed private packet/preview and embedded input hashes,
checked all 18 recorded source/dependency identities against the frozen Git
revision, and reconciled four reserve/finish event pairs with intents, choices,
local delivery and summary. Token arithmetic and cost estimates agree. Private
hashes, IDs, questions, journals and reviewer artifacts are not published here.

The execution gate record references [eight successful CI checks](https://github.com/shuxiachai/academic-commercialization-agent/actions/runs/36227845563)
on that frozen head and separate implementation/launcher reviews. These are
historical evidence, not new closeout tests. Hardcoded governance booleans
express that the runner does not independently verify consent, remote CI or
review; they are not proof of missing consent or an authorization bypass.

The post hoc reviewer used a requested read-only strong-review role; effective
backend model metadata was unavailable. It inspected local records and frozen
code, made no provider calls, and did not separately revalidate the original
reference-review artifacts. Raw provider responses were not preserved for
independent reconstruction. Accepted-choice journals are not packet capture,
provider-weight attestation or invoice verification.

## Decision

Close the consumed batch as a failed development gate and close its preparation
PR with this result linked. Preserve reproducibility by immutable reference,
without adding another ended experiment to the main test suite. Existing frozen
modules/tests and production behavior remain unchanged. The saved-source wrapper
stays execution-disabled; its separate prepared production acceptance is neither
invalidated nor broadened by this experiment.

The later NQ and ordered-window studies retain their own failed results and
denominators. They do not repair this batch. No new paid run is proposed here.
