#!/usr/bin/env python3
# Summarize a scoring dataset: counts, averages, histograms

import xarray as xr

from helpers import *
from mpi_list import *

data = Path("/gpfs/alpine/world-shared/stf006/rogersdd/docking")

def stat(u):
    #keep = ['score', 'score2', 'score3', 'vs_dude_v2', 'rf3', 'vs_dude_v22', 'rf32', 'vs_dude_v23', 'rf33', 'v2', 'r3']
    #u = df.loc[:,keep]
    #u = df[keep]
    return pd.DataFrame([u.count(), u.min(), u.max(), u.sum()], \
                        index=['count','min','max','sum'])


def final(ans):
    lo = ans.loc['min'].min()
    hi = ans.loc['max'].max()

    tot = ans.loc['count'].sum()
    asum = ans.loc['sum'].sum() / tot
    return pd.DataFrame( [tot, lo, hi, asum],
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
    C = Context()
    out  = Path(prot)
    assert data.is_dir(), f"Input path '{data}' does not exist!"
    if C.rank == 0:
        out.mkdir(parents=True, exist_ok=True)

    t0 = time()
    dfm = C . iterates(N) \
            . flatMap( lambda n: read_scored(data, prot, n) ) \
            . map( best_scores )

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
        ans.to_parquet(out / "summary_i.pq")
        df = final(ans)
        print(df)
        df.to_parquet(out / "summary.pq")

        #lo = df.loc['min'].min()
        #hi = df.loc['max'].max()
        lo = df.loc['min']
        hi = df.loc['max']

    # broadcast histogram parameters
    lo,hi = C.comm.bcast((lo,hi), root=0)
    H = Hist(lo, hi, 301, 201)

    def npsum(a,b):
        a += b
        return a

    t2 = time()
    ret = dfm . map( lambda df: H.his2d(df, 'score', 'r3') ) \
              . reduce( npsum, 0 )
    t3 = time()
    if C.rank == 0:
        print(f"Collected histogram1 in {t3-t2} secs.")
        ret.to_netcdf(str(out / "score_rf3.nc"))

    t2 = time()
    ret = dfm . map( lambda df: H.his2d(df, 'v2', 'r3') ) \
              . reduce( npsum, 0 )
    t3 = time()
    if C.rank == 0:
        print(f"Collected histogram2 in {t3-t2} secs.")
        ret.to_netcdf(str(out / "dude_rf3.nc"))

    t2 = time()
    ret = dfm . map( lambda df: H.his2d(df, 'v2', 'score') ) \
              . reduce( npsum, 0 )
    t3 = time()
    if C.rank == 0:
        print(f"Collected histogram3 in {t3-t2} secs.")
        ret.to_netcdf(str(out / "dude_score.nc"))

if __name__=="__main__":
    import sys
    main(sys.argv)
