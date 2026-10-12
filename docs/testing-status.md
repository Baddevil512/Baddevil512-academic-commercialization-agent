# Testing status and boundary map

Evidence snapshot: 2026-10-06. This audit starts from production revision
`9acdf13d23b051435c721d3727473e5b00800e9c`. Test counts describe an executed
revision and environment, not report accuracy, source truth or model quality.
The implementation and experimental evidence remain qualified in the
[current evidence ledger](evidence-status.md).

## Executed observations

| Observation | Identity and scope | Result |
|---|---|---|
| Local audit baseline | Clean checkout of `9acdf13`, Windows, CPython 3.12.9, Node 24.14.0, locked dependencies; complete ordinary suite without coverage instrumentation | 7,412 passed, 1 skipped, 1,670 subtests passed; 632.25 seconds |
| Local audit candidate, complete regression | Same local checkout layout/interpreter/dependency lock, with the bounded test-only changes described below; actual process exit 0 | 7,417 passed, 1 skipped, 1,677 subtests passed; 654.53 seconds |
| Local candidate, targeted contracts | API projection, runtime-summary integrity, auxiliary accounting and web usage tests, including the actual Node subprocess | 169 passed, 116 subtests passed; no failures/errors/skips; 10.19 seconds |
| Contributor PR #192 CI | Fork head `4f24148fa2e5cd80d9bfa42286822fd3ce0fe510` against `9acdf13`; Linux/Windows x Python 3.11/3.12 | Each cell: 7,416 passed, 1 skipped, 1,670 subtests passed; overall workflow failed in Ruff |
| PR #192 coverage/browser/container | Same fork CI identity; Ubuntu 3.12 coverage, zero-provider Chromium and Docker runtime checks | Coverage 90.70% against the unchanged 85% floor; browser and container checks passed |

The [PR workflow](https://github.com/shuxiachai/academic-commercialization-agent/actions/runs/37366182854)
does not validate this audit's later edits. Its Ruff failure was B010 at
`ablation.py:392`; the following Pylint step did not run. The PR's timeout and
cleanup implementation also remains subject to its independent change request.
Passing its new tests does not establish that running work stops at the deadline.

The local candidate also passed the prescribed latest-Ruff invocation and narrow
Pylint check. A non-author read-only review verified the frozen nine-file
candidate and found no P1/P2 blocker. Its final document-only result update is
reviewed separately. This candidate has not acquired a new four-cell CI,
Chromium or container observation; those rows above retain the fork identity.

The one skipped ordinary test is
`RealReportsTests::test_no_baseline_report_is_flagged` in
`tests/test_consistency.py`. A public clean checkout lacks the local benchmark
reports required by its existing conditional skip. The test is not counted as
passed, and this audit does not add a skip or publish private reports to remove it.

## What each test layer establishes

| Surface | Existing verification | Important limit or boundary |
|---|---|---|
| Retrieval, evidence and scoring | Offline units, saved-fixture checks and calibrated historical runs | A green suite does not validate a new topic or general claim entailment; scoring rules and frozen cohorts stay unchanged |
| Run/PDF admission and ownership | HTTP and actual-thread/process tests, durable receipt fault controls | A read capability does not fund new work; unresolved receipts cannot redispatch; ownership survives physical shutdown |
| Recovery, deadlines and terminal records | Real subprocess/crash tests and immutable-record checks | Worker exit, terminal publication and usage completeness are separate facts; provider exactly-once delivery is not established |
| API projections | Real disk to status/progress HTTP tests, missing/corrupt metadata controls | Key presence and endpoint agreement alone can miss both endpoints replacing a non-default value with the same default |
| Browser delivery | Actual JavaScript/Node contracts and opt-in Chromium journeys | Formatter literals alone do not exercise an application caller or DOM update; Node VM results are not Chromium observations |
| Auxiliary accounting | Synthetic ledger, HTTP, formatter and attachment/receipt tests | Helper/PDF observations stay separate from Crew totals; unavailable is not zero; prior PDF references are not new spend |
| Source locator | Default-off/consent/receipt tests, intercepted transports and separate closed native trials | Metadata location is not claim support; test execution does not activate production or reopen a paid allowance |
| Container/export | Docker build/runtime checks and font/export units | Local Python tests do not install or establish the deployed image's fonts, process supervisor or readiness |
| Reviewer experiments | Separate pre-registration, source locks and explicitly invoked checks | Ordinary collection does not execute the isolated experiment invoker or establish a successful native/semantic result |

## Verified boundary changes

The bounded changes verified in this round are test changes:

- Compare every public field in both HTTP responses with one frozen, actual
  disk-derived projection. Exercise non-default optional summaries and keep
  schema declaration checks. Include controls for an omitted progress argument
  and a common default substitution in both endpoints.
- Deliver actual status/progress response bodies to the real run-page JavaScript
  and inspect its usage DOM. Cover independent Crew/auxiliary facts, missing and
  unreadable observations, reference-only PDF usage, and a known-to-missing
  update that clears stale values and tooltip text.
- Corrupt usage and accounting together. Preserve both field-local faults,
  unavailable accounting, the report and healthy neighboring summaries, and
  unchanged persisted bytes.

The API omission/common-default controls traverse the real HTTP endpoints.
The Node control disconnects auxiliary formatting and must fail with the exact
lost-auxiliary-observation assertion, rather than an unrelated startup error.
The stale-accounting dictionary control checks its assertion helper; it is not
a production-reader mutation. The positive combined-corruption case does
exercise actual persisted bytes and both HTTP readers. The Node VM observation
does not substitute for a fresh Chromium run.

The first two targeted candidates exposed test-construction errors, including
`subTest` exception handling, the public terminal projection's shape and a
shared `subprocess.Popen` mock. Their failed records were retained. A strong
expert corrected the bounded test harness; the executed results above cover
that later candidate. No production source, guard, threshold, dependency lock,
CI configuration, skip rule or warning policy was changed.

## Safe performance work

The measured slow phases include actual subprocess/import isolation, physical
shutdown and default-off negative controls. Their duration is evidence for
profiling, not permission to replace those boundaries with mocks or remove cases.
This round prioritizes shared assertion code and stronger executable contracts;
it makes no measured full-suite speedup claim.

The two complete local observations were 632.25 and 654.53 seconds. The later
run took 22.28 seconds longer in these observations; additional coverage and
host/cache variation are not separated by this single before/after pair. This
is a contract-strengthening and duplicated-request cleanup, not a measured
end-to-end speed improvement.

Keep before/after measurements on the same checkout layout, interpreter and
dependency lock. Do not run another test suite concurrently. Coverage tracing,
filesystem/cache state and CI host differences affect elapsed time; the PR's
33-minute coverage cell and this local uninstrumented run are not a controlled
speed comparison.

Place source checkouts outside `outputs`. Some existing offline audit tests
deliberately reject any source read whose path contains that reserved data
directory. The first audit checkout there recorded two such failures before any
edits; its failed result was preserved. A fresh checkout under the already
excluded `.claude/worktrees` boundary passed the two original cases and the
complete baseline without changing a guard, source file, assertion or warning
policy. Give a nested offline checkout its own empty, ignored `.env` boundary
so dotenv discovery does not walk up to a parent's real configuration, and
create its own virtual environment rather than reusing an editable install
bound to another checkout.

Use the unchanged checks in [Contributing](../CONTRIBUTING.md#checks-before-and-after-a-change).
Experimental invokers, live calls, private-data transfers and production actions
retain their separate authorization requirements.
