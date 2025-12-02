from flow_conversion_labeling import pcap_to_flow, save_file, label_ds_binary_class, clean_and_scale
import os
import pandas as pd

def main():
    folder_path = "flow_ds"
    attack_victim_ips = ['10.11.2.189', '10.11.2.74', '10.11.2.50', '10.11.1.187',
                         '10.11.2.63', '10.11.1.48', '10.11.2.199', '10.11.1.216', '10.11.2.142']
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # read the file
            file_path = os.path.join(root, file)
            df = pd.read_csv(file_path, index_col=0)
            file_name = os.path.basename(file)
            # label and save datasets
            new_file_name = 'testlabeled_' + file_name
            label_ds_binary_class(df, attack_victim_ips, new_file_name)
            # scale and save datasets
            ignored_columns = ['id', 'expiration_id', 'src_ip', 'src_mac', 'src_oui', 'src_port', 'dst_ip', 'dst_mac',
                               'dst_oui', 'dst_port', 'protocol', 'ip_version', 'vlan_id', 'tunnel_id',
                               'bidirectional_first_seen_ms', 'bidirectional_last_seen_ms', 'src2dst_first_seen_ms',
                               'src2dst_last_seen_ms', 'dst2src_first_seen_ms', 'dst2src_last_seen_ms']
            new_file_name = 'scaled_' + new_file_name
            clean_and_scale(df, ignored_columns, new_file_name)

    print('---------end-----------')


if __name__ == '__main__':
    main()
