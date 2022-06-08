#!/bin/bash
#SBATCH -A stf006
#SBATCH -t 20
#SBATCH -N 20
#SBATCH -J summary
#SBATCH -o summary.%J

. /gpfs/alpine/world-shared/stf006/rogersdd/venvs/env.sh
nodes=$SLURM_JOB_NUM_NODES

echo `date` "Starting job"

#dirnames=(MPro_5R84 MPro_6WQF Spike_6M0J NSP15_6WLC PLPro_7JIR RDRP)
#Ns=(2592 2592 2592 2640 2049 2048)
dirnames=(Spike_6M0J)
Ns=(2592)
for((i=0;i<${#dirnames[*]};i++)); do
  dir=${dirnames[$i]}
  N=${Ns[$i]}
  srun --ntasks $[nodes*16] -N $nodes --cpus-per-task=2 --cpu-bind=cores \
       python -m mpi4py summary.py $dir $N
done

echo `date` "Completed job"
