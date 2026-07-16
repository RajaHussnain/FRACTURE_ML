#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Ev_cox_300p
#SBATCH -p node
#SBATCH -t 2:00:00
#SBATCH --output=Logs/Lasso/Ev_cox_300p.log
#SBATCH --error=Logs/Lasso/Ev_cox_300p.err


eval "$(conda shell.bash hook)"
conda activate analysis



MODEL_NAME="Cox_300p"

~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/EV_COX.py --MODEL_NAME $MODEL_NAME
