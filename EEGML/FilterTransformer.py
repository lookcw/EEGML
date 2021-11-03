from os.path import exists, join
from os import makedirs, mkdir
from EEGML.Patient import Patient
from collections.abc import Callable
from EEGML.utils.Hasher import get_transformer_hash
from EEGML.TransformerInterface import TransformerInterface
from EEGML.utils.EEGLoader import load_eeg

EEG_DATA_FOLDER = "EEGData"


class FilterTransformer(TransformerInterface):

    def __init__(self, name, activity: Callable, is_write=False):
        self.name = name
        self.activity = activity
        self.is_write = is_write

    def is_transformed_patient_file_exist(self, patient: Patient) -> bool:
        return exists(self.get_transformed_patient_filepath(patient))

    def apply(self, patient: Patient) -> None:
        applied_raw = self.activity(patient.get_raw(), self.config)
        patient.set_raw(applied_raw)
        if self.is_write and not self.is_transformed_patient_file_exist(patient):
            self.write_transformed_patient(patient)
        return patient

    def get_folder_name(self) -> str:
        return self.name + "_" + get_transformer_hash(self)
    
    def get_folder_path(self) -> str:
        return join(self.pipeline_name, EEG_DATA_FOLDER, self.get_folder_name())
    
    def get_transformed_patient_filepath(self, patient:Patient) -> str:
        return join(self.get_folder_path(), patient.get_fif_filename())
    
    def get_loaded_transformed_patient(self, patient:Patient) -> Patient:
        loaded_patient = Patient(patient._filepath, patient._classification)
        # loaded_patient._mne_raw = load_eeg(self.get_transformed_patient_filepath(patient))
        return loaded_patient
    
    def write_transformed_patient(self, patient:Patient) -> None:
        if not exists(self.get_folder_path()):
            makedirs(self.get_folder_path())
        patient.write_eeg_to_filepath(self.get_transformed_patient_filepath(patient))