#!/bin/bash

#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --mem=32G

#SBATCH --partition=puffin
#SBATCH --gres=gpu:a30


OUTPUT_NAME_DIR="$1"


RUN_OPERATION="$2"


source /sci/labs/orzuk/steveabecassis/colabfold_new/bin/activate.csh

module load torch/1.3
mkdir -p $OUTPUT_NAME_DIR/output_cmap_esm
python3  ./runESM.py  --input_msas $OUTPUT_NAME_DIR/output_msa_cluster -o $OUTPUT_NAME_DIR/output_cmap_esm
