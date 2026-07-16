import pandas as pd
import os
from lifelines import CoxPHFitter
import argparse
import dask
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
def main( output_dir,  input_csv, penalty, Nvars):

    ################################ Read Data ################
    
    df1 = pd.read_parquet(input_csv)
    df1 = df1[df1['Sub_Cohort'] == 'Development']
    df1 = df1.drop(columns=['Sub_Cohort']) 


############################  balance data
    df_ones = df1[df1.Inc_Fx_Inc_fx_hip_bin_cens == 1]

    df_zeros = df1[df1.Inc_Fx_Inc_fx_hip_bin_cens== 0].sample(n=len(df_ones))
    df_train = pd.concat([df_ones, df_zeros]) 


    ######################## FIT THE MODEL ################
    
   
    model = fit_lasso_cox(df_train, penalty)

    print(f"Program is now fitting the model") 
  


    ########################################## SAVING THE MODEL ##################
    with open (os.path.join(output_dir, "Cox_"+str(Nvars)+"_XG.pkl"),"wb") as f:
       pickle.dump(model,f)
    
    print("Model saved at:", os.path.join(output_dir, "Cox_"+str(Nvars)+"_XG.pkl"))




#################### EXECUTES THE SCRIPT##############################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Multivariable Cox with Dask and save the results.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")
    parser.add_argument("--input_csv",type=str,required=True, help="input_csv")
    parser.add_argument("--penalty",type=float,required=True, help="Penalty parameter")
    parser.add_argument("--Nvars",type=int,required=True, help="Variable number")
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the main function with the provided arguments
    main( args.output_dir, args.input_csv,  args.penalty, args.Nvars)
    
