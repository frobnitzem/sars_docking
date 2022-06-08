#!/usr/bin/env python3
# Create MACCS fingerprints for molecules in a pq file.

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import MACCSkeys

FP_SIZE = 167

import oddt.toolkits.rdk as R

def fingerprint(mol): return MACCSkeys.GenMACCSKeys(mol)
def compute_fingerprints(mol_set): return [fingerprint(m) for m in mol_set]
def fps_to_numpy(fps):
    fps_numpy = np.empty([len(fps),FP_SIZE], dtype=np.uint8)
    fp_buf    = np.empty((FP_SIZE),          dtype=np.uint8)
    for i in range(len(fps)):
        DataStructs.ConvertToNumpyArray(fps[i],fp_buf)
        fps_numpy[i] = fp_buf
    return fps_numpy

Falso = False
def gen_mols(col):
    for m in col:
        #yield Chem.rdmolfiles.MolFromPDBBlock(m)
        yield R.MolFromPDBQTBlock(m,
                    sanitize=Falso,
                    removeHs=Falso)

def main(argv):
    assert len(argv) == 3, f"Usage: {argv[0]} <input.pq> <output.npy>"
    #mol_set = Chem.SDMolSupplier('./Enamine_Discovery_Diversity_Set_plated_10560cmpds_20200524.sdf')
    #num_mols = len(mol_set)
    ligs = pd.read_parquet(argv[1])
    mol_set = gen_mols(ligs['conf'])

    mol_fps = compute_fingerprints(mol_set)
    mol_fps_numpy = fps_to_numpy(mol_fps)

    mol_fps_bits = np.packbits(mol_fps_numpy.astype(np.uint8), axis=1)
    np.save(argv[2], mol_fps_bits)

if __name__=="__main__":
    import sys
    main(sys.argv)
