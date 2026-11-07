# ResearchOS-Fusion

**An experimental epistemic-assurance layer for AI-assisted nuclear fusion research.**

ResearchOS-Fusion explores how Topological Epistemic Control Theory (TECT) can organize scientific claims, evidence, adversarial challenges, reproducibility checks, governance gates, and auditable transitions. It is a **research prototype**, not a deployed fusion controller, plasma predictor, validated fusion simulator, or safety certification system.

## Implemented in v0.1.0

- Claim lifecycle: `generated → unverified → supported → reproduced → validated → stable → assured`, with `contested` and conservative re-review.
- Structured, timestamped evidence and provenance groups; conflict-triggered reopening.
- Explicit transition gates for independent reproduction, adversarial tests, stability, and governance.
- JSON-exportable claim/audit records.
- Deterministic reference functions for deuterium–tritium fusion energy (`17.6 MeV` per reaction, approximate) and `E=mc²`.
- CLI demonstration, unit tests, and GitHub Actions checks.

**Important:** The assurance state is an internal workflow label, not proof of scientific truth. The booleans marking reproduction/test completion are placeholders for future independently verified adapters. A string provenance group is not evidence of actual independence. Audit logs are in-memory and mutable, not cryptographically tamper-evident.

## Quick start

```bash
python -m pip install -e '.[dev]'
pytest -q
researchos-fusion demo
researchos-fusion dt-energy --reactions 1e18
```

Without an installation, run `PYTHONPATH=src python -m researchos_fusion.cli demo`.

The demo registers an example D-T fusion claim, checks a reference calculation, and stops at **supported**. It does **not** self-promote to independently reproduced, stable, or assured.

## Intended architecture

```text
Fusion hypotheses / simulations / materials candidates
                    ↓
Claims + dependencies + evidence provenance
                    ↓
Physics consistency and experimental validation [planned]
                    ↓
Adversarial perturbation and independent reproduction [planned]
                    ↓
TECT transition controller and governance
                    ↓
Versioned assurance record [planned; JSON snapshot available today]
```

## Research work packages

1. **Plasma disruption assurance:** Benchmark model predictions on held-out discharge data and track false alarms, missed events, and lead time.
2. **Materials evidence graph:** Trace candidate materials to measured thermal/radiation properties and credible modeling assumptions.
3. **Physics verification:** Couple applicable conservation checks, reference datasets, simulation cross-checks, and uncertainty characterization to claim transitions.

These are **planned investigations**; the repository presently contains no trained model, experimental database, tokamak integration, or physical reactor design.

## Development conventions

- Every scientific claim must carry assumptions, provenance and a documented acceptance scope.
- Conflicting evidence should reopen a claim; agreement between correlated sources is not independent reproduction.
- Do not use the internal `assured` label as regulatory, operational, or scientific certification.
- Changes to scientific validation policy should include tests and explicit review criteria.

## Roadmap

- [ ] Persistent, append-only evidence ledger and schema validation
- [ ] Verified provenance and evidence-independence checks
- [ ] Domain-specific numerical and physics validation adapters
- [ ] Plasma benchmark importers with license/data governance
- [ ] Automated adversarial test runners and report artifacts
- [ ] Statistical baseline comparisons and external evaluation

## License

See [LICENSE](LICENSE) for repository terms.
