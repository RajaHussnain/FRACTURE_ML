import os
import numpy as np
import dask.dataframe as dd
import xgboost as xgb
import argparse

import pandas as pd

def make_xgb_response(data, event, time_to_event):
    df = data.copy()
    df["xgb_response"] = 100000.0
    df["y_lower"] = -10.0
    df["y_upper"] = -10.0
    
    df.loc[df[event] == 1, "xgb_response"] = df[time_to_event].astype(float)
    df["y_lower"] = df[time_to_event].astype(float)
    df.loc[df[event] == 1, "y_upper"] = df[time_to_event].astype(float)
    df.loc[df[event] == 0, "y_upper"] = np.inf
    df["y_upper"] = df["y_upper"].replace(np.inf, 1e10)
    
    return df
# Feature importance
def save_feature_importance(booster, predictors, output_dir):

    feature_importance = booster.get_score(importance_type='weight')
    feature_importance_gain = booster.get_score(importance_type='gain')
    feature_map = {f"f{i}": feature for i, feature in enumerate(predictors)}
    
    feature_importance_df = pd.DataFrame({
        'Feature': [feature_map.get(key, key) for key in feature_importance.keys()],
        'Importance_Score_Weight': list(feature_importance.values()),
        'Importance_Score_Gain': list(feature_importance_gain.values())
    })

    feature_importance_df = feature_importance_df.sort_values(by='Importance_Score_Weight', ascending=False)
    feature_importance_df.to_csv(os.path.join(output_dir, 'A1_important_features.csv'), index=False)
    print(f"Important features saved at: {os.path.join(output_dir, 'A1_important_features.csv')}")

    
    return feature_importance_df['Feature'].tolist()
    

def main(input_csv, model_path, output_dir):

    df = dd.read_parquet(input_csv, engine="pyarrow")

    df = df[df['Sub_Cohort'] == 'Validation']

    df = df.drop(columns=['Sub_Cohort'])

    predictors = df.columns.difference(["Inc_Fx_Inc_fx_hip_bin_cens", "Inc_Fx_Inc_fx_hip_days_to_cens"]).tolist()

    df2 = df.map_partitions(make_xgb_response,
                            event="Inc_Fx_Inc_fx_hip_bin_cens",
                            time_to_event="Inc_Fx_Inc_fx_hip_days_to_cens")

    booster = xgb.Booster()
    booster.load_model(model_path)

    dmatrix = xgb.DMatrix(df2[predictors].compute(), feature_names=predictors)
    y_pred = booster.predict(dmatrix)

    y_pred_series = dd.from_array(y_pred, columns='predicted_time_to_fracture')
    df2['predicted_time_to_fracture'] = y_pred_series

    df2['actual_time_to_fracture'] = df2["xgb_response"]  
    

    df2 = df2.reset_index()

    df3 = df2[['LopNr', 'predicted_time_to_fracture', 'actual_time_to_fracture']].compute()

    # Saving preditions
    df3.to_csv(os.path.join(output_dir, "A1_predictions.csv"), index=False)
    print("Predictions saved at:", os.path.join(output_dir, "A1_predictions.csv"))

   

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test XGBoost model and save predictions, C-index, and feature importance.")
    parser.add_argument("--input_csv", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the saved XGBoost model.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the predictions and feature importance will be saved.")
    parser.add_argument("--importance_threshold", type=float, default=5, help="Importance threshold for selecting important features.")

    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    main(args.input_csv, args.model_path, args.output_dir, args.importance_threshold)
