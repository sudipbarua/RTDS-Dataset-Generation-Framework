import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime


# reading data from flow dataset
df = pd.read_csv("./binary_class_labeled_ds/labeled_sc-16_filtered_periodic_CD_without_attack.csv", index_col=0)
sc_name = "sc-16"

df = df.sort_values(by='bidirectional_first_seen_ms', ascending=True)
df['bidirectional_first_seen_ms'] = pd.to_datetime(df['bidirectional_first_seen_ms'], unit='ms')
mask_normal = df["Label"] == 0
mask_abnormal = df["Label"] == 1
# x_normal = df[mask_normal]["id"]
# x_abnormal = df[mask_abnormal]["id"]
x_normal = df[mask_normal]["bidirectional_first_seen_ms"]
x_abnormal = df[mask_abnormal]["bidirectional_first_seen_ms"]
# Create subplots vertically stacked
fig, axs = plt.subplots(4, 1, figsize=(15, 15), sharex=True)

# Plot data on each subplot
axs[0].plot(x_normal, df[mask_normal]['bidirectional_packets'], color='b', label='Normal')
axs[0].plot(x_abnormal, df[mask_abnormal]['bidirectional_packets'], color='r', label='Abnormal')
# axs[0].plot(x, df['bidirectional_packets'], color='b', label='Normal')
axs[0].set_ylabel('Number of Packets')
axs[0].legend()

axs[1].plot(x_normal, df[mask_normal]["bidirectional_bytes"], color='g', label='Normal')
axs[1].plot(x_abnormal, df[mask_abnormal]["bidirectional_bytes"], color='r', label='Abnormal')
axs[1].set_ylabel('Number of Bytes')
axs[1].legend()

axs[2].plot(x_normal, df[mask_normal]["bidirectional_mean_ps"], color='b', label='Normal')
axs[2].plot(x_abnormal, df[mask_abnormal]["bidirectional_mean_ps"], color='r', label='Abnormal')
axs[2].set_ylabel('Packet Size')
axs[2].legend()

axs[3].plot(x_normal, df[mask_normal]["bidirectional_mean_piat_ms"], color='g', label='Normal')
axs[3].plot(x_abnormal, df[mask_abnormal]["bidirectional_mean_piat_ms"], color='r', label='Abnormal')
axs[3].set_xlabel('Timestamp')
axs[3].set_ylabel('IAT')
axs[3].legend()

# Adjust spacing between subplots
plt.tight_layout()

# save the figure before showing: once being showed, it will be cleared/removed/deleted
#fig = plt.gcf()

# Show the plot
plt.show()

fig.savefig(f"./plots/{sc_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png", dpi=150)
