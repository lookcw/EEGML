from EEGML.PostTransformer import PostTransformer
from EEGML.Pipeline import Pipeline
from EEGML.FilterTransformer import FilterTransformer
from EEGML.ExtractTransformer import ExtractTransformer
from EEGML.Validator import Validator
import numpy as np
from testFunctions.domFreq_features import getHeader, extractFeatures
import mne
from testFunctions.ICA_function import decompose
from sklearn.ensemble import RandomForestClassifier


def notch_activity(mne_data:mne.io.Raw, config:dict):
    print("running notch activity")
    mne_data.notch_filter(np.arange(60, 241, 60), filter_length='auto',
                     phase='zero')
    return mne_data
    # mne.viz.plot_raw_psd(mne_data)

def low_pass_activity(mne_data:mne.io.Raw, config:dict):
    print("running low pass activity")
    mne_data.filter(l_freq=config['l_freq'], h_freq=None)
    # mne.viz.plot_raw_psd(mne_data)
    return mne_data

config = {'input_folders': ['sample_neg','sample_pos'],
        'l_freq':10,
        'lower_bound': 4,
        'upper_bound': 14,
        'region_schema': {
        'F': [0, 1, 2, 3, 4, 5, 6, 7, 30, 31, 32, 33, 34, 35, 36, 37, 70, 71, 
              72, 94, 95, 96, 97],
        'LT': [8, 12, 17, 41, 56, 58, 62, 64, 77, 81, 98, 102, 103, 108, 112],
        'C': [9, 10, 13, 14, 15, 38, 39, 40, 42, 43, 73, 74, 75, 78, 79, 99, 100, 104, 105],
        'RT': [11, 16, 20, 44, 57, 59, 63, 65, 76, 80, 84, 101, 106, 107, 111, 115],
        'P': [18, 19, 21, 22, 23, 24, 25, 26, 45, 46, 47, 48, 49, 50, 51, 52, 
              53, 54, 55, 60, 61, 68, 69, 82, 83, 85, 86, 87, 88, 89, 90, 109, 
              110, 113, 114, 116, 117, 118, 119, 121, 122],
        'O': [27, 28, 29, 66, 67, 91, 92, 93, 120, 123, 124, 125]}}
pipeline = Pipeline(config, pipeline_name='test_run')

pipeline.add_filter_transformer(FilterTransformer('notch',notch_activity, is_write=True))
pipeline.add_filter_transformer(FilterTransformer('low_pass',low_pass_activity, is_write=True))
pipeline.add_extract_transformer(ExtractTransformer('dom_freq',extractFeatures, header_func=getHeader))
pipeline.add_post_transformer(PostTransformer('ICA',decompose,is_write=True))
pipeline.add_validator(Validator('rf', num_folds=2, clfs=[RandomForestClassifier()]))
pipeline.run()

