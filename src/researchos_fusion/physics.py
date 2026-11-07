"""Small deterministic fusion reference calculations (not reactor-performance models)."""

from __future__ import annotations

from math import isfinite

SPEED_OF_LIGHT_M_S = 299_792_458.0
MEV_TO_JOULE = 1.602_176_634e-13
DT_FUSION_Q_MEV = 17.6  # Rounded reference value for D + T -> alpha + n


def energy_from_mass_defect(mass_defect_kg: float) -> float:
    """Calculate E=delta_m*c^2 in joules for positive mass defect (kg)."""
    if not isfinite(mass_defect_kg) or mass_defect_kg < 0:
        raise ValueError("Mass defect must be finite and nonnegative")
    return mass_defect_kg * SPEED_OF_LIGHT_M_S**2


def dt_fusion_energy_mev(reactions: float = 1) -> float:
    """Approximate released energy in MeV for a number of D-T fusion reactions."""
    if not isfinite(reactions) or reactions < 0:
        raise ValueError("Reaction count must be finite and nonnegative")
    return DT_FUSION_Q_MEV * reactions


def dt_fusion_energy_joules(reactions: float = 1) -> float:
    """Approximate total released energy in joules, before conversion losses."""
    return dt_fusion_energy_mev(reactions) * MEV_TO_JOULE
