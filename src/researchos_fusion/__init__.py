"""Experimental epistemic-assurance building blocks for nuclear fusion research."""

from .core import Claim, Evidence, ClaimStatus, AssuranceEngine, ValidationResult, TransitionError
from .physics import dt_fusion_energy_mev, dt_fusion_energy_joules, energy_from_mass_defect

__all__ = ["Claim", "Evidence", "ClaimStatus", "AssuranceEngine", "ValidationResult", "TransitionError", "dt_fusion_energy_mev", "dt_fusion_energy_joules", "energy_from_mass_defect"]
