#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Ev_DS_35
#SBATCH -p node
#SBATCH -t 12:00:00
#SBATCH --output=Logs/Lasso/Ev_DS_35.log
#SBATCH --error=Logs/Lasso/Ev_DS_35.err


eval "$(conda shell.bash hook)"
conda activate analysis


MODEL_NAME="35"
DATA_PATH="/path/to/project/Data/XGBoost/best_unique_35.parquet"
MODEL_PATH="/path/to/project/Output/DeepSurv/35f/35_newdeep_surv.pth"

~/.conda/envs/analysis/bin/python Prog/Scripts/Deep/Ev_Deep_surv.py --MODEL_NAME $MODEL_NAME --data_path $DATA_PATH --model_path $MODEL_PATH



