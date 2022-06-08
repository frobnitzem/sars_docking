#!/usr/bin/env python3
# Create sub-lists of the dataset based on selection criteria.

from helpers import *
from mpi_list import *

from hashlib import blake2b

# create a 10-byte hex digest and interpret
# as a number modulo 2^31 - 1
def digest(name):
    P = (1<<31) - 1
    h = blake2b(digest_size=10)
    h.update(name.encode('utf-8'))
    dig = h.digest()
    v = dig[0]
    for i in dig[1:]:
        v = ( (v<<8) + i ) % P
    return v

# Number actually selected follows Poisson distribution
def rand_10k(name, cut = (((1<<31) - 1)*10300. / 1.3e9)):
    return digest(name) < cut

# protein  AD       rf3
#MPro_5R84 -13.2207 8.0323
#MPro_6WQF -12.8656 7.9543
#PLPro_7JIR -15.2611 8.1760
#NSP15_6WLC -13.5347 7.9845
#Spike_6M0J -11.7395 7.9704
#RDRP -12.4353 8.0216
def mk_lists(prot):
    cut = {          #      AD,   rf3,      ADrf3,           v2rf3,            v2AD
        'MPro_5R84' : [-13.220, 8.032, (-11.786, 7.768), (6.714, 7.874), (6.460, -11.668)]
      , 'MPro_6WQF' : [-12.865, 7.954, (-11.474, 7.722), (6.618, 7.825), (6.369, -11.332)]
      , 'PLPro_7JIR': [-15.261, 8.176, (-14.062, 7.961), (6.349, 7.800), (6.359, -13.327)]
      , 'NSP15_6WLC': [-13.534, 7.984, (-11.551, 7.597), (6.194, 7.701), (6.161, -11.663)]
      , 'Spike_6M0J': [-11.739, 7.970, (-10.078, 7.459), (6.106, 7.352), (6.148, -10.330)]
      , 'RDRP'      : [-12.435, 8.021, (-11.032, 7.722), (6.329, 7.722), (6.304, -10.813)]
        }[prot]

    rand =  lambda df: df.index.map(rand_10k)
    lists = { 'AD'   : lambda df: df['score']  < cut[0]
            , 'rf3'  : lambda df: df['r3']     > cut[1]
            , 'ADrf3': lambda df: (df['score'] < cut[2][0]) & (df['r3'] > cut[2][1])
            , 'v2rf3': lambda df: (df['v2'] > cut[3][0]) & (df['r3']    > cut[3][1])
            , 'v2AD' : lambda df: (df['v2'] > cut[4][0]) & (df['score'] < cut[4][1])
            , 'rand' : rand
            }
    return lists

data = Path("/gpfs/alpine/world-shared/stf006/rogersdd/docking")

def main(argv):
    assert len(argv) == 3, f"Usage: {argv[0]} <prot> <N>"
    prot = argv[1]
    lsts = mk_lists(prot)

    N = int(argv[2])
    C = Context()

    out = Path(prot)
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

    for name,sel in lsts.items():
        t2 = time()
        ret = dfm . map(lambda df: df[sel(df)]) \
                  . nodeMap(lambda rank,E: [concatDF(E)]) \
                  . collect()
        t3 = time()
        if C.rank == 0:
            ans = pd.concat(ret)
            print(f"Collected {len(ans)} records in {name} in {t3-t2} secs.")
            ans.to_parquet(out / f"{name}.pq")

if __name__=="__main__":
    import sys
    main(sys.argv)
