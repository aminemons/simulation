"""Numerical diagnostics: fit-window sensitivity and timestep sweeps."""

from dataclasses import replace

import numpy as np

from .dynamics import SimulationConfig, SimulationResult, simulate
from .geometry import PeriodicDiskGeometry
from .statistics import estimate_diffusivity


def fit_window_sensitivity(
    result: SimulationResult,
    windows: tuple[tuple[float, float], ...] = (
        (0.1, 0.6), (0.2, 0.8), (0.3, 0.9), (0.4, 1.0)
    ),
) -> list[dict]:
    """Quantify the effect of fitting-time selection on D_eff."""
    records = []
    for start, end in windows:
        fit = estimate_diffusivity(result, start=start, end=end)
        records.append({
            "start": start,
            "end": end,
            "relative_diffusivity": fit.relative_diffusivity,
            "r_squared": fit.r_squared,
        })
    return records


def timestep_sweep(
    geometry: PeriodicDiskGeometry,
    baseline: SimulationConfig,
    dt_values: tuple[float, ...],
    *,
    duration: float,
) -> list[dict]:
    """Keep physical total duration fixed while changing the numerical timestep.

    Different dt grids are NOT pathwise coupled. Compare trends with sampling
    uncertainty, rather than interpreting one random ordering as convergence.
    """
    if duration <= 0 or not np.isfinite(duration):
        raise ValueError("duration must be finite and positive")
    if not dt_values or any(d <= 0 or not np.isfinite(d) for d in dt_values):
        raise ValueError("dt_values must be finite and positive")
    results = []
    for i, dt in enumerate(dt_values):
        steps = round(duration / dt)
        if steps < 2:
            raise ValueError("duration / dt must produce >= 2 steps")
        cfg = replace(
            baseline,
            dt=duration / steps,
            steps=steps,
            seed=baseline.seed + i * 10_000,
        )
        run = simulate(cfg, geometry)
        fit = estimate_diffusivity(run)
        results.append({
            "dt": cfg.dt,
            "steps": cfg.steps,
            "duration": cfg.dt * cfg.steps,
            "rms_step_to_disk_radius": (
                cfg.rms_step / geometry.radius if geometry.count else None
            ),
            "relative_diffusivity": fit.relative_diffusivity,
            "acceptance_fraction": run.acceptance_fraction,
            "fit_r_squared": fit.r_squared,
        })
    return results
