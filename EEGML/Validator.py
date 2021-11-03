# from EEGML.ExtractTransformer import ExtractTransformer
# from EEGML.utils.PatientLoader import get_patients_from_filepath
# from EEGML.utils.FileManager import create_folder
from EEGML.FeatureSet import FeatureSet
# from os.path import exists
from sklearn.model_selection import KFold
import sklearn.metrics
from sklearn.metrics import get_scorer
from sklearn.base import BaseEstimator
from typing import List


INPUT_FOLDERS_KEY = 'input_folders'


def default_kfold_validator(num_folds):
    return KFold(n_splits=num_folds, shuffle=True, random_state=1)


class Validator:

    # https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter
    def __init__(self, name,
                 clfs:List[BaseEstimator]=[], 
                 metric_names=['accuracy','roc_auc'], 
                 metric_funcs = [],
                 num_folds = 4,
                 k_fold=None) -> None:
        if not clfs:
            raise ValueError("need to pass in a list of classifiers to validator")
        self.clfs = clfs
        self.metric_names = metric_names
        self.metric_funcs = metric_funcs
        self.num_folds = num_folds
        if not k_fold:
            self.k_fold = default_kfold_validator(num_folds)
        self._set_metric_funcs()
    
    def _set_metric_funcs(self):
        self.metric_funcs += [
            get_scorer(name) for name in self.metric_names
            ]


    def _get_preds(self, clf, feature_set:FeatureSet, num_folds, kf):
        X = feature_set.get_x()
        Y = feature_set.get_y()
        all_y_pred = []
        all_y_true = []
        for train_index, test_index in kf.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test =Y.iloc[train_index], Y.iloc[test_index]
            clf.fit(X_train, y_train)
            print(X_train)
            print(y_train)
            y_pred = clf.predict(X_test)
            all_y_true += list(y_test)
            all_y_pred += list(y_pred)
        return (all_y_true, all_y_pred)

    def _get_metrics(self, clf, feature_set):
        (y_true, y_pred) = self._get_preds(clf,feature_set, self.num_folds, self.k_fold)
        print(self.metric_funcs)
        for metric_func in self.metric_funcs:
            print(metric_func.__class__.__name__ + " : " + str(metric_func._score_func(y_true, y_pred)))
        
    def get_all_metrics(self, feature_set):
        for clf in self.clfs:
            self._get_metrics(clf, feature_set)
