#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J xgb_test_dev_50f
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/XGBoost/xgb_test_dev_50f.log
#SBATCH --error=Logs/XGBoost/xgb_test_dev_50f.err

eval "$(conda shell.bash hook)"

conda activate analysis

INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_50.parquet"
MODEL_PATH="/path/to/project/Output/Multivariable_XGBoost/xgb_model_dev_50f.json"
OUTPUT_DIR="/path/to/project/Output/Multivariable_XGBoost/dev/"

/home/$USER/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/MultivariableXGBoost_testing_dev_50f.py --input_csv $INPUT_CSV --model_path $MODEL_PATH --output_dir $OUTPUT_DIR




 
