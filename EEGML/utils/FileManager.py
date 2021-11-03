from os import makedirs, pipe
from os.path import exists, join
from EEGML.ExtractTransformer import FEATURESET_FOLDER
from EEGML.FeatureSet import FeatureSet
from EEGML.FilterTransformer import EEG_DATA_FOLDER

def create_pipeline_folder(pipeline_name):
    if not exists(pipeline_name):
        makedirs(pipeline_name)
        makedirs(join(pipeline_name, EEG_DATA_FOLDER))
        makedirs(join(pipeline_name, FEATURESET_FOLDER))