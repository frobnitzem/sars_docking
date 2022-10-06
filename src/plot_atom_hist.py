#!/usr/bin/env python3
# plot 2D histograms of molecular properties (present in *.nc files)

import pylab as plt
import xarray as xr
import numpy as np
from pathlib import Path

# autodock cutoff, copied from src/dataset/sublists.py
cut = { 'MPro_5R84' : -13.220
      , 'MPro_6WQF' : -12.865
      , 'PLPro_7JIR': -15.261
      , 'NSP15_6WLC': -13.534
      , 'Spike_6M0J': -11.739
      , 'RDRP'      : -12.435
      }

def read_counts(name):
    return xr.open_dataset(name)['count']

# Note: we "guess" which direction the xy box goes because
# negative scores want to be as neg as possible and pos. want
# to be as pos. as possible.
def guess_sl(z):
    if z < 0:
        return slice(None,z)
    else:
        return slice(z,None)

def plot(H, x0, y0, loc=None):
    dim0, dim1 = H.dims
    fig, ax = plt.subplots(figsize=(4.5,3.5))
    #np.log(H+0.5).plot(ax=ax)
    xr.plot.imshow(np.log(H+0.5), ax=ax, zorder=-1)

    if x0 is not None:
        plt.axhline(x0, color='black', linewidth=1, zorder=1)
    if y0 is not None:
        plt.axvline(y0, color='black', linewidth=1, zorder=1)

    plt.tight_layout()
    if loc:
        plt.savefig(loc / f'{dim0}-{dim1}.pdf')

def main(argv):
    assert len(argv) == 2, f"Usage: {sys.argv[0]} <dir>"
    loc = Path(argv[1])
    assert loc.is_dir()

    cutoff = cut[loc.parent.name]

    H = read_counts(loc / "atoms_score.nc")
    plot(H, None, cutoff, loc)
    plt.clf()

    H = read_counts(loc / "atoms_tors.nc").sel(tors=slice(None, 20))
    plot(H, None, None, loc)
    plt.clf()

    H = read_counts(loc / "tors_score.nc").sel(tors=slice(None, 20))
    plot(H, None, cutoff, loc)
    plt.clf()

    return 0

if __name__=="__main__":
    import sys
    exit( main(sys.argv) )
