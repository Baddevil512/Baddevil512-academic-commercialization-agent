# Synthetic restoration now includes auxiliary observations

Starting revision: `3e43dc08108105ba0b0e534f88c6a0b81cb40965`.
Only the existing offline rehearsal and documentation change. No production
code, real volume, provider request, backup schedule or paid gate is changed.

## Verified boundary

The existing bounded fixture now uses real auxiliary writers for a synthetic
planning observation (18 tokens), an unresolved translation and an earlier PDF
invocation (142 tokens). The PDF is a frozen historical reference, not part of
the run's current total. The original inventory bounds remain 128 entries and
2 MiB, with the same quiescence, path and byte-integrity requirements.

After copying, the synthetic source is temporarily hidden inside its existing
test sandbox, and observation caches are cleared. Actual run status/progress
handlers and response models, paper receipt handler and replay projection read
the restored data. Repeated observations retain terminal truth, known use and
unknown settlement; auxiliary writers and paid/execution entry points must have
zero calls, and all restored bytes remain unchanged.

Missing/corrupt sidecars are rejected by the original inventory. Separate reader
checks then distinguish absent, unreadable and usable status-fallback facts.
Fallback preserves the known 18-token lower bound; unknown use remains null.
Loss of the private PDF source ledger does not erase its already-snapshotted
reference or add 142 tokens to current usage. A real injected publication failure
before temporary-file creation leaves an older pending sidecar and a newer
failed-write status snapshot; the restored reader reconciles them without sum
or repair. No leftover temporary file is removed to force quiescence.

The old-snapshot negative now also settles the source's translation after the
copy: the current source observes 26 tokens while the intact older snapshot
still observes only 18 and an unresolved call. Passing an old inventory remains
neither freshness evidence nor permission to resume paid work.

## Validation and limitations

Before edits, the full local suite passed 7,393 tests and 1,632 subtests. The
first focused attempt had one setup error when framework initialization tried
to invoke dotenv; the guard stopped it without reading the configuration file.
The isolated handler import now stubs unused provider configuration fail-fast
rather than weakening the environment/network guard. Final focused checks passed
14 tests. Three actual in-memory defect injections (omitted auxiliary copy,
unknown-to-zero projection, historical PDF double counting) failed their target
checks and were restored before the final focused run.

These are synthetic state/read observations, not real token consumption,
provider invoices, HTTP/browser transport, process restart, checkpoint execution,
Railway restore, achieved RPO/RTO or multi-instance consistency. The app's actual
storage readers are exercised, but its startup/provider configuration is not.
Full regression, independent review and release CI remain separate gates.

The deployment metadata inspection could confirm a single replica and an
`/app/outputs` mount but could not inspect backup schedules or snapshot history.
That state remains **unavailable**, not absent or healthy. No live backup or
restore was attempted. See the [current rehearsal and operator prerequisites](offline-volume-restore.md).
