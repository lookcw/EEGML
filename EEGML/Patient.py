import mne
from EEGML.utils.EEGLoader import load_eeg, filepath_to_fif


class Patient():

    def __init__(self, filepath, classification):
        self._classification = classification
        self._filepath = filepath
        self._filename = filepath.split('/')[-1]
        self._identifier = filepath.split('/')[-1].split('.')[0]
        self._mne_raw = None

    
    def load_patient(self):
        self._mne_raw = load_eeg(self._filepath)
        self._mne_raw.load_data()
    
    def get_filename(self):
        return self._filename
    
    def get_fif_filename(self):
        return filepath_to_fif(self._filename)

    def get_identifier(self):
        return self._identifier
    
    def get_raw(self):
        return self._mne_raw
    
    def set_raw(self, mne_raw):
        self._mne_raw = mne_raw
    
    def get_filepath(self):
        return self._filepath
    

    def write_eeg_to_filepath(self, filepath:str) -> None:
        print(filepath_to_fif)
        self._mne_raw.save(filepath_to_fif(filepath))


    def clone(self):
        patient_clone = Patient(self._filepath,self._classification)
        patient_clone._mne_raw = self._mne_raw
        return patient_clone

