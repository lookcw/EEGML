from EEGML.Patient import Patient
from os import listdir
from os.path import join, isfile
from typing import List

def get_patients_from_folder(foldername:str, classification) -> List[Patient]:
    eeg_filepaths = [join(foldername,f) for f in listdir(foldername) if _is_eeg_file(join(foldername, f))]
    return [get_patient_from_filepath(filepath, classification) for filepath in eeg_filepaths]


def get_patient_from_filepath(filepath:str, classification: int) -> Patient:
    return Patient(filepath, classification)


def _is_eeg_file(filename) -> bool:
    return not filename.endswith('fdt') and isfile(filename)