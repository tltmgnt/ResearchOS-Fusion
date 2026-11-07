import pytest

from researchos_fusion import AssuranceEngine, Claim, ClaimStatus, Evidence, TransitionError


def _evidence(identifier="e1", supports=True, group="source1"):
    return Evidence(identifier, "c1", "test source", "test method", "finding", supports, group)


def _unverified():
    engine = AssuranceEngine()
    engine.register(Claim("c1", "Testable scientific claim"))
    engine.transition("c1", ClaimStatus.UNVERIFIED, rationale="Start reviewing")
    return engine


def test_new_claim_initial_state_and_history():
    engine = AssuranceEngine()
    engine.register(Claim("c1", "An assertion"))
    output = engine.export("c1")
    assert output["status"] == "generated"
    assert output["history"][0]["action"] == "register"


def test_support_requires_evidence():
    engine = _unverified()
    with pytest.raises(TransitionError, match="Supporting evidence"):
        engine.transition("c1", ClaimStatus.SUPPORTED, rationale="No evidence")
    engine.add_evidence(_evidence())
    engine.transition("c1", ClaimStatus.SUPPORTED, rationale="Evidence supplied")
    assert engine.claims["c1"].status == ClaimStatus.SUPPORTED


def test_contradictory_evidence_reopens_supported_claim():
    engine = _unverified()
    engine.add_evidence(_evidence())
    engine.transition("c1", ClaimStatus.SUPPORTED, rationale="Supported")
    engine.add_evidence(_evidence("e2", False, "source2"))
    assert engine.claims["c1"].status == ClaimStatus.CONTESTED
    engine.transition("c1", ClaimStatus.UNVERIFIED, rationale="Reassess contradiction")
    with pytest.raises(TransitionError, match="Unresolved contradictory"):
        engine.transition("c1", ClaimStatus.SUPPORTED, rationale="Ignore conflict")


def test_reproduction_requires_independence_and_flag():
    engine = _unverified()
    engine.add_evidence(_evidence())
    engine.transition("c1", ClaimStatus.SUPPORTED, rationale="Supported")
    with pytest.raises(TransitionError, match="two provenance"):
        engine.transition("c1", ClaimStatus.REPRODUCED, rationale="Not independently reproduced")
    engine.claims["c1"].independent_reproduction = True
    engine.add_evidence(_evidence("e2", True, "source2"))
    engine.transition("c1", ClaimStatus.REPRODUCED, rationale="Independent method")
    assert engine.claims["c1"].status == ClaimStatus.REPRODUCED


def test_full_gate_sequence():
    engine = _unverified()
    engine.add_evidence(_evidence())
    engine.add_evidence(_evidence("e2", True, "source2"))
    claim = engine.claims["c1"]
    claim.independent_reproduction = True
    engine.transition("c1", ClaimStatus.SUPPORTED, rationale="Initial evidence")
    engine.transition("c1", ClaimStatus.REPRODUCED, rationale="Independent reproduction")
    with pytest.raises(TransitionError, match="Adversarial"):
        engine.transition("c1", ClaimStatus.VALIDATED, rationale="Premature")
    claim.adversarial_test_passed = True
    engine.transition("c1", ClaimStatus.VALIDATED, rationale="Challenge suite completed")
    claim.stability_test_passed = True
    engine.transition("c1", ClaimStatus.STABLE, rationale="Defined perturbations tested")
    with pytest.raises(TransitionError, match="Governance"):
        engine.transition("c1", ClaimStatus.ASSURED, rationale="Premature")
    claim.governance_approved = True
    engine.transition("c1", ClaimStatus.ASSURED, rationale="Approved for defined use")
    assert claim.status == ClaimStatus.ASSURED


def test_duplicate_evidence_rejected():
    engine = _unverified()
    engine.add_evidence(_evidence())
    with pytest.raises(ValueError, match="Duplicate evidence"):
        engine.add_evidence(_evidence())


def test_dependency_not_assured_blocks_assurance():
    engine = _unverified()
    engine.register(Claim("c2", "Upstream dependency"))
    engine.claims["c1"].dependencies = ["c2"]
    engine.add_evidence(_evidence())
    engine.add_evidence(_evidence("e2", True, "source2"))
    claim = engine.claims["c1"]
    claim.independent_reproduction = True
    claim.adversarial_test_passed = True
    claim.stability_test_passed = True
    claim.governance_approved = True
    for target in (ClaimStatus.SUPPORTED, ClaimStatus.REPRODUCED, ClaimStatus.VALIDATED, ClaimStatus.STABLE):
        engine.transition("c1", target, rationale="Test progression")
    with pytest.raises(TransitionError, match="Dependency"):
        engine.transition("c1", ClaimStatus.ASSURED, rationale="Dependency unresolved")
