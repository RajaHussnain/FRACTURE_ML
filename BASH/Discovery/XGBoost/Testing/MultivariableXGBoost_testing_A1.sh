#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J xgb_test_A1
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/XGBoost/xgb_test_A1.log
#SBATCH --error=Logs/XGBoost/xgb_test_A1.err

eval "$(conda shell.bash hook)"

conda activate analysis

INPUT_CSV="/path/to/project/Data/XGBoost/A_1.parquet"
MODEL_PATH="/path/to/project/Output/Multivariable_XGBoost/xgb_model_A1.json"
OUTPUT_DIR="/path/to/project/Output/Multivariable_XGBoost/"

/home/$USER/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/MultivariableXGBoost_testing_A1.py --input_csv $INPUT_CSV --model_path $MODEL_PATH --output_dir $OUTPUT_DIR

conda deactivate



 
