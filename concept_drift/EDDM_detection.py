from supervised_concept_drift_detector import SupervisedCDDetector
import menelaus.concept_drift.eddm as eddm


class EDDMDetection(SupervisedCDDetector):
    def __init__(self, train_df, test_df, classifier, drift_dimarcs, drop_cols=None, load_model=False, model_path=None,
                 check_points=100):
        super().__init__(train_df, test_df, classifier, drift_dimarcs, drop_cols, load_model,
                         model_path, check_points)

    def get_detector(self):
        return eddm.EDDM(n_threshold=self.check_points, warning_thresh=0.7, drift_thresh=0.5)
