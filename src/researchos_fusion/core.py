"""Prototype TECT claim/evidence state machine; not an external scientific certification."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ClaimStatus(str, Enum):
    GENERATED = "generated"
    UNVERIFIED = "unverified"
    SUPPORTED = "supported"
    CONTESTED = "contested"
    REPRODUCED = "reproduced"
    VALIDATED = "validated"
    STABLE = "stable"
    ASSURED = "assured"


class TransitionError(ValueError):
    """Raised for a prohibited or insufficiently evidenced state transition."""


@dataclass(frozen=True)
class Evidence:
    identifier: str
    claim_id: str
    source: str
    method: str
    finding: str
    supports: bool
    independent_group: str
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all((self.identifier.strip(), self.claim_id.strip(), self.source.strip(),
                    self.method.strip(), self.finding.strip(), self.independent_group.strip())):
            raise ValueError("Evidence identifiers, provenance, method, finding and group are required")


@dataclass
class Claim:
    identifier: str
    statement: str
    assumptions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    status: ClaimStatus = ClaimStatus.GENERATED
    evidence: list[Evidence] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    adversarial_test_passed: bool = False
    independent_reproduction: bool = False
    governance_approved: bool = False
    stability_test_passed: bool = False

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.statement.strip():
            raise ValueError("Claim identifier and statement are required")
        if self.identifier in self.dependencies:
            raise ValueError("A claim cannot depend on itself")


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    reason: str
    test_name: str


# Deliberately conservative linear lifecycle. CONTESTED can be entered from any
# non-generated state and reviewed back to UNVERIFIED only, preventing bypass.
_NEXT: dict[ClaimStatus, frozenset[ClaimStatus]] = {
    ClaimStatus.GENERATED: frozenset({ClaimStatus.UNVERIFIED}),
    ClaimStatus.UNVERIFIED: frozenset({ClaimStatus.SUPPORTED, ClaimStatus.CONTESTED}),
    ClaimStatus.SUPPORTED: frozenset({ClaimStatus.REPRODUCED, ClaimStatus.CONTESTED}),
    ClaimStatus.REPRODUCED: frozenset({ClaimStatus.VALIDATED, ClaimStatus.CONTESTED}),
    ClaimStatus.VALIDATED: frozenset({ClaimStatus.STABLE, ClaimStatus.CONTESTED}),
    ClaimStatus.STABLE: frozenset({ClaimStatus.ASSURED, ClaimStatus.CONTESTED}),
    ClaimStatus.ASSURED: frozenset({ClaimStatus.CONTESTED}),
    ClaimStatus.CONTESTED: frozenset({ClaimStatus.UNVERIFIED}),
}


class AssuranceEngine:
    def __init__(self) -> None:
        self.claims: dict[str, Claim] = {}
        self._evidence_ids: set[str] = set()

    def register(self, claim: Claim) -> None:
        if claim.identifier in self.claims:
            raise ValueError(f"Duplicate claim: {claim.identifier}")
        if claim.status != ClaimStatus.GENERATED or claim.evidence or claim.history:
            raise ValueError("New claims must begin generated, without evidence/history")
        self.claims[claim.identifier] = claim
        self._log(claim, "register", "Registered new candidate claim")

    def add_evidence(self, evidence: Evidence) -> None:
        claim = self.claims[evidence.claim_id]
        if evidence.identifier in self._evidence_ids:
            raise ValueError(f"Duplicate evidence identifier: {evidence.identifier}")
        claim.evidence.append(evidence)
        self._evidence_ids.add(evidence.identifier)
        self._log(claim, "evidence", evidence.identifier)
        if not evidence.supports and claim.status not in (ClaimStatus.GENERATED, ClaimStatus.CONTESTED):
            prior = claim.status
            claim.status = ClaimStatus.CONTESTED
            self._log(claim, "transition", f"{prior.value} -> contested: conflicting evidence {evidence.identifier}")

    def transition(self, claim_id: str, target: ClaimStatus, *, rationale: str) -> None:
        claim = self.claims[claim_id]
        if target not in _NEXT[claim.status]:
            raise TransitionError(f"Invalid transition: {claim.status.value} -> {target.value}")
        if not rationale.strip():
            raise TransitionError("A transition rationale is required")
        if target == ClaimStatus.SUPPORTED:
            if not claim.evidence or not any(e.supports for e in claim.evidence):
                raise TransitionError("Supporting evidence required")
            if any(not e.supports for e in claim.evidence):
                raise TransitionError("Unresolved contradictory evidence")
        if target == ClaimStatus.REPRODUCED:
            support_groups = {e.independent_group for e in claim.evidence if e.supports}
            if not claim.independent_reproduction or len(support_groups) < 2:
                raise TransitionError("Reproduction flag and two provenance groups required")
        if target == ClaimStatus.VALIDATED and not claim.adversarial_test_passed:
            raise TransitionError("Adversarial testing required")
        if target == ClaimStatus.STABLE and not claim.stability_test_passed:
            raise TransitionError("Defined stability test required")
        if target == ClaimStatus.ASSURED and not claim.governance_approved:
            raise TransitionError("Governance approval required")
        if target == ClaimStatus.ASSURED:
            for dep in claim.dependencies:
                if dep not in self.claims or self.claims[dep].status != ClaimStatus.ASSURED:
                    raise TransitionError(f"Dependency {dep} is not assured")
        before = claim.status
        claim.status = target
        self._log(claim, "transition", f"{before.value} -> {target.value}: {rationale}")

    def export(self, claim_id: str) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of the claim and audit history."""
        return asdict(self.claims[claim_id])

    @staticmethod
    def _log(claim: Claim, action: str, detail: str) -> None:
        claim.history.append({"timestamp": datetime.now(timezone.utc).isoformat(),
                              "action": action, "detail": detail})
