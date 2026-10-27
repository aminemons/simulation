import numpy as np
import pytest

from nanoporous.diagnostics import fit_window_sensitivity, timestep_sweep
from nanoporous.dynamics import SimulationConfig, simulate
from nanoporous.geometry import PeriodicDiskGeometry
from nanoporous.tracking import time_averaged_msd


def test_time_averaged_msd_matches_ballistic_tracks():
    t = np.arange(12)
    positions = np.zeros((12, 3, 2))
    positions[:, :, 0] = t[:, None] * np.array([1.0, 2.0, 3.0])
    output = time_averaged_msd(positions, frame_interval=0.5, max_lag=3)
    assert output.lag_time.tolist() == [0.5, 1.0, 1.5]
    np.testing.assert_allclose(output.mean, np.array([1.0, 4.0, 9.0]) * 14 / 3)
    np.testing.assert_array_equal(output.valid_track_counts, [3, 3, 3])


def test_missing_frames_only_remove_invalid_lag_pairs():
    positions = np.zeros((10, 3, 2))
    positions[:, :, 0] = np.arange(10)[:, None]
    positions[4, 0, :] = np.nan
    output = time_averaged_msd(positions, frame_interval=1, max_lag=2)
    np.testing.assert_allclose(output.mean, [1, 4])
    assert np.all(output.valid_track_counts == 3)


def test_numerical_diagnostics_are_reproducible():
    geom = PeriodicDiskGeometry(16, np.empty((0, 2)), 0.5)
    config = SimulationConfig(steps=100, particles=70, sample_every=5, seed=71)
    run = simulate(config, geom)
    windows = fit_window_sensitivity(run)
    assert len(windows) == 4
    first = timestep_sweep(geom, config, (0.01, 0.02), duration=2)
    second = timestep_sweep(geom, config, (0.01, 0.02), duration=2)
    assert first == second
    assert all(point["duration"] == pytest.approx(2) for point in first)


def test_invalid_track_input():
    with pytest.raises(ValueError):
        time_averaged_msd(np.ones((3, 3, 2)), 1)
