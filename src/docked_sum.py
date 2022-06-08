#!/usr/bin/env python3
# Print out info from summary.pq files.

import pandas as pd
import sys

x = pd.read_parquet(sys.argv[1])
print(x.loc['count']['score'])
print("| attr | min | max | avg |")
print("| ---- | --- | --- | --- |")
for col in x.columns:
    a = int(x.loc['min'][col]*1000)/1000
    b = int(x.loc['max'][col]*1000)/1000
    c = int(x.loc['avg'][col]*1000)/1000
    print(f"| {col} | {a} | {b} | {c} |")
