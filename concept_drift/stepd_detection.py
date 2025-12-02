from supervised_concept_drift_detector import SupervisedCDDetector
from menelaus.concept_drift.stepd import STEPD


class STEPDDetection(SupervisedCDDetector):
    def __init__(self, train_df, test_df, classifier, drift_dimarcs, drop_cols=None, load_model=False, model_path=None,
                 check_points=100):
        super().__init__(train_df, test_df, classifier, drift_dimarcs, drop_cols, load_model,
                         model_path, check_points)

    def get_detector(self):
        return STEPD(window_size=250)
