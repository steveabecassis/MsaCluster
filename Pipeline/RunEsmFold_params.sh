#!/bin/bash

#SBATCH --time=24:00:00
#SBATCH --ntasks=8
#SBATCH --mem=24G
#SBATCH --partition=dogfish
#SBATCH --gres=gpu:a100:2

OUTPUT_NAME_DIR="$1"


.  /sci/labs/orzuk/steveabecassis/steve_venv/bin/activate


mkdir -p ./Pipeline/$OUTPUT_NAME_DIR/output_esm_fold
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256
python3  ./ESMFoldHF.py  -input $OUTPUT_NAME_DIR








