#!/bin/bash

#SBATCH --time=05:00:00
#SBATCH --ntasks=8
#SBATCH --mem=10G

FASTA_FILE_INPUT="$1"
OUTPUT_NAME_DIR="$2"


mkdir Pipeline
mkdir Pipeline/$OUTPUT_NAME_DIR
mkdir Pipeline/$OUTPUT_NAME_DIR/output_get_msa
python3 ./get_msa.py $FASTA_FILE_INPUT ./Pipeline/$OUTPUT_NAME_DIR/output_get_msa  -name 'DeepMsa'
mkdir Pipeline/$OUTPUT_NAME_DIR/output_msa_cluster
python3  ./ClusterMSA_moriah.py --keyword ShallowMsa -i ./Pipeline/$OUTPUT_NAME_DIR/output_get_msa/DeepMsa.a3m  -o ./Pipeline/$OUTPUT_NAME_DIR/output_msa_cluster
mkdir ./Pipeline/$OUTPUT_NAME_DIR/AF_preds
sbatch ./Pipeline/RunAF_params.sh $OUTPUT_NAME_DIR
mkdir Pipeline/$OUTPUT_NAME_DIR/esm_fold_output
sbatch /sci/labs/orzuk/steveabecassis/MsaCluster/Pipeline/RunEsmFold_params.sh
mkdir  ./Pipeline/$OUTPUT_NAME_DIR/output_cmap_esm
sbatch ./CmapESM_params.sh $OUTPUT_NAME_DIR



