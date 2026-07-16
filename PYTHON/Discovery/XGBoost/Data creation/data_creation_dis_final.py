import pandas as pd
import os
import argparse

def main(output_dir):
    file_column_mapping = pd.read_csv('/path/to/project/Data/XGBoost/XGboost_vars_2percent.csv', sep=",")
    all_columns = file_column_mapping["Variable"].unique()

    additional_columns = [
        'LopNr', 'Sub_Cohort', "Inc_Fx_Inc_fx_hip_bin_cens", "Inc_Fx_Inc_fx_hip_days_to_cens",
        "Sex", "Age", 'Prev_fx_occ_n_13y_bin', 'Prev_fx_occ_n_10y_bin', 
        'Prev_fx_occ_n_5y_bin', 'Prev_fx_occ_n_2y_bin', 'Prev_fx_occ_n_1y_bin'
    ]

    folder_paths = [
        '/path/to/project/Data/XGBoost/A_1.parquet',
        '/path/to/project/Data/XGBoost/A_2.parquet',
        '/path/to/project/Data/XGBoost/A_3.parquet',
        '/path/to/project/Data/XGBoost/A_4.parquet',
        '/path/to/project/Data/XGBoost/A_5.parquet'
    ]

    dataframes = []
    print("Merging in progress")

    # Iterate through each folder path and read the Parquet file if it exists
    for folder in folder_paths:
        if os.path.exists(folder):
            print(f"Reading: {folder}")
            df = pd.read_parquet(folder)

            if 'A_1.parquet' in folder:
                columns_to_keep = list(set(all_columns) | set(additional_columns))
            else:
                columns_to_keep = list(set(all_columns) | set(["LopNr"]))

            existing_columns = [col for col in columns_to_keep if col in df.columns]
            df = df[existing_columns]
            print(f"Number of columns read: {len(df.columns)}")

            dataframes.append(df)

    #merged_df = pd.concat(dataframes, ignore_index=True)
    df1 = dataframes[0]
    df2 = dataframes[1]
    df3 = dataframes[2]
    df4 = dataframes[3]
    df5 = dataframes[4]

    del(df)
    del(dataframes)

    df1 = df1.merge(df2, on='LopNr', how='left')
    del(df2)
    df1 = df1.merge(df3, on='LopNr', how='left')
    del(df3)
    df1 = df1.merge(df4, on='LopNr', how='left')
    del(df4)
    df1 = df1.merge(df5, on='LopNr', how='left')
    del(df5)

    output_file_path = os.path.join(output_dir, 'A_dis_final_4500.parquet')
    df1.to_parquet(output_file_path)
    print(f"Merged file saved at: {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data creation for XGBoost models.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    main(args.output_dir)