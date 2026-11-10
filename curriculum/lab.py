"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")




def run():
    from researchos_fusion.core import AssuranceEngine, Claim, ClaimStatus, TransitionError, Evidence
    engine = AssuranceEngine(); engine.register(Claim("c","Synthetic claim"))
    rejects("cannot skip to assured", lambda: engine.transition("c",ClaimStatus.ASSURED,rationale="premature"), TransitionError)
    engine.transition("c",ClaimStatus.UNVERIFIED,rationale="inspect candidate")
    rejects("support requires evidence", lambda: engine.transition("c",ClaimStatus.SUPPORTED,rationale="unsupported"), TransitionError)
    engine.add_evidence(Evidence("e","c","fictional:source","synthetic method","synthetic support",True,"declared-group"))
    engine.transition("c",ClaimStatus.SUPPORTED,rationale="recorded synthetic evidence")
    check("supported is recorded state", engine.claims["c"].status.value, "supported")
    rejects("one group is not reproduction", lambda: engine.transition("c",ClaimStatus.REPRODUCED,rationale="premature"), TransitionError)
    engine.add_evidence(Evidence("conflict","c","fictional:other","synthetic method","contradictory result",False,"other-group"))
    check("contradiction reopens claim", engine.claims["c"].status.value, "contested")

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
