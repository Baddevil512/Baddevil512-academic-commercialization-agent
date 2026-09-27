# Offline ordered-window candidate comparison

Registered before prototype implementation from
`45bfc49ce1a255996e21d14fd2a07b4f6e8208d2` on 2026-09-27.
Method: `ordered_window_conjunction_v1`. This is a zero-provider development
comparison after the [closed NQ failure](results-2026-09-27-candidate-query-synthetic-canary.md),
not a repair or replay of that batch. No credential access, model call, external
search, production route, source read, answer generation or scoring change.

## Single changed variable

Keep every supplied query, source field and source order unchanged. The baseline
is the complete frozen literal-plus-separator result. The candidate preserves
that result and adds one separately reported matching lane. Only search
interpretation changes, exactly as defined below; supplied queries, source
bytes, proposer and baseline remain unchanged. Matching requires **ordered,
nearby co-occurrence**, not arbitrary unordered AND.
No proposer, QUERY_POLICY, native request, stemming or casefold behavior changes.
Testing a shorter model-generated query would change another component and is
therefore deferred. This comparison cannot measure model query generation.

## Frozen candidate rule

- Validate a plain nonblank Unicode-scalar query of at most 256 characters.
- Candidate grammar: 2-8 atoms separated by one or more ASCII spaces/tabs.
  Each atom is `[A-Za-z]+(?:-[A-Za-z]+)*`; no leading/trailing whitespace.
- Match exact case. A hyphenated compound is one indivisible atom. No Unicode,
  sign, unit, number, plural, stemming or abbreviation equivalence is inferred.
- Search each title and summary separately, never concatenate fields/sources.
- Hard boundaries are ASCII `.,;:!?()[]{}"'` and any whitespace other than ASCII
  space/tab. No match crosses a boundary.
- Split each nonempty segment into complete space/tab-delimited atoms. If any
  whole atom fails the grammar, the whole segment is ineligible; do not salvage
  an ASCII suffix from a number, Unicode word, slash, sign or compound.
- Query atoms must occur in order at distinct positions. Repeated atoms require
  repeated occurrences. From the first start to final end the original span is
  at most **128 Unicode code points**, including intervening spaces/words.
- Titlecase/plural/order differences cause a miss, not an unsupported query.
  A grammar-supported query need not find a valid match.

This window is a preselected engineering constraint, not a calibrated relevance
threshold. Same-segment proximity can still join unrelated relations; no
semantic or negation rule will be added after results are observed.

## Output and denominator contract

Revalidate/detach the snapshot before comparison, retaining current capacity
limits. Call the unchanged baseline. Reconstruct both old lanes' complete
membership and require consistency with their totals/visible prefixes. Remove
ALL those members from new additions, including hidden sixth and later hits.
A mismatch is unavailable comparison, not zero new candidates.

Keep baseline fields intact. New additions have their own total/truncation and
at most five visible saved metadata records in source order; do not merge or
rank the lanes. An offline audit may record complete addition IDs and matched
field names to measure false candidates beyond the visible cap, but never
excerpts or claimed support. Use the existing bounded JSON renderer; oversized
delivery is an explicit failure, not silent truncation to make a gate pass.
Keep `selection=null`, semantic support and unit equivalence `not_assessed`.

Separate invalid input, unsupported new grammar, no eligible segments, eligible
scan with no match, matches entirely masked by the baseline, actual additions
and unavailable observation. Keep missing/empty/whitespace-only saved fields
distinct through baseline metadata. Unsupported observations use null counts,
not invented zero failures. Old literal casefolded matches are not repaired or
promoted to unit equivalence by this new lane.

## Fresh fixed development data and provenance

Twelve fictional tasks were authored in a separate worker context without
seeing the matcher design or old NQ fixtures. A second LLM saw only questions,
queries and source fields, not draft references, method or results. Its review
agreed on eleven positive reference sets and marked C08/A1 uncertain: tension
measurement and guided-wave damage inspection are both mentioned, but their
relationship is not specified. Keep that disagreement and uncertainty rather
than manufacturing a positive or negative label.

The frozen fixture SHA-256 is
`3e92ab315981a9cdd4ef2b172428cca2b540e2c63cb7691f945f0210c994a747`.
Raw author/reviewer replies stay local. The final fixture contains only fictional
task data and explicit positive/uncertain sets, not real reviewer submissions.
Private reference prompt SHA-256:
`37c9fc0ff2f88f6f92211b9c0ad5294bd72ef9c5300611105eb1f140775b77e7`;
response SHA-256:
`1c6e7e53190987645bb53951eaa1c8d9fcf2c08c7212998b4a5d7333e13062a6`.
Requested roles were worker Terra/medium and reviewer Astra/high; effective
backend metadata is unavailable. No external sources or project-provider calls.

The author's suggested challenge names are not verified token inventories.
Natural titlecase, plurals, synonyms and missing literal query words are kept,
even when unfavorable to this intentionally narrow rule. No question/query or
source field will be rewritten after implementation. All twelve cases remain
in the table: eleven positive questions, one uncertain-only question, eleven
positive source IDs, one uncertain source ID and twelve definite distractors.
The uncertainty case is excluded only from the positive-reference denominator,
not from mechanical observation or visibility reporting.

## Gates fixed before execution

1. Baseline preservation, all boundary/serialization controls and accounting of
   all twelve comparison observations succeed.
2. At least **two newly covered positive questions**, with at least one gain
   from a title and one from a summary. All eleven positive questions stay in
   the denominator, including unsupported or missed cases.
3. **Zero definite nonreference IDs in the complete additions**, not merely in
   their visible prefix. Also report baseline nonreference IDs and uncertain
   returned IDs separately; uncertainty is never forced into either class.
4. At least one definite distractor is actually examined with a supported query
   and an eligible nonempty field segment. Abstaining on every negative is not
   evidence of precision. Missing required observations leave a gate unproven.

Report mechanical invariant status, old/new coverage, new gains, per-reference
ID coverage, full added nonreference IDs, uncertain IDs, scan/abstention states
and truncation separately. A literal hit is never a declaration of relevance.
Do not invent a percentage accuracy from this tiny author-created data set.
Failure closes this comparison. Do not tune the rule or references to make
this cohort pass; preserve the failed result.

## Implementation, verification and publication boundary

Implement a compact prototype and explicit self-tests first in an ignored
`outputs/` directory after the whole-suite baseline passes. No package/API or
provider integration follows. Test positive windows, repeated/overlapping starts,
128/129-span boundaries, field/segment/compound/Unicode/unit safety, unavailable
states, hidden baseline membership, full addition counts and output-byte bounds.
Reinject representative field-join, casefold and hidden-prefix masking defects;
the real boundary assertions must fail. Test results are engineering controls,
not reference agreement or model quality.

The exact prototype, fictional fixture, self-tests and measured output may be
copied into a clearly isolated frozen `evals/` reproduction archive after
review. This is not promotion to production or an automatically collected new
runtime test suite. Raw review transcripts remain private. Publish the qualified
decision and identities, run final regression/latest Ruff/narrow Pylint, and
wait for CI. No permission for paid execution or rollout follows from either
an offline pass or a merge.
