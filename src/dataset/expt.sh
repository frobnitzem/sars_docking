#!/bin/bash
#SBATCH -A STF006
#SBATCH -t 50:00
#SBATCH -N 54
#SBATCH -o expt.log
#SBATCH -J expt

. /gpfs/alpine/world-shared/stf006/rogersdd/venvs/env.sh
nodes=$SLURM_JOB_NUM_NODES

echo `date` "Starting job"

k=7

dirnames=(MPro_5R84 MPro_6WQF Spike_6M0J NSP15_6WLC PLPro_7JIR RDRP)
Ns=(2592 2592 2592 2640 8194 8193)
#Ns=(8 8 8 8 25 25)
for((i=0;i<${#dirnames[*]};i++)); do
  dir=${dirnames[$i]}
  N=${Ns[$i]}
  #jsrun -g0 -c$k -bpacked:$k -r$[42/k] \
  #srun --ntasks $[nodes*8] -N $nodes --cpus-per-task=4 --cpu-bind=cores \
  srun --ntasks $[nodes*4] -N $nodes --cpus-per-task=8 --cpu-bind=cores \
      python -m mpi4py fish.py $N $dir
done

echo `date` "Completed job"
