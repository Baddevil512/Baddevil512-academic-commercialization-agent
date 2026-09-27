# Auxiliary LLM observations without changing Crew accounting

This maintenance increment adds separate observations for planning, translation,
heading translation, synonym helpers and inline PDF extraction. It changes no
prompt, provider destination, retry policy, paid admission, score or experimental
Tool Calling gate. No new paid experiment is part of this verification.

## Scope and units

The existing `usage` and `usage_accounting` remain Crew-node observations, with
their original exclusions. The additive `auxiliary_usage` field never replaces
or silently increases those totals. Search-service charges, remote invoices and
unobserved retries remain outside this collection; `end_to_end_cost_complete`
stays false. Historical absence is `not_recorded`, not a reconstructed zero.

Language helpers record each HTTP attempt immediately before dispatch, and
capture returned usage before interpreting model text. A failed plan followed
by a translation is two attempts, not one successful planning operation. Valid
usage survives invalid output; a timeout or missing usage remains unknown.

PDF uses the invocation's own SDK summary. The SDK and project retry layers
can hide attempts, so its unit is `llm_invocation`, provider attempt count is
null, and observed use is incomplete/lower-bound rather than a full bill. An
all-zero SDK default or a success counter without coherent tokens is not proof
of zero spend. The actual extraction thread owns finalization even if its HTTP
waiter is cancelled; queue abandonment does not invent a dispatched call.

Only allowlisted model identities, fixed stages/states and validated numeric
facts are persisted. Unknown models, booleans in integer fields, negative or
nonfinite counters and malformed records do not become priced zeroes. Price
estimates use the existing versioned model table without operator price overrides;
their basis is exposed. They are not a provider invoice or a new budget gate.

## Persistence, recovery and delivery

- Runs use `outputs/<run_id>/auxiliary_usage.json`, plus a strictly validated
  status snapshot for fault fallback. There is no new terminal-v1 field: an old
  reader can still interpret its immutable terminal after rollback.
- Initial API-to-worker handoff contains only bounded accounting facts and an
  already-authorized PDF association. It retains a first-publication failure
  instead of letting the worker manufacture a new complete empty ledger.
- Snapshots reconcile by call sequence and immutable identity, not by summing
  snapshots. Conflicting final facts are unreadable. Known observations survive
  a sidecar publication failure when an independent status write succeeds.
- PDF ledgers live under `outputs/_auxiliary_usage/`, independently of raw PDF
  deletion. Completed fault observations also have a bounded process-local
  cache; process loss during storage failure can lose those observations.
- A run snapshots the authorized PDF ledger as `reference_only`. Recovery copies
  that association, not parent helper calls. A real new translation in a child
  is still recorded. GETs and receipt replays do not dispatch or add costs.
- PDF observation retention is 48 hours, covering the existing 24-hour receipt
  window. Its maintenance stage is independent. Active-thread ownership protects
  the corresponding ledger and strict-named temporary file from expiry cleanup.

Both run endpoints, PDF delivery/error responses and paper receipt observations
expose the independent scope. The browser shows recorded, unavailable, incomplete
and storage-failed observations separately from Crew statistics. Accounting loss
does not convert a completed report to failed, retry paid work or erase a known
usage lower bound. A pending observation after a killed worker means settlement
was not observed, not that the provider or local worker is known to be running.

## Verification and remaining limits

Regression controls exercise actual HTTP response models, the real composer
DOM, receipt recovery, actual-thread cancellation, snapshot handoff and storage
faults. Defect reinjection targets dropped fields, duplicate accumulation,
unknown-to-zero conversion, missing thread settlement, event-loop blocking and
lost known observations. All responses used for these checks are synthetic or
intercepted; they do not establish a new native provider result.

The first full development run exposed a frozen i18n-byte change, an outdated
composer substitute, an invalid synthetic paper identity and read guards
rejecting a checkout under `outputs/`. The frozen asset was restored, substitutes
were brought to the real interface, and validation moved outside the private
output boundary. No frozen hash, warning policy or assertion was relaxed.

This is single-process observation, not transactional billing, provider
exactly-once execution, complete auxiliary/search costs, crash-proof persistence
on a failed volume or an independently verified invoice. Bounded known totals
do not estimate missing requests. Whole-volume backups must include the new
sidecars; the earlier synthetic restore rehearsal did not test these new fields.
