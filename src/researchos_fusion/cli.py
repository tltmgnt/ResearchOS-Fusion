"""CLI entry points for an auditable demonstration, with no external services."""

import argparse
import json
import math
import sqlite3
from pathlib import Path

from .lab import Ledger, evaluate

from .core import AssuranceEngine, Claim, ClaimStatus, Evidence
from .physics import dt_fusion_energy_joules, dt_fusion_energy_mev


def run_demo() -> dict:
    engine = AssuranceEngine()
    claim = Claim("DT-Q-001", "A D-T fusion reaction releases approximately 17.6 MeV")
    engine.register(claim)
    engine.transition(claim.identifier, ClaimStatus.UNVERIFIED, rationale="Register for evaluation")
    value = dt_fusion_energy_mev()
    engine.add_evidence(Evidence("E-001", claim.identifier, "Reference D-T reaction Q value",
                                 "deterministic calculation", f"Computed reference {value} MeV",
                                 True, "reference-model"))
    engine.transition(claim.identifier, ClaimStatus.SUPPORTED, rationale="Reference calculation supports the claim")
    # Stop here: an internal calculation is not independent reproduction or assurance.
    return engine.export(claim.identifier)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimental ResearchOS-Fusion tools")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Emit a sample claim and provenance record")
    demo.add_argument("--indent", type=int, default=2)
    energy = sub.add_parser("dt-energy", help="Compute approximate D-T fusion reaction energy")
    energy.add_argument("--reactions", type=float, default=1.0)
    lab = sub.add_parser("lab-run", help="Evaluate a local manifest and append an audit record")
    lab.add_argument("manifest", type=Path)
    lab.add_argument("--ledger", type=Path, required=True)
    verify = sub.add_parser("ledger-verify", help="Verify stored records and optional retained head")
    verify.add_argument("ledger", type=Path)
    verify.add_argument("--expected-head")
    args = parser.parse_args()
    if args.command in ("lab-run", "ledger-verify"):
        try:
            if args.command == "lab-run":
                report = evaluate(args.manifest)
                print(json.dumps(Ledger(args.ledger).append(report), indent=2, allow_nan=False))
                if report["status"] != "reviewed":
                    raise SystemExit(1)
            else:
                print(json.dumps(Ledger(args.ledger).verify(args.expected_head), indent=2))
        except (ValueError, OSError, sqlite3.Error) as error:
            parser.exit(2, f"error: {error}\n")
        return
    if args.command == "demo":
        print(json.dumps(run_demo(), indent=args.indent))
    elif args.command == "dt-energy":
        if not math.isfinite(args.reactions) or args.reactions < 0:
            parser.error("reactions must be finite and nonnegative")
        try:
            result = {"reactions": args.reactions,
                      "energy_mev": dt_fusion_energy_mev(args.reactions),
                      "energy_joules": dt_fusion_energy_joules(args.reactions)}
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
