#!/usr/bin/env python3
# First attempt - gather data directly from docking (no re-scoring)

from helpers import *
from mpi_list import *

data = Path("/gpfs/alpine/world-shared/stf006/rogersdd/docking")
def concatDF(dfs):
    if len(dfs) == 0:
        return pd.DataFrame()
    else:
        return pd.concat(dfs)

# sample k from a dfm of size n
def rand_sample(dfm, n, k, seed=12):
    rng = np.random.default_rng(seed)
    rsamples = rng.choice(n,10000,replace=False,shuffle=False) # random sample list
    rsamples.sort()

    start = dfm.map(len).scan(lambda a,b: a+b)

    def get_ans(rank, E):
        ans = []
        for j,df in zip(start.E, E):
            i = j - len(df)

            ind = rsamples[ (rsamples >= i) * (rsamples < j) ]
            if len(ind) > 0:
                ans.append( df.iloc[ind - i] )
        return ans

    # with rand() < pct ~ Poisson(10100.0)
    #pct = 10100.0 / n
    # map(lambda df: df[np.random.random(len(df)) < pct]) \
    return dfm . nodeMap(get_ans)

def main(argv):
    N = int(argv[1])
    cut = float(argv[2])
    prot = argv[3]
    C = Context()
    if C.rank == 0:
        Path(prot).mkdir(parents=True, exist_ok=True)

    t0 = time()
    dfm = C . iterates(N) \
            . flatMap(lambda n: read_docked(data, prot, n))
    N = dfm.map(len).reduce(lambda a,b: a+b, 0)

    t1 = time()
    if C.rank == 0:
        print(f"Read {N} molecules in {t1-t0} secs.")

    top = dfm \
            . map(lambda df: df[df['score'] < cut]) \
            . nodeMap(lambda rank,E: [concatDF(E)]) \
            . collect()
    t2 = time()
    if C.rank == 0:
        ans = concatDF(top)
        n = len(ans)
        print(f"Filtered {n} top scoring in {t2-t1} secs.")
        ans.to_parquet(f"{prot}/top_AD.pq")

    t3 = time()
    ret = rand_sample(dfm, N, 10000).collect()
    t4 = time()
    if C.rank == 0:
        ans = concatDF(ret)
        n = len(ans)
        print(f"Collected {n} randoms in {t4-t3} secs.")
        ans.to_parquet(f"{prot}/random.pq")

if __name__=="__main__":
    import sys
    main(sys.argv)
