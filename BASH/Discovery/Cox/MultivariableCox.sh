#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J CoxG1_43
#SBATCH -p node
#SBATCH -n 3
#SBATCH -t 24:00:00
#SBATCH --output=Logs/Lasso/CoxG1_43.log
#SBATCH --error=Logs/Lasso/CoxG1_43.err

eval "$(conda shell.bash hook)"
conda activate analysis

OUTPUT_DIR="/path/to/project/Output/MultivariableCox/Lasso"

for GROUP_ID in $(seq 1 43); do
    ~/.conda/envs/analysis/bin/python Prog/Scripts/multivariablecox.py \
        --output_dir $OUTPUT_DIR \
        --Group_ID $GROUP_ID \
        --penalty 0.1
done
