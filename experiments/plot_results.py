"""Create a publication-style diagnostic figure from a saved simulation JSON.

Usage:
    pip install -e ".[plots]"
    python -m nanoporous.cli simulate --out outputs/simulation.json
    python experiments/plot_results.py outputs/simulation.json --out outputs/figure.png

The generated graphs show simulated values ONLY. The free-particle curve is
an analytic reference, not an experimental measurement.
"""

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, default=Path("outputs/figure.png"))
    args = parser.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = json.loads(args.input.read_text(encoding="utf-8"))
    t = np.asarray(data["time"], dtype=float)
    y = np.asarray(data["msd"], dtype=float)
    sem = np.asarray(data["msd_sem"], dtype=float)
    params = data["parameters"]
    paths = np.asarray(data["tracked_unwrapped_trajectories"], dtype=float)
    centers = np.asarray(data["geometry"]["centers"], dtype=float)
    side = float(data["geometry"]["side"])
    r = float(data["geometry"]["radius"])

    fig, (ax, tracks_ax) = plt.subplots(1, 2, figsize=(11.2, 4.6))
    ax.plot(t, y, color="#234e70", lw=2, label="Simulated ensemble MSD")
    ax.fill_between(t, np.maximum(0, y - sem), y + sem,
                    color="#234e70", alpha=0.15, label="SEM across particles")
    ax.plot(t, 4 * params["diffusivity"] * t, "--",
            color="#bf613d", lw=1.7, label="Free Brownian reference")
    ax.set(xlabel="Time (model units)", ylabel="MSD (model length²)",
           title="Nanoparticle transport")
    ax.grid(alpha=0.17)
    ax.legend(frameon=False, fontsize=8)

    # Tracks are unwrapped. Plot each displacement relative to its origin so
    # trajectories are directly comparable and not clipped to one unit cell.
    if paths.ndim == 3 and paths.shape[1] > 0:
        for k in range(paths.shape[1]):
            p = paths[:, k] - paths[0, k]
            tracks_ax.plot(p[:, 0], p[:, 1], alpha=0.85, lw=0.9)
            tracks_ax.scatter(p[0, 0], p[0, 1], s=7, color="#222222", zorder=4)
    tracks_ax.set_aspect("equal", adjustable="box")
    tracks_ax.set(xlabel="Unwrapped Δx (model length)",
                  ylabel="Unwrapped Δy (model length)",
                  title="Selected simulated trajectories")
    tracks_ax.grid(alpha=0.17)

    # Inset geometry is deliberately omitted: unwrapped displacements and
    # wrapped disk centers live in different coordinate systems.
    fig.suptitle(
        f"NanoPorous · {len(centers)} periodic disks · L={side:g} · r={r:g}",
        fontsize=11,
    )
    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved diagnostic figure to {args.out}")


if __name__ == "__main__":
    main()
