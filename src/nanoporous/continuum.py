"""Mass-conserving 1D finite-volume continuum diffusion baseline.

PDE: dc/dt = d/dx(D(x) dc/dx) on a periodic domain.
This solver is currently *independent* of the particle-scale solver. Computing
D_eff from Brownian dynamics and calibrating a continuum closure is future work.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ContinuumConfig:
    side: float = 1.0
    cells: int = 128
    dt: float = 1e-5
    steps: int = 1000
    save_every: int = 100

    def __post_init__(self) -> None:
        if self.side <= 0 or not np.isfinite(self.side):
            raise ValueError("side must be positive")
        if self.cells < 3 or self.dt <= 0 or self.steps < 1 or self.save_every < 1:
            raise ValueError("invalid continuum resolution/time discretization")

    @property
    def dx(self) -> float:
        return self.side / self.cells


@dataclass
class ContinuumResult:
    positions: np.ndarray
    time: np.ndarray
    concentrations: np.ndarray
    initial_mass: float
    relative_mass_error: float
    positivity_min: float


def run_continuum(
    config: ContinuumConfig, initial: np.ndarray, diffusivity: np.ndarray | float
) -> ContinuumResult:
    """Conservative explicit scheme with harmonic face diffusivities.

    Requiring dt <= dx²/(2 max D_face) is sufficient for positivity with
    nonnegative initial concentrations. For speed, no implicit solver is used.
    """
    c = np.asarray(initial, dtype=float).copy()
    if c.shape != (config.cells,) or not np.isfinite(c).all() or np.any(c < 0):
        raise ValueError("initial concentration must be nonnegative shape (cells,)")
    d = np.broadcast_to(np.asarray(diffusivity, dtype=float), c.shape)
    if not np.isfinite(d).all() or np.any(d <= 0):
        raise ValueError("diffusivity must be finite and strictly positive")
    neighbor = np.roll(d, -1)
    face_d = 2.0 * d * neighbor / (d + neighbor)
    if config.dt > config.dx**2 / (2 * np.max(face_d)) * (1 + 1e-12):
        raise ValueError("unstable timestep: reduce dt or increase dx")
    x = (np.arange(config.cells) + 0.5) * config.dx
    c0_mass = float(c.sum() * config.dx)
    if c0_mass <= 0:
        raise ValueError("initial total mass must be positive")

    saved = [c.copy()]
    times = [0.0]
    for step in range(1, config.steps + 1):
        right_flux = -face_d * (np.roll(c, -1) - c) / config.dx
        c -= config.dt * (right_flux - np.roll(right_flux, 1)) / config.dx
        if step % config.save_every == 0 or step == config.steps:
            saved.append(c.copy())
            times.append(step * config.dt)

    masses = np.array([array.sum() * config.dx for array in saved])
    return ContinuumResult(
        positions=x,
        time=np.asarray(times),
        concentrations=np.stack(saved, axis=0),
        initial_mass=c0_mass,
        relative_mass_error=float(np.max(np.abs(masses - c0_mass)) / c0_mass),
        positivity_min=float(np.min(saved)),
    )
