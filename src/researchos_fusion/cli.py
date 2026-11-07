"""CLI entry points for an auditable demonstration, with no external services."""

import argparse
import json

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
    args = parser.parse_args()
    if args.command == "demo":
        print(json.dumps(run_demo(), indent=args.indent))
    elif args.command == "dt-energy":
        print(json.dumps({"reactions": args.reactions,
                          "energy_mev": dt_fusion_energy_mev(args.reactions),
                          "energy_joules": dt_fusion_energy_joules(args.reactions)}, indent=2))


if __name__ == "__main__":
    main()
