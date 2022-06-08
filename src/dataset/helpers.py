# accessory functions for data analysis
import numpy as np
import pandas as pd
from pathlib import Path
from time import time

from lazydf import LazyDataFrame

def n_scored(prot):
    scored = dict(
       MPro_5R84=2592,
       MPro_6WQF=2592,
       Spike_6M0J=2592,
       NSP15_6WLC=2640,
       PLPro_7JIR=2049,
       RDRP=2048)
    return scored[prot]

def n_docked(prot):
    docked = dict(
       MPro_5R84=2592,
       MPro_6WQF=2592,
       Spike_6M0J=2592,
       NSP15_6WLC=2640,
       PLPro_7JIR=8194,
       RDRP=8193)
    return docked[prot]

def read_pq(name):
    try:
        df = [pd.read_parquet(name)]
        #df = [LazyDataFrame(name)]
    except Exception as e:
        print(f"Error reading {name}: {e}")
        df = []
    return df

def read_docked(data, prot, n):
    name = data / prot / 'docked' / f"{n}.pq"
    return read_pq(name)

def read_scored(data, prot, n):
    name = data / prot / 'scored' / f"{n}.pq"
    return read_pq(name)

def best_scores(df):
    df['v2'] = df[['vs_dude_v2','vs_dude_v22','vs_dude_v23']].max(axis=1)
    df['r3'] = df[['rf3','rf32','rf33']].max(axis=1)
    return df

def concatDF(dfs):
    if len(dfs) == 0:
        return pd.DataFrame()
    else:
        return pd.concat(dfs)

