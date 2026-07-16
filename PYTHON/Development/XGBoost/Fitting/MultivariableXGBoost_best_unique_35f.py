import os
import numpy as np
import xgboost as xgb
import argparse
import pandas as pd
from lifelines.utils import concordance_index

def main(input_csv, output_dir):

    df = pd.read_parquet(input_csv)
    #df_train = df[df['Sub_Cohort'] == 'Development']
    df_train = df[df['Sub_Cohort'].isin(['Development', 'Discovery'])]
    df_train =df_train.drop(columns=['Sub_Cohort'])
    df_val = df[df['Sub_Cohort'] == 'Validation']
    df_val =df_val.drop(columns=['Sub_Cohort'])
    del(df)

    # Undersamplying data to handle imbalance data
    df_ones = df_train[df_train.Inc_Fx_Inc_fx_hip_bin_cens == 1]
    df_zeros = df_train[df_train.Inc_Fx_Inc_fx_hip_bin_cens== 0].sample(n=len(df_ones))
    df_train = pd.concat([df_ones, df_zeros])

    outcome_columns = ["Inc_Fx_Inc_fx_hip_bin_cens", "Inc_Fx_Inc_fx_hip_days_to_cens"]
    predictors_train = df_train.columns.difference(outcome_columns).tolist()
    predictors_val = df_val.columns.difference(outcome_columns).tolist()

    # Create lower and upper bounds for survival analysis
    df_train['label_lower'] = df_train['Inc_Fx_Inc_fx_hip_days_to_cens']
    df_train['label_upper'] = np.where(df_train['Inc_Fx_Inc_fx_hip_bin_cens']==1, df_train['Inc_Fx_Inc_fx_hip_days_to_cens'], 4200)

    df_val['label_lower'] = df_val['Inc_Fx_Inc_fx_hip_days_to_cens']
    df_val['label_upper'] = np.where(df_val['Inc_Fx_Inc_fx_hip_bin_cens']==1, df_val['Inc_Fx_Inc_fx_hip_days_to_cens'], 4200)

    X_train = df_train[predictors_train].values
    y_lower_train = df_train['label_lower'].values
    y_upper_train = df_train['label_upper'].values
    X_val = df_val[predictors_val].values
    y_lower_val = df_val['label_lower'].values
    y_upper_val = df_val['label_upper'].values

    # Convert X_train and X_test to DataFrames with proper column names
    X_train_df = pd.DataFrame(X_train, columns=predictors_train)
    X_val_df = pd.DataFrame(X_val, columns=predictors_val)
    # Prepare DMatrix for training and testing with DataFrames
    dtrain = xgb.DMatrix(X_train_df, feature_names=predictors_train)
    dtrain.set_float_info('label_lower_bound', y_lower_train)
    dtrain.set_float_info('label_upper_bound', y_upper_train)
    dval = xgb.DMatrix(X_val_df, feature_names=predictors_val)
    dval.set_float_info('label_lower_bound', y_lower_val)
    dval.set_float_info('label_upper_bound', y_upper_val)

    # Public example settings only; study-specific tuning is not included.
    params = {
            "verbosity": 2,
            "tree_method": "hist",
            "objective": "survival:aft",  # AFT model for survival analysis
            "aft_loss_distribution": "normal",
            "aft_loss_distribution_scale": 1.0,
            "eval_metric": "aft-nloglik",
            "max_depth": 3,
            "min_child_weight": 1,
            "eta": 0.1
        }

    evals_result = {}
    evals = [(dtrain, 'train'), (dval, 'validation')]
    bst = xgb.train(params, dtrain, num_boost_round=200, evals=evals, evals_result=evals_result, early_stopping_rounds=20)
 
    # Save the model
    bst.save_model(os.path.join(output_dir, "xgb_model_best_unique_35f.json"))
    print("Model saved at:", os.path.join(output_dir, "xgb_model_best_unique_35f.json"))

    y_pred_val = bst.predict(dval)
    ci_val = concordance_index(y_lower_val, y_pred_val)
    print(f'Concordance Index (Validation): {ci_val:.4f}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train XGBoost model and save the results.")
    parser.add_argument("--input_csv", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")

    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the main function with the provided arguments
    main(args.input_csv, args.output_dir)


#python train_model.py --input_csv %INPUT_CSV% --output_dir %OUTPUT_DIR%
