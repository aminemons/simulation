import numpy as np
import pytest

from nanoporous.geometry import PeriodicDiskGeometry, random_disk_geometry


def test_periodic_nearest_image_collision():
    box = PeriodicDiskGeometry(10, np.array([[0.2, 5.0]]), 0.5)
    assert bool(box.blocked(np.array([[9.9, 5.0]]))[0])
    assert not bool(box.blocked(np.array([[9.0, 5.0]]))[0])


def test_probes_expand_exclusion_radius():
    box = PeriodicDiskGeometry(10, np.array([[5.0, 5.0]]), 0.5)
    points = np.array([[5.8, 5.0]])
    assert not box.blocked(points)[0]
    assert box.blocked(points, probe_radius=0.4)[0]


def test_packing_is_deterministic_and_nonoverlapping():
    a = random_disk_geometry(side=16, radius=0.8, count=22, seed=101)
    b = random_disk_geometry(side=16, radius=0.8, count=22, seed=101)
    np.testing.assert_array_equal(a.centers, b.centers)
    for i in range(a.count):
        for j in range(i + 1, a.count):
            separation = a.minimum_image_displacement(a.centers[i], a.centers[j])
            assert np.linalg.norm(separation) >= 1.6 - 1e-12


def test_sample_free_positions_are_accessible():
    geom = random_disk_geometry(side=16, radius=0.8, count=20, seed=1)
    points = geom.sample_free_positions(100, probe_radius=0.2, seed=2)
    assert points.shape == (100, 2)
    assert not np.any(geom.blocked(points, probe_radius=0.2))


def test_invalid_geometry():
    with pytest.raises(ValueError):
        PeriodicDiskGeometry(0, np.empty((0, 2)), 0.5)
    with pytest.raises(ValueError):
        PeriodicDiskGeometry(10, np.array([1.0, 2.0]), 0.5)
