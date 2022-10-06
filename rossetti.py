#!/usr/bin/env python3

import pandas as pd

def read_lists():
    r = pd.read_parquet('MPro_5R84/docked_lists/rossetti.pq')
    q = pd.read_parquet('MPro_6WQF/docked_lists/rossetti.pq')
    df = pd.read_csv('rossetti2022.csv')

    r['Compound ID'] = [name.split('_',1)[0] for name in r.index]
    q['Compound ID'] = [name.split('_',1)[0] for name in q.index]

    # All compound IDs from Rossetti
    cpds = set(df['Compound ID'])
    # Hits from Rossetti (scores reported)
    hit = df.iloc[df['IC50'].dropna().index]
    hits = set(hit['Compound ID']) # subset of cpds

    nonspecific = hit.loc[ hit['note'] == 'nonspecific' ]
    nonspecs = set(nonspecific['Compound ID']) # subset of hits

    # select hits from r
    # r[r['Compound ID'].isin(hits)]

    # rc = set(r['Compound ID'])
    # qc = set(q['Compound ID'])
    # >>> len(rc & qc)
    # 653
    # >>> len(cpds & qc)
    # 785
    # >>> len(cpds & rc)
    # 660
    # >>> (qc|rc)-cpds
    # {'Z109826012', 'Z230477622', 'Z997964142', 'Z32868741', 'Z414969712', 'Z31294074', 'Z126246430'}

    # Create a color column.
    # 3 = nonspecific binder
    # 2 = hit
    # 1 = compound in Rossetti list
    # 0 = not in Rossetti list
    r['color'] = r['Compound ID'].isin(hits).astype(int) \
               + r['Compound ID'].isin(cpds).astype(int) \
               + r['Compound ID'].isin(nonspecs).astype(int)
    q['color'] = q['Compound ID'].isin(hits).astype(int) \
               + q['Compound ID'].isin(cpds).astype(int) \
               + q['Compound ID'].isin(nonspecs).astype(int)
    return r, q

if __name__=="__main__":
    import sys
    
    r, q = read_lists()
    print(q.groupby('color').count())
