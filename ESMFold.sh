#!/bin/bash

#SBATCH --time=05:00:00
#SBATCH --ntasks=16
#SBATCH --mem=256G


mkdir output/esm_fold_output
python3 ./ESMFoldHF.py -input ./msas4esm/cluster_001.a3m -output ./output/esm_fold_output -name 'Cluster001_'

