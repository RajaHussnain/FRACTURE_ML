#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J data_creation_dev_70
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/XGBoost/data_creation_dev_70.log
#SBATCH --error=Logs/XGBoost/data_creation_dev_70.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Data/XGBoost/"

~/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/data_creation_dev_70.py --output_dir $OUTPUT_DIR