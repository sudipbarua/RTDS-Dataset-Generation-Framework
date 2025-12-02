from nfstream import NFStreamer
import os
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

def save_file(df, folder, filename):
    # check if "./flow_ds" exists. Create if not found
    is_exist = os.path.exists(folder)
    if not is_exist:
        os.mkdir(folder)
    file_path = os.path.join(folder, filename)
    df.to_csv(file_path)


# nfstream converts the pcaps to flow (.csv files) and saved to "./flow_ds" folder
def pcap_to_flow(pcap_path, filename):
    # convert the pcap to dataframe located in "pcap_path"
    df = NFStreamer(source=pcap_path, n_dissections=0, statistical_analysis=True).to_pandas()
    folder = "./flow_ds"
    print(f"-------------------------Saving converted file: {filename}--------------------------------")
    save_file(df, folder, filename)

def clean_and_scale(df, ignored_columns, filename):
    # selected_columns = list(set(df.columns) - set(ignored_columns))  # select columns to be scaled
    df = df.drop(columns=ignored_columns, axis=1, errors='ignore')  # drop irrelevant columns
    df = df.dropna()  # drop nans
    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    folder = "./binary_class_labeled_ds"
    print(f"-------------------------Saving cleaned and scaled file: {filename}--------------------------------")
    save_file(df_scaled, folder, filename)


# label ds based on list of intruder source IPs: label 1 if source IPs match, else 0
def label_ds_binary_class(df, ips, filename):
    # at first label all the flow to 0
    df['Label'] = 0
    # now label the flow that contain the ips from the list "ips" (N.B.-the attacker and victim IPs)
    df.loc[df["src_ip"].isin(ips) & df["dst_ip"].isin(ips), "Label"] = 1
    # save ds to "./binary_class_labeled_ds" folder
    print(f"-------------------------Saving Labeled Dataset: {filename}--------------------------------")
    folder = "./binary_class_labeled_ds"
    save_file(df, folder, filename)


# label ds multclass according to attack based on time
def label_ds_multiclass():
    pass
