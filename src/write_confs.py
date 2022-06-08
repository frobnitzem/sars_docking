#!/usr/bin/env python3

import pandas as pd
from pathlib import Path

def read_pd(fname):
    if fname[-3:] == "csv":
        return pd.read_csv(fname)
    return pd.read_parquet(fname)

def main(argv):
    assert len(argv) == 3, f"Usage: {argv[0]} <in.csv/pq> <out dir>"
    ligs = read_pd(argv[1])
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)

    for name, row in ligs.iterrows():
        for i,x in enumerate(["conf", "conf2", "conf3"]):
          conf = row[x]
          with open(out / f"{name}.{i+1}.pdbqt", 'w', encoding='utf-8') as f:
            f.write(conf)

if __name__=="__main__":
    import sys
    main(sys.argv)
