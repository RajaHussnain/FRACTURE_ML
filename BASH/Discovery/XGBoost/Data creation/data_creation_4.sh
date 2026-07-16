#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J data_creation_4
#SBATCH -p node
#SBATCH -n 3
#SBATCH -t 24:00:00
#SBATCH --output=Logs/XGBoost/data_creation_4.log
#SBATCH --error=Logs/XGBoost/data_creation_4.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Data/XGBoost/"

~/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/data_creation_4.py --output_dir $OUTPUT_DIR --Group_ID 4