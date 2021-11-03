import mne

eeg_data = mne.io.read_raw_eeglab('/home/lookcw/Documents/EC013_filt_bch_sreg_wICAd_ChIn_Clean_Rref.set')
print(eeg_data)
print(eeg_data.load_data())

print(eeg_data.load_data())