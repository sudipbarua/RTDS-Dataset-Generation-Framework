from flow_conversion_labeling import pcap_to_flow, save_file, label_ds_binary_class
import os

def main():
    folder_path = "../pcaps/"
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            # Remove the file extension
            file_name_without_extension = os.path.splitext(file_name)[0]

            # Create the new file name with the desired extension
            new_file_name = file_name_without_extension + ".csv"
            # convert the pcaps to csv files
            pcap_to_flow(file_path, new_file_name)

    file_paths = ["/mnt/d/MS_TUC/My_files/Thesis/MEASURENTS/CD_Scenarios/scenario-12_Gradual-CD_Brutefoce-SSH_Exfil-C2/sc-12_filtered_gradual_CD_bruteforce-SSH_Exfil-C2.pcapng",
                  "/mnt/d/MS_TUC/My_files/Thesis/MEASURENTS/CD_Scenarios/scenario-13_Gradual-CD_Brute-SSH_Efil-DNS/sc-13_filtered_gradual_CD_bruteforce-SSH_Exfil-DNS.pcapng",
                  "/mnt/d/MS_TUC/My_files/Thesis/MEASURENTS/CD_Scenarios/scenario-15_Gradual-CD_Brute-telnet_Efil-FTP/sc-15_filtered_gradual_CD_bruteforce-telnet_Exfil-FTP.pcapng",
                  "/mnt/d/MS_TUC/My_files/Thesis/MEASURENTS/CD_Scenarios/scenario-16_periodic-CD/sc-16_filtered_periodic_CD_without_attack.pcapng"]
    for path in file_paths:
        file_name = os.path.basename(path)
        # Remove the file extension
        file_name_without_extension = os.path.splitext(file_name)[0]

        # Create the new file name with the desired extension
        new_file_name = file_name_without_extension + ".csv"
        pcap_to_flow(path, new_file_name)

if __name__ == '__main__':
    main()
