#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Cox_35
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/Lasso/Cox_35.log
#SBATCH --error=Logs/Lasso/Cox_35.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Output/MultivariableCox/Lasso"
INPUT_CSV="/path/to/project/Data/XGBoost/best_unique_35.parquet"


~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/cox_300p_.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1




