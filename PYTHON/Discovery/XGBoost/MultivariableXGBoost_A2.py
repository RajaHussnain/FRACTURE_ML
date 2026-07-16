import os
import numpy as np
import dask.dataframe as dd
import dask.distributed
import xgboost as xgb
import argparse

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


def main(input_csv, output_dir):

    df = dd.read_parquet(input_csv, engine="pyarrow")

    df = df[df['Sub_Cohort'] == 'Discovery']

    df = df.drop(columns=['Sub_Cohort'])

    outcome_columns = ["Inc_Fx_Inc_fx_hip_bin_cens", "Inc_Fx_Inc_fx_hip_days_to_cens"]
    predictors = df.columns.difference(outcome_columns).tolist()

    # Apply the custom response function to each partition
    df2 = df.map_partitions(make_xgb_response,
                            event="Inc_Fx_Inc_fx_hip_bin_cens",
                            time_to_event="Inc_Fx_Inc_fx_hip_days_to_cens")

    del(df) 

    # Ensure y_lower and y_upper are part of the Dask DataFrame
    y_lower = df2["y_lower"].to_dask_array(lengths=True)
    y_upper = df2["y_upper"].to_dask_array(lengths=True)

    # Set up the Dask cluster and client
    cluster = dask.distributed.LocalCluster()
    client = dask.distributed.Client(cluster)

    # Prepare the DaskDMatrix for XGBoost training
    dtrain = xgb.dask.DaskDMatrix(client,
                                  data=df2[predictors].to_dask_array(lengths=True),
                                  label=df2["xgb_response"].to_dask_array(lengths=True),
                                  label_lower_bound=y_lower,
                                  label_upper_bound=y_upper)

    # Train an illustrative XGBoost AFT model
    output = xgb.dask.train(
        client=client,
        # Public example settings only; study-specific tuning is not included.
        params = {
            "verbosity": 2,
            "tree_method": "hist",
            "objective": "survival:aft",  # AFT model for survival analysis
            "aft_loss_distribution": "normal",
            "aft_loss_distribution_scale": 1.0,
            "eval_metric": "aft-nloglik",
            "max_depth": 3,
            "eta": 0.1
        },
        dtrain=dtrain,
        num_boost_round=200,  # Adjust this as needed for quicker results
        evals=[(dtrain, "train")],
        early_stopping_rounds=20
    )

    # Save the model
    model = output['booster']
    model.save_model(os.path.join(output_dir, "xgb_model_A2.json"))
    print("Model saved at:", os.path.join(output_dir, "xgb_model_A2.json"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train XGBoost model with Dask and save the results.")
    parser.add_argument("--input_csv", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")

    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the main function with the provided arguments
    main(args.input_csv, args.output_dir)


