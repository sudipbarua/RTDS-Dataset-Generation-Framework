import pandas as pd
from supervised_concept_drift_detector import get_drift_dimarcs, SupervisedCDDetector, plot
from sklearn.ensemble import RandomForestClassifier
from EDDM_detection import EDDMDetection
from stepd_detection import STEPDDetection

def main():
    # # generate the .csv files from pcaps
    # pcap_to_flow("../pcaps/woCD_mixtr.pcap", "train_df.csv")
    # pcap_to_flow("../pcaps/withCD2-2_mixtr.pcap", "test_df2x.csv")
    # pcap_to_flow("../pcaps/withCD4_mixtr.pcap", "test_df4x.csv")
    # pcap_to_flow("../pcaps/withCD6_mixtr.pcap", "test_df6x.csv")
    # # get the train and test datasets
    # train_df = pd.read_csv("./flow_ds/train_df.csv", index_col=0)
    # test_df2x = pd.read_csv("./flow_ds/test_df2x.csv", index_col=0)
    # test_df4x = pd.read_csv("./flow_ds/test_df4x.csv", index_col=0)
    # test_df6x = pd.read_csv("./flow_ds/test_df6x.csv", index_col=0)
    # # labelling and saving datasets
    # label_ds(train_df, ['10.10.51.17'], "train_df_labeled.csv")
    # label_ds(test_df2x, ['10.10.51.17'], "test_df2x_labeled.csv")
    # label_ds(test_df4x, ['10.10.51.17'], "test_df4x_labeled.csv")
    # label_ds(test_df6x, ['10.10.51.17'], "test_df6x_labeled.csv")
    train_df1 = pd.read_csv("./binary_class_labeled_ds/labeled_sc-1_filtered_Normal_bruteforce_exfiltrate-C2-http.csv", index_col=0)
    train_df2 = pd.read_csv("./binary_class_labeled_ds/labeled_sc-2_filtered_Normal_brute-ssh_exfil-DNS.csv", index_col=0)
    train_df3 = pd.read_csv("./binary_class_labeled_ds/labeled_sc-3_filtered_Normal_brute-ssh_exfil-SCP.csv", index_col=0)
    test_df1 = pd.read_csv("./binary_class_labeled_ds/labeled_sc-12_filtered_gradual_CD_bruteforce-SSH_Exfil-C2.csv", index_col=0)
    test_df2 = pd.read_csv("./binary_class_labeled_ds/labeled_sc-13_filtered_gradual_CD_bruteforce-SSH_Exfil-DNS.csv", index_col=0)
    test_df3 = pd.read_csv("./binary_class_labeled_ds/labeled_sc-15_filtered_gradual_CD_bruteforce-telnet_Exfil-FTP.csv", index_col=0)
    drop_cols = ['id', 'expiration_id', 'src_ip', 'src_mac', 'src_oui', 'src_port', 'dst_ip', 'dst_mac',
                 'dst_oui', 'dst_port', 'protocol', 'ip_version', 'vlan_id', 'tunnel_id',
                 'bidirectional_first_seen_ms', 'bidirectional_last_seen_ms', 'src2dst_first_seen_ms',
                 'src2dst_last_seen_ms', 'dst2src_first_seen_ms', 'dst2src_last_seen_ms']
    rf_model = RandomForestClassifier()
    list_id_sim_drift_dimarcs1 = get_drift_dimarcs(test_df1, 3)  # list of simulated drift points
    list_id_sim_drift_dimarcs2 = get_drift_dimarcs(test_df2, 3)  # list of simulated drift points
    list_id_sim_drift_dimarcs3 = get_drift_dimarcs(test_df3, 3)  # list of simulated drift points
    # test_df_norm = test_df2x.loc[test_df2x['Label'] == 0]

    detector_1 = STEPDDetection(train_df=train_df1, test_df=test_df1, classifier=rf_model, drop_cols=drop_cols,
                                          model_path="./saved_models", drift_dimarcs=list_id_sim_drift_dimarcs1,
                                          check_points=100)
    detector_2 = STEPDDetection(train_df=train_df2, test_df=test_df2, classifier=rf_model, drop_cols=drop_cols,
                                          model_path="./saved_models", drift_dimarcs=list_id_sim_drift_dimarcs2,
                                          check_points=100)
    detector_3 = STEPDDetection(train_df=train_df3, test_df=test_df3, classifier=rf_model, drop_cols=drop_cols,
                                          model_path="./saved_models", drift_dimarcs=list_id_sim_drift_dimarcs3,
                                          check_points=100)
    detector_1.detection()
    detector_2.detection()
    detector_3.detection()
    # rdf = pd.read_csv("./result/n-30_2023-01-04_15-37-38.csv", index_col=0)
    # plot(rdf, list_id_sim_drift_dimarcs1)


if __name__ == '__main__':
    main()
