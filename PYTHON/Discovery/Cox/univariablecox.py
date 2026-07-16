#################################### Import libraries for analysis ##############################
import pandas as pd
import os
from lifelines import CoxPHFitter
import sys
import dask.dataframe as dd
import dask.array as da
from os.path import exists
from lifelines.exceptions import ConvergenceError
from lifelines.exceptions import ConvergenceWarning
import warnings

######################################### Read enviroment variables ####################################

Job_Id = os.getenv("SLURM_ARRAY_TASK_ID")   # Array jobs are used for parallelization 
stride =  16                                # Number of array jobs
Nsim_start = int(Job_Id) + 1                # Start from 1 to skip LopNr
folder = sys.argv[1]                        # Read folder from bash script
file_name = sys.argv[2]                     # Read file from bash script
#covariate_files = "/path/to/raw_data/"+folder+"/"+file_name #Where to find the file
covariate_files = "/path/to/curated_data/"+folder+"/"+file_name #Where to find the file
######################################  READ DATA ###################################################
Covariates = dd.read_csv(covariate_files, encoding="utf-8", sep=",", assume_missing=True).columns
Nsim_stop = len(Covariates)         # Number of columns in file (not counting LopNr)

###########################################  READ OUTCOMES ##############################################
data_file = "/path/to/project/Data/der/sub_cohort_censored.csv"  #  Path of file with outcomes, age and sex
Event = "Inc_Fx_Inc_fx_hip_bin_cens"
Time = "Inc_Fx_Inc_fx_hip_days_to_cens"
LopNr = "LopNr"

df = pd.read_csv(data_file,engine="pyarrow")
df = df[df["Sub_Cohort"]=="Discovery"]         #Filter the data
df = df[[LopNr,Event, Time,"Age","Sex"]]


save_path = "/path/to/project/Output/Univariate analyses/"+folder+"/Uni_Cox"+file_name # Where to save results

##########################################  FIT UNIVARIABLE COX MODEL ############################


for ind in range(Nsim_start, Nsim_stop, stride): # LOOP THROUGH COLUMNS OF THE FILE
    column = Covariates[ind]
    ################################## READ LOPNR AND COVARIATE ####################################
    print(Covariates[ind])
    df_covariate = dd.read_csv(covariate_files, encoding="utf-8", sep=",", assume_missing=True, usecols =[0,ind])
    df_cov = df_covariate.compute()
    df_tmp = []
    ####################################### MERGE OUTCOMES AND COVARIATE ########################################
    df_tmp = df.merge (df_cov, on = ["LopNr"])
    df_tmp = df_tmp.drop("LopNr",axis=1)
    df_tmp = pd.get_dummies(df_tmp,columns=[column], drop_first=True)# categorical
    print("Fitting the model...")
    ################################################# Try to fit model#################################
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)  # IGNORE SIMPLE WARNINGS
            cph = CoxPHFitter()
            cph.fit(df_tmp , Time, Event)   
    ################################################## SAVE RESULTS ####################
            Suma = cph.summary
            Suma["Covariate"] = Covariates[ind]
            Suma["File"] = file_name
            Suma["Job_id"] = Job_Id
            if(exists(save_path)):
                Suma.to_csv (save_path, sep = ",", index = False, header = False, mode="a")
            else:
                Suma.to_csv(save_path, sep = ",", index = False)

    ######################################## SKIP COVARIATE IF MODEL FAILS ########################
    except ConvergenceError as e: #If fails log with empty data and Covariate name
        print(f"Convergence error for covariate {Covariates[ind]}: {e}")
    except Exception as e:
        print(f"An error occured with covariate {Covariates[ind]}: {e}")

    

    