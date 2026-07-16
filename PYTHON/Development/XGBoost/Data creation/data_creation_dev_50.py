import pandas as pd
import os
import argparse

def main(output_dir):
    file_column_mapping = pd.read_csv('/path/to/project/Data/XGBoost/XGboost_50_final.csv', sep=",")
    all_columns = file_column_mapping["Feature"]

    additional_columns = [
        'LopNr', 'Sub_Cohort', "Inc_Fx_Inc_fx_hip_bin_cens", "Inc_Fx_Inc_fx_hip_days_to_cens"]

    folder = [
        '/path/to/project/Data/XGBoost/A_dev_70.parquet'
    ]

    print("Merging in progress")

    df = pd.read_parquet(folder)

    columns_to_keep = list(set(all_columns) | set(additional_columns))
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    df = df[existing_columns]
    print(f"Number of columns read: {len(df.columns)}")

    output_file_path = os.path.join(output_dir, 'A_dev_50.parquet')
    df.to_parquet(output_file_path)
    print(f"Merged file saved at: {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data creation for XGBoost models.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    main(args.output_dir)