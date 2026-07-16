#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Cox300_XG
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH -C mem256GB
#SBATCH --output=Logs/Lasso/Cox300_XG.log
#SBATCH --error=Logs/Lasso/Cox300_XG.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Output/MultivariableCox/Lasso"
INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_2500.parquet"


~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 300
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 10
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 30



