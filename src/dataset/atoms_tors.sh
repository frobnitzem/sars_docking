#!/bin/bash
#SBATCH -A stf006
#SBATCH -t 10
#SBATCH -N 100
#SBATCH -J atoms_tors
#SBATCH -o atoms_tors.%J

. /gpfs/alpine/world-shared/stf006/rogersdd/venvs/env.sh
nodes=$SLURM_JOB_NUM_NODES

echo `date` "Starting job"

dirnames=(MPro_5R84 MPro_6WQF Spike_6M0J NSP15_6WLC PLPro_7JIR RDRP)
for((i=0;i<${#dirnames[*]};i++)); do
  dir=${dirnames[$i]}
  N=${Ns[$i]}
  echo $dir
  srun --ntasks-per-node 8 -N $nodes --cpus-per-task=4 --cpu-bind=cores \
       python -m mpi4py atoms_tors.py $dir 0
done

echo `date` "Completed job"
