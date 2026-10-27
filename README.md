# NanoPorous

**Physics-based nanoparticle transport in heterogeneous functional hydrogels.**

NanoPorous is a reproducible computational-materials research project. It connects
an overdamped Brownian particle model in periodic porous microstructures with
continuum diffusion, transport statistics, and an exploratory inverse-design baseline.

> **Research status:** computational prototype. The code includes numerical and
> analytical checks, but is **not experimentally validated** and does not predict
> clinical drug delivery or in-vivo outcomes.

## Why this matters

Effective particle mobility in hydrogels depends on particle size, matrix
geometry, and interactions. Rather than treating a gel as one uniform diffusion
coefficient, we test how excluded-volume obstacles alter trajectories and
long-time diffusivity.

Our initial, falsifiable hypothesis is that accessible pore geometry can
reduce the long-time diffusion coefficient relative to the Stokes–Einstein
free-particle baseline, and that the inferred transport response depends on
time resolution and geometry. This phase deliberately excludes binding,
electrostatics, polymer flexibility, and 3D effects.

## Implemented scope

- Reproducible 2D periodic disk-obstacle microstructures and steric probes.
- Vectorized overdamped Brownian dynamics with rejection at hard obstacles.
- Unwrapped trajectories and ensemble mean-squared displacement (MSD).
- Estimation of effective diffusion and trajectory uncertainty.
- A conservative 1D continuum finite-volume solver.
- A coarse microstructure inverse-design grid search, with independent repeats.
- Unit and numerical regression tests, research notes and an example CLI.

## Installation

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
python -m nanoporous.cli simulate --seed 17 --out outputs/example.json
python -m nanoporous.cli design --target 0.7 --out outputs/design.json
```

The quantities are **dimensionless by default**: domain size, displacement,
diffusion coefficient and timestep must use one consistent unit system.
`target` in the inverse design command means `D_eff / D_free`, not an
experimentally calibrated material property.

## Model

For free particles, overdamped Langevin dynamics are approximated by

```text
X(t + dt) = X(t) + sqrt(2 D_free dt) * Normal(0, I_2)
MSD(t) = E[|X(t) - X(0)|²] = 4 D_free t
```

For disk obstacles, a proposed move that lands in a forbidden region is
rejected; physical positions are periodic but **unwrapped positions** are
retained for the MSD. This is a finite-step approximation to reflecting
Brownian motion. It is not exact when steps cross thin obstacles, and
convergence with decreasing timestep must be checked.

See [MODEL.md](MODEL.md), [VALIDATION.md](VALIDATION.md) and
[RESEARCH_PLAN.md](RESEARCH_PLAN.md) for assumptions, acceptance criteria,
and division of future research tasks.

## Repository layout

```text
src/nanoporous/    geometry, stochastic dynamics, statistics, continuum, design, CLI
tests/             free-diffusion, geometry, finite-volume, reproducibility
experiments/       research protocols
data/              licensed data manifest only; raw measurements excluded
.github/workflows/ unit-test pipeline
```

## Research provenance

Scientific conclusions require independent experimental validation.
Relevant starting points and licensing notes are collected in
[data/SOURCES.md](data/SOURCES.md). No literature result is claimed to be
reproduced until that reproduction is executed and documented.

## Collaboration

Implementation and documentation contributed through the connected
`aminemons` GitHub account. Scientific review, experimental calibration,
and extensions remain open for Asmaa and collaborators. Git commit authorship
must reflect actual work; no history is backdated or assigned to someone else.

MIT License.