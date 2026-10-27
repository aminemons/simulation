# Experimental data sources and provenance

No external experimental measurements are vendored into this repository.
The default examples generate **synthetic model output** only.

## Source A — published 2024 study

M. Lorenzo Lopez, V. R. Kearns, J. M. Curran and E. A. Patterson,
"Diffusion of nanoparticles in heterogeneous hydrogels as vitreous humour
in vitro substitutes", *Scientific Reports* 14, 17441 (2024).
DOI: https://doi.org/10.1038/s41598-024-68267-0

Experiment: tracked Au nanoparticle motion across agar–hyaluronic acid
hydrogel conditions. Paper includes 2D nanoparticle-track MSD methodology
and heterogeneity observations. Data availability points to University of
Liverpool DataCat record 2603. Consult the original article for exact
experimental parameters and data permissions.

Dataset reference: https://datacat.liverpool.ac.uk/2603/

## Source B — 2025 University of Liverpool data collection

M. Lorenzo Lopez et al. (2025), "Nanoparticles motion in simple fluids and
hydrogels; alongside the bulk rheological characterisation of the
corresponding media." Liverpool DataCat, 2899.

DOI: https://doi.org/10.17638/datacat.liverpool.ac.uk/2899
URL: https://datacat.liverpool.ac.uk/2899/

Described content: optical microscopy videos of 100-nm gold nanoparticle
nanoprobes in simple fluids, heterogeneous agar–hyaluronic acid hydrogels
and thermosensitive Pluronic F127, plus Excel bulk rheology measurements.
Check terms on the dataset landing page and individual file before reuse.

## Required import record

Each experimental import must record:
- Stable DOI/URL, publication date, license and data-file checksum.
- Material formulation, temperature, particle size, charge and localization.
- Camera frame rate, spatial calibration, tracking and filtering rules.
- Which files are calibration/training and which are evaluation by sample.
- Scripts and configuration reproducing the reported plots.

**Do not present synthetic trajectories as measured nanoparticle data.**
Physical length and time units can only be attached after documented
calibration. The current simulator's arbitrary default units are not
automatically equivalent to nm, µm, seconds, or physiological parameters.
