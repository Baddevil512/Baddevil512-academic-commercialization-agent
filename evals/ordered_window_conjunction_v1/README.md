# Closed offline ordered-window comparison

This is a reproducibility archive of a **failed development hypothesis**, not
an installed search module, provider adapter, production feature or new default
test suite. No model or external-search request was made. See the
[frozen rule](../../docs/prereg-2026-09-27-ordered-window-conjunction-offline.md)
and [result with method limitations](../../docs/results-2026-09-27-ordered-window-conjunction-offline.md).

The old literal-plus-separator baseline covered 1/11 positive questions. Adding
the exact-case ordered-window rule still covered 1/11: zero new candidates and
zero gains. Twelve eligible distractors were scanned, but zero returned
candidates cannot establish useful precision. The uncertain twelfth question
remains visible and is not forced into the positive or negative reference set.

## Contents and execution

- `fixture.json`: fictional task/source data and LLM-reviewed references.
- `prototype.py`: frozen evaluation-only implementation; imports the unchanged
  local snapshot/search library, not a provider, API factory or source reader.
- `checks.py`: 101 fresh engineering controls, explicitly invoked only.
  Naming it outside `test_*.py`/`*_test.py` keeps default collection unchanged
  without adding a skip, changing pytest configuration or dropping old tests.
- `result.json`: exact recorded JSON bytes; do not overwrite this observation.
- `manifest.json`: file identities and separately observed verification facts.

From the repository root, after installing dependencies with `uv sync`:

```bash
uv run python evals/ordered_window_conjunction_v1/prototype.py
uv run pytest -q evals/ordered_window_conjunction_v1/checks.py
```

The first command verifies the fixed fixture and reports identity only. The
self-tests do not evaluate the twelve-case cohort. If local pytest temporary
permissions fail, use a new, unoccupied workspace `--basetemp` as described in
[Contributing](../../CONTRIBUTING.md); never select an existing data directory.

An explicit `--evaluate` prints a deterministic reproduction of the old
observation to stdout. It is not a fresh experiment or a license to tune this
cohort until it passes. Do not redirect it over the archived result. Gate 1 in
that JSON stays `unproven` because a matcher cannot attest its own external
tests, mutation verification or independent review. Those facts are separately
recorded in the manifest and result document, not injected into measured bytes.

The four hash-bound files have directory-local, exact-name `-text` attributes so
Windows/Linux Git line-ending conversion cannot silently change their recorded
identities. The root attributes and old experiment identity gates are unchanged.
The two imported dependency blobs belong to the recorded base revision; future
changes require reproducing that revision rather than assuming comparability.

## Provenance limits

References were authored and reviewed by LLMs in separate contexts, not humans.
One rejected initial self-test inadvertently computed this cohort before the
corrected measurement; no saved outcome or manual result analysis was reported.
Rules, queries and references were not changed after that execution. This is
disclosed development evidence, never a pristine unseen test or user-value study.
Raw review transcripts, rejected code and local operator helpers stay outside
the public archive. No production admission or new paid allowance follows.
