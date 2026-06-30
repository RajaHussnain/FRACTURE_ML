# Hip Fracture Survival Modelling Scripts

This repository contains public-facing analysis scripts for the hip fracture survival modelling project submitted to PLOS Medicine. The release is intended to document the analysis workflow and code structure. It does not contain raw registry data, derived datasets, fitted model artifacts, feature-selection mapping files, private model weights, or the study-specific model configurations used for the manuscript results.

The training scripts include simplified example settings so that the code remains readable and auditable without exposing the final model configuration. These public settings are placeholders and should not be interpreted as the tuned parameters or final specifications used in the study.

## Repository Contents

```text
BASH/
  Data_curation/              SLURM wrappers for data curation and summary jobs
  Discovery/                  SLURM wrappers for discovery Cox and XGBoost jobs
  Development/                SLURM wrappers for development Cox, XGBoost, and DeepSurv jobs
 Development/

PYTHON/
  Data_curation/              Data preparation and descriptive summary scripts
  Discovery/
    Cox/                      Univariable and multivariable Cox screening scripts
    XGBoost/                  XGBoost data creation, fitting, and evaluation scripts
  Development/
    Cox/                      Cox model fitting and evaluation scripts
    XGBoost/                  XGBoost fitting and evaluation scripts
    DeepSurv/                 DeepSurv-style neural Cox fitting and evaluation scripts

Recalibration/
  R CODE/                     R scripts for preparing and plotting recalibration outputs
```

## Runtime Environment

The scripts were originally developed for a Linux HPC environment using SLURM job submission. The included `BASH/` wrappers preserve the execution pattern but now use placeholder paths such as `/path/to/project`, `/path/to/raw_data`, and `/path/to/curated_data`. These must be replaced with local paths before running any code.

Two dependency files are provided:

```bash
conda env create -f environment.yml
conda activate hip-fracture-survival
```

or:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For GPU-enabled PyTorch, install a PyTorch build appropriate for the target CUDA version before installing the remaining packages.

## Expected Data Schema

Most scripts expect a cohort/outcome file and covariate files that can be joined by an individual identifier. The common columns referenced across the scripts are:

- `LopNr`: individual/person identifier used for merging covariate files.
- `Sub_Cohort`: cohort assignment, commonly including discovery, development, and validation partitions.
- `Inc_Fx_Inc_fx_hip_bin_cens`: event indicator for incident hip fracture.
- `Inc_Fx_Inc_fx_hip_days_to_cens`: time-to-event or censoring time in days.
- `Age`: age variable used in several Cox models.
- `Sex`: sex variable used in several data preparation and subgroup workflows.

Additional predictor columns are expected to be supplied by local covariate files. The private feature-selection mapping files are not included.

## Workflow Summary

The code is organized around three broad phases:

1. Data curation and descriptive summaries.
2. Discovery-stage variable screening and candidate predictor reduction.
3. Development-stage model fitting, validation, evaluation, and recalibration plotting.

The implemented model families are:

- Cox proportional hazards models using `lifelines`.
- XGBoost accelerated failure-time survival models using `xgboost`.
- DeepSurv-style neural Cox models using `pycox`, `torchtuples`, and `torch`.

Evaluation scripts compute time-horizon performance summaries, including discrimination metrics, classification summaries, calibration plots, and report/figure outputs. These outputs are generated locally and are intentionally ignored by `.gitignore`.

## Public Model Configuration Policy

The public training scripts intentionally use simple example settings. They are present to show the modelling approach and code flow, not to reveal the tuned model configuration used for the study.

In particular:

- XGBoost fitting scripts use simplified public example AFT settings and short training limits.
- DeepSurv training uses a small illustrative neural network configuration.
- Cox wrapper scripts use generic example penalties.
- Exact final model settings, private feature maps, fitted models, and calibration factors are not included.

Users with approved access to the original secure environment would need the private data, feature-selection files, model artifacts, and study-specific configuration files to reproduce the manuscript results.

## Running Jobs

Most batch scripts are intended to be submitted with SLURM:

```bash
sbatch BASH/Discovery/XGBoost/Fitting/MultivariableXGBoost_A1.sh
```

Before running any job, update:

- SLURM account and partition settings.
- Conda/Python executable path.
- Input data paths.
- Output/report paths.
- Any local folder names referenced by the script.

Some Python scripts also expect `SLURM_ARRAY_TASK_ID` when run through array jobs.

## Recalibration Scripts

The R scripts in `Recalibration/R CODE/` prepare and plot calibration summaries. They require locally supplied prediction/calibration input files, which are not included in this repository.
