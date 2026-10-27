# Validation strategy and acceptance gates

We distinguish **software tests**, **numerical convergence**, and
**experimental validation**. Passing the first does not imply the others.

## Gate A — completed test infrastructure

1. Free motion: recover `MSD(t) ~= 4Dt` statistically with many independent
   particles, allowing a fixed numerical tolerance.
2. Seed replay: identical geometry and trajectory arrays across repeated runs.
3. Periodic minimum-image collision detection, expanded probe radius and
   sampled initial points outside obstacles.
4. Constant and heterogeneous continuum fields: relative mass error < 1e-12.
5. Fourier-mode analytical solution: final concentration error < 3e-4
   for the fixed test grid and step.
6. Reproducible stochastic inverse-design candidate ranking.
7. Expose model assumptions and uncertainties in every JSON result.

## Gate B — numerical verification to execute and report

Run a fixed **physical duration** with
`dt = [0.04, 0.02, 0.01, 0.005]`, increasing the number of steps accordingly.
For obstacle-containing systems, compare estimated diffusivities and the
fraction of rejected moves. Change one numerical factor at a time.

Perform independent particle-count and box-size studies; use multiple geometry
seeds and fitting windows. The endpoint-only collision approximation can
artificially allow trajectories to cross obstacles: test this specifically.
No definitive convergence claim should be made before recording the results.

## Gate C — actual external experimental evidence (not yet completed)

1. Obtain licensed raw tracking datasets and record exact citations.
2. Calibrate length and frame time; check tracking precision and blur.
3. Recompute measured experimental time-lag MSD (different from ensemble MSD
   from a common trajectory start) and characterize heterogeneity.
4. Identify physical variables independently, avoiding parameter leakage.
5. Split data by independent sample/gel, not randomly by individual frames.
6. Report absolute errors, distributions, sensitivity and uncertainty bands.
7. Compare to homogeneous Brownian model and at least one published method.
8. Assess model mismatch: charge, local viscosity, binding, and 3D projection.

## Publishability gate

A paper would require a genuinely new hypothesis or method plus careful
comparison with published baselines. A pretty dashboard, an optimizer, or a
simulation alone do not establish novelty or experimental validity.
