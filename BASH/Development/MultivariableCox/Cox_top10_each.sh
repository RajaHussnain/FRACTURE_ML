#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J Data_create_male
#SBATCH -p node
#SBATCH -t 24:00:00
#SBATCH --output=Logs/Lasso/Data_create_male.log
#SBATCH --error=Logs/Lasso/Data_create_male.err


eval "$(conda shell.bash hook)"
conda activate analysis


OUTPUT_DIR="/path/to/project/Data/XGBoost/Subgroup"

INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_21.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/data_create_subgroup.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --subgroup "Male" --Nvar 21

INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_30.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/data_create_subgroup.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --subgroup "Male" --Nvar 30

INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_50.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/data_create_subgroup.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --subgroup "Male" --Nvar 50

INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_70.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/data_create_subgroup.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --subgroup "Male" --Nvar 70


INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_500.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/data_create_subgroup.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --subgroup "Male" --Nvar 500


INPUT_CSV="/path/to/project/Data/XGBoost/A_dev_2500.parquet"
~/.conda/envs/analysis/bin/python Prog/Scripts/Cox_Dev/data_create_subgroup.py --output_dir $OUTPUT_DIR --input_csv $INPUT_CSV --subgroup "Male" --Nvar 2500

