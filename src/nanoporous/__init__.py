"""NanoPorous: research-grade foundations for nanoparticle transport models.

The version number describes software maturity, not experimental validation.
"""

from .dynamics import SimulationConfig, SimulationResult, simulate
from .geometry import PeriodicDiskGeometry, random_disk_geometry
from .statistics import DiffusionEstimate, bootstrap_diffusivity, estimate_diffusivity

__version__ = "0.1.0"
__all__ = [
    "SimulationConfig",
    "SimulationResult",
    "simulate",
    "PeriodicDiskGeometry",
    "random_disk_geometry",
    "DiffusionEstimate",
    "bootstrap_diffusivity",
    "estimate_diffusivity",
]
