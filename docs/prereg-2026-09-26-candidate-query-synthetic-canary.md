# NQ: question-only native queries over synthetic saved candidates

Registered before runner implementation from merged
`08ae25cc1b96c39a1a1dc91fcd75820f681a041c` on 2026-09-26.
Protocol identity: `saved_source_candidate_query_canary_v1`.
The [candidate library](saved-source-candidate-search.md) and
[native adapter](prereg-2026-09-26-candidate-query-qwen-transport.md) stay unchanged.
No earlier batch, reference, output or allowance is reopened.

## Question, controls and pre-live observations

Can the exact model emit an admitted native query, and can that unedited query
locate acceptable candidates in a local synthetic collection? Three positive
questions and one explicit cancellation exercise different boundaries. The
model sees ONLY the current question and existing fixed controls, never sources,
case IDs, reference labels, the other questions or local results. These controls
are development data, not unseen evaluation or independent factual truth.

| Case | Control | Frozen acceptable IDs/action |
|---|---|---|
| NQ01 | English acoustic-emission tank inspection | query; A1 or A3 |
| NQ02 | Chinese low-temperature regeneration, relevant text only in summary | query; A1 |
| NQ03 | Laser-induced breakdown spectroscopy for scrap sorting, case/separator challenge | query; A1 |
| NQ04 | Chinese explicit request not to search and to cancel the question | decline; no local search |

Fixture: `tests/fixtures/saved_source_candidate_query_qwen.json`, raw SHA-256
`e4d4889f0b8e352bd448b6e2618201414408c79c2f274a1b399388db7e144afb`.
All twelve sources are newly authored fiction. No real report or user data is
used. A fresh label-blinded LLM context independently chose the sets above from
questions/titles/summaries. It saw no draft labels, queries or prior results.
NQ02 is not restricted to batteries by the question; A1 is simply the available
matching candidate. NQ03's soil-testing and magnetic-sorting records are only
partially relevant and remain outside the acceptable set. Cancellation does not
prove the ability to detect absent evidence. This is not human expert gold.

Requested judge role: `route_reviewer` (configured Astra/high); actual backend
model metadata unavailable. External-source access: none. Private local review
artifacts have UTF-8/LF identities: prompt SHA-256
`ebd5ef730f3f7a79a3480d419a3e7610a36ec1237d53a0c38171921d7b4af149`,
response SHA-256
`fe5221f978e96f226621b39c24d48523ff1c11349594ebd15cbe831526cef14e`.

Before implementation, the existing library was measured with scripted queries:
`acoustic emission` returns A1/A3; the Chinese regeneration phrase returns A1;
lower-case `laser-induced breakdown spectroscopy` returns only the soil record
A2. The lexical lane deliberately preserves case and does not add capitalized
`Laser induced ...` A1. Keep this known failure and the references unchanged;
do not repair case policy, manually shorten the native query or call this a
perfect baseline. A shorter native query might cover A1 while also returning A2.
Coverage and irrelevant-candidate counts must remain separate.

Canonical request bodies measure 1415/1436/1420/1448 bytes. The SHA-256 of
`_encoded([native._request(case['question']) for case in cases])` in frozen order
is `1b1f5ca4042466e4b68be5d62570f78d26449cfee933e41e884b3189b37fa574`.
This is a local byte preview, not evidence of a provider call.

## Dedicated execution and identity

Add one new runner module `saved_source_candidate_query_canary.py` under
`src/academic_agent/` and dedicated tests; use its `python -m` entry point.
Default operation requires expected commit, fixture hash and request-preview
hash and verifies identity only: no credential/environment lookup, HTTP client
or output creation. Execution requires the new exact protocol acknowledgement.
That acknowledgement cannot independently verify user consent, review or CI.

Bind the actual source/dependency closure, package init, `.gitattributes`,
runner/tests, fixture, this protocol, the unchanged candidate/native contracts,
`pyproject.toml`, `uv.lock`, installed relevant dependency versions and fixed
configuration. Compare disk with committed blobs under the repository's fixed
CRLF-to-LF text rule; retain both hashes. Package-version identity is not package
byte attestation. Recheck before AND after each attempted callback, including
failures. Preserve observed usage even when post-call identity validation fails.

Use only process `DASHSCOPE_API_KEY` when explicitly executing; no dotenv read,
fallback provider key or alternate destination. The parent operator must first
freeze and review the exact revision and wait for CI. No native request runs
during implementation or tests. Reading a local key file remains a separate
credential-access action, not implied by a CLI flag.

The fixed new output is `outputs/saved_source_candidate_query_canary_v1`.
Reject any occupancy, symlink or reparse path; do not overwrite, resume, switch
directories or restart the batch. Persist identity, preview, configuration and
operator acknowledgement before dispatch. Persist/fsync each aggregate slot
before creating its separate one-request native ledger; record reserved slots
separately from native requests to avoid double-counting or claiming a POST.
The adapter independently fsyncs native intent before possible HTTP dispatch.

## Budget and composition

The owner's standing low-cost synthetic Qwen permission is narrowed to at most
four sequential requests to exact `qwen3.5-plus`, one per case, USD 0.05 total
soft stop. A single in-flight request can slightly exceed a soft stop. Existing
frozen estimates are not current prices or invoices. Four native reservations
total USD 0.044597248. Account conservatively for reserved aggregate slots even
when a child journal cannot be created; never mistake a reserved slot for an
observed model request. Check max(reserved, known estimated cost) plus the next
reservation before admission. Unknown usage, unresolved intent or persistence
failure blocks all following requests.

Directly compose the unchanged transport with the local search function, not
the automatic query wrapper: NQ04 must execute zero local searches even if the
model wrongly proposes a query. Preserve that proposal as a failed decline
control, never silently repair it. Other admitted queries execute one local
search; declines execute none. Validate the rendered JSON against the actual
search result and trusted snapshot, keeping literal/lexical lanes separate.
No `read_source`, external search, generated answer, second model turn,
production route, activation, retry, redirect, repair, fallback or recovery.
This does not establish an end-to-end production wrapper or browser result.

## Gates and publication

Mechanical checks require exact callback/native/preview bytes, durable native
reserve/finish records, exact response model, coherent known usage, a plain
admitted proposal and accurate local-search/serialized-result observations.
Keep callback entries, reserved slots, native intents, reported responses and
local searches distinct. Persist the admitted bounded query and code-owned
candidate JSON, never raw response bodies/arguments/refusals, headers, secrets
or arbitrary exception strings. Scan serialized publication values for the
explicit key, including recoverable escapes, before writing. Publish once via
complete write/flush/fsync/close and atomic link; failed publication stops.

First mechanical, identity, accounting or persistence failure stops the batch.
A mechanically valid reference miss does NOT stop: finish the remaining fixed
controls without retries or tuning. Outcomes use separate reference failure
and execution stop fields so this difference cannot be lost in the summary.
Unrun/uncheckable controls remain null/unrun, never zero-error passes.

Predeclared gates: mechanical success 4/4; positive-case visible candidate
coverage 3/3 (at least one acceptable ID per case); explicit decline 1/1.
Also report visible reference IDs covered/available, per-lane nonreference IDs
and the deduplicated nonreference count. NQ01 may cover one or both references.
No extra-candidate threshold is invented after observing results. Truncated
results only describe visible candidates; lexical candidates are not support.
The combined development gate additionally requires complete outcome/summary
publication and no unresolved accounting. Report every component, never only
the combined boolean. Monotonic elapsed times include local work and specified
publication; they are not isolated provider latency or production SLOs.

## Offline acceptance and limits

Use fake keys and intercepted physical HTTP through the actual new runner and
unchanged adapter/search path. Cover wrong/dirty identity, no-key default,
preview drift, occupied/indirect output, fifth slot, budget/unknown usage,
fsync faults, native/text distinction, reference misses continuing, mechanical
faults stopping, explicit cancellation without search and safe diagnostics.
Reinject pre-dispatch identity bypass, reservation-after-POST, cap bypass and
stop-policy defects; existing behavior assertions must turn red. Full baseline
and final suites, latest Ruff, narrow Pylint and independent review precede use.

The four dependent synthetic controls cannot establish unseen accuracy,
general candidate precision, calibrated relevance, source truth, evidence
support, user benefit or production admission. No outcome reopens a closed
experiment. Any later semantic interpretation uses a fresh LLM context with
honest provenance, not an additional paid judge or a fictional human reviewer.
