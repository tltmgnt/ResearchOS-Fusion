# Topology compatibility and curriculum v2 — ResearchOS-Fusion

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | application research |
| Minimum useful mathematics | Typed evidence graphs and finite-state assurance logic |
| Relationships to preserve | Fusion-research claims, methods, findings and review transitions |
| Concrete operation / capstone | Trace a fictional unsupported claim through a prohibited transition and identify the missing evidence |
| Necessity and scope boundary | A claim-state engine is not a plasma topology solver, fusion controller or safety certification |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with typed evidence graphs and finite-state assurance logic and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify fusion-research claims, methods, findings and review transitions. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain typed evidence graphs and finite-state assurance logic. | Trace a fictional unsupported claim through a prohibited transition and identify the missing evidence. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `32403fe1c837145b8203bf975e84382a40310be3` in [src/researchos_fusion/core.py](../../src/researchos_fusion/core.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [11](../../src/researchos_fusion/core.py#L11) | `class ClaimStatus(str, Enum):` | State the input/output contract and trace one normal and one failing case. |
| [22](../../src/researchos_fusion/core.py#L22) | `class TransitionError(ValueError):` | State the input/output contract and trace one normal and one failing case. |
| [27](../../src/researchos_fusion/core.py#L27) | `class Evidence:` | State the input/output contract and trace one normal and one failing case. |
| [38](../../src/researchos_fusion/core.py#L38) | `def __post_init__(self) -> None:` | State the input/output contract and trace one normal and one failing case. |
| [40](../../src/researchos_fusion/core.py#L40) | `raise ValueError("Evidence supports must be a boolean")` | Construct the triggering input and explain why rejection preserves the contract. |
| [43](../../src/researchos_fusion/core.py#L43) | `raise ValueError("Evidence identifiers, provenance, method, finding and group are required")` | Construct the triggering input and explain why rejection preserves the contract. |
| [47](../../src/researchos_fusion/core.py#L47) | `class Claim:` | State the input/output contract and trace one normal and one failing case. |
| [60](../../src/researchos_fusion/core.py#L60) | `def __post_init__(self) -> None:` | State the input/output contract and trace one normal and one failing case. |
| [62](../../src/researchos_fusion/core.py#L62) | `raise ValueError("Claim identifier and statement are required")` | Construct the triggering input and explain why rejection preserves the contract. |
| [64](../../src/researchos_fusion/core.py#L64) | `raise ValueError("A claim cannot depend on itself")` | Construct the triggering input and explain why rejection preserves the contract. |
| [68](../../src/researchos_fusion/core.py#L68) | `class ValidationResult:` | State the input/output contract and trace one normal and one failing case. |
| [88](../../src/researchos_fusion/core.py#L88) | `class AssuranceEngine:` | State the input/output contract and trace one normal and one failing case. |
| [89](../../src/researchos_fusion/core.py#L89) | `def __init__(self) -> None:` | State the input/output contract and trace one normal and one failing case. |
| [93](../../src/researchos_fusion/core.py#L93) | `def register(self, claim: Claim) -> None:` | State the input/output contract and trace one normal and one failing case. |
| [95](../../src/researchos_fusion/core.py#L95) | `raise ValueError(f"Duplicate claim: {claim.identifier}")` | Construct the triggering input and explain why rejection preserves the contract. |
| [97](../../src/researchos_fusion/core.py#L97) | `raise ValueError("New claims must begin generated, without evidence/history")` | Construct the triggering input and explain why rejection preserves the contract. |
| [100](../../src/researchos_fusion/core.py#L100) | `raise ValueError("New claims cannot carry preapproved gates")` | Construct the triggering input and explain why rejection preserves the contract. |
| [102](../../src/researchos_fusion/core.py#L102) | `raise ValueError("Duplicate dependencies")` | Construct the triggering input and explain why rejection preserves the contract. |
| [104](../../src/researchos_fusion/core.py#L104) | `raise ValueError("Dependencies must already be registered")` | Construct the triggering input and explain why rejection preserves the contract. |
| [108](../../src/researchos_fusion/core.py#L108) | `def add_evidence(self, evidence: Evidence) -> None:` | State the input/output contract and trace one normal and one failing case. |
| [111](../../src/researchos_fusion/core.py#L111) | `raise ValueError(f"Duplicate evidence identifier: {evidence.identifier}")` | Construct the triggering input and explain why rejection preserves the contract. |
| [118](../../src/researchos_fusion/core.py#L118) | `def transition(self, claim_id: str, target: ClaimStatus, *, rationale: str) -> None:` | State the input/output contract and trace one normal and one failing case. |
| [121](../../src/researchos_fusion/core.py#L121) | `raise TransitionError(f"Invalid transition: {claim.status.value} -> {target.value}")` | Construct the triggering input and explain why rejection preserves the contract. |
| [123](../../src/researchos_fusion/core.py#L123) | `raise TransitionError("A transition rationale is required")` | Construct the triggering input and explain why rejection preserves the contract. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_core.py](../../tests/test_core.py)
- [tests/test_lab.py](../../tests/test_lab.py)
- [tests/test_physics.py](../../tests/test_physics.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. A claim-state engine is not a plasma topology solver, fusion controller or safety certification.
