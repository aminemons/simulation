# Numerical experiments

These scripts are deterministic *when run with the same software and RNG
versions*; every result must include its parameters and seed.

## First smoke experiment

```bash
python -m pip install -e ".[dev,plots]"
python -m nanoporous.cli simulate --seed 17 --out outputs/example.json
python experiments/plot_results.py outputs/example.json --out outputs/example.png
```

The JSON saves model, geometry, MSD, standard error, selected full unwrapped
paths, slope estimate, trajectory-level bootstrap bounds and acceptance rate.
The PNG labels all data as simulated, with an *analytic* free-particle curve.

## Numerical convergence

```bash
python experiments/convergence.py --out outputs/convergence.json
```

This writes one simulation per step size. A scientific convergence figure
requires repeats and a statistical comparison across geometry seeds. This
diagnostic should not be reported as a completed verification study by itself.

## Coarse inverse design

```bash
python -m nanoporous.cli design --target 0.7 --out outputs/design.json
```

The target is a dimensionless ratio D_eff/D_free. Discrete obstacle counts
approximate candidate solid area fractions and candidate ranking contains
random sampling error, not measured material quality.

## Reproducibility requirements

When adding a real experimental figure, record sample IDs, provenance, units,
experimental acquisition conditions and data split. Do not mix measured and
synthetic data within a legend or train on points from the evaluation sample.
