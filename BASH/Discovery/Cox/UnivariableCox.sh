#!/bin/bash
#SBATCH -A <project_account>
#SBATCH -J univariableCox_all
#SBATCH -p core
#SBATCH -n 1
#SBATCH --mem=7G
#SBATCH --array=0-15
#SBATCH -t 48:00:00
#SBATCH --output=Logs/Univariable/univariableCox_all.log
#SBATCH --error=Logs/Univariable/univariableCox_all.err

#
eval "$(conda shell.bash hook)"
conda activate analysis

PYTHON=~/.conda/envs/analysis/bin/python
SCRIPT=Prog/Scripts/univariablecox.py
TASK=$SLURM_ARRAY_TASK_ID

# Input folders
AI1_DIR="/path/to/curated_data/AI1"
AI2_DIR="/path/to/curated_data/AI2"
AI3_DIR="/path/to/curated_data/AI3"
AI4_DIR="/path/to/curated_data/AI4"
AI5_DIR="/path/to/curated_data/extracted"
# 
echo "Running AI_1 files..."
for CSV in "$AI1_DIR"/*.csv; do
    $PYTHON $SCRIPT AI_1 "$(basename $CSV)" $TASK
done

echo "Running AI_2 files..."
for CSV in "$AI2_DIR"/*.csv; do
    $PYTHON $SCRIPT AI_2 "$(basename $CSV)" $TASK
done

echo "Running AI_3 files..."
for CSV in "$AI3_DIR"/*.csv; do
    $PYTHON $SCRIPT AI_3 "$(basename $CSV)" $TASK
done

echo "Running AI_4 files..."
for CSV in "$AI4_DIR"/*.csv; do
    $PYTHON $SCRIPT AI_4 "$(basename $CSV)" $TASK
done

echo "Running AI_5 files..."
for CSV in "$AI5_DIR"/*.csv; do
    $PYTHON $SCRIPT AI_5 "$(basename $CSV)" $TASK
done