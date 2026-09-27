# Ordered-window result: no gain over the unchanged baseline

Date: 2026-09-27. Base revision:
`45bfc49ce1a255996e21d14fd2a07b4f6e8208d2`.
The [fixed offline rule](prereg-2026-09-27-ordered-window-conjunction-offline.md)
was compared on twelve fictional development questions without a model call,
credential read, external search, saved-source read or production modification.
This follows the closed NQ failure but does not rerun or relabel that batch.

## Observation and decision

| Quantity | Old literal + separator | Old lanes + ordered window |
|---|---:|---:|
| Covered positive questions, visible and full | 1/11 | 1/11 |
| Covered acceptable source IDs | 1/11 | 1/11 |
| New candidates / newly covered questions | not applicable | 0 / 0 |
| Returned definite nonreference IDs | 0 | 0 |
| Returned uncertain IDs | 0 | 0 |

C09/A1 was the only positive hit, already found by the literal baseline. C01-C08
and C10-C12 had no baseline candidates; no case gained an ordered-window hit.
Every new lane reported `eligible_no_match`. All twelve queries were supported,
with eligible title and summary segments for all twelve definite distractors.
There were no missing observations, truncated result lanes or hidden additions.
The uncertain C08/A1 reference was retained separately: it neither became a
positive reference nor a definite distractor.

All twelve baseline JSON objects, including snapshot hashes, matched the
pre-prototype baseline exactly. The corrected comparison uses the actual frozen
library, reconstructs both complete memberships, and checks the delivered old
response rather than substituting a handwritten imitation.

| Pre-registered gate | Outcome |
|---|---|
| 1. Baseline, boundary controls and all twelve observations | Passed with separately observed controls |
| 2. At least two new positive questions, including title and summary gains | **Failed: zero gains** |
| 3. Zero definite nonreference IDs in complete additions | Passed; vacuous as evidence of useful precision |
| 4. At least one eligible definite distractor actually examined | Passed: twelve |
| Combined rule | **Failed** |

The raw matcher JSON deliberately leaves gate 1 `unproven`: it cannot attest
external tests or review. The manifest's combined assessment adds those
separately observed engineering facts; it does not rewrite the raw result.
Zero candidates means candidate precision has no returned-item denominator,
not 100% precision. Passing controls does not make this retrieval method useful.

**Decision: close and archive this candidate, without production integration.**
No rule, supplied query or reference was tuned after the outcome. Scoring,
evidence registration, model proposal policy, the Sources viewer, production
saved-source execution switches and all closed provider batches are unchanged.

## What this does and does not explain

Allowing gaps while preserving exact case, atom identity and word order did
not resolve these task queries. Natural source text retained titlecase, plurals,
different word order, compounds and abbreviations rather than being rewritten
to favor the algorithm. For example, the geothermal task asks for `lithium
recovery geothermal brine membrane`, while its title orders membranes,
geothermal brine and lithium recovery differently; its summary also uses
different terms. Nearby-word matching alone is not a general semantic selector.

This rejects this exact rule on these development references. It does not
establish that every conjunction, ranking or shorter-query strategy fails,
isolate one cause across the cohort, or measure model query-generation quality.
All supplied queries were fixed local strings. It would be misleading to
combine this 1/11 result with the separate native NQ 1/3 denominator.

## Verification and a retained procedure deviation

The initial implementation was rejected because it reproduced old predicates
without calling the real baseline and hardcoded successful accounting. Other
issues included eligibility and question-gain counting and a weak hidden-member
test. After two unsuccessful implementation/validation attempts, a separate
strong-tier implementation corrected the evaluator without changing the method.

That initial self-test also inadvertently called the entire twelve-case
comparison. Its author reported no manual result inspection, and no official
outcome was saved. This is a procedural deviation, not evidence of unseen
evaluation. The rejected bytes remain local; corrected self-tests now test only
new engineering fixtures, and their identity-only CLI check forbids cohort
evaluation. Preserve the deviation rather than obtaining a clean label by
renaming the cohort.

Before the corrected measurement, the operator ran all **101** focused controls
successfully and actually injected three defects into process-local copies:

- Joining title and summary produced A1 where the field-boundary test required
  no additions; that assertion failed.
- Casefolding the new lane produced A1 where exact-case delivery required no
  additions; that assertion failed.
- Masking only visible old hits reintroduced A6, A7, A13 and A14; the complete
  membership assertion failed.

Each mutant exited with one pytest assertion failure, not an import or syntax
error. The intact files were never overwritten by these injections. An
independent read-only reviewer inspected the implementation and actual mutation
logs and found no blockers before the corrected recorded measurement. The
requested reviewer role was Astra/high; effective backend metadata is unavailable.
Reference creation/review was also LLM-only and label-blind on the first review;
neither process is human expert gold, source-truth verification or observed use.

The pre-change full suite passed **7341 tests + 1609 subtests**. Final full-suite
and CI outcomes belong to the accompanying change checks; historical totals
are not a substitute for their status. The archive adds no automatically
collected runtime tests, no skips and no pytest configuration change.

The first post-archive full run failed after byte-preservation rules were added
to the root attributes file: frozen canaries correctly rejected its changed
normalization contract. A separate document-index link was also missing. The
minimal correction restores the root file and places four exact-name rules
inside this new archive only, then supplies the missing protocol link. It does
not relax any frozen check or alter source/fixture/result bytes. The failed run
is retained; new full-run and Git byte-roundtrip checks must pass before release.

## Reproduction and next boundary

The [isolated archive](../evals/ordered_window_conjunction_v1/README.md) retains
the exact prototype, fixture, explicitly invoked self-tests, measured JSON and
manifest. Raw reviewers, private project notes and operator paths are excluded.
Fixture SHA-256: `3e92ab315981a9cdd4ef2b172428cca2b540e2c63cb7691f945f0210c994a747`.
Recorded result SHA-256: `7c1aeb499d0cb58ab41ef9bbf006b42fc53cf09e082d340354868242674acc61`.
The four hash-bound artifacts use narrow Git byte-preservation attributes.

Do not spend on another native query batch for this rule or retune it to make
these references pass. First decide whether question-only query generation
is worth pursuing versus the already separately tested catalog-selection route.
Any successor should change one component, freeze its own task distribution and
reference protocol, and demonstrate nonempty useful additions as well as false
candidate control offline. Reusing this cohort is diagnostic development, not
a new independent success claim. No activation or paid permission follows here.
