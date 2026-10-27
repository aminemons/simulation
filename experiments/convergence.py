"""Reproducible numerical diagnostic artifact for fixed-duration timestep sweeps.

Run after 'pip install -e .' from repository root:
    python experiments/convergence.py --out outputs/convergence.json

This *generates numerical data only*. No claim of convergence is hard-coded.
"""

import argparse
import json
from pathlib import Path

from nanoporous.diagnostics import timestep_sweep
from nanoporous.dynamics import SimulationConfig
from nanoporous.geometry import random_disk_geometry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="outputs/convergence.json")
    parser.add_argument("--duration", type=float, default=12.0)
    parser.add_argument("--particles", type=int, default=400)
    parser.add_argument("--seed", type=int, default=2042)
    args = parser.parse_args()

    geometry = random_disk_geometry(
        side=16, radius=0.8, count=20, seed=args.seed
    )
    config = SimulationConfig(
        particles=args.particles, steps=100,
        sample_every=10, tracked_particles=0, seed=args.seed + 10,
    )
    records = timestep_sweep(
        geometry, config, (0.04, 0.02, 0.01, 0.005),
        duration=args.duration
    )
    artifact = {
        "status": "numerical_diagnostic_only",
        "geometry_seed": args.seed,
        "particle_count": args.particles,
        "obstacles": 20,
        "records": records,
        "notes": (
            "One independent run per dt is insufficient to establish "
            "convergence. Repeat with multiple geometry and simulation seeds."
        ),
    }
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
