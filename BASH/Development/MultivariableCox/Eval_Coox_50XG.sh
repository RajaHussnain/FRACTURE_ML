#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Ev_cox_50xg
#SBATCH -p node
#SBATCH -t 2:00:00
#SBATCH --output=Logs/Lasso/Ev_cox_50xg.log
#SBATCH --error=Logs/Lasso/Ev_cox_50xg.err


eval "$(conda shell.bash hook)"
conda activate analysis



MODEL_NAME="Cox_50_XG"

~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/EV_COX.py --MODEL_NAME $MODEL_NAME
