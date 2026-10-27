"""Exploratory, simulation-only inverse design of accessible pore area.

This is a coarse grid-search baseline, not a proven optimal material design.
Results depend on random-sequential-adsorption geometry and finite-time MSD fits.
"""

from dataclasses import dataclass, replace

import numpy as np

from .dynamics import SimulationConfig, simulate
from .geometry import random_disk_geometry
from .statistics import estimate_diffusivity


@dataclass(frozen=True)
class DesignConfig:
    target_relative_diffusivity: float = 0.7
    fractions: tuple[float, ...] = (0.0, 0.05, 0.1, 0.15, 0.2)
    replicates: int = 3
    side: float = 16.0
    obstacle_radius: float = 0.8
    seed: int = 2026

    def __post_init__(self) -> None:
        if self.target_relative_diffusivity <= 0:
            raise ValueError("target must be positive")
        if self.replicates < 2 or self.side <= 0 or self.obstacle_radius <= 0:
            raise ValueError("replicates >= 2 and positive geometry required")
        if not self.fractions or any(not 0 <= f < 0.35 for f in self.fractions):
            raise ValueError("fractions must lie in [0, 0.35)")
        if tuple(sorted(set(self.fractions))) != tuple(self.fractions):
            raise ValueError("fractions must be sorted and unique")


def search_microstructures(
    design: DesignConfig,
    simulation: SimulationConfig | None = None,
) -> dict:
    """Rank nominal solid fractions by mean transport error across replicates.

    Fractions are discretized to whole disks, so actual achieved fractions
    differ slightly. Independent geometry and particle RNG seeds are used.
    No gradients, surrogate models, or empirical calibration are assumed.
    """
    if simulation is None:
        simulation = SimulationConfig(
            diffusivity=1.0, dt=0.012, steps=1000, particles=160,
            sample_every=10, tracked_particles=0
        )
    records = []
    for idx, nominal_fraction in enumerate(design.fractions):
        disk_count = round(nominal_fraction * design.side**2 /
                           (np.pi * design.obstacle_radius**2))
        measured = []
        acceptance = []
        for replicate in range(design.replicates):
            geometry_seed = design.seed + 1_000 * idx + replicate
            geometry = random_disk_geometry(
                side=design.side,
                radius=design.obstacle_radius,
                count=disk_count,
                seed=geometry_seed,
            )
            case = replace(
                simulation, seed=geometry_seed + 100_000, tracked_particles=0
            )
            result = simulate(case, geometry)
            measured.append(estimate_diffusivity(result).relative_diffusivity)
            acceptance.append(result.acceptance_fraction)
        mean_d = float(np.mean(measured))
        point = {
            "nominal_solid_fraction": nominal_fraction,
            "realized_solid_fraction": float(
                disk_count * np.pi * design.obstacle_radius**2 / design.side**2
            ),
            "obstacle_count": disk_count,
            "relative_diffusivity_mean": mean_d,
            "relative_diffusivity_sd": float(np.std(measured, ddof=1)),
            "replicate_values": [float(x) for x in measured],
            "acceptance_fraction_mean": float(np.mean(acceptance)),
            "target_absolute_error": abs(
                mean_d - design.target_relative_diffusivity
            ),
        }
        records.append(point)
    records.sort(key=lambda p: p["target_absolute_error"])
    return {
        "status": "unvalidated_simulation_grid_search",
        "target_relative_diffusivity": design.target_relative_diffusivity,
        "replicates": design.replicates,
        "best": records[0],
        "candidates_ranked": records,
        "warning": (
            "Finite-time 2D idealized obstacle model only. "
            "No empirical calibration or production-design guarantee."
        ),
    }
