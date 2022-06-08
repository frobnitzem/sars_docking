#!/usr/bin/env python3
# Plot 2D histograms of docking scores (present in *.nc files)
# Also determines cutoff scores by searching the cumulative
# distribution for the given count (percentile).

import pylab as plt
import xarray as xr
import numpy as np
from pathlib import Path

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

def plot(H, x0, y0, xy, loc=None):
    dim0, dim1 = H.dims
    fig, ax = plt.subplots(figsize=(4.5,3.5))
    np.log(H+0.5).plot(ax=ax)
    #print(x0,y0,xy)

    if x0 is not None:
        plt.axhline(x0, color='black', linewidth=1)
    if y0 is not None:
        plt.axvline(y0, color='black', linewidth=1)

    if xy is not None:
        ar = H*np.nan
        xs = guess_sl(xy[0])
        ys = guess_sl(xy[1])
        ar.loc[xs,ys] = 0.3
        ar.plot(ax=ax, alpha=0.2, cmap="bone", vmin=0.0, vmax=1.0, add_colorbar=False)
        #ax.imshow(ar, alpha=0.5, cmap="RdBu")

    #plt.axhline(xy[0], color='black', linewidth=1)
    #plt.axvline(xy[1], color='black', linewidth=1)
    if loc:
        plt.savefig(loc / f'{dim0}-{dim1}.pdf')
    #plt.show()

def min_cut(H, dim0, N, reverse=False):
    # return the smallest x such that sum_{y < x} u(y) >= N
    for dim in H.dims:
        if dim == dim0:
            continue
        H = H.sum(dim)

    crd = H.coords[dim0].values
    if (crd[1] < crd[0]) ^ reverse:
        H = np.flip(H)
        crd = H.coords[dim0].values

    u = H.cumsum()
    d = np.where(u >= N)[0][0]
    #if reverse:
    #    d = len(H)-1 - d

    #print(d)
    #print( crd[:d] )
    #print( u.values[:d+1] )
    x0 = 0.5*(crd[d] + crd[d+1])
    return x0

def min_cut2(H, rev0, rev1, N):
    dim0, dim1 = H.dims
    print(H.dims)
    if (H.coords[dim0][1] < H.coords[dim0][0]) ^ rev0:
        H = H[::-1]
    if (H.coords[dim1][1] < H.coords[dim1][0]) ^ rev1:
        H = H[:, ::-1]
    x = H.coords[dim0].values
    y = H.coords[dim1].values

    cdf0 = H.sum(dim1).cumsum().values
    cdf1 = H.sum(dim0).cumsum().values
    K = H.sum().values # total number

    j = 0
    for i,n in enumerate(cdf0):
        while cdf1[j] < n:
            j += 1
        M = H[:i+1,:j+1].sum().values
        if M >= N:
            break

    print(cdf0[i]/K, cdf1[j]/K, M)

    return 0.5*(x[i]+x[i+1]), 0.5*(y[j]+y[j+1])

def flip(ab):
    return ab[1], ab[0]

def main(argv):
    assert len(argv) == 2, f"Usage: {sys.argv[0]} <dir>"
    N = 10000
    loc = Path(argv[1])
    assert loc.is_dir()

    H = read_counts(loc / "score_rf3.nc")
    d1 = min_cut( H, 'score', N )
    d2 = min_cut( H, 'r3', N, True )

    d3 = min_cut2( H, False, True, N )
    plot(H, d1, d2, d3, loc)
    plt.clf()

    H = read_counts(loc / "dude_rf3.nc")
    d4 = min_cut2( H, True, True, N )
    plot(H, None, d2, d4, loc)
    plt.clf()

    H = read_counts(loc / "dude_score.nc")
    d5 = min_cut2( H, True, False, N )
    plot(H, None, d1, d5, loc)
    plt.clf()

    print([d1, d2, d3, d4, d5])
    return 0

if __name__=="__main__":
    import sys
    exit( main(sys.argv) )
