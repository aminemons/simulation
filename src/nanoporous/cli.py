"""Command line experiments. No hidden network calls or downloaded datasets."""

import argparse
import json
from pathlib import Path

from .design import DesignConfig, search_microstructures
from .dynamics import SimulationConfig, simulate
from .geometry import random_disk_geometry
from .statistics import bootstrap_diffusivity, estimate_diffusivity


def _save(path: str, payload: dict) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(f"Saved {destination.resolve()}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="nanoporous", description="Reproducible nanoparticle diffusion experiments"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    sim_parser = commands.add_parser("simulate", help="Run particle-level transport")
    sim_parser.add_argument("--seed", type=int, default=17)
    sim_parser.add_argument("--particles", type=int, default=300)
    sim_parser.add_argument("--steps", type=int, default=1800)
    sim_parser.add_argument("--dt", type=float, default=0.01)
    sim_parser.add_argument("--obstacles", type=int, default=16)
    sim_parser.add_argument("--radius", type=float, default=0.8)
    sim_parser.add_argument("--probe-radius", type=float, default=0.0)
    sim_parser.add_argument("--out", default="outputs/simulation.json")

    design_parser = commands.add_parser("design", help="Coarse simulated inverse design")
    design_parser.add_argument("--target", type=float, default=0.7)
    design_parser.add_argument("--seed", type=int, default=2026)
    design_parser.add_argument("--replicates", type=int, default=3)
    design_parser.add_argument("--out", default="outputs/design.json")

    args = parser.parse_args(argv)
    if args.command == "simulate":
        cfg = SimulationConfig(
            particles=args.particles,
            steps=args.steps,
            dt=args.dt,
            probe_radius=args.probe_radius,
            seed=args.seed,
        )
        geometry = random_disk_geometry(
            side=16.0, radius=args.radius, count=args.obstacles, seed=args.seed + 1000
        )
        run = simulate(cfg, geometry)
        estimate = estimate_diffusivity(run)
        interval = bootstrap_diffusivity(run, seed=args.seed + 2000)
        payload = {
            "status": "simulation_only_not_experimentally_validated",
            "model": "2D overdamped Brownian, periodic box, hard-disk endpoint rejection",
            "parameters": vars(cfg),
            "geometry": {
                "side": geometry.side,
                "radius": geometry.radius,
                "centers": geometry.centers.tolist(),
                "solid_area_fraction": geometry.solid_area_fraction,
            },
            "numerical_caution": {
                "rms_step": cfg.rms_step,
                "rms_step_to_disk_radius": (
                    cfg.rms_step / geometry.radius if geometry.count else None
                ),
            },
            "time": run.time.tolist(),
            "msd": run.msd.tolist(),
            "msd_sem": run.msd_sem.tolist(),
            "tracked_unwrapped_trajectories": run.trajectories.tolist(),
            "fit": estimate.to_dict(),
            "bootstrap": interval,
            "acceptance_fraction": run.acceptance_fraction,
        }
        _save(args.out, payload)
        print(f"D_eff / D_free = {estimate.relative_diffusivity:.3f}")
    else:
        design = DesignConfig(
            target_relative_diffusivity=args.target,
            seed=args.seed,
            replicates=args.replicates,
        )
        response = search_microstructures(design)
        _save(args.out, response)
        print(
            "Best nominal solid fraction:",
            response["best"]["nominal_solid_fraction"],
        )


if __name__ == "__main__":
    main()
