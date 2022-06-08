# SARS Cov2 Docking Summary Data



This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).

![https://creativecommons.org/licenses/by-sa/4.0/](https://licensebuttons.net/l/by-sa/4.0/88x31.png)


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

## Cite this work as:

SARS Cov2 Docking Summary Data, "https://code.ornl.gov/99R/sars\_docking" Oak Ridge National Laboratory, 2020-2022.
