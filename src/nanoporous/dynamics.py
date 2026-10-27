"""Overdamped Brownian transport through fixed, impermeable periodic disks.

A rejected trial endpoint approximates reflecting boundaries only as dt -> 0.
This method does not resolve trajectory/obstacle *segment* intersections.
Finite-step bias must be assessed before physical interpretation.
"""

from dataclasses import dataclass

import numpy as np

from .geometry import PeriodicDiskGeometry


@dataclass(frozen=True)
class SimulationConfig:
    """Dimensionless parameters; use one consistent physical unit system."""

    diffusivity: float = 1.0
    dt: float = 0.01
    steps: int = 1500
    particles: int = 256
    sample_every: int = 10
    probe_radius: float = 0.0
    seed: int = 42
    tracked_particles: int = 12

    def __post_init__(self) -> None:
        if not np.isfinite(self.diffusivity) or self.diffusivity <= 0:
            raise ValueError("diffusivity must be finite and positive")
        if not np.isfinite(self.dt) or self.dt <= 0:
            raise ValueError("dt must be finite and positive")
        if self.steps < 2 or self.particles < 2 or self.sample_every < 1:
            raise ValueError("steps >= 2, particles >= 2 and sample_every >= 1 required")
        if self.probe_radius < 0 or not np.isfinite(self.probe_radius):
            raise ValueError("probe_radius must be finite and nonnegative")
        if not 0 <= self.tracked_particles <= self.particles:
            raise ValueError("tracked_particles must be in [0, particles]")

    @property
    def rms_step(self) -> float:
        """Root-mean-square 2D Brownian displacement in one timestep."""
        return float(np.sqrt(4 * self.diffusivity * self.dt))


@dataclass
class SimulationResult:
    config: SimulationConfig
    time: np.ndarray
    msd: np.ndarray
    msd_sem: np.ndarray
    squared_displacements: np.ndarray
    trajectories: np.ndarray
    geometry: PeriodicDiskGeometry
    acceptance_fraction: float

    @property
    def relative_diffusion_baseline(self) -> np.ndarray:
        return 4.0 * self.config.diffusivity * self.time


def simulate(config: SimulationConfig, geometry: PeriodicDiskGeometry) -> SimulationResult:
    """Run independent particles; store MSD and a small set of unwrapped tracks.

    Periodic *wrapped* locations are used for collisions. Accumulated accepted
    displacements are stored separately to avoid a false MSD plateau at L².
    """
    rng = np.random.default_rng(config.seed)
    starts = geometry.sample_free_positions(
        config.particles, probe_radius=config.probe_radius, seed=config.seed + 1
    )
    wrapped = starts.copy()
    unwrapped = starts.copy()
    times: list[float] = []
    squared: list[np.ndarray] = []
    tracks: list[np.ndarray] = []
    accepted_moves = 0

    def record(step: int) -> None:
        displacement = unwrapped - starts
        squared.append(np.einsum("ij,ij->i", displacement, displacement).copy())
        times.append(step * config.dt)
        tracks.append(unwrapped[:config.tracked_particles].copy())

    record(0)
    sigma = np.sqrt(2 * config.diffusivity * config.dt)
    for step in range(1, config.steps + 1):
        increments = rng.normal(0, sigma, size=(config.particles, 2))
        trials = (wrapped + increments) % geometry.side
        allowed = ~geometry.blocked(trials, probe_radius=config.probe_radius)
        accepted_moves += int(np.count_nonzero(allowed))
        update = increments * allowed[:, None]
        wrapped = (wrapped + update) % geometry.side
        unwrapped += update
        if step % config.sample_every == 0 or step == config.steps:
            record(step)

    sq = np.stack(squared, axis=0)
    mean = np.mean(sq, axis=1)
    sem = np.std(sq, axis=1, ddof=1) / np.sqrt(config.particles)
    return SimulationResult(
        config=config,
        time=np.asarray(times),
        msd=mean,
        msd_sem=sem,
        squared_displacements=sq,
        trajectories=np.stack(tracks, axis=0),
        geometry=geometry,
        acceptance_fraction=accepted_moves / (config.steps * config.particles),
    )
