# Contributor workflow

NanoPorous welcomes contributions in computational physics, microscopy
analysis, numerical methods and reproducible research.

## Run checks

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check src tests
```

Before merging scientific changes, include:
1. Governing assumptions and measurement units.
2. Deterministic seed and a saved, inexpensive reference case.
3. Regression/analytic tests and numerical tolerance rationale.
4. Source DOI and data license for all measured quantities.
5. A failure case or limitation documented in the PR.
6. Honest plots with fully identified axes and measurement provenance.

## Scientific integrity

Do not fabricate data, claim a simulation was validated experimentally,
rewrite timestamps to imitate a long project history, or use another person's
Git author identity. Commit real milestones when work is completed.
Both collaborators should author their own changes.

## Pull request title examples

- `physics: compare endpoint rejection against reflected-step integrator`
- `data: import licensed particle-tracking coordinates with provenance`
- `validation: add timestep convergence study with confidence intervals`
- `docs: explain measured and simulated lag-MSD definitions`
