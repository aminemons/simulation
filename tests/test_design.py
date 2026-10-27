import numpy as np
import pytest

from nanoporous.design import DesignConfig, search_microstructures
from nanoporous.dynamics import SimulationConfig


def test_inverse_design_is_reproducible_and_ranks_error():
    design = DesignConfig(
        target_relative_diffusivity=0.8,
        fractions=(0.0, 0.05),
        replicates=2,
        seed=901,
    )
    simulation = SimulationConfig(
        steps=130, particles=60, sample_every=10, seed=5,
        tracked_particles=0,
    )
    first = search_microstructures(design, simulation)
    second = search_microstructures(design, simulation)
    assert first == second
    assert first["status"] == "unvalidated_simulation_grid_search"
    assert len(first["candidates_ranked"]) == 2
    error = [item["target_absolute_error"] for item in first["candidates_ranked"]]
    assert error == sorted(error)
    for item in first["candidates_ranked"]:
        assert np.isfinite(item["relative_diffusivity_mean"])
        assert len(item["replicate_values"]) == 2


def test_design_rejects_unphysical_parameters():
    with pytest.raises(ValueError):
        DesignConfig(fractions=(0.3, 0.1))
    with pytest.raises(ValueError):
        DesignConfig(replicates=1)
