# ResearchOS-Fusion

<!-- research-workbench:start -->
## Research workbench

[Open this repository's private workbench](https://tltmgnt-researchos-fusion.troturn31.chatgpt.site) · [All repository workbenches](https://tltmgnt-research-workbenches.troturn31.chatgpt.site)

The hosted interface requires ChatGPT sign-in and access to the private Site. It supports browser-local research records, evidence fingerprints and workspace export. It is a prototype: no live AI model or repository backend is connected, and it does not establish external validation.
<!-- research-workbench:end -->


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

## Offline lab workflow (v0.2.0)

Evaluate local JSON measurements against declared acceptance tolerances, verify
artifact hashes, record independent-review attestations, and retain transactional
SQLite records with an integrity hash chain:

```bash
researchos-fusion lab-run examples/reference_run.json --ledger runs.sqlite > report.json
# Expected exit 1: the synthetic example awaits review.
researchos-fusion ledger-verify runs.sqlite
```

Read the [lab evaluation protocol](docs/LAB_READINESS.md) for the manifest contract,
exit codes, checkpoint verification, data handling and real-data qualification steps.
`reviewed` means checks passed with recorded approvals; identities, source independence
and scientific truth are not automatically verified. The lab workflow does not promote
the prototype claim engine to `assured` and does not control equipment.

## ResearchOS / TECT concept integration

The [ResearchOS / Topological Epistemic Control Theory technical concept paper](docs/researchos/TECT_WHITE_PAPER.md) proposes an epistemic control and assurance infrastructure for AI-generated knowledge. Read the [repository integration status](docs/researchos/INTEGRATION.md) and [machine-readable scope](docs/researchos/integration.json) for the boundary between the concept and implemented capabilities. Performance targets are research objectives, not achieved results. This documentation addition does not implement the complete ResearchOS architecture or change operational authority.

## Portfolio implementation boundary

See [current implementation and shared-core integration](docs/portfolio/INTEGRATION.md) and [machine-readable status](docs/portfolio/STATUS.json). Independent empirical reproduction and real-provider acceptance remain separate from software checks.

**∞**

## Topology compatibility and curriculum

See the [repository-specific v2 curriculum](docs/portfolio/TOPOLOGY_CURRICULUM_V2.md) for topology choices, worked explanations, a graded laboratory and adoption boundaries. Run the offline answer key from this repository root:\n\n```sh\npython curriculum/lab.py --verify\n```\n\n[Expected answers](curriculum/expected.json) · [Recorded local validation](curriculum/VALIDATION.json). The guide states any existing dependency needed for the lab.
