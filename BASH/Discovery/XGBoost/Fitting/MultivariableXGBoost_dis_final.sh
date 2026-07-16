#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J xgb_train_dis_final
#SBATCH -p node
#SBATCH -t 48:00:00
#SBATCH -C mem512GB
#SBATCH --output=Logs/XGBoost/xgb_train_dis_final.log
#SBATCH --error=Logs/XGBoost/xgb_train_dis_final.err

eval "$(conda shell.bash hook)"

conda activate analysis

INPUT_CSV="/path/to/project/Data/XGBoost/A_dis_final_4500.parquet"
OUTPUT_DIR="/path/to/project/Output/Multivariable_XGBoost"

/home/$USER/.conda/envs/analysis/bin/python Prog/Scripts/XGBoost_scripts/MultivariableXGBoost_dis_final.py --input_csv $INPUT_CSV --output_dir $OUTPUT_DIR

conda deactivate



 
