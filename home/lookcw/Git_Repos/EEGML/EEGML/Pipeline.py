from EEGML.ExtractTransformer import ExtractTransformer
from EEGML.PatientLoader import get_patients
from copy import deepcopy
from EEGML.utils.FileManager import create_folder
from EEGML.FeatureSet import FeatureSet
from os.path import exists

INPUT_FOLDERS_KEY = 'input_folders'


class Pipeline:

    def __init__(self, config, pipeline_name=None):
        self._pipeline_name = pipeline_name
        self._config = config
        self._filter_transformers = []
        self._extract_transformer = None
        self._post_transformers = []
        self._validator = None

    def describe(self):
        """TODO: write json that describes the pipeline well/ can be pretty printed.
        """

    def get_transformer_names(self, transformers):
        return [x.name for x in transformers]
    
    def set_transformer(self, transformer, previous_transformers):
        transformer.set_config(self._config)
        transformer.set_previous_transformers(
            deepcopy(previous_transformers))
        transformer.set_pipeline_name(self._pipeline_name)


    def add_filter_transformer(self, filter_transformer):
        self.set_transformer(filter_transformer,self._filter_transformers)
        self._filter_transformers.append(filter_transformer)

    def add_extract_transformer(self, extract_transformer):
        self.set_transformer(extract_transformer,self._filter_transformers)
        self._extract_transformer = extract_transformer

    def add_post_transformer(self, post_transformer):
        self.set_transformer(post_transformer,self._filter_transformers+[self._extract_transformer])
        self._post_transformers.append(post_transformer)

    def add_filter_transformers(self, filter_transformers):
        for transformer in filter_transformers:
            transformer.set_config(self._config)
        self._filter_transformers += filter_transformers

    def add_post_transformers(self, post_transformers):
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

    def create_data_folder(self):
        create_folder(self._pipeline_name)

    def filter_transform(self, patient):
        # only load
        for (i, filter_transformer) in enumerate(self._filter_transformers):
            if not filter_transformer.is_file_exist(patient):
                print(f'loading {patient.identifier}')
                patient.load_patient()
                patient = filter_transformer.apply(patient)
            elif (i < len(self._filter_transformers) - 1) and \
                    not self._filter_transformers[i+1].is_file_exist(patient) or \
                    i == len(self._filter_transformers) - 1:
                print('loading transformed')
                patient = filter_transformer.load_transformed(patient)
                # patient = patient.load_transformed(filter_transformer)
        return patient

    def should_create_feature_set(self):
        return self._extract_transformer. exists(self._extract_transformer.extract_filepath())

    def get_featureset(self):
        if self._extract_transformer.should_write():
            for (i, input_folder) in enumerate(self._config[INPUT_FOLDERS_KEY]):
                if self._extract_transformer.should_write():
                    patients = get_patients(input_folder)
                    # header can only be set at runtime when the eeg file is read
                    # otherwise array of electrodes is not known
                    is_header_set = False if i == 0 else True
                    header = []
                    # filter and extraction
                    for patient in patients:
                        # set header of extractor (this has to be done at run time unfortunately)
                        if not is_header_set:
                            patient.load_patient()
                            header = self._extract_transformer.get_header(patient.get_raw())
                            featureset = FeatureSet(header)
                            is_header_set = True
                        patient = self.filter_transform(patient)
                        featureset.add_feature(
                            patient._identifier, self._extract_transformer.apply(patient.get_raw()), i)
            if self._extract_transformer.should_write():
                self._extract_transformer.write(featureset)
        else:
            featureset = self._extract_transformer.load_feature_set()
        return featureset

    def post_transform(self, featureset):
        # only load
        for (i, post_transformer) in enumerate(self._post_transformers):
            if not exists(post_transformer.post_filepath()):
                featureset = post_transformer.apply(featureset)
            elif (i < len(self._post_transformers) - 1) and \
                    not exists(self._post_transformers[i+1].post_filepath()) or \
                    i == len(self._post_transformers) - 1:
                featureset = post_transformer.apply(featureset)
        return featureset
    
    def cross_validate(self, featureset):
        self.validator.get_all_metrics(featureset)

    # TODO Add functionality for naming own folders and overwriting when necessary.
    # instead of using hashes
    def run(self):
        self._validate()
        self.create_data_folder()
        featureset = self.get_featureset()
        post_featureset = self.post_transform(featureset)
        self.cross_validate(post_featureset)
        print(post_featureset.df)
