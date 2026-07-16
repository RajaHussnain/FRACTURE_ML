#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J xgb_train_A5
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/XGBoost/xgb_train_A5.log
#SBATCH --error=Logs/XGBoost/xgb_train_A5.err

eval "$(conda shell.bash hook)"

conda activate analysis

INPUT_CSV="/path/to/project/Data/XGBoost/A_5.parquet"
OUTPUT_DIR="/path/to/project/Output/Multivariable_XGBoost"

/home/$USER/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/MultivariableXGBoost_A5.py --input_csv $INPUT_CSV --output_dir $OUTPUT_DIR

conda deactivate



 
