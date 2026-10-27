"""Diffusion estimation and bootstrap uncertainty from independent particles."""

from dataclasses import dataclass

import numpy as np

from .dynamics import SimulationResult


@dataclass(frozen=True)
class DiffusionEstimate:
    diffusivity: float
    relative_diffusivity: float
    slope: float
    intercept: float
    r_squared: float
    fit_from: float
    fit_to: float

    def to_dict(self) -> dict:
        return {
            "diffusivity": self.diffusivity,
            "relative_diffusivity": self.relative_diffusivity,
            "slope": self.slope,
            "intercept": self.intercept,
            "r_squared": self.r_squared,
            "fit_from": self.fit_from,
            "fit_to": self.fit_to,
        }


def _fit(times: np.ndarray, msd: np.ndarray, start: float, end: float) -> tuple:
    if not 0 <= start < end <= 1:
        raise ValueError("fit window must satisfy 0 <= start < end <= 1")
    begin = times[0] + start * (times[-1] - times[0])
    finish = times[0] + end * (times[-1] - times[0])
    window = (times >= begin) & (times <= finish)
    if np.count_nonzero(window) < 3:
        raise ValueError("fit window needs at least three observations")
    t = times[window]
    y = msd[window]
    matrix = np.column_stack([t, np.ones_like(t)])
    slope, intercept = np.linalg.lstsq(matrix, y, rcond=None)[0]
    predicted = slope * t + intercept
    ss_res = float(np.sum((y - predicted)**2))
    ss_total = float(np.sum((y - np.mean(y))**2))
    r2 = 1 - ss_res / ss_total if ss_total > 0 else float("nan")
    return float(slope), float(intercept), r2, float(t[0]), float(t[-1])


def estimate_diffusivity(
    result: SimulationResult, *, start: float = 0.3, end: float = 0.9
) -> DiffusionEstimate:
    """Estimate D from MSD(t) ~ 4 D t (2D).

    A high R² alone does not prove asymptotic diffusion: also inspect MSD
    shape, fitting-window sensitivity, finite-size effects and convergence.
    """
    slope, intercept, r2, a, b = _fit(result.time, result.msd, start, end)
    d = slope / 4
    return DiffusionEstimate(
        diffusivity=d,
        relative_diffusivity=d / result.config.diffusivity,
        slope=slope,
        intercept=intercept,
        r_squared=r2,
        fit_from=a,
        fit_to=b,
    )


def bootstrap_diffusivity(
    result: SimulationResult, *, repeats: int = 300, seed: int = 123,
    start: float = 0.3, end: float = 0.9
) -> dict:
    """Percentile CI from resampling *entire independent particle tracks*.

    Avoid resampling individual timepoints: observations along one Brownian
    trajectory are temporally correlated. This CI reflects particle-sampling
    noise, NOT finite-timestep, geometric, or model-form uncertainties.
    """
    if repeats < 20:
        raise ValueError("bootstrap repeats must be >= 20")
    sq = result.squared_displacements
    rng = np.random.default_rng(seed)
    values = np.empty(repeats, dtype=float)
    for i in range(repeats):
        ids = rng.integers(0, sq.shape[1], size=sq.shape[1])
        msd = sq[:, ids].mean(axis=1)
        slope, *_ = _fit(result.time, msd, start, end)
        values[i] = slope / 4
    lo, hi = np.percentile(values, [2.5, 97.5])
    return {
        "method": "independent-particle-bootstrap",
        "repeats": repeats,
        "ci95": [float(lo), float(hi)],
        "relative_ci95": [
            float(lo / result.config.diffusivity),
            float(hi / result.config.diffusivity),
        ],
        "bootstrap_sd": float(np.std(values, ddof=1)),
    }
