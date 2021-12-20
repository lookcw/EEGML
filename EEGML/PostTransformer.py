from os.path import exists, join
from os import makedirs
from EEGML.FeatureSet import FeatureSet
from EEGML.Patient import Patient
from collections.abc import Callable
from EEGML.utils.Hasher import get_transformer_hash
from EEGML.TransformerInterface import TransformerInterface
from typing import List
from pandas import DataFrame


FEATURESET_FOLDER = "FeaturesetData"

class PostTransformer(TransformerInterface):

    def __init__(self,
                 name,
                 activity:Callable,
                 is_write=True):
        self.name = name
        self.activity = activity
        self.is_write = is_write
    
    def get_transformed_featureset_filename(self):
        return self.name + "_" + get_transformer_hash(self) + ".csv"

    def get_transformed_featureset_filepath(self):
        return join(self.pipeline_name,FEATURESET_FOLDER,self.get_transformed_featureset_filename())
    
    def is_transformed_featureset_exists(self):
        return exists(self.get_transformed_featureset_filepath())
    
    def apply(self, feature_set:FeatureSet):
        transformed_featureset = feature_set.map(self.activity, self.config)
        if self.is_write:
            transformed_featureset.write(self.get_transformed_featureset_filepath())
        return feature_set.map(self.activity, self.config)

    def load_transformed_featureset(self):
        return FeatureSet.load_from_file(self.get_transformed_featureset_filepath())
    