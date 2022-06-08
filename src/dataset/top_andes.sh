#!/bin/bash
#SBATCH -A stf006
#SBATCH -t 20
#SBATCH -N 128
#SBATCH -J topN
#SBATCH -o topN.%J

. /gpfs/alpine/world-shared/stf006/rogersdd/venvs/env.sh
nodes=$SLURM_JOB_NUM_NODES

echo `date` "Starting job"

#dirnames=(MPro_5R84 MPro_6WQF Spike_6M0J NSP15_6WLC PLPro_7JIR RDRP)
#Ns=(2592 2592 2592 2640 8194 8193)
dirnames=(PLPro_7JIR RDRP)
Ns=(8194 8193)
for((i=0;i<${#dirnames[*]};i++)); do
  dir=${dirnames[$i]}
  N=${Ns[$i]}
  srun --ntasks $[nodes*8] -N $nodes --cpus-per-task=2 --cpu-bind=cores \
      python -m mpi4py get_lists.py $N $dir \
                AD.pq  rf3.pq ADrf3.pq v2AD.pq v2rf3.pq rand.pq
done

echo `date` "Completed job"
