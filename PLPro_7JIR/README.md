# PLPro Target Notes

The targets/ subdirectory contains several different prepared inputs.
The files named `7jir+w2` were used for the docking.
The `+w<n>` notation indicates that `<n>` strongly bound waters
were retained in the structure.

## Comparison of crystal structures to re-docked poses.

Conclusions
===========

The most informative summary view of these results would be obtained from
making a table of h-bond and hydrophobic contacts present/absent in each pose.

Comparison would show generally that both water and non-water targets
have structures in the top-3 hits that have the binding pattern
expected from the xtal target.

6wx4
----

```
pymol 6wx4-ligand*.pdbqt 6wx4-aligned.pdb PLPro_7jit.pdbqt 
```

followed by `align 6wx4-aligned, PLPro_7jit`
shows that none of the docked confs have the same pose as the covalently bound inhibitor.

The old and new AD-GPU versions are nearly identical for the top pose, and differ more with poses 2, 3.

7jn2
----

```
pymol 7jn2-ligand*.pdbqt 7jn2.pdb PLPro_7jit.pdbqt
```

followed by `align 7jn2, PLPro_7jit`
shows that the non-water poses are much closed to the xtal target than the water-containing ones.  There is no meaningful structural difference between confs 1, 2, and 3.

The old and new AD-GPU versions are indistinguishable.

7jir
----

```
pymol 7jir-ligand*.pdbqt 7jir.pdb PLPro_7jit.pdbqt
```

followed by `align 7jir, PLPro_7jit` shows,
surprisingly, that alignments with water are not as exact as those without.
The top hit from the no-water case compared most favorably
with the xtal target. This is non-trivial, since there were variations in the
ring system orientation as well as two poses found for the hydrophilic
group at the bottom.

Old and new AD-GPU versions show ranking variation in the top-2 structures,
but very comparable structures are present from both.

7jit
----

```
pymol 7jit-ligand*.pdbqt 7jit.pdb PLPro_7jit.pdbqt
```

For the old method, all 3 top poses looked right with water present.  However, the new method with water showed only 2 of 3 docked in the correct position.  The difference for the no water case was even more stark.  Both of the top two no-water poses looked OK with the old method, but only the third no-water pose was OK with the new method.
This difference might be due to a bad scoring function and better sampling with the new method -- or just due to random chance.

# Computational Scripts
```
# Script to prepare a pdbqt file
# by Josh Vermaas

import subprocess
import os
def mysymlink(source, dest):
	#print source, dest
	if not os.path.exists(dest):
		os.symlink(source, dest)
minimizationscript = '''
set system %s
structure $system.psf
coordinates $system.pdb

temperature 300 

paraTypeCharmm      on
parameters par_all36m_prot.prm
parameters par_water.prm

exclude             scaled1-4
1-4scaling          1.0
cutoff              12.
switching           on
vdwForceSwitching   on
switchdist          10.
pairlistdist        14
outputName          $system-output

GBIS on

constraints on
consref $system.pdb
conskfile $system.pdb
conskcol O
binaryoutput no
minimize 1000
'''
# for pdb in ['7jir', '7jit', '7jiv', '7jiw', '7jn2']:
# 	#I had to remove the UNK from 7jn2. pdb2pqr wasn't having it.
# 	subprocess.call("pdb2pqr30 --ff CHARMM --ffout CHARMM --titration-state-method propka --with-ph 7.0 --pdb2pka-out %s-propka.out %s.pdb %s.pqr" %(pdb, pdb, pdb), shell=True)
# 	subprocess.call("vmd -dispdev text -e makepsf.tcl -args %s" % pdb, shell=True)
# 	fout = open("minimize.namd", "w")
# 	fout.write(minimizationscript % (pdb + "-system"))
# 	fout.close()
# 	subprocess.call("~/namd/Linux-x86_64-g++/namd2 +p8 minimize.namd", shell=True)
def writegpf(pdb):
	fout = open("PLPro_%s.gpf" % pdb, "w")
	fout.write(f'''npts 65 65 65                       # num.grid points in xyz
gridfld PLPro_{pdb}.maps.fld             # grid_data_file
spacing 0.375                        # spacing(A)
receptor_types A C OA N SA HD NA Zn    # receptor atom types
ligand_types C N OA HD A NA F SA S Cl P I Br Fe   # ligand atom types
receptor PLPro_{pdb}.pdbqt               # macromolecule
gridcenter 51.51 32.16 -0.55 # xyz coordinates for the center of the box.Picked based on the bound ligand from {pdb}-aligned.pdb
smooth 0.5                           # store minimum energy w/in rad(A)
map PLPro_{pdb}.C.map                    # atom-specific affinity map
map PLPro_{pdb}.N.map                    # atom-specific affinity map
map PLPro_{pdb}.OA.map                   # atom-specific affinity map
map PLPro_{pdb}.HD.map                    # atom-specific affinity map
map PLPro_{pdb}.NA.map                    # atom-specific affinity map
map PLPro_{pdb}.A.map                   # atom-specific affinity map
map PLPro_{pdb}.F.map                   # atom-specific affinity map
map PLPro_{pdb}.Cl.map                   # atom-specific affinity map
map PLPro_{pdb}.SA.map                   # atom-specific affinity map
map PLPro_{pdb}.S.map                   # atom-specific affinity map
map PLPro_{pdb}.P.map                   # atom-specific affinity map
map PLPro_{pdb}.I.map                   # atom-specific affinity map
map PLPro_{pdb}.Br.map                   # atom-specific affinity map
map PLPro_{pdb}.Fe.map                   # atom-specific affinity map
elecmap PLPro_{pdb}.e.map                # electrostatic potential map
dsolvmap PLPro_{pdb}.d.map              # desolvation potential map
dielectric -0.1465                   # <0, AD4 distance-dep.diel;>0, constant)
''' )
	fout.close()

def prepdocking(pdb):
	print(pdb + "-system-output.coor")
	mysymlink(pdb + "-system-output.coor", pdb + "-system-output.pdb")
	subprocess.call("python /usr/lib/python2.7/dist-packages/AutoDockTools/Utilities24/prepare_receptor4.py -r %s -A bonds -U nphs_lps_nonstdres -o PLPro_%s.pdbqt" % (pdb + "-system-output.pdb", pdb), shell=True)
	writegpf(pdb)
	subprocess.call("autogrid4 -p PLPro_%s.gpf" % pdb, shell=True)
	#Now don't include crystal waters
	subprocess.call("python /usr/lib/python2.7/dist-packages/AutoDockTools/Utilities24/prepare_receptor4.py -r %s -A bonds -o PLPro_%s-nowater.pdbqt" % (pdb + "-system-output.pdb", pdb), shell=True)
	writegpf(pdb+"-nowater")
	subprocess.call("autogrid4 -p PLPro_%s-nowater.gpf" % pdb, shell=True)
def docking(pdb):
	subprocess.call(f"autodock-cuda -ffile PLPro_{pdb}.maps.fld -lfile {pdb}-ligand.pdbqt -lsmet sw -nrun 100 -resnam {pdb}-ligand -xraylfile {pdb}-ligand.pdbqt", shell=True)
	subprocess.call(f"autodock-cuda -ffile PLPro_{pdb}-nowater.maps.fld -lfile {pdb}-ligand.pdbqt -lsmet sw -nrun 100 -resnam {pdb}nowater-ligand -xraylfile {pdb}-ligand.pdbqt", shell=True)
def prepligand(pdb):
	subprocess.call("vmd -dispdev text -e getligand.tcl -args %s" % pdb, shell=True)
	subprocess.call(f"python /usr/lib/python2.7/dist-packages/AutoDockTools/Utilities24/prepare_ligand4.py -l {pdb}-ligand.pdb -A bonds_hydrogens -o {pdb}-ligand.pdbqt", shell=True)
for pdb in ['7jir', '7jit', '7jiv', '7jiw', '7jn2']:
	#prepligand(pdb)
	#prepdocking(pdb)
	docking(pdb)
exit()
```
