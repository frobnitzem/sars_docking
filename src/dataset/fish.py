#!/usr/bin/env python3
# fish out this list of cpds
# note, error in:
#  /gpfs/alpine/world-shared/stf006/rogersdd/docking/RDRP/docked/1907.pq
#
# To reduce the size of this computation, we could
#  1. load only a few columns from each dataframe, then re-read dataframes we
#     care about: pd.read_parquet("timeseries_wide.parquet", columns=columns)
#  2. replace the dataframe with a "lazy" dataframe
#     that reads the data from source each time it is queried

from helpers import *
from mpi_list import *

data = Path("/gpfs/alpine/world-shared/stf006/rogersdd/docking")

def fish(df):
    cpds = [f"{x}_" for x in """Z1095050454
        Z645864910
        Z796033100
        Z770086746
        Z604406248
        Z816756928
        Z1075411466
        Z996950516
        Z1038017018""".split()]

    E = []
    if 'name' in df.columns:
        df.set_index('name', inplace=True)
    for name in cpds:
        ans = df.loc[df.index.str.startswith(name)]
        if len(ans) > 0:
            E.append(ans)

    return concatDF(E)

def main(argv):
    assert len(argv) == 3, f"Usage: {argv[0]} <N> <prot>"
    N = int(argv[1])
    prot = Path(argv[2])

    C = Context()
    if C.rank == 0:
        prot.mkdir(parents=True, exist_ok=True)

    t0 = time()
    dfm = C . iterates(N) \
            . flatMap(lambda n: read_docked(data, prot, n))

    N = dfm.map(len).reduce(lambda a,b: a+b, 0)

    t1 = time()
    if C.rank == 0:
        print(f"Read {N} molecules in {t1-t0} secs.")

    for out in ["expt_hits"]:
        t1 = time()

        # exact match
        #    . map(lambda df: df.loc[df.index.intersection(cpds)]) \
        ans = dfm \
                . map(lambda ldf: ldf(fish)) \
                . nodeMap(lambda rank,E: [concatDF(E)]) \
                . collect()
        t2 = time()
        if C.rank == 0:
            ans = concatDF(ans)
            n = len(ans)
            print(f"Filtered {n} molecules from {out} in {t2-t1} secs.")
            ans.to_parquet((prot / out).with_suffix(".out.pq"))

if __name__=="__main__":
    import sys
    main(sys.argv)
