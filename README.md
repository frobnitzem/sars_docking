# SARS Cov2 Docking Summary Data

This work is based on the [SARS-CoV2 Docking Dataset](https://doi.ccs.ornl.gov/ui/doi/348), by David M. Rogers, Jens Glaser, Rupesh Agarwal, Josh Vermaas, Micholas Smith, Jerry Parks, Connor Cooper, Ada Sedova, Swen Boehm, Matthew Baker, and Jeremy Smith.
It is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

![https://creativecommons.org/licenses/by/4.0/](https://licensebuttons.net/l/by/4.0/88x31.png)

It includes the file `rossetti.csv`, which is a list of noncovalent inhibitors of SARS-CoV2 main protease disclosed in the reference:
Rossetti, G.G., Ossorio, M.A., Rempel, S. et al. Non-covalent SARS-CoV-2 Mpro inhibitors developed from in silico screen hits. Sci Rep 12, 2505 (2022). https://doi.org/10.1038/s41598-022-06306-4.

The content of that file is a concatenation of all Supplementary Information tables from the Rossetti article.  Four additional columns contain the IC50 listed in the Rossetti article's main text and Supplementary Figures, the IC50 unit (always uM for micro-molar here), a notes text-column, and a number from 1-8 indicating which of their supplementary tables the record originated from.

It has also been released by its authors under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).


## Layout

The top-level directory contains protein names, like `MPro\_6WQF`, as its
subdirectories.  It also contains common information, like `src`,
holding processing files.

### Per-Target Data

* docked - summary plots and raw array data for 2D histograms
  - atoms-tors.pdf, atoms\_tors.nc
  - atoms-score.pdf atoms\_score.nc
  - tors-score.pdf tors\_score.nc
  - score-r3.pdf score\_rf3.nc
  - v2-r3.pdf dude\_rf3.nc
  - v2-score.pdf dude\_score.nc
  - summary\_i.pq
  - summary.pq

* docked\_lists - short lists of compounds and scores
  - rand.out.pq	- random selection
  - AD.out.pq - sorted by AutoDock-GPU score
  - rf3.out.pq - sorted by RF3 score
  - v2AD.out.pq - sorted by both DUD-E v2 and RF3
  - ADrf3.out.pq - sorted by both AutoDock-GPU and RF3
  - v2rf3.out.pq - sorted by both DUD-E v2 and RF3

* target 
  - tgz files containing AutoDock data prepared for docking (e.g. `7jir+w2.tgz`)
  - extracted protein pdbqt used for docking (e.g. `7jir+w2.pdbqt`)

### Source Files

* src
  - write\_confs.py - extract pdbqt files from parquet files
  - docked\_sum.py - print count, min, max, avg summaries from `summary.pq` files
  - plot\_atom\_hist.py - create 2D plots containing atoms, torsions, etc.
  - plot\_score\_hist.py - create 2D plots containing scores
  - maccs.py - compute MACCS fingerprints for molecules within a parquet file
  - interaction.py - list neighboring protein/ligand atoms by chemical interaction

* dataset
  - requirements.txt - list of python package dependencies
  - helpers.py - utility functions for common tasks
  - lazydf.py - low-memory wrapper for parquet files
  - read\_sizes.py - utility program to display parquet file sizes
  - expt.sh, fish.py - batch script and source file for extracting compounds by name
  - list\_10k.py - initial script to gather molecules based on cutoff
  - lists.sh, sublists.py, lists.000 - Create sub-lists of the score dataset based on score selection.  These are used as input to get\_lists.py.
  - top.sh, top\_andes.sh, get\_lists.py, topN.000 - batch script, source file, and example job output for extracting compounds by full name (including \_T\_0 suffix).
  - summary.sh, summary.py, summary.52533 - batch script, source file, and example output for creating bounds and summary histograms for dataset
  - atoms\_tors.sh, atoms\_tors.py, atoms\_tors.000 - batch script, source file, and example output for creating histograms of atoms and torsions

* dash - a (plotly/dash)[https://dash.plotly.com] viewer for docked structures and scores


## Cite this work as:

SARS Cov2 Docking Summary Data, "https://github.com/frobnitzem/sars\_docking" Oak Ridge National Laboratory / CC-BY-4.0, 2020-2022.

or

Rogers, Agarwal, Agarwal, et. al., "SARS-CoV2 Billion-Compound Docking." Scientific Data, 2022.
