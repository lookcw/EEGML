from os.path import exists, join
from os import makedirs
from EEGML.FeatureSet import FeatureSet
from EEGML.Patient import Patient
from collections.abc import Callable
from EEGML.utils.Hasher import get_transformer_hash
from EEGML.TransformerInterface import TransformerInterface
from typing import List
import mne

FEATURESET_FOLDER = "FeaturesetData"

def default_header_func(self, featureset: List[float]):
    return ['col' + i for i in range(1, len(featureset) + 1, 1)]


class ExtractTransformer(TransformerInterface):

    def __init__(self,
                 name,
                 activity:Callable,
                 is_write=True,
                 header_func=default_header_func):
        self.name = name
        self.activity = activity
        self.is_write = is_write
        self.header_func=header_func


    def get_featureset_filename(self):
        return self.name + "_" + get_transformer_hash(self) + ".csv"
    
    def get_header(self, mne_raw: mne.io.Raw, config):
        return self.header_func(mne_raw, config)

    def get_featureset_filepath(self):
        return join(self.get_featureset_folder(), self.get_featureset_filename())

    def get_featureset_folder(self):
        return join(self.pipeline_name,FEATURESET_FOLDER)

    def write(self, featureset: FeatureSet):
        if not exists(self.get_featureset_folder()):
            makedirs(self.get_featureset_folder())
        featureset.write(self.get_featureset_filepath())

    def should_write(self):
        return self.is_write

    def is_featureset_exists(self):
        return exists(self.get_featureset_filepath())

    def apply(self, patient: Patient):
        return self.activity(patient.get_raw(), self.config)

    def load_featureset(self):
        return FeatureSet.load_from_file(self.get_featureset_filepath())