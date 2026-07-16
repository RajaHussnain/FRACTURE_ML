#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Cox_t10_each_filter
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/Lasso/Cox_t10_each_filter.log
#SBATCH --error=Logs/Lasso/Cox_t10_each_filter.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Output/MultivariableCox/Lasso"
INPUT_CSV="/path/to/project/Output/MultivariableCox/Lasso/Cox_t10_each_filter.parquet"


~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/cox_t10_each_filter_.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --penalty 0.1




