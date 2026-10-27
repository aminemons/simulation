import numpy as np
import pytest

from nanoporous.dynamics import SimulationConfig, simulate
from nanoporous.geometry import PeriodicDiskGeometry, random_disk_geometry
from nanoporous.statistics import bootstrap_diffusivity, estimate_diffusivity


def test_free_brownian_diffusivity_recovers_einstein_relation():
    # Statistical tolerance intentionally larger than sampling variability.
    box = PeriodicDiskGeometry(16, np.empty((0, 2)), 0.8)
    config = SimulationConfig(
        diffusivity=0.6, dt=0.02, steps=1000, particles=2200,
        sample_every=20, seed=50, tracked_particles=3,
    )
    run = simulate(config, box)
    fit = estimate_diffusivity(run, start=0.1, end=0.9)
    assert abs(fit.relative_diffusivity - 1) < 0.13
    assert run.acceptance_fraction == 1.0
    assert run.time[0] == 0
    assert run.time[-1] == pytest.approx(20)


def test_seeded_trajectories_reproduce_bitwise():
    geom = random_disk_geometry(side=16, radius=0.8, count=8, seed=123)
    cfg = SimulationConfig(steps=51, particles=50, sample_every=10, seed=72)
    first = simulate(cfg, geom)
    second = simulate(cfg, geom)
    np.testing.assert_array_equal(first.msd, second.msd)
    np.testing.assert_array_equal(first.trajectories, second.trajectories)
    assert np.all(np.diff(first.time) > 0)
    assert first.time[-1] == pytest.approx(0.51)


def test_obstacles_reject_moves_and_reduce_acceptance():
    geom = random_disk_geometry(side=16, radius=0.8, count=25, seed=34)
    run = simulate(SimulationConfig(steps=200, particles=200, seed=8), geom)
    assert 0 < run.acceptance_fraction < 1
    assert np.all(run.msd >= 0)
    assert run.trajectories.shape[-1] == 2


def test_bootstrap_is_deterministic_and_has_sensible_bounds():
    geom = PeriodicDiskGeometry(10, np.empty((0, 2)), 0.5)
    run = simulate(SimulationConfig(steps=200, particles=120, seed=9), geom)
    first = bootstrap_diffusivity(run, repeats=30, seed=19)
    second = bootstrap_diffusivity(run, repeats=30, seed=19)
    assert first == second
    lo, hi = first["ci95"]
    assert lo < hi
    assert first["bootstrap_sd"] > 0


def test_invalid_configuration():
    with pytest.raises(ValueError):
        SimulationConfig(dt=-1)
