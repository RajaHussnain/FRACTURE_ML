import pandas as pd
import os
from lifelines import CoxPHFitter
import sys
import dask.dataframe as dd
from os.path import exists
from lifelines.exceptions import ConvergenceError
from lifelines.exceptions import ConvergenceWarning
import warnings

################################## Read enviroment variables
Job_Id = os.getenv("SLURM_ARRAY_TASK_ID") 
Nsim_start = int(Job_Id) + 1
stride = 16
folder = sys.argv[1]
file_name = sys.argv[2]

covariate_files = "/path/to/curated_data/"+folder+"/"+file_name
######################################  READ OUTCOMES ###################################################
Covariates = dd.read_csv(covariate_files, encoding="utf-8", sep=",", assume_missing=True).columns

Nsim_stop = len(Covariates) 

data_file = "/path/to/project/Data/der/sub_cohort_censored.csv"
Event = "Inc_Fx_Inc_fx_hip_bin_cens"
Time = "Inc_Fx_Inc_fx_hip_days_to_cens"
LopNr = "LopNr"

df = pd.read_csv(data_file,engine="pyarrow")
df = df[df["Sub_Cohort"]=="Discovery"]
df = df[[LopNr,Event, Time,"Age","Sex"]]

save_path = "/path/to/project/Output/Univariate analyses interaction/"+folder+"/int_Uni_Cox"+file_name

########################################## FIT MODEL with age interaction
for ind in range(Nsim_start, Nsim_stop, stride):
    column = Covariates[ind]
    ######################################  READ DATA ###################################################
    df_covariate = dd.read_csv(covariate_files, encoding="utf-8", sep=",", assume_missing=True, usecols =[0,ind])
    df_cov = df_covariate.compute()
    df_tmp = []
####################################### MERGE OUTCOMES AND COVARIATE ########################################
    df_tmp = df.merge (df_cov, on = ["LopNr"])
    df_tmp = df_tmp.drop("LopNr",axis=1)
    df_tmp = pd.get_dummies(df_tmp,columns=[column], drop_first=True)
    print("Fitting the model ....")
        ################################################# Try to fit model#################################
    try:
        with warnings.catch_warnings():
            covs = df_tmp.columns.difference(["Sex","Age",'Inc_Fx_Inc_fx_hip_bin_cens', 'Inc_Fx_Inc_fx_hip_days_to_cens'])
            formula = "Sex+"
            for cov in covs:
                formula = formula + "Age*"+cov+"+"
            formula = formula[:-1]
            formula
            warnings.simplefilter("ignore", ConvergenceWarning)
            cph = CoxPHFitter()
            cph.fit(df = df_tmp , duration_col = Time, event_col = Event, formula = formula)   
            ################################################## SAVE RESULTS ####################
            Suma = cph.summary
            Suma["Covariate_tested"] = Covariates[ind]
            Suma["File"] = file_name
            Suma["Job_id"] = Job_Id
            Suma["Covariates_model"] = cph.summary.index
            if(exists(save_path)):
                Suma.to_csv (save_path, sep = ",", index = False, header = False, mode="a")
            else:
                Suma.to_csv(save_path, sep = ",", index = False)
######################################## SKIP COVARIATE IF MODEL FAILS ########################            
    except ConvergenceError as e: #If fails log with empty data and Covariate name
        print(f"Convergence error for covariate {Covariates[ind]}: {e}")
    except Exception as e:
        print(f"An error occured with covariate {Covariates[ind]}: {e}")

    

    