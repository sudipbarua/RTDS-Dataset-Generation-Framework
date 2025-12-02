"""
As the general drift detector DDM is used here
"""
import os
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import pickle
from datetime import datetime
import menelaus.concept_drift.ddm as ddm
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score, confusion_matrix
from flow_conversion_labeling import save_file
import time

def get_drift_dimarcs(df, drift_segments):
    """
    This function returns the approximate indexes of simulated drift points.
    Prerequisites: The dataset must have equal time spans of drift and no drift segments (e.g.: 5min drift, 5min without drift...)
    In this case, we split the df according to "drift_segments" and return the index of the first datapoint
    """
    col_key = 'bidirectional_first_seen_ms'
    split_size = (max(df[col_key]) - min(df[col_key])) / drift_segments
    start_time = min(df[col_key])
    drift_dimarcs = []
    for i in range(drift_segments):
        end_time = start_time + split_size
        df_win = df[(df[col_key] >= start_time) & (df[col_key] <= end_time)]
        drift_dimarcs.append(df_win['id'].iloc[0])
        start_time = end_time
    return drift_dimarcs


def plot(result_df, drift_dimarcs, detector_name, name=None):
    plt.figure(figsize=(20, 6))
    # plt.scatter("index", "F1", data=result_df, label="F1 Score", color='red')
    # plt.scatter("index", "precision", data=result_df, label="Precision Score", color='m')
    # plt.scatter("index", "recall", data=result_df, label="Recall Score", color='y')

    # Plotting lines with missing values of performance metrics
    xs = result_df["index"].to_numpy()
    # xs = result_df["time"].to_numpy()
    f1_series = np.array(result_df["F1"].to_numpy()).astype(np.double)
    pr_series = np.array(result_df["precision"].to_numpy()).astype(np.double)
    tnr_series = np.array(result_df["TNR"].to_numpy()).astype(np.double)
    f1_mask = np.isfinite(f1_series)
    recall_series = np.array(result_df["recall"].to_numpy()).astype(np.double)
    pr_mask = np.isfinite(pr_series)
    tnr_mask = np.isfinite(tnr_series)
    recall_mask = np.isfinite(recall_series)
    # plt.plot(xs[f1_mask], f1_series[f1_mask], label="F1 Score", color='red', linestyle='-', marker='o')
    # plt.plot(xs[pr_mask], pr_series[pr_mask], label="Precision Score", color='m', linestyle='-', marker='o')
    plt.plot(xs[tnr_mask], tnr_series[tnr_mask], label="TNR Score", color='red', linestyle='-', marker='o')
    # plt.plot(xs[recall_mask], recall_series[recall_mask], label="Recall Score", color='y', linestyle='-', marker='o')

    plt.grid(False, axis="x")
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.title(f"{detector_name} Results: Performance metrics", fontsize=22)
    plt.ylabel("Values", fontsize=18)
    plt.xlabel("Number of Samples", fontsize=18)
    ylims = [0.7, 1.1]
    plt.ylim(ylims)

    # Draw orange lines that indicate where warnings of drift were provided
    plt.vlines(
        x=result_df.loc[result_df["drift_detected"] == "warning"]["index"],
        ymin=ylims[0],
        ymax=ylims[1],
        label="Warning",
        color="orange",
        alpha=0.2,
    )

    # Draw red lines that indicate where drift was detected
    plt.vlines(
        x=result_df.loc[result_df["drift_detected"] == "drift"]["index"],
        ymin=ylims[0],
        ymax=ylims[1],
        label="Drift Detected",
        color="red",
        alpha=0.5
    )

    # Draw Black lines indicating simulated drift points
    for id in drift_dimarcs:
        if id > 0:
            plt.vlines(
                x=result_df.loc[result_df["index"] == int(id)]["index"],
                ymin=ylims[0],
                ymax=ylims[1],
                label="Simulated drift points",
                color="k",
                linestyles="dotted"
            )
    # save the figure before showing: once being showed, it will be cleared/removed/deleted
    fig = plt.gcf()
    plt.legend()
    plt.show()
    # Save figure/plot in ./plots folder
    is_exist = os.path.exists("./plots")
    if not is_exist:
        os.mkdir("./plots")
    fig.savefig(f"./plots/{detector_name}_drift_status_vs_performance_{name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png", dpi=150)


class SupervisedCDDetector:
    def __init__(self, train_df, test_df, classifier, drift_dimarcs, drop_cols=None, load_model=False, model_path=None,
                 check_points=100):
        self.drop_cols = drop_cols
        self.train_df = train_df
        self.test_df = test_df
        self.clf = classifier
        self.load_model = load_model
        self.model_path = model_path
        self.drift_dimarcs = drift_dimarcs
        # amount of recent data points to check the performance metrics and DDM reset threshold
        self.check_points = check_points

    def clean_scale_ds(self, df):
        df = df.drop(columns=self.drop_cols, axis=1, errors='ignore')  # drop irrelevant columns
        df = df.dropna()  # drop rows with nans
        cols = df.columns
        scaler = MinMaxScaler()
        df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=cols)
        return df_scaled

    def train_model(self):
        print("-----------------------Training ML model-------------------------------")
        self.train_df = self.clean_scale_ds(self.train_df)
        x_train = self.train_df.drop(['Label'], axis=1)
        y_train = self.train_df['Label']
        self.clf.fit(x_train, y_train)
        self.save_model()

    def save_model(self):
        print("-----------------------Saving ML model-------------------------------")
        if self.model_path is None:
            self.model_path = "./saved_models"
        is_exist = os.path.exists(self.model_path)
        if not is_exist:
            os.mkdir(self.model_path)
        # get the classifier name
        model_name = str(type(self.clf)).split(".")[-1][:-2]
        # dt = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # save model with timestamp
        with open(f'{self.model_path}/{model_name}.pkl', 'wb') as f:
            pickle.dump(self.clf, f)

    # DDM detector getter
    def get_detector(self):
        return ddm.DDM(n_threshold=self.check_points, warning_scale=2, drift_scale=3)

    def detection(self):
        if self.load_model:
            with open(self.model_path, 'rb') as f:
                self.clf = pickle.load(f)
        else:
            self.train_model()
        # drift detector object
        detector = self.get_detector()
        detector_name = str(type(detector)).split(".")[-1][:-2]

        self.result_df = pd.DataFrame(columns=["index", "time", "y_true", "y_pred", "drift_detected",
                                               "precision", "recall", "F1", "TNR"])
        self.test_df = self.clean_scale_ds(self.test_df)#.sample(n=1000))
        y_pred_accumulated, y_true_accumulated = [], []
        print("-----------------------Initiating Drift Detection-------------------------------")
        for i in range(len(self.test_df)):
            x_test = self.test_df.iloc[[i]]
            x_test = x_test.drop(['Label'], axis=1)
            y_pred = int(self.clf.predict(x_test))
            y_true = int(self.test_df.loc[[i], "Label"])
            # accumulate the predicted and true labels for performance metric calculation
            y_pred_accumulated.append(y_pred)
            y_true_accumulated.append(y_true)
            # get the date-time of the flow record
            # date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x_test['bidirectional_first_seen_ms']))
            date_time = 1
            # update drift detector: detect drift
            detector.update(y_true, y_pred)
            # calculate metrics: precision, recall, F1 scores of last n value equal to number of DDM check points
            if i % self.check_points == 0 or detector.drift_state == "warning" or detector.drift_state == "drift":
                print(f"-----------------------Measuring performance metrics iter: {i}-------------------------------")
                pr = precision_score(y_true_accumulated[-self.check_points:], y_pred_accumulated[-self.check_points:], zero_division=1)
                recall = recall_score(y_true_accumulated[-self.check_points:], y_pred_accumulated[-self.check_points:], zero_division=1)
                f1 = f1_score(y_true_accumulated[-self.check_points:], y_pred_accumulated[-self.check_points:], zero_division=1)
                # to calculate, tnr we need to set the positive label to the other class
                tnr = recall_score(y_true_accumulated[-self.check_points:], y_pred_accumulated[-self.check_points:],
                                   zero_division=1, pos_label=0)
            else:
                pr, recall, f1, tnr = None, None, None, None
            self.result_df.loc[i] = [i, date_time, y_true, y_pred, detector.drift_state, pr, recall, f1, tnr]
        # save the results in "./result" folder
        save_file(self.result_df, "./result", f"{detector_name}_n-{self.check_points}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")
        print("-----------------------------------Plotting Results-------------------------------------")
        plot(self.result_df, self.drift_dimarcs, detector_name, name=f"n-{self.check_points}")
        print("-----------------------Process Finished-------------------------------")
        