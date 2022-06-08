RNA-dependent RNA polymerase model based on 6YYT

10/8/20: After a false start, and Jerry - `S_0341_mod_renum.pdb`
  1. aligned structure from Connor and Jerry

  - Model includes both Zn2+ and Mg2+
  - aligned the active site residues with a Hep C crystal structure (PDB ID: 4WTD)
  - set up restraints during model building for the residues coordinating Mg2+

10/8/20: Micholas minimizes to: `RDRP_postEM_wZn2_wMg2_protonate3d.pdb`

  - Protonate3D (at pH7) was used to set protonation states
  - EM relaxed system with the ions

10/9/20: Connor summarizes structure and analysis with Jerry:
 
  - We modeled the Mg2+ coordinating residues in using distance and angle restraints from 4WTD
  - See ![RDRP_postEM_wZn2_wMg2_protonate3d.png] for how they are arranged in the original model before EM.
  - One Mg2+ should be coordinated to Asp618(OD1), Asp760(OD1), and Asp761(OD1).
    The other Mg2+ should be coordinated to Asp618(OD2), Asp619(O), and Asp 760(OD2).
 
  - In the minimized structure these residues all look fine except Asp761.
 
  - The Zn2+ coordinating residues were modeled based on 6WTD.
  - One Zn2+ should be coordinated to Cys487(SG), His642(ND1), Cys645(SG), and Cys646(SG).
     - this one is good
  - The other Zn2+ should be coordinated to His295(ND1), Cys301(SG), Cys306(SG), and Cys310(SG).
 
  - Cys306 in the other cluster is protonated
  - His295 is a bit off from how it should be oriented (maybe that’s fine)
 
  * definitely need to fix Cys306
    - Can you redo the minimization with the listed Cys residues all deprotonated
  * How much the other stuff matters might depend on where you want to dock.

10/9/20: Micholas
 
  - Mg2+ ions matter for the remdesivir binding site
  - tethered the Mg2+ ions to their original location
  - will re-run the energy minimization again with the Amber14SB ff plus the modified ion potentials
 
  - For the MD, I’ll manually adjust the protonation state for the Cys306
    * protonation predictions indicated at that pH 7 it should be protonated
    * will check for deprotonation at each step and adjust if needed.
 
10/9/20: Micholas Smith produced `RDRP_postEM_wZn2_wMg2_protonate3d.pdb`
  - Ran relaxation with “fix” constraints on the Mg2+ binding pocket
  - manually modified the protonation on the Cys306, relaxed
  - re-ran protonate3d to make sure the protonation’s remained unchanged (they do)
  - not much deviation after EM

10/10/20: Connor Cooper modified to: `RDRP_postEM_wZn2_wMg2_tethered_MG2_protonate3d.pdb`

10/28/20: Strategy discussion - dock to non-metal-binding sites?
  - Rupesh: check Folding@Home Cryptic Binding sites for RDRP
  - Rupesh: check against apo structure https://www.rcsb.org/structure/7BV1
            or look at relevant lit. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7261222/
  - Jerry: need to check small-molecule binding modes
    * experimental cpds - watch for prodrugs & covalent bonds
  - Micholas: use blind docking of diversity set to probe
              site/chemical space-dependence
    * do they bind at some specific pocket in the RNA binding site?
    * check remdecivir alignment
    * check all pores / active site residues
    * understand interaction of metals
    * check RNA alignment for displacement)
    - potential conclusion = we can only dock nucleoside analogues
    -        or  = specific residues are "druggable"
    -        or  = some class of compounds align with remdecivir covalent attachment site
    -        or  = some site selection works best
  - Jeremy: dock diversity set broadly, identify gigadocking sites
    * helpful if docking site is too large initially
    * RNA is large, what piece is key?


## Computational Preparation

```
# Receptor Preparation script from Josh Vermaas
#

import subprocess
subprocess.call("python /usr/lib/python2.7/dist-packages/AutoDockTools/Utilities24/prepare_receptor4.py -r RDRP.pdb -o RDRP.pdbqt -A bonds_hydrogens", shell=True)
string= "RDRP"
thestring = " ".join(list(set(subprocess.check_output("cat %s.pdbqt | awk '{print $13}'" % string, shell=True).split())))

gpfinput = '''npts 65 65 65                        # num.grid points in xyz
gridfld %s.maps.fld             # grid_data_file
spacing 0.375                        # spacing(A)
receptor_types %s     # receptor atom types
ligand_types C N OA HD A NA F SA S Cl P I Br   # ligand atom types
receptor %s.pdbqt               # macromolecule
gridcenter 93.88 83.08 97.29 # xyz coordinates for the center of the box.
smooth 0.5                           # store minimum energy w/in rad(A)
map %s.C.map                    # atom-specific affinity map
map %s.N.map                    # atom-specific affinity map
map %s.OA.map                   # atom-specific affinity map
map %s.HD.map                    # atom-specific affinity map
map %s.NA.map                    # atom-specific affinity map
map %s.A.map                   # atom-specific affinity map
map %s.F.map                   # atom-specific affinity map
map %s.Cl.map                   # atom-specific affinity map
map %s.SA.map                   # atom-specific affinity map
map %s.S.map                   # atom-specific affinity map
map %s.P.map                   # atom-specific affinity map
map %s.I.map                   # atom-specific affinity map
map %s.Br.map                   # atom-specific affinity map
elecmap %s.e.map                # electrostatic potential map
dsolvmap %s.d.map              # desolvation potential map
dielectric -0.1465                   # <0, AD4 distance-dep.diel;>0, constant
'''

fout = open("RDRP.gpf", "w")

fout.write(gpfinput % (string, thestring,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string))
fout.close()
fout.close()
subprocess.call("autogrid4 -p RDRP.gpf", shell=True)
```
