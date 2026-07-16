#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Ev_DS_35_sub_perm
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/DeepSurv/permutation/Ev_DS_35_perm.log
#SBATCH --error=Logs/DeepSurv/permutation/Ev_DS_35_perm.err


eval "$(conda shell.bash hook)"
conda activate analysis


DATA_PATH="/path/to/project/Data/XGBoost/best_unique_35.parquet"
MODEL_PATH="/path/to/project/Output/DeepSurv/35f/35_newdeep_surv.pth"
OUTPUT_PATH="/path/to/project/Output/DeepSurv/35f/permutation/"

~/.conda/envs/analysis/bin/python Prog/Scripts/Deep/Ev_Deep_surv_perm.py --output_path $OUTPUT_PATH --data_path $DATA_PATH  --model_path $MODEL_PATH
