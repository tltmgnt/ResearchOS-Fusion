# Offline lab evaluation protocol

## Readiness scope

Version 0.2 provides an offline evidence evaluation and audit workflow suitable for
software evaluation by a research lab. It is not validated for experimental decisions,
reactor control, safety interlocks, scientific certification, or plasma prediction.
No real discharge data, trained models, materials measurements, or lab approvals are
included. The synthetic fixture validates software plumbing only.

| Acceptance area | Delivered | Required before experimental use |
| --- | --- | --- |
| Input validation | Versioned manifest; strict fields, finite numbers, duplicate rejection | Lab data dictionary and unit review |
| Artifact provenance | SHA-256, source, license and provenance group required | Verify ownership, license and source independence |
| Numerical checks | JSON measurement extraction; absolute tolerance comparison | Domain-approved quantities, uncertainty budgets and tolerances |
| Review | Explicit named approval/rejection recorded; operator self-review blocked | Authenticate identities and obtain authorized independent review |
| Audit persistence | Transactional SQLite append API, chain verification, external head checkpoint | Controlled storage, backups, access policy and checkpoint retention |
| Claim engine | Conservative transitions; challenge invalidates dependent gates | Replace mutable boolean gate attestations with verified adapters |
| Physics | Rounded energy reference functions; overflow rejection | Independent physics benchmarks and measured-data validation |
| Equipment | No connection or actuation | Separate hardware qualification and institutional authorization |

## Installation and software qualification

Use Python 3.10 or newer in an isolated environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
researchos-fusion demo
researchos-fusion dt-energy --reactions 1e18
researchos-fusion lab-run examples/reference_run.json --ledger runs.sqlite > report.json
# Exit 1 is expected: this synthetic example intentionally has no independent review.
researchos-fusion ledger-verify runs.sqlite
```

Keep the JSON report and its `record_hash` outside the ledger. Later verify with:

```bash
researchos-fusion ledger-verify runs.sqlite --expected-head HASH_FROM_LATEST_REPORT
```

The expected head must refer to the latest accepted append. An older checkpoint will
fail after a legitimate append. Hash chaining detects changed records and internal
missing records; only an externally retained head detects tail truncation or a
complete rewrite. SQLite is not signed, encrypted, or write-once storage. Do not share
an active ledger over a network filesystem. Back up it using SQLite's backup API or
a consistent offline copy, and retain reports separately. The append API serializes
concurrent writers and rolls back failed transactions. Duplicate run IDs are rejected.

## Manifest contract

Copy `examples/reference_run.json` beside your artifacts. Relative artifact paths must
resolve within that directory; path traversal and escaping symbolic links are rejected.
Every artifact declares its ID, path, source, license, provenance group and expected
SHA-256. Hashes are verified before measurement extraction; the same bytes are used
for both. Artifacts used by checks must be UTF-8 JSON objects with numeric top-level
measurement keys. Calculate the expected digest before review, for example:

```bash
sha256sum measurements.json
```

Each check declares an artifact ID, measurement `observed_key`, human-readable
quantity, unit, expected value and nonnegative absolute tolerance. Acceptance is
`abs(observed - expected) <= absolute_tolerance`. Unit conversion, uncertainty
propagation and physical plausibility are not inferred. Review the reference and
unit compatibility explicitly. All checks must pass. NaN, infinity, numeric booleans,
unknown fields, missing fields, duplicate IDs and duplicate JSON keys are rejected.

The manifest requires schema version 1, run ID, claim, acceptance scope, operator,
artifacts, checks and reviews. Reviews contain `reviewer`, `decision` (`approve` or
`reject`) and `rationale`. Reviewers must differ from the operator and each other.
These names are attestations, not authenticated identities. One or more approvals
and no rejections yields `reviewed` only if every check passes. Otherwise passing
checks yield `pending_review`; failing checks yield `failed` regardless of reviews.
Neither a provenance-group string nor agreement establishes independent reproduction.

CLI exit status is 0 for a recorded reviewed run or successful ledger verification,
1 for a recorded failed/pending run, and 2 for invalid input or persistence failure.
Invalid inputs create no run record. Failed and pending runs are deliberately retained.
Use a new run ID for each revision. Reports include checks, artifacts, reviews, runtime,
manifest digest, timestamp, limitations and ledger chain metadata. Reports contain
manifest text and local relative artifact paths; apply the lab's data handling policy.
The hash covers canonical parsed JSON, not the original manifest whitespace.

## Real-data handoff

1. Select one lab use case, dataset and permitted purpose. Document ownership,
   access, license, exclusions and acceptance scope before importing data.
2. Freeze an independent reference dataset and preregister checks and tolerances.
   Record instrument calibration, sampling, units and measurement uncertainty.
3. Export measured quantities as JSON; retain original data and extraction code as
   hashed artifacts. This workflow does not execute extraction code or train models.
4. Exercise passing, failing, missing-data and corrupted-data cases. Compare results
   against independent analysis. For prediction studies, define split leakage checks,
   baselines, false alarms, missed events, lead times and confidence intervals first.
5. Have authorized reviewers verify the evidence and record decisions. Archive each
   report, ledger backup and external head checkpoint under controlled access.
6. Obtain institutional scientific and equipment authorization separately. Do not
   translate `reviewed` or an in-memory `assured` label into equipment commands.

## Known boundaries

The original in-memory claim engine is retained for exploration. Its public mutable
objects and boolean gates are not an authentication boundary or durable evidence
store. The lab ledger is a separate run-level record; it does not upgrade claim
status. Contradictory evidence remains unresolved in the engine until a future
explicit evidence-resolution protocol is designed. No scientific readiness claim
should be made from test coverage or the synthetic example.
