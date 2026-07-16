import os
import argparse
import pycox
import matplotlib.pyplot as plt
import torch
import torchtuples as tt
from pycox.models import CoxPH
import pandas as pd
from sklearn.model_selection import train_test_split

def main(input_csv, output_dir,MODEL_NAME):

    #  READ DATA
    df = pd.read_parquet(input_csv, engine="pyarrow")
    df = df [df['Sub_Cohort'] == 'Development']
    df = df.drop('Sub_Cohort',axis=1)

    #  Balance data
    df_ones = df[df.Inc_Fx_Inc_fx_hip_bin_cens == 1]
    df_zeros = df[df.Inc_Fx_Inc_fx_hip_bin_cens== 0].sample(n=len(df_ones))
    df = pd.concat([df_ones, df_zeros]) 

    # TRAIN, VAL SPLIT
    df_train, df_val = train_test_split(df, test_size=0.15)
    
    #  DATA STANDARDIZATION
    get_target = lambda df: (df['Inc_Fx_Inc_fx_hip_days_to_cens'].values, df['Inc_Fx_Inc_fx_hip_bin_cens'].values)
    get_feat = lambda df: (df.drop(['Inc_Fx_Inc_fx_hip_days_to_cens','Inc_Fx_Inc_fx_hip_bin_cens'],axis=1).values)
    df_train = df_train.dropna()
    df_val = df_val.dropna()
    y_train = get_target(df_train)
    y_val = get_target(df_val)
    x_train = get_feat (df_train)
    x_val = get_feat ( df_val)
    x_train = x_train.astype("float32")
    x_val = x_val.astype("float32")
    val = x_val, y_val

    # NEURAL NETWORK CONFIGURATION
    # Public example settings only; the study-specific architecture and tuning are not included.
    in_features = x_train.shape[1]
    num_nodes = [16]
    out_features = 1
    batch_norm = False
    dropout = 0.0
    net = tt.practical.MLPVanilla(in_features, num_nodes, out_features, batch_norm, dropout)
    model = CoxPH(net, tt.optim.Adam)
    batch_size = 128
    epochs = 5
    callbacks = [tt.callbacks.EarlyStopping(patience=2)]

    # MODEL FITTING
    log = model.fit(x_train, y_train, batch_size, epochs, 
    callbacks, 
    val_data=val, val_batch_size=batch_size)

    # MODEL DIAGNOSTICS
    _ = log.plot()
    plt.savefig(os.path.join(output_dir,MODEL_NAME+"Logplot.png")) 

    #  SAVING MODEL
    save_path = os.path.join(output_dir,MODEL_NAME+"deep_surv.pth")
    torch.save(model.net, save_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Deep surv model and save the results.")
    parser.add_argument("--input_csv", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory where the output will be saved.")
    parser.add_argument("--MODEL_NAME", type=str, required=True, help="Model name.")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the main function with the provided arguments
    main(args.input_csv, args.output_dir,args.MODEL_NAME)