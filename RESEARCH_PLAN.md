# NanoPorous research roadmap

## Research question

How accurately can a minimal steric model of nanoparticle transport predict
long-time diffusion in a heterogeneous gel, and which extensions (local
viscosity, reversible attachment, real 3D geometries) are necessary to explain
independent experimental particle-tracking observations?

A *negative* result is informative: the model may not capture the measured
transport, and the goal is to identify why, not tune until curves overlap.

## Hypothesis and controls

**H1:** Dense, impermeable microstructure can reduce effective diffusivity
relative to free Brownian motion.

**H2 (untested):** Local drag heterogeneity and reversible particle/matrix
interactions explain experimental differences not explained by excluded-volume
geometry alone.

Primary controls:
- Homogeneous free Brownian motion at known diffusion coefficient.
- Fixed obstacles without interactions.
- Homogeneous effective-diffusion continuum description.
- A literature-based comparison selected *before* final experiments.

Metrics: lag-time MSD, effective diffusivity, measured diffusion distributions,
anomalous scaling if justified, error vs independent experiment, uncertainty
and numerical convergence.

## Current state: software foundation, NOT a completed thesis

Implemented: Python package, obstacle geometry, fixed-step Brownian dynamics,
periodic unwrapped tracks, trajectory-level uncertainty, continuum
finite-volume baseline, simple inverse grid search, lag-MSD utilities,
automated tests and explicit assumptions.

Not implemented: empirical parameter fit, extraction of raw tracking video,
real hydrogel morphology, 3D transport, binding potentials, reliable
reflecting-boundary integrator and multiscale validated closure.

## Phase II: Asmaa's scientific work

### W1: choose one published experimental dataset

Read the Liverpool nanorheology and 2024 Scientific Reports studies. Decide
which exact condition can be modelled without requiring unknown parameters.
Document sample composition, nanoparticle size, acquisition rate, microscopy
resolution, coordinate units, charge and raw data terms of reuse.
Avoid claiming comparison with experimental trajectories until obtaining them.

### W2: reproduce measured observables

Build a provenance-preserving import pipeline:
`data/raw/` (gitignored) -> `data/processed/` (gitignored) ->
`experiments/analysis/` (scripts) -> publication figures. Extract tracks
with Trackpy/TrackMate as appropriate, preserve per-track IDs and timestamps,
and compute time-lag MSD with localization-error caveats.

### W3: improve the physical solver

The initial endpoint-rejection scheme can miss thin obstacles. Choose and
justify a numerically convergent reflecting-Brownian method, assess behavior
at closely spaced obstacles, and compare against the initial baseline.
Then add a physically identified interaction term, **only if measurements
support its parameters**. Implement independent analytic tests.

### W4: inference and independent evaluation

Define training/calibration and held-out experimental conditions by *sample*.
Fit minimal parameters and report uncertainty. Compare against free
Brownian and homogeneous-effective-D baselines. Run time-step, particle
count, geometry-seed, fit-window, and finite-domain sensitivity.

### W5: paper and reproducibility

Deliver a methods report: physical model, algorithms, baselines, error
metrics, limitations, figures and complete instructions. Verify every
reported graph against a saved run and configuration file. A future
publication claim requires scientific novelty and an actual comparative
evaluation.

## Author and contribution policy

Contributors use their own GitHub accounts, current timestamps, meaningful
atomic changes and reviewable pull requests. Do not attribute a collaborator
as author or co-author unless they contributed to that work. Refer to the
GitHub history for provenance, not invented timelines.

## Definition of done for a research-ready v1

1. Physics and units documented; all tests green.
2. Independent experimental dataset imported with license/provenance.
3. At least one result from a paper re-analyzed independently.
4. At least three numerical convergence sweeps documented.
5. Baseline comparisons and held-out sample evaluation.
6. Uncertainty, failure cases, and limits clearly stated.
7. Research poster, figures and reproducible manuscript draft.

This is an **aspirational checklist**, not a claim these tasks are finished.
