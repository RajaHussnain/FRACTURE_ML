#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Cox_small_xg
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/Lasso/Coxsmall__XG_.log
#SBATCH --error=Logs/Lasso/Coxsmall__XG_.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Output/MultivariableCox/Lasso"
INPUT_CSV="/path/to/project/Output/MultivariableCox/Lasso/Cox_70_XG.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost_.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 70

INPUT_CSV="/path/to/project/Output/MultivariableCox/Lasso/Cox_50_XG.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost_.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 50

INPUT_CSV="/path/to/project/Output/MultivariableCox/Lasso/Cox_30_XG.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost_.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 30

INPUT_CSV="/path/to/project/Output/MultivariableCox/Lasso/Cox_21_XG.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost_.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 21


INPUT_CSV="/path/to/project/Output/MultivariableCox/Lasso/Cox_300_XG.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/multivariablecox_300_xgboost_.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1 --Nvars 300




