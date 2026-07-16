#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J DeepSurv_500_dev
#SBATCH -p node
#SBATCH -t 48:00:00
#SBATCH --output=Logs/DeepSurv/DeepSurv_500_dev.log
#SBATCH --error=Logs/DeepSurv/DeepSurv_500_dev.err

eval "$(conda shell.bash hook)"

conda activate analysis

INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_500.parquet"
OUTPUT_DIR="/path/to/project/Output/DeepSurv/500f"
MODEL_NAME="500_new"

/home/$USER/.conda/envs/analysis/bin/python Prog/Scripts/Deep_surv.py --input_csv $INPUT_CSV --output_dir $OUTPUT_DIR --MODEL_NAME $MODEL_NAME



 
