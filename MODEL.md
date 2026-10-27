# Scientific model and numerical assumptions

**Status: computational model, no experimental validation.**

## Microscopic model (implemented)

The 2D overdamped stochastic differential equation in free space is

```text
dX_t = sqrt(2 D_free) dW_t
```

where independent Wiener components produce the exact free-space identity
`MSD(t) = 4 D_free t`. Coordinates are dimensionless unless a physical
unit system is explicitly specified.

Random-sequential-adsorption disks represent **idealized impermeable obstacles**
in a periodically repeated square. Probe centers are forbidden to enter disks
enlarged by the probe's steric radius. Obstacles are static and nonreactive.
Initial probe centers are uniformly sampled from accessible space.

At each Euler timestep:

1. Draw a Gaussian 2D increment of variance `2 D_free dt` per axis.
2. Wrap the proposed endpoint to the periodic cell.
3. Reject increments ending inside any forbidden disk.
4. Otherwise accept and add the increment to an *unwrapped* position history.

This endpoint rejection is a numerical approximation to reflecting Brownian
motion. **Segments can pass through an obstacle without the endpoint being
inside it**. The bias becomes important when steps are large relative to disk
size or narrow pore widths. Numerical timestep-convergence is necessary; the
current implementation is not a rigorous first-passage or boundary-reflection
solver.

### What we estimate

Ensemble squared displacement from a fixed starting position:

```text
MSD(t) = (1/N) sum_i |X_i(t) - X_i(0)|²
D_eff = (1/4) d(MSD)/dt
```

The slope is estimated over the middle 30–90% of *observed time*, using a
free intercept. Fitting-window sensitivity and the linear-diffusive regime
must be checked before accepting the effective diffusion coefficient.

We bootstrap entire independent particle tracks (not individual time points)
to estimate sampling uncertainty. This does not cover geometric sampling
variation, finite timestep bias, model error or measurement uncertainties.

## Continuum model (implemented, currently independent)

A 1D, spatially variable Fickian diffusivity field satisfies

```text
partial_t c = partial_x(D(x) partial_x c)
```

We use a periodic, conservative cell-centered finite-volume discretization.
Diffusivities at cell faces are harmonically averaged. Explicit forward Euler
updates satisfy a sufficient positive-coefficient stability limit

```text
dt <= dx² / (2 max_i D_face,i)
```

with nonnegative initial concentrations. The solver is benchmarked against
a Fourier-mode decay solution for uniform diffusivity.

## Inverse design (implemented as a baseline)

We vary **nominal disk area fraction**, generate multiple random independent
microstructures at each candidate fraction, simulate trajectories, fit
`D_eff / D_free`, and rank candidates by absolute distance from a target.
The rounded integer disk count produces slightly different realized fractions.

This is a *simulation-only grid search*. It is neither experimentally
calibrated nor a unique inversion. Different pore geometries can produce
similar long-time diffusion coefficients.

## Deliberate omissions and required future work

- No electrostatic interactions or reversible particle–gel binding yet.
- No full 3D fibrous/voxelized hydrogel geometry.
- No measured pore distribution or experimental microstructure import.
- No adaptive reflecting-boundary collision correction.
- No particle-to-continuum closure fitted or validated yet.
- No physically scaled time/length mapping to a specific experimental gel.
- No drug delivery, dose, or biomedical efficacy conclusions.

## Reproducibility

Store RNG seed, geometry, timestep, particle number, fit window, and analysis
script for every output. Never report a CI from resampling as proof that
systematic numerical and modeling uncertainties are small.
