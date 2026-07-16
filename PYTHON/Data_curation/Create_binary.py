import pandas as pd
import numpy as np
import csv
import dask.dataframe as dd
import sys

########################### Function for creating binary variables

def binarize_columns(dask_df):
    # Apply a vectorized operation to binarize the columns
    return dask_df.map_partitions(lambda df: df.applymap(lambda x: 1 if x != 0 else 0))


############################## Function for renaming variables and keeping lopnr
def apply_and_rename(df):
    first_column = df.columns[0]
    other_columns = df.columns[1:]
    
    binary_df = binarize_columns( df[other_columns])
    binary_df = binary_df.rename(columns={col: f"{col}_bin" for col in binary_df.columns})
    
    # Concatenate the first column back with the binary columns
    result_df = dd.concat([df[first_column], binary_df], axis=1)
    
    return result_df

######################################### Read enviroment variables ####################################

#Job_Id = os.getenv("SLURM_ARRAY_TASK_ID")   # Array jobs are used for parallelization 
#stride =  16                                # Number of array jobs
#Nsim_start = int(Job_Id) + 1                # Start from 1 to skip LopNr
folder = sys.argv[1]                        # Read folder from bash script
file_name = sys.argv[2]                     # Read file from bash script
covariate_files = "/path/to/raw_data/"+folder+"/"+file_name #Where to find the file


save_path = "/path/to/curated_data/"+folder+"/"+file_name # Where to save results

################################## READ DATA ####################################
df_covariate = dd.read_csv(covariate_files, encoding="utf-16", sep="\t",assume_missing = True)

################################# BINARIZE #######################################
binary_df = apply_and_rename(df_covariate)

######################################## SAVING #########################################
binary_df.to_csv(save_path, single_file=True,index=False)