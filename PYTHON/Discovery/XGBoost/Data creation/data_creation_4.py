import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import pyarrow.parquet as pq
import csv
import random
import math
import sys
import dask.dataframe as dd
import dask.array as da
from os.path import exists
import warnings
import argparse
import dask
from dask import delayed
from dask import compute
from dask.distributed import Client
import pickle

def main( output_dir,  Group_ID):
    cluster = dask.distributed.LocalCluster()
    client = dask.distributed.Client(cluster)
    
    ########################################## Read Outcomes ##############
    df = dd.read_csv('/path/to/project/Data/der/sub_cohort_censored.csv',
    usecols=['LopNr', 'Sub_Cohort',"Inc_Fx_Inc_fx_hip_bin_cens","Inc_Fx_Inc_fx_hip_days_to_cens","Sex","Age",'Prev_fx_occ_n_13y_bin',
       'Prev_fx_occ_n_10y_bin', 'Prev_fx_occ_n_5y_bin', 'Prev_fx_occ_n_2y_bin','Prev_fx_occ_n_1y_bin'],engine = "pyarrow") 
    df = df.set_index("LopNr")                  #For faster merging
    #########################################################  Read fractures #########################

   ################################     READ CSV WITH SIGNIFICANT COVARIATES
    file_column_mapping = pd.read_csv('/path/to/project/Data/XGBOOST_with_groups.csv', sep=",") 
    ################################### folder paths for data ###########################
    folder_paths = ['/path/to/curated_data/AI_1',# path_to_folder1
                '/path/to/curated_data/AI_2',#  'path_to_folder2', 
                '/path/to/curated_data/AI_3',#  'path_to_folder3', 
                '/path/to/curated_data/AI_4',# path to folder4
                ] 
    
    ############################################ filte covariates based on CoxGroup ##################
    file_column_mapping = file_column_mapping[file_column_mapping["XGGroup"]==Group_ID]
    files = file_column_mapping["File"].unique()

    print("Merging in progress")
    ########################################  MERGE OUTCOMES AND COVARIATES #####################
    for folder in folder_paths:
        for file in files:
            file_path = os.path.join(folder, file)
            if (os.path.exists(file_path)):
                print(file_path)
                column_name = file_column_mapping["Covariate"][file_column_mapping ["File"]==file]
                column_names = np.append(column_name, "LopNr")
                ddf = dd.read_csv(file_path, engine = "pyarrow",sep=",",encoding="utf-8")
                ddf = ddf[column_names] 
                ddf = ddf.set_index("LopNr")
                df = dd.merge(df,ddf, on="LopNr",shuffle_method = "tasks",how="inner",broadcast=True, suffixes=('', '_DROP'))
                df = df[df.columns[~df.columns.str.endswith("_DROP")]]
                df = df.persist()
                del(ddf)

    # Save dataset with controlled number of partitions
    target_partition_size = "500MB"  
    df = df.repartition(partition_size=target_partition_size)

    # Save as parquet
    df.to_parquet(os.path.join(output_dir, f'A_{Group_ID}.parquet'))


#################### EXECUTES THE SCRIPT##############################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data creation for XGBoost models.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")
    parser.add_argument("--Group_ID",type=int,required=True, help="XGBoost group ID")
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the main function with the provided arguments
    main( args.output_dir,  args.Group_ID)