#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J xgb_ev_2500
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH -C mem512GB
#SBATCH --output=Logs/XGBoost/xgb_ev_2500.log
#SBATCH --error=Logs/XGBoost/xgb_ev_2500.err


eval "$(conda shell.bash hook)"
conda activate analysis

INPUT_DIR="/path/to/project/Data/XGBoost/A_dev_2500.parquet"
MODEL='/path/to/project/Output/Multivariable_XGBoost/xgb_model_dev_2500f.json'
OUTPUT_DIR="/path/to/project/Output/Multivariable_XGBoost/dev/2500f/XGBoost_2500f.docx"
OUTPUT_FIG="/path/to/project/Output/Multivariable_XGBoost/dev/2500f/XGBoost_2500f"

~/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/xgb_evaluation_script.py --input_dir $INPUT_DIR --model $MODEL --output_dir $OUTPUT_DIR --output_fig $OUTPUT_FIG