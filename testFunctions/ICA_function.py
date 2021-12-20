import pandas as pd
from pandas import DataFrame
import argparse
from scipy import signal
import numpy as np
from sklearn.decomposition import FastICA
import sys


def decompose(df:DataFrame, config:dict):
    pre_ica = df.values
    print(config['region_schema'])
    schema_header = sorted(config['region_schema'].keys())
    post_ica = np.zeros((pre_ica.shape[0], len(schema_header)))
    for (i, region) in enumerate(schema_header):
        region_columns = pre_ica[:, config['region_schema'][region]]
        ica = FastICA(n_components=1)
        post_ica[:, i] = ica.fit_transform(region_columns)[:, 0]

    ica_df = pd.DataFrame(data=post_ica, columns=schema_header)
    return ica_df