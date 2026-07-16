#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J xgb_test_dis_final
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH -C mem512GB
#SBATCH --output=Logs/XGBoost/xgb_test_dis_final.log
#SBATCH --error=Logs/XGBoost/xgb_test_dis_final.err

eval "$(conda shell.bash hook)"

conda activate analysis

INPUT_CSV="/path/to/project/Data/XGBoost/A_dis_final_4500.parquet"
MODEL_PATH="/path/to/project/Output/Multivariable_XGBoost/xgb_model_dis_final.json"
OUTPUT_DIR="/path/to/project/Output/Multivariable_XGBoost/"

/home/$USER/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/MultivariableXGBoost_testing_dis_final.py --input_csv $INPUT_CSV --model_path $MODEL_PATH --output_dir $OUTPUT_DIR

conda deactivate



 
