#!/usr/bin/env python3
# Summarize a scoring dataset: counts, averages, histograms

import pandas as pd

def get_tors(x : str) -> int:
    if not isinstance(x, str):
        return 0
    return x.count('\nBRANCH')

def get_atoms(x : str) -> int:
    if not isinstance(x, str):
        return 0
    return x.count('\nATOM')

def add_info(df):
    if 'atoms' not in df.columns:
        df['atoms'] = df['conf'].map(get_atoms)
    if 'tors' not in df.columns:
        df['tors'] = df['conf'].map(get_tors)

import xarray as xr

from helpers import *
from mpi_list import *

data = Path("/gpfs/alpine/world-shared/stf006/rogersdd/docking")

def format(df):
    add_info(df)
    keep = ['score', 'atoms', 'tors']
    return df[keep]

def stat(u):
    return pd.DataFrame([u.count(), u.min(), u.max(), u.sum()], \
                        columns=u.columns,
                        index=['count','min','max','sum'])


def final(ans):
    lo = ans.loc['min'].min()
    hi = ans.loc['max'].max()

    tot = ans.loc['count'].sum()
    asum = ans.loc['sum'].sum() / tot
    return pd.DataFrame( [tot, lo, hi, asum],
                         columns=ans.columns,
                         index=['count','min','max','avg'] )

class Hist:
    def __init__(self, low, hi, Nx=201, Ny=201):
        self.low = low
        self.hi = hi
        self.Nx = Nx
        self.Ny = Ny

    def domain(self, a): # input histogram domain
        return self.low[a], self.hi[a]

    def his(self, df, a, b):
        xlim = self.domain(a)
        H, xs = np.histogram(df[a].values, bins=self.Nx, range=xlim)
        dx = xs[1]-xs[0]
        xs += 0.5*dx
        return xr.DataArray(H, coords=[xs[:-1]], dims=[a],
                            name='count')

    def his2d(self, df, a, b):
        xlim = self.domain(a)
        ylim = self.domain(b)
        H, xs, ys = np.histogram2d(df[a].values, df[b].values,
                        bins=[self.Nx,self.Ny], range=[xlim,ylim])
        dx = xs[1]-xs[0]
        xs += 0.5*dx
        dy = ys[1]-ys[0]
        ys += 0.5*dy
        return xr.DataArray(H, coords=[xs[:-1], ys[:-1]], dims=[a,b],
                            name='count')

def main(argv):
    assert len(argv) == 3, f"Usage: {argv[0]} <prot> <N>"
    prot = argv[1]
    N = int(argv[2])
    if N == 0:
        N = n_docked(prot)
    C = Context()
    out  = Path(prot)
    assert data.is_dir(), f"Input path '{data}' does not exist!"
    if C.rank == 0:
        out.mkdir(parents=True, exist_ok=True)

    t0 = time()
    dfm = C . iterates(N) \
            . flatMap( lambda n: read_docked(data, prot, n) ) \
            . map( lambda ldf: ldf(format) )

    t1 = time()
    n = dfm.len()
    if C.rank == 0:
        print(f"Read {n} pq files to {C.procs} processes in {t1-t0} secs.")

    t2 = time()
    ret = dfm . map(stat) . collect()
    t3 = time()
    if C.rank == 0:
        print(f"Collected stats to rank 0 in {t3-t2} secs.")

    lo = None
    hi = None
    # list of pd stats
    if C.rank == 0:
        ans = pd.concat(ret)
        ans.to_parquet(out / "atoms_i.pq")
        df = final(ans)
        print(df)
        df.to_parquet(out / "atoms.pq")

        #lo = df.loc['min'].min()
        #hi = df.loc['max'].max()
        lo = df.loc['min']
        hi = df.loc['max']

    # broadcast histogram parameters
    lo,hi = C.comm.bcast((lo,hi), root=0)
    atoms_bins = int(hi['atoms']-lo['atoms'])+1
    tors_bins = int(hi['tors']-lo['tors'])+1
    H = Hist(lo, hi, atoms_bins, tors_bins)

    def npsum(a,b):
        a += b
        return a

    t2 = time()
    ret = dfm . map( lambda df: H.his2d(df, 'atoms', 'tors') ) \
              . reduce( npsum, 0 )
    t3 = time()
    if C.rank == 0:
        print(f"Collected histogram1 in {t3-t2} secs.")
        ret.to_netcdf(str(out / "atoms_tors.nc"))

    H = Hist(lo, hi, atoms_bins, 201)
    t2 = time()
    ret = dfm . map( lambda df: H.his2d(df, 'atoms', 'score') ) \
              . reduce( npsum, 0 )
    t3 = time()
    if C.rank == 0:
        print(f"Collected histogram2 in {t3-t2} secs.")
        ret.to_netcdf(str(out / "atoms_score.nc"))

    H = Hist(lo, hi, tors_bins, 201)
    t2 = time()
    ret = dfm . map( lambda df: H.his2d(df, 'tors', 'score') ) \
              . reduce( npsum, 0 )
    t3 = time()
    if C.rank == 0:
        print(f"Collected histogram3 in {t3-t2} secs.")
        ret.to_netcdf(str(out / "tors_score.nc"))

if __name__=="__main__":
    import sys
    main(sys.argv)
