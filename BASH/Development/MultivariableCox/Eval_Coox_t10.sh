#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Ev_cox_t10
#SBATCH -p node
#SBATCH -t 2:00:00
#SBATCH --output=Logs/Lasso/Ev_cox_t10.log
#SBATCH --error=Logs/Lasso/Ev_cox_t10.err


eval "$(conda shell.bash hook)"
conda activate analysis


MODEL_NAME="Cox_t10_each"

~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/EV_COX.py --MODEL_NAME $MODEL_NAME


