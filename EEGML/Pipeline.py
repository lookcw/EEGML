from EEGML.ExtractTransformer import ExtractTransformer
from EEGML.FilterTransformer import FilterTransformer
from EEGML.PostTransformer import PostTransformer
from EEGML.TransformerInterface import TransformerInterface
from EEGML.Patient import Patient
from EEGML.utils.PatientLoader import get_patients_from_folder
from copy import deepcopy
from EEGML.utils.FileManager import create_pipeline_folder
from EEGML.FeatureSet import FeatureSet
from os.path import exists
from typing import List

INPUT_FOLDERS_KEY = 'input_folders'


class Pipeline:

    def __init__(self, config, pipeline_name=None):
        self._pipeline_name = pipeline_name
        self._config = config
        self._filter_transformers:List[FilterTransformer] = []
        self._extract_transformer:ExtractTransformer = None
        self._post_transformers:List[PostTransformer] = []
        self._validator = None

    def describe(self):
        """TODO: write json that describes the pipeline well/ can be pretty printed.
        """

    def get_transformer_names(self, transformers:TransformerInterface):
        return [x.name for x in transformers]
    
    def set_transformer(self, 
                        transformer:TransformerInterface, 
                        previous_transformers:List[TransformerInterface]):
        transformer.set_config(self._config)
        transformer.set_previous_transformers(
            deepcopy(previous_transformers))
        transformer.set_pipeline_name(self._pipeline_name)


    def add_filter_transformer(self, filter_transformer:FilterTransformer):
        self.set_transformer(filter_transformer,self._filter_transformers)
        self._filter_transformers.append(filter_transformer)

    def add_extract_transformer(self, extract_transformer:FilterTransformer):
        self.set_transformer(extract_transformer,self._filter_transformers)
        self._extract_transformer = extract_transformer

    def add_post_transformer(self, post_transformer:PostTransformer):
        self.set_transformer(post_transformer,self._filter_transformers+[self._extract_transformer])
        self._post_transformers.append(post_transformer)

    def add_filter_transformers(self, filter_transformers:List[FilterTransformer]):
        for transformer in filter_transformers:
            transformer.set_config(self._config)
        self._filter_transformers += filter_transformers

    def add_post_transformers(self, post_transformers:List[PostTransformer]):
        for transformer in post_transformers:
            transformer.set_config(self._config)
        self._post_transformers += post_transformers

    def add_validator(self, validator):
        self.validator = validator

    def _validate(self):
        if INPUT_FOLDERS_KEY not in self._config:
            raise KeyError('input_folders not in config')
        if not self._extract_transformer or not isinstance(self._extract_transformer, ExtractTransformer):
            raise Exception("Do not have exactly one extract_transformer")

    def create_pipeline_folder(self):
        create_pipeline_folder(self._pipeline_name)

    def filter_transform(self, patient:Patient):    
        # only load
        for (i, filter_transformer) in enumerate(self._filter_transformers):
            if not filter_transformer.is_transformed_patient_file_exist(patient):
                print(f'loading {patient.get_identifier()}')
                patient.load_patient()
                patient = filter_transformer.apply(patient)
            elif (i < len(self._filter_transformers) - 1) and \
                    not self._filter_transformers[i+1].is_transformed_patient_file_exist(patient) or \
                    i == len(self._filter_transformers) - 1:
                print('loading transformed')
                patient = filter_transformer.get_loaded_transformed_patient(patient)
                # patient = patient.load_transformed(filter_transformer)
        print("printing patient: ")
        print(patient)
        return patient

    def get_featureset(self):
        if not self._extract_transformer.is_featureset_exists():
            for (i, input_folder) in enumerate(self._config[INPUT_FOLDERS_KEY]):
                if self._extract_transformer.should_write():
                    patients = get_patients_from_folder(input_folder, i)
                    print(patients)
                    # header can only be set at runtime when the eeg file is read
                    # otherwise array of electrodes is not known
                    is_header_set = False if i == 0 else True
                    header = []
                    # filter and extraction
                    for patient in patients:
                        # set header of extractor (this has to be done at run time unfortunately)
                        if not is_header_set:
                            patient.load_patient()
                            header = self._extract_transformer.get_header(patient.get_raw(), self._config)
                            featureset = FeatureSet(header)
                            is_header_set = True
                        patient = self.filter_transform(patient)
                        if not patient.get_raw():
                            patient.load_patient()
                        featureset.add_feature(
                            patient._identifier, self._extract_transformer.apply(patient), patient._classification)
        else:
            featureset = self._extract_transformer.load_featureset()
        return featureset

    def post_transform(self, featureset:FeatureSet):
        # only load
        for (i, post_transformer) in enumerate(self._post_transformers):
            if not post_transformer.is_transformed_featureset_exists():
                featureset = post_transformer.apply(featureset)
            elif (i < len(self._post_transformers) - 1) and \
                    post_transformer.is_transformed_featureset_exists() or \
                    i == len(self._post_transformers) - 1:
                featureset = post_transformer.load_transformed_featureset()
            else:
                featureset = post_transformer.load_transformed_featureset()
        return featureset
    
    def cross_validate(self, featureset):
        self.validator.get_all_metrics(featureset)

    # TODO Add functionality for naming own folders and overwriting when necessary.
    # instead of using hashes
    def run(self):
        self._validate()
        self.create_pipeline_folder()
        featureset = self.get_featureset()
        post_featureset = self.post_transform(featureset)
        self.cross_validate(post_featureset)
        print(post_featureset.df)
