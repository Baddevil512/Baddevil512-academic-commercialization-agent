"""Private PDF observations with actual-thread ownership and independent TTL.

No authorization is introduced here. Callers must first use the existing paper
or receipt authority. These records contain no input, key, owner or endpoint.
"""
from contextlib import contextmanager
from pathlib import Path
import re
import threading
import time

from academic_agent import auxiliary_usage as usage

_LOCK = threading.RLock()
_ACTIVE: dict[Path, usage.Collector] = {}
_FAULTS: dict[Path, tuple[float, dict]] = {}
RETENTION_SECONDS = 48 * 3600  # At least the existing 24-hour receipt window.


def paper_path(paper_id: str) -> Path:
    from api import papers

    if not isinstance(paper_id, str) or re.fullmatch(r"paper-[0-9a-f]{32}", paper_id) is None:
        raise ValueError("Invalid auxiliary paper identity")
    return papers.PAPERS_ROOT.parent / "_auxiliary_usage" / f"{paper_id}.json"


def paper_summary(paper_id: str) -> dict:
    try:
        path = paper_path(paper_id)
    except ValueError:
        return usage.unavailable("unreadable")
    with _LOCK:
        if path in _ACTIVE:
            return _ACTIVE[path].summary()
        if path in _FAULTS:
            # GETs never write/settle/dispatch. A failed volume cannot promise
            # durability across process loss; a prior pending disk record stays
            # uncertain if this bounded process-local fault observation is lost.
            return usage.project(usage.Ledger.model_validate(_FAULTS[path][1]))
        return usage.read_summary(path)


@contextmanager
def paper_operation(paper_id: str):
    path = paper_path(paper_id)
    with _LOCK:
        collector = usage.Collector(path)
        _ACTIVE[path] = collector
    try:
        with usage.bind(collector):
            yield collector
    finally:
        with _LOCK:
            collector.finish()
            result = collector.summary()
            if result["record_state"] == "write_failed":
                if len(_FAULTS) >= 1024:
                    _FAULTS.pop(next(iter(_FAULTS)))
                _FAULTS[path] = (time.time(), collector.snapshot())
            _ACTIVE.pop(path, None)


def paper_reference(paper_id: str):
    path = paper_path(paper_id)
    with _LOCK:
        snapshot = (_ACTIVE[path].snapshot() if path in _ACTIVE else
                    _FAULTS[path][1] if path in _FAULTS else None)
        if snapshot is not None:
            reference = {"relation": "reference_only", "observation": snapshot}
            return {"relation": "reference_only", "observation": usage.validate_reference(reference)}
        return usage.pdf_reference(path)


def prune() -> int:
    from api import papers

    root = papers.PAPERS_ROOT.parent / "_auxiliary_usage"
    removed = 0
    cutoff = time.time() - RETENTION_SECONDS
    with _LOCK:
        for path, (stamp, _) in list(_FAULTS.items()):
            if stamp < cutoff:
                _FAULTS.pop(path, None)
        if not root.exists():
            return 0
        for path in root.iterdir():
            match = re.fullmatch(r"(paper-[0-9a-f]{32}\.json)(?:\.tmp)?", path.name)
            # Failed atomic publication can leave a sibling .json.tmp. Both
            # entries belong to the canonical ledger's actual-thread owner;
            # checking the temporary path itself would miss its active lease.
            if match is None or root / match[1] in _ACTIVE:
                continue
            if path.is_file() and not path.is_symlink() and path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
    return removed
