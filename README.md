# EEGML
EEGML is a library designed to make developing methods for EEG based machine learning diagnoses easier. You, the researcher should only need to write the business logic, choose the filters, write the featureset extraction code, add some featureset processing, and EEGML handles the rest. It is built on existing libraries like [mne](https://mne.tools/stable/index.html), [pandas](https://pandas.pydata.org/) and [sci-kit learn](https://scikit-learn.org/stable/)

## Why I did this

EEGML was inspired by my work at [Synapto](www.synapto.io). We spent four years trying to find a way to diagnose Alzheimer's using EEG signals and machine learning. While we unfortunately did not make much progress in the field, we did discover a lot about the engineering challenges behind testing several different methods of diagnoses quickly. We tried an exploding number of combinations of filtering methods, features, post processing methods, models, etc. We realized quickly that we were writing the same code over and over and over. We tried writing a centralized pipeline three times, and all three times they required a lot of changes every time we wanted to do something that we did not initially plan for. It was a harder design challenge than I thought. This project is meant to fix that. Lets get into it. 

## How it works

EEGML extracts features from EEG, add class labels (that you provide) and applies cross validation to see how differentiable they are. 

There are four steps as follows

1. Filtering on EEG data
2. Feature Extraction
3. Feature Set processing
4. (Cross) Validation

These steps are all orchestrated in `pipeline.py`. Pipeline consumes three types of transformers that act as blue for what type of filtering, feature extraction, and featureset processing should be done. Each Transformer is instantiated with a name, and an "activity" function that is the business logic of each transformer

### Filter Transfomer
A filter transformer takes an mne raw object as input, and outputs a mne raw object. A pipeline can have several filter transformers so that several filters can be applied.
It can be instantiated as follows: 
```python
def notch_activity(mne_data:mne.io.Raw, config:dict):
    mne_data.notch_filter(numpy.arange(60, 241, 60), filter_length='auto',phase='zero')
    return mne_data
FilterTransformer('notch',notch_activity)
```

### Extract Transformer
An Extract Transformer takes an mne raw object as input and outputs an array of features. It also allows you to define a header function to take in an mne raw object and output a header to describe what each feature means. It becomes the header of the dataframe for the next step.

You can instantiate it as follows:
```python
def getHeader(mne_raw: mne.io.Raw, config:dict):
    return mne_raw.ch_names

# Its a terrible feature
def dumb_extract_activity(mne_data:mne.io.Raw, config:dict):
    dumb_avg_feature = np.average(np.transpose(mne_raw.get_data()))
    return dum_avg_feature

ExtractTransformer('dumb_average',extractFeatures, header_func=getHeader)    
```

### Post Transformer
A Post Transformer takes a dataframe as input and outputs a dataframe. This is for processesing of the featureset like dimensionality reduction, addition of other features from other files, and more. In the end, the dataframe is reappended with the class labels and identifiers, so make sure you do not shuffle the rows.

You can instantiate it as follows:
 ```python


def dumb_post_processing_activity(df:DataFrame, config:dict):
    res = df.mean(axis=1).to_frame()]
    return res
PostTransformer('dumber_average',dumb_post_processing_activity)

 ```

### Validation
The Validator allows validation of different metrics like accuracym, ROC AUC, and more, along with input of what sklearn models you want to use. As long as it has a `.fit` and `.predict` function itll work with the Validator.

You can instantiate it as follows:
```python
pipeline.add_validator(Validator('rf', num_folds=2, clfs=[RandomForestClassifier()]))

```

## Configurations
The pipeline allows for a global configuration thats accessible in any function you want to give it. If you want to encode the pipeline to dynamically choose what frequency to do a low pass filter at, you can put that  config dictionary in the pipeline and call it from the function 

Example code is just in this package under `main.py`. You can just run it and as long as you have the dependent packages it should all work. I need to put in the requirements.txt for this.
