# Reviewer follow-up: reason-schema and local-rule closeout

Date: 2026-10-11 (Australia/Sydney). Disposition: closed without a successful
schema observation or a Reviewer comparison result. This record consolidates
events after the [Reviewer v3 closeout](results-2026-10-10-reviewer-comparison-v3.md)
without changing that result or the original
[reason-schema probe proposal](prereg-2026-10-10-reviewer-reason-schema-probe.md).

## Starting point

Reviewer v3 remains a closed mechanical failure: one response contained a
378-code-point reason despite the transmitted 300-code-point bound. It produced
zero delivered reports, and its semantic comparison is `not_run`. The v3 result
does not establish provider field enforcement, model compatibility, or semantic
benefit. The contemporaneous [offline feasibility review](reviewer-output-constraint-feasibility.md)
also leaves provider field enforcement unestablished.

A separate reason-schema implementation was prepared and independently reviewed
at [source commit `50cac1a`](https://github.com/shuxiachai/academic-commercialization-agent/tree/50cac1a9867a2242d08f6b1a5e34930008f8220e).
Four preparation CI cells and eight ordinary checks passed before the authorized
native invocation. Those checks support the prepared boundary only; they are not
native schema evidence.

## Reason-schema invocation

The single authorized invocation exited with status 1. RSP01 is recorded as
`observation_unavailable` with `worker_preflight_or_persistence_failed`; the
local schema and control were therefore not checked. RSP02 and RSP03 are
`not_run`.

The actual number of provider POSTs is unknown, with an upper bound of one.
Usage is unknown. A CNY 0.04 reservation existed, so this outcome must not be
described as free. No response-backed schema conclusion, delivered Reviewer
report, semantic judgment, or production result follows.

The authorization is consumed. The sealed invocation is closed: it must not be
replayed, repaired, or used as a remainder for another batch. The dated proposal
above retains its original design-only wording; this later closeout supplies the
current status rather than rewriting historical records.

## Offline local-rule diagnostic

After the closure, an offline diagnostic passed 22 synthetic cases and three
rejection controls. It made no provider calls. A separately authorized single
local Observe operation then completed. The original parser still rejected the
snapshot: after the original one-layer paired-quote operation, its length
predicate was satisfied, but fixed rule R5 failed because at least one character
was outside the allowed ASCII letter, digit, underscore, and hyphen set.

This diagnostic does not identify the particular character or representation,
validate a credential, or establish whether an earlier snapshot was the same.
It also does not explain the reason-schema invocation's historical failure,
complete Reviewer v3, prove provider compatibility, or yield semantic benefit.

## Current boundary

This maintenance closeout makes no production change, does not alter scoring,
and does not merge the preparation branch. No new Reviewer or schema batch is
authorized by these records. Any future work needs a new protocol and explicit
authorization that preserves the closed batches, unknown POST/usage facts, and
the distinction between local parser classification and provider behavior.
