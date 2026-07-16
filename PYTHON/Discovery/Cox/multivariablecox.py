import pandas as pd
import numpy as np
import os
from lifelines import CoxPHFitter
import dask.dataframe as dd
import argparse
import dask
from dask import delayed
from dask import compute
import pickle

#################### MODEL FUNCTION ##############
def fit_lasso_cox(df,penalty):
    Event = "Inc_Fx_Inc_fx_hip_bin_cens"
    Time = "Inc_Fx_Inc_fx_hip_days_to_cens"
    covs = df.columns.difference(['Inc_Fx_Inc_fx_hip_bin_cens', 'Inc_Fx_Inc_fx_hip_days_to_cens',"Age"])
    df = pd.get_dummies(df,columns=covs, drop_first=True)
    covs = df.columns.difference(['Inc_Fx_Inc_fx_hip_bin_cens', 'Inc_Fx_Inc_fx_hip_days_to_cens',"Age"])
    formula = "Age +"
    for cov in covs:
       formula = formula + "+"+cov 
    cph = CoxPHFitter(penalizer= penalty,l1_ratio=1.0) #l1_ratio=1.0 is L1 regularization, l1_ratio = 0.0 is L2 regularization
    cph.fit(df,Time, Event, formula=formula)
    return cph

#### MAIN FUNCTION
def main( output_dir,  Group_ID, penalty):
    cluster = dask.distributed.LocalCluster()
    client = dask.distributed.Client(cluster)
    
    ########################################## Read Outcomes ##############
    df = dd.read_csv('/path/to/project/Data/der/sub_cohort_censored.csv',
    usecols=['LopNr', 'Sub_Cohort',"Inc_Fx_Inc_fx_hip_bin_cens","Inc_Fx_Inc_fx_hip_days_to_cens","Sex","Age",'Prev_fx_occ_n_13y_bin',
       'Prev_fx_occ_n_10y_bin', 'Prev_fx_occ_n_5y_bin', 'Prev_fx_occ_n_2y_bin','Prev_fx_occ_n_1y_bin'],engine = "pyarrow") 
    df = df.set_index("LopNr")                  #For faster merging
    df = df[df["Sub_Cohort"] == "Discovery"]    #Filter data
#########################################################  Read fractures #########################

   ################################     READ CSV WITH SIGNIFICANT COVARIATES
    file_column_mapping = pd.read_csv('/path/to/private_feature_maps/Cox_groups_new.csv', sep=",")
    file_column_mapping = file_column_mapping.drop_duplicates(subset="Covariate") 
    ################################### folder paths for data ###########################
    folder_paths = ['/path/to/curated_data/AI_1',# path_to_folder1
                '/path/to/curated_data/AI_2',#  'path_to_folder2', 
                '/path/to/curated_data/AI_3',#  'path_to_folder3', 
                '/path/to/curated_data/AI_4',# path to folder4
                '/path/to/curated_data/AI_5/extracted'#  'path_to_folder5'
                ] 
    
    ############################################ filte covariates based on CoxGroup ##################
    file_column_mapping = file_column_mapping[file_column_mapping["CoxGroup"]==Group_ID]
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
    
    df = df.drop(["Sub_Cohort"],axis=1)

    ######################## FIT THE MODEL ################
    
    delayed_fit = delayed(fit_lasso_cox)(df, penalty)

    print(f"Program is now fitting the model")
    model = compute(delayed_fit)


    ########################################## SAVING THE MODEL ##################
    with open (os.path.join(output_dir, "MultiCoxLassoGroup_" + str(Group_ID) + ".pkl"),"wb") as f:
        pickle.dump(model,f)
    
    print("Model saved at:", os.path.join(output_dir, "MultiCoxLassoGroup_" + str(Group_ID) + ".pkl"))




#################### EXECUTES THE SCRIPT##############################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Multivariable Cox with Dask and save the results.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")
    parser.add_argument("--Group_ID",type=int,required=True, help="Cox group ID")
    parser.add_argument("--penalty",type=float,required=True, help="Penalty parameter")
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the main function with the provided arguments
    main( args.output_dir,  args.Group_ID, args.penalty)
    
