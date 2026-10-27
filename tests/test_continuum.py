import numpy as np
import pytest

from nanoporous.continuum import ContinuumConfig, run_continuum


def test_constant_field_stays_constant():
    cfg = ContinuumConfig(cells=64, dt=2e-5, steps=100, save_every=20)
    run = run_continuum(cfg, np.ones(64) * 1.8, diffusivity=0.5)
    np.testing.assert_allclose(run.concentrations, 1.8, atol=1e-12)
    assert run.relative_mass_error < 1e-12


def test_periodic_fourier_mode_matches_analytic_decay():
    cfg = ContinuumConfig(side=1, cells=128, dt=1e-5, steps=1000, save_every=250)
    x = (np.arange(cfg.cells) + 0.5) * cfg.dx
    initial = 1 + 0.3 * np.cos(2 * np.pi * x)
    d = 0.3
    result = run_continuum(cfg, initial, d)
    exact = 1 + 0.3 * np.exp(-d * (2 * np.pi)**2 * result.time[-1]) * np.cos(2 * np.pi * x)
    np.testing.assert_allclose(result.concentrations[-1], exact, atol=3e-4)
    assert result.relative_mass_error < 1e-12
    assert result.positivity_min >= 0


def test_heterogeneous_diffusion_conserves_mass():
    cfg = ContinuumConfig(cells=64, dt=1e-5, steps=300)
    x = (np.arange(cfg.cells) + 0.5) * cfg.dx
    d = np.where(x < 0.5, 0.2, 0.7)
    result = run_continuum(cfg, 0.2 + np.exp(-((x - 0.3) / 0.12)**2), d)
    assert result.relative_mass_error < 1e-12
    assert result.positivity_min >= -1e-12


def test_stability_limit_detected():
    cfg = ContinuumConfig(cells=64, dt=0.001, steps=10)
    with pytest.raises(ValueError, match="unstable"):
        run_continuum(cfg, np.ones(64), 1.0)
