import mne

def load_eeg(filepath:str) -> mne.io.Raw:
    if filepath.endswith('.set'):
        return mne.io.read_raw_eeglab(filepath)
    elif filepath.endswith('.fif'):
        return mne.io.read_raw_fif(filepath)
    else:
        raise AssertionError("unsupported file type")

def filepath_to_fif(filepath:str) -> str:
     return ''.join(filepath.split('.')[:-1]) + '.fif'