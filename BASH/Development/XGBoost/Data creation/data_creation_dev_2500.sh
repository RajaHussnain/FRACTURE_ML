#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J data_creation_dev_2500
#SBATCH -p node
#SBATCH -t 72:00:00
#SBATCH -C mem512GB
#SBATCH --output=Logs/XGBoost/data_creation_dev_2500.log
#SBATCH --error=Logs/XGBoost/data_creation_dev_2500.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Data/XGBoost/"

~/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/data_creation_dev_2500.py --output_dir $OUTPUT_DIR