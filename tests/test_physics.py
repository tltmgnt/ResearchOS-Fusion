import math
import pytest

from researchos_fusion import dt_fusion_energy_mev, dt_fusion_energy_joules, energy_from_mass_defect
from researchos_fusion.cli import run_demo


def test_reference_dt_reaction_energy():
    assert dt_fusion_energy_mev() == 17.6
    assert math.isclose(dt_fusion_energy_joules(), 2.81983087584e-12, rel_tol=1e-12)
    assert dt_fusion_energy_mev(2) == 35.2


def test_mass_energy():
    assert energy_from_mass_defect(0) == 0
    assert math.isclose(energy_from_mass_defect(1), 299_792_458**2)


@pytest.mark.parametrize("invalid", [-1.0, float("nan"), float("inf")])
def test_invalid_inputs(invalid):
    with pytest.raises(ValueError):
        dt_fusion_energy_mev(invalid)
    with pytest.raises(ValueError):
        energy_from_mass_defect(invalid)


def test_demo_does_not_claim_certification():
    output = run_demo()
    assert output["status"] == "supported"
    assert output["independent_reproduction"] is False


@pytest.mark.parametrize("function", [dt_fusion_energy_mev, dt_fusion_energy_joules, energy_from_mass_defect])
def test_overflow_rejected(function):
    with pytest.raises(ValueError, match="overflow"):
        function(1e308)
