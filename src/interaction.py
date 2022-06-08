#!/usr/bin/env python3

from pathlib import Path
import interactions_oddt
import oddt

# example list:
# TODO: iterate with categorization to include all important atoms
site_list = [
        ("Cys145", "CG",   "hbond",    "S1"),
        ("Cys145", "CG",   "hphob",    "S1"),
        ("His41",  "NE1",  "donor",    "S1"),
        ("His41",  "ND1",  "acceptor", "S1"),
        ("His41",  "NH",   "acceptor", "S1"),
        ("Tyr54",  "",     "hphob",    "S2"),
     ]

# Create a lookup table from atom numbers to interactions.
# Note: This only lets an atom be associated to 1 interaction type
#       right now.  The code needs revision to support more than
#       one role per atom.
#
# lookup_atom = {
#        342: 0, # site list number 0
#        400: 1, # site list number 1
#        }
def lookup_sites(pdb):
    fp = open(pdb, 'r', encoding='utf8')
    lookup_atom = {}
    for line in fp:
        tok = line.split()
        if tok[0] == "ATOM": # FIXME: parse names correctly
            # FIXME: search through site_list and set index
            # correctly [ 0 <= site_number < len(site_list) ]
            lookup_atom[i] = site_number
    fp.close()

    return lookup_atom

# returns count of atoms interacting with site_list
# as a vector of length (site_list)
def interact(protein, lig, lookup_atom):
    lig = Path(lig)
    list_atoms = []
    ligand = next(oddt.toolkit.readfile(lig.suffix[1:], lig))
    ans = [0] * len(site_list)
    leftovers = [] # list of interacting atoms that were not on the site_list

    # FIXME: fill out list of interaction names and functions here:
    for name, fn in zip([("hbond", interactions_oddt.hbonds),
                         ("hphob", interactions_oddt.nonpolar),
                         ("saltbr", interactions_oddt.saltbridge),
                        ]):
        protein_atoms, ligand_atoms, strict = fn(protein, ligand)
        for i in protein_atoms:
            try:
                interaction_number = lookup_atom[i]
                # check whether this is the right interaction
                if site_list[interaction_number][2] != name:
                    leftovers.append( (name, i) )
                else:
                    ans[interaction_number] += 1
            except KeyError:
                leftovers.append( (name, i) )

    return ans, leftovers

# Example matrix output
#
# Z1 [ 1,    0, 1, 1] <- S1 and S2
# Z2 [ 1,    0, 0, 0] <- just S1
# Z3 [ 0,    1, 1, 0]
#    ---------------- Summary:
#     |S1|  | S2   |
#
def main(argv):
    assert len(argv) > 3, "Usage: %s <protein.pdb> <lig1> ..."%argv[0]

    lookup_atoms = lookup_sites(argv[1])
    protein = next(oddt.toolkit.readfile('pdb', argv[1]))

    ligands = argv[2:]
    for lig in ligands:
        ans, leftovers = interact(protein, lig, lookup_atoms)
        print(lig + " " + " ".join("%d"%a for a in ans)

if __name__=="__main__":
    import sys
    main(sys.argv)

