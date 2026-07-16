#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Ev_DS_50
#SBATCH -p node
#SBATCH -t 12:00:00
#SBATCH --output=Logs/Lasso/Ev_DS_50.log
#SBATCH --error=Logs/Lasso/Ev_DS_50.err


eval "$(conda shell.bash hook)"
conda activate analysis


MODEL_NAME="50"
DATA_PATH="/path/to/project/Data/XGBoost/A_dev_50.parquet"
MODEL_PATH="/path/to/project/Output/DeepSurv/50f/50deep_surv.pth"

~/.conda/envs/analysis/bin/python Prog/Scripts/Deep/Ev_Deep_surv.py --MODEL_NAME $MODEL_NAME --data_path $DATA_PATH --model_path $MODEL_PATH



