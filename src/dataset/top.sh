#!/bin/bash
#BSUB -P STF006
#BSUB -W 0:20
#BSUB -nnodes 371
#BSUB -q batch
#BSUB -J topN

#. /gpfs/alpine/world-shared/stf006/rogersdd/venvs/env.sh

echo `date` "Starting job"

k=7

#dirnames=(MPro_5R84 MPro_6WQF Spike_6M0J NSP15_6WLC PLPro_7JIR RDRP)
#Ns=(2592 2592 2592 2640 8194 8193)
dirnames=(PLPro_7JIR RDRP)
Ns=(8194 8193)
for((i=0;i<${#dirnames[*]};i++)); do
  dir=${dirnames[$i]}
  N=${Ns[$i]}
  jsrun -g0 -c$k -bpacked:$k -r$[42/k] \
      python -m mpi4py get_lists.py $N $dir \
                AD.pq  rf3.pq ADrf3.pq v2AD.pq v2rf3.pq rand.pq
done

echo `date` "Completed job"
