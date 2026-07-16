#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J xgb_ev_50
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/XGBoost/xgb_ev_50.log
#SBATCH --error=Logs/XGBoost/xgb_ev_50.err


eval "$(conda shell.bash hook)"
conda activate analysis

INPUT_DIR="/path/to/project/Data/XGBoost/A_dev_50.parquet"
MODEL='/path/to/project/Output/Multivariable_XGBoost/xgb_model_dev_50f.json'
OUTPUT_DIR="/path/to/project/Output/Multivariable_XGBoost/dev/50f/XGBoost_50f.docx"
OUTPUT_FIG="/path/to/project/Output/Multivariable_XGBoost/dev/50f/XGBoost_50f"

~/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/xgb_evaluation_script.py --input_dir $INPUT_DIR --model $MODEL --output_dir $OUTPUT_DIR --output_fig $OUTPUT_FIG