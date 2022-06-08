#!/usr/bin/env python3

from helpers import *
from mpi_list import *

data = Path("/gpfs/alpine/world-shared/stf006/rogersdd/docking")

cols = ['atoms', 'tors', 'score', 'score2', 'score3', 'conf', 'conf2', 'conf3']

def main(argv):
    assert len(argv) >= 4, f"Usage: {argv[0]} <N> <prot> <list1> <...>"
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

    for out in argv[3:]:
        if not (prot/out).exists():
            if C.rank == 0:
                print(f"Missing {prot/out}")
            continue

        t1 = time()
        lst = pd.read_parquet(prot / out)
        # get rid of columns we already know
        lst.drop(cols, axis=1, inplace=True, errors='ignore')

        ans = dfm \
                . map(F.join(lst, how='inner')) \
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
