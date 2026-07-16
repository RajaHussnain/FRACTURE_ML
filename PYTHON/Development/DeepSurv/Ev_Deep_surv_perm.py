import os
import pandas as pd
import numpy as np
import argparse
from sklearn.metrics import roc_auc_score
from pycox.models import CoxPH
import torch



def permutation_importance(model, x_val, y_test_event, surv, days, predictors, n_repeats=10):
    """
    Calculate permutation importance for each feature based on drop in ROC-AUC.

    Parameters:
        model: Trained CoxPH model.
        x_val: Validation feature matrix.
        y_test_event: Binary events for the specific time horizon.
        surv: Predicted survival probabilities dataframe.
        days: Time horizon in days.
        predictors: List of predictor names.
        n_repeats: Number of permutations for each feature.

    Returns:
        DataFrame, importance mean, and standard deviation.
    """
    baseline_auc = roc_auc_score(y_test_event, 1 - surv.iloc[days].values)
    importances = []

    for i, col in enumerate(predictors):
        drop_in_auc = []
        for _ in range(n_repeats):
            x_val_permuted = x_val.copy()
            np.random.shuffle(x_val_permuted[:, i])  # Shuffle feature column
            surv_permuted = model.predict_surv_df(x_val_permuted)
            auc_permuted = roc_auc_score(y_test_event, 1 - surv_permuted.iloc[days].values)
            drop_in_auc.append(baseline_auc - auc_permuted)

        importances.append({
            "Feature": col,
            "Importance Mean": np.mean(drop_in_auc),
            "Importance Std": np.std(drop_in_auc)
        })

    return pd.DataFrame(importances).sort_values(by="Importance Mean", ascending=False)

def main(data_path, model_path, output_path, year=5, n_repeats=10):
    """
    Main function to calculate permutation importance for a specific year.

    Parameters:
        data_path: Path to the validation dataset.
        model_path: Path to the trained model.
        output_path: Path to save the permutation importance results.
        year: Time horizon in years (default is 5 years).
        n_repeats: Number of repetitions for permutation importance.
    """
    print("Loading validation data...")
    df_val = pd.read_parquet(data_path, engine="pyarrow")
    df_val =  df_val[df_val['Sub_Cohort'] == 'Validation']

    df_val = df_val.drop(columns=['Sub_Cohort'])
    df_val = df_val.dropna()
    predictors = [col for col in df_val.columns if col not in ['Inc_Fx_Inc_fx_hip_days_to_cens','Inc_Fx_Inc_fx_hip_bin_cens']]

    get_target = lambda df: (df['Inc_Fx_Inc_fx_hip_days_to_cens'].values, df['Inc_Fx_Inc_fx_hip_bin_cens'].values)
    get_feat = lambda df: (df.drop(['Inc_Fx_Inc_fx_hip_days_to_cens','Inc_Fx_Inc_fx_hip_bin_cens'],axis=1).values)
    df_val = df_val.dropna()
    x_val = get_feat(df_val)
    x_val = x_val.astype("float32")
    durations_val, events_val = get_target(df_val)


    days = 365 * year
    y_test_event = (durations_val < days).astype(int)
    y_test_event[events_val == 0] = 0  # Set to 0 for censored data

    print("Loading model...")
    net = torch.load(model_path)
    model = CoxPH(net)
    model.net.eval()

    print("Computing baseline hazards...")
    model.compute_baseline_hazards(x_val, (durations_val, events_val))

    print("Computing survival probabilities...")
    surv = model.predict_surv_df(x_val)

    # Validate `days` index
    if days not in surv.index:
        closest_days = surv.index[-1]
        print(f"Specified time horizon {days} is out of range. Using closest valid time point: {closest_days}")
        days = closest_days

    # Ensure no empty or NaN predictions
    if surv.iloc[days].isna().any():
        print("Removing NaN values in survival predictions for the specified time point.")
        surv = surv.dropna(axis=1)

    # Validate `surv.iloc[days]` contains valid samples
    survival_probs = 1 - surv.iloc[days].values
    if len(survival_probs) == 0:
        raise ValueError(f"No valid survival predictions available at {days} days.")

    print(f"Calculating permutation importance for {year}-year survival...")
    perm_importance_df = permutation_importance(
        model=model,
        x_val=x_val,
        y_test_event=y_test_event,
        surv=surv,
        days=days,
        predictors=predictors,
        n_repeats=n_repeats,
    )

    print("Saving results...")
    perm_importance_df.to_csv(os.path.join(output_path, f"Permutation_Importance_{year}Years.csv"), index=False)
    print(f"Permutation importance saved to {output_path}")
   

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate permutation importance for 5-year survival.")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the validation dataset.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the trained model.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the results.")
    parser.add_argument("--year", type=int, default=5, help="Time horizon in years (default: 5).")
    parser.add_argument("--n_repeats", type=int, default=10, help="Number of repetitions for permutation importance (default: 10).")
    args = parser.parse_args()

    main(args.data_path, args.model_path, args.output_path, args.year, args.n_repeats)