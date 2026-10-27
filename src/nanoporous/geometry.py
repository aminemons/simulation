"""Periodic 2D hard-disk microstructures for excluded-volume transport.

All coordinates and radii use the same length unit; there is no implied
nanometre or micrometre calibration.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PeriodicDiskGeometry:
    """A square 2D unit cell tiled periodically in both directions."""

    side: float
    centers: np.ndarray
    radius: float

    def __post_init__(self) -> None:
        if not np.isfinite(self.side) or self.side <= 0:
            raise ValueError("side must be finite and positive")
        if not np.isfinite(self.radius) or not 0 <= self.radius < self.side / 2:
            raise ValueError("radius must satisfy 0 <= radius < side / 2")
        centers = np.asarray(self.centers, dtype=float)
        if centers.ndim != 2 or centers.shape[1] != 2:
            raise ValueError("centers must have shape (n_obstacles, 2)")
        if not np.isfinite(centers).all():
            raise ValueError("obstacle coordinates must be finite")
        object.__setattr__(self, "centers", centers % self.side)

    @property
    def count(self) -> int:
        return self.centers.shape[0]

    @property
    def solid_area_fraction(self) -> float:
        """Nominal disk area / unit-cell area (nonoverlap assumed)."""
        return float(self.count * np.pi * self.radius**2 / self.side**2)

    def minimum_image_displacement(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Return displacement a-b to the nearest periodic image."""
        delta = np.asarray(a) - np.asarray(b)
        return delta - self.side * np.floor(delta / self.side + 0.5)

    def blocked(self, points: np.ndarray, probe_radius: float = 0.0) -> np.ndarray:
        """Whether N probe centers overlap any obstacle under periodic images.

        A nonzero probe_radius expands the exclusion region around each disk.
        """
        pts = np.asarray(points, dtype=float)
        if pts.ndim != 2 or pts.shape[1] != 2:
            raise ValueError("points must be an (n, 2) array")
        if probe_radius < 0 or not np.isfinite(probe_radius):
            raise ValueError("probe_radius must be finite and nonnegative")
        if self.count == 0:
            return np.zeros(len(pts), dtype=bool)
        if self.radius + probe_radius >= self.side / 2:
            raise ValueError("exclusion radius must be less than side / 2")
        result = np.zeros(len(pts), dtype=bool)
        # Loop over obstacles to bound peak memory at O(n_particles).
        for center in self.centers:
            delta = self.minimum_image_displacement(pts, center)
            result |= np.einsum("ij,ij->i", delta, delta) < (self.radius + probe_radius)**2
        return result

    def sample_free_positions(
        self, count: int, *, probe_radius: float = 0.0, seed: int = 0
    ) -> np.ndarray:
        """Sample starting centers uniformly from the accessible unit cell."""
        if count < 1:
            raise ValueError("count must be positive")
        rng = np.random.default_rng(seed)
        accepted: list[np.ndarray] = []
        total = 0
        for _ in range(200):
            proposals = rng.uniform(0, self.side, size=(max(count, 64), 2))
            free = proposals[~self.blocked(proposals, probe_radius)]
            if len(free):
                accepted.append(free)
                total += len(free)
                if total >= count:
                    return np.concatenate(accepted, axis=0)[:count]
        raise RuntimeError("Could not sample accessible space; reduce obstacle density")


def random_disk_geometry(
    *,
    side: float,
    radius: float,
    count: int,
    seed: int,
    min_gap: float = 0.0,
    max_attempts: int = 100_000,
) -> PeriodicDiskGeometry:
    """Sequentially pack nonoverlapping obstacles, including across boundaries.

    This produces a *sequential adsorption* ensemble, not an equilibrium
    disordered polymer network. At high packing fractions it may fail.
    """
    if count < 0 or radius <= 0 or side <= 0 or min_gap < 0:
        raise ValueError("invalid geometry parameters")
    if 2 * radius + min_gap >= side and count > 1:
        raise ValueError("obstacles too large for a periodic unit cell")
    rng = np.random.default_rng(seed)
    centers: list[np.ndarray] = []
    for _ in range(max_attempts):
        if len(centers) == count:
            break
        point = rng.uniform(0, side, 2)
        if centers:
            delta = np.asarray(centers) - point
            delta -= side * np.floor(delta / side + 0.5)
            if np.any(np.sum(delta**2, axis=1) < (2 * radius + min_gap)**2):
                continue
        centers.append(point)
    if len(centers) != count:
        raise RuntimeError(f"Packed {len(centers)}/{count} disks; lower packing fraction")
    return PeriodicDiskGeometry(side, np.asarray(centers).reshape(-1, 2), radius)
