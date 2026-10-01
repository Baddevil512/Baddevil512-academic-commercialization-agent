# Offline common Reviewer output contract

The closed [Reviewer v2 attempt](../../docs/results-2026-10-01-reviewer-comparison-v2.md)
received JSON whose reasons exceeded a local limit missing from its request.
This small successor prepares a complete shared output contract for new direct
comparison requests. It has no CLI, client, credential reader, output directory
or provider dispatcher. It is not connected to production or a new native batch.
Inspection of current production Reviewer configuration shows JSON Object mode
without supplying the complete schema. This preparation does not change that
separate integration or supply a new production HTTP observation.

## Interface and trust

```python
from academic_agent.evidence import ReviewerCorrectionPlan
from evals.reviewer_output_contract_v1.contract import append_common_contract

new_body = append_common_contract(
    already_rendered_request_bytes,
    trusted_schema=ReviewerCorrectionPlan.model_json_schema(),
)
```

The caller owns the original request and the trusted model. The transformer
imports only the standard library and does not discover or authenticate a
schema. The example's normal model import has the project's usual framework
initialization; this is not a cold-process credential-access audit.

Supported input is a JSON Object request with exactly one text system message
followed by one text user message. Only the system content receives an identical,
deterministic contract suffix. Every other parsed JSON value and original message
string is retained. Serialization may change whitespace, key order and escape
forms; the returned full UTF-8 bytes require a new request identity.

The suffix contains the complete supplied JSON Schema, including nested types,
length/list bounds, defaults and extra-field restrictions. It separately states
the task's explicit `corrections` envelope: the authentic model still permits
omission through its default array. Length limits include endpoints and use
Unicode code points; `maxLength: 2000` is the precise machine bound despite older
"under 2,000" prose. No validator bound is changed or response clipped.

Duplicate JSON keys, nonfinite or lossy schema values, unsupported message shapes,
repeated addition and an oversized complete request are refused. The 48 KiB
check applies after schema addition, not just to the original body.

## Explicit checks

```bash
uv run pytest -q tests/reviewer_output_contract_checks.py
```

The checks live under `tests/` to use the existing provider-isolation fixtures.
Their explicit filename keeps the default suite unchanged, without skips or a
pytest configuration change. They compare before/after suffixes, full real-model
schemas, original fields and actual HTTP content received by `MockTransport`;
they also exercise inclusive model bounds and refusal paths. The synthetic
messages are mechanical controls, not the historical six-prompt reproduction or
held-out semantic tasks. No paid or external request occurs.

Local intercepted delivery does not establish provider reception, compliance,
correction quality or paired gain. The closed v1/v2 batches, original responses,
labels and hashes stay unchanged. A future native experiment needs its own
frozen request/implementation identity and applicable authority; this utility
alone supplies neither a runner nor production activation.

## Recorded offline verification

Observed on 2026-10-01, using the current real local validator:

- Explicit checks: 35 passed on CPython 3.12.9 (1.87 seconds) and 3.11.9 (5.25 seconds).
- Ordinary baseline: 7,411 tests and 1,697 subtests, 828.20 seconds.
- Ordinary after-test: 7,411 tests and 1,700 subtests, 613.95 seconds.
- Latest Ruff and narrow Pylint, including the added files, passed.
- Missing reason bound, one-arm addition, stale HTTP bytes, overwritten duplicate
  keys and normalized nonfinite values each reached their intended assertion;
  runtime patches were restored. No execution source was changed by reinjection.
- Fresh read-only review found a duplicate/NaN test confounder; corrected valid
  request controls and their reinjections were reviewed again without another finding.
  Requested role was `route_reviewer` (Astra/high); backend metadata was unavailable.

The default test denominator excludes these explicit development checks. Its
three added subchecks concern documentation links; do not add 35 to 7,411 or
infer a performance improvement from the two full-run times.

The initial Windows 3.11 editable import failed: the local `site.py` reads `.pth`
with locale encoding cp936 while the project's non-ASCII path was stored in
UTF-8. A UTF-8-mode probe still found no package. The successful invocation used
a process-scoped `PYTHONPATH` to the real `src`, verified interpreter/prefix/module
identity first, then ran unchanged checks and restored the environment. This
qualifies source validation, not repaired editable packaging or a global locale
change. Original 3.12 dependencies, production and historical batches were untouched.
