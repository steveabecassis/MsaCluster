#!/bin/bash

#SBATCH --time=05:00:00
#SBATCH --ntasks=8
#SBATCH --mem=8G

OUTPUT_NAME_DIR="$1"

source /sci/labs/orzuk/steveabecassis/colabfold_new/bin/activate.csh

python3 ./Analysis_params.py -input $OUTPUT_NAME_DIR

#3v0tA_3uyiA