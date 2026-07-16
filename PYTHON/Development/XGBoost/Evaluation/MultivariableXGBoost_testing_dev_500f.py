import os
import numpy as np
import pandas as pd
import xgboost as xgb
import argparse
import matplotlib.pyplot as plt
from lifelines.utils import concordance_index
from lifelines import KaplanMeierFitter
from scipy.stats import linregress
from sklearn.utils import resample
from sklearn.calibration import CalibrationDisplay

def plot_feature_importance(model, feature_names, output_dir):

    feature_importance = model.get_score(importance_type='weight')
    feature_map = {f"f{i}": feature for i, feature in enumerate(feature_names)}
    
    feature_importance_df = pd.DataFrame({
        'Feature': [feature_map.get(key, key) for key in feature_importance.keys()],
        'Importance_Score_Weight': list(feature_importance.values())
    })

    feature_importance_df = feature_importance_df.sort_values(by='Importance_Score_Weight', ascending=False)
    feature_importance_df.to_csv(os.path.join(output_dir, 'dev_500f_important_features.csv'), index=False)
    print(f"Important features saved at: {os.path.join(output_dir, 'dev_500f_important_features.csv')}")

    plt.figure(figsize=(10, 8))
    ax = xgb.plot_importance(model, importance_type='weight', max_num_features=30, height=0.8)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=7) 

    ax.set_title('Feature Importance (Top 30)', fontsize=12)
    plt.savefig(os.path.join(output_dir, 'dev_500f_feature_importance.png'))
    plt.close()
    print(f"Feature importance plot saved at: {os.path.join(output_dir, 'dev_500f_feature_importance.png')}")


def calculate_calibration(y_true, y_pred, years, output_dir):
    plt.figure(figsize=(8, 6))
    ax = plt.gca()  # Create a single set of axes to reuse for each plot

    for year in years:
        days = year * 365
        y_pred_binary = np.array([1 if time < days else 0 for time in y_pred])
        y_true_binary = np.array([1 if time < days else 0 for time in y_true])

        # Calibration in the large (CIL)
        cil = np.mean(y_pred_binary) - np.mean(y_true_binary)
        print(f"Year {year} - Calibration in the large: {cil:.4f}")

        # Calibration slope
        slope, intercept, r_value, p_value, std_err = linregress(y_pred_binary, y_true_binary)
        print(f"Year {year} - Calibration Slope: {slope:.4f}")

        # Plot each year's calibration curve on the same axes
        display = CalibrationDisplay.from_predictions(y_true_binary, y_pred_binary, n_bins=10, ax=ax, name=f"{year} Year(s)")
    
    # Adjust plot settings
    plt.title("Calibration Curve for 1 to 5 Years")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Observed Probability")
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'dev_500f_calibration_curve.png'))
    plt.close()
    print(f"Combined calibration plot saved at: {os.path.join(output_dir, 'dev_500f_calibration_curve.png')}")

def calculate_concordance_index(y_true, y_pred, years, output_dir, n_bootstraps=1000, alpha=0.05):
    c_indices = []
    ci_lower_bounds = []
    ci_upper_bounds = []

    for year in years:
        days = year * 365
        mask = y_true < days
        y_true_filtered = y_true[mask]
        y_pred_filtered = y_pred[mask]
        
        if len(y_true_filtered) > 0:
            # Calculate the C-index for the filtered data
            c_index = concordance_index(y_true_filtered, y_pred_filtered)
            print(f"Year {year} - Concordance Index: {c_index:.4f}")
            c_indices.append(c_index)
            
            # Bootstrapping for confidence intervals
            c_index_bootstraps = []
            for _ in range(n_bootstraps):
                # Resample with replacement
                y_true_sample, y_pred_sample = resample(y_true_filtered, y_pred_filtered)
                
                # Calculate C-index for the bootstrap sample
                c_index_sample = concordance_index(y_true_sample, y_pred_sample)
                c_index_bootstraps.append(c_index_sample)
            
            # Calculate confidence intervals
            ci_lower = np.percentile(c_index_bootstraps, 100 * alpha / 2)
            ci_upper = np.percentile(c_index_bootstraps, 100 * (1 - alpha / 2))
            ci_lower_bounds.append(ci_lower)
            ci_upper_bounds.append(ci_upper)
            print(f"Year {year} - C-index Confidence Interval: [{ci_lower:.4f}, {ci_upper:.4f}]")
        else:
            # If no data points are available for this year, append NaN
            c_indices.append(np.nan)
            ci_lower_bounds.append(np.nan)
            ci_upper_bounds.append(np.nan)
            print(f"Year {year} - Not enough data for Concordance Index calculation")

    # Plotting Concordance Index for each year
    plt.figure(figsize=(8, 6))
    plt.plot(years, c_indices, marker='o', linestyle='-', color='b', label="Concordance Index")
    plt.fill_between(years, ci_lower_bounds, ci_upper_bounds, color='b', alpha=0.2, label="95% CI")
    plt.xlabel("Years")
    plt.ylabel("Concordance Index")
    plt.title("Concordance Index for Different Years (1 to 5)")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'dev_500f_concordance_index_per_year.png'))
    plt.close()
    print(f"Concordance index plot saved at: {os.path.join(output_dir, 'dev_500f_concordance_index_per_year.png')}")

def main(input_csv, model_path, output_dir):
    # Load validation data
    df = pd.read_parquet(input_csv)
    df = df[df['Sub_Cohort'] == 'Validation']
    df = df.drop(columns=['Sub_Cohort'])

    outcome_columns = ["Inc_Fx_Inc_fx_hip_bin_cens", "Inc_Fx_Inc_fx_hip_days_to_cens"]
    predictors = df.columns.difference(outcome_columns).tolist()
    print("Data loaded")

    df['label_lower'] = df['Inc_Fx_Inc_fx_hip_days_to_cens']
    df['label_upper'] = np.where(df['Inc_Fx_Inc_fx_hip_bin_cens']==1, df['Inc_Fx_Inc_fx_hip_days_to_cens'], 4200)

    X = df[predictors].values
    y_lower = df['label_lower'].values
    y_upper = df['label_upper'].values

    X_df = pd.DataFrame(X, columns=predictors)

    dval = xgb.DMatrix(X_df, feature_names=predictors)
    dval.set_float_info('label_lower_bound', y_lower)
    dval.set_float_info('label_upper_bound', y_upper)

    # Load the trained model
    model = xgb.Booster()
    model.load_model(model_path)
    print(f"Model loaded from: {model_path}")

    # Make predictions
    y_pred = model.predict(dval)
    y_true = y_lower

    # Save predictions and actual values
    results = pd.DataFrame({'Actual': y_true, 'Predicted': y_pred})
    results.to_csv(os.path.join(output_dir, 'dev_500f_predictions.csv'), index=False)
    print(f"Predictions saved at: {os.path.join(output_dir, 'dev_500f_predictions.csv')}")

    # Calculate and save concordance index
    ci = concordance_index(y_true, y_pred)
    with open(os.path.join(output_dir, 'dev_500f_concordance_index.txt'), 'w') as f:
        f.write(f"Concordance Index: {ci:.4f}")
    print(f"Concordance Index: {ci:.4f}")

    # Plot and save Kaplan-Meier curve
    kmf = KaplanMeierFitter()
    kmf.fit(y_true, event_observed=(y_upper == y_lower))
    kmf.plot_survival_function()
    plt.title('Kaplan-Meier Estimate of Survival for Validation Data')
    plt.savefig(os.path.join(output_dir, 'dev_500f_kaplan_meier.png'))
    plt.close()
    print(f"Kaplan-Meier plot saved at: {os.path.join(output_dir, 'dev_500f_kaplan_meier.png')}")

    # Calculate and plot calibration scores for each year from 1 to 5 in a single figure
    calculate_calibration(y_true, y_pred, years=range(1, 6), output_dir=output_dir)

    # Calculate and plot Concordance Index for each year
    calculate_concordance_index(y_true, y_pred, years=range(1, 6), output_dir=output_dir)

    # Plot and save Feature Importance
    plot_feature_importance(model, predictors, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate XGBoost model on validation data.")
    parser.add_argument("--input_csv", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the saved XGBoost model.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")

    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the main function with the provided arguments
    main(args.input_csv, args.model_path, args.output_dir)
