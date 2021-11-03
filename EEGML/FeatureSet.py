import pandas as pd

CLASS_IDENTIFIER = 'class'
INSTANCE_IDENTIFIER = 'identifier'

class FeatureSet:



    def __init__(self, header = None, df = None):
        self.extra_cols = [INSTANCE_IDENTIFIER, CLASS_IDENTIFIER]
        if not header and not isinstance(df, pd.DataFrame):
            raise ValueError('Either header or df must be populated in constructor')
        if header:
            self.header = [INSTANCE_IDENTIFIER] + header + [CLASS_IDENTIFIER]
            self.df = pd.DataFrame(columns=self.header)
        else:
            self.df = df
            self.header = df.columns.values
    
    def add_feature(self, identifier, feature, class_value):
        if len(feature) != len(self.df.columns) - len(self.extra_cols):
            raise ValueError('number of input features does not match featureset')
        series = pd.Series([identifier] + feature + [class_value], index=self.header)
        self.df = self.df.append(series, ignore_index=True)
 
    def __str__(self):
        return self.df.to_string()

    def map(self, df_function, config):
        feature_df, extra_cols = self.get_feature_df(), self._get_extra_cols()
        applied_df = df_function(feature_df, config)
        if len(applied_df) != len(feature_df):
            raise ValueError('different number of instances before ' 
                f'and after map on {df_function.__name__}')
        return FeatureSet(df = pd.concat([extra_cols,applied_df],axis=1))

    def get_feature_df(self):
        return self.df.drop(columns=self.extra_cols)

    def get_x(self):
        return self.df.drop(columns=self.extra_cols + [CLASS_IDENTIFIER])

    def get_y(self):
        return self.df[CLASS_IDENTIFIER]

    def _get_extra_cols(self):
        return self.df[self.extra_cols]
    
    def write(self, filepath):
        self.df.to_csv(filepath, index=False)

    def get_num_instances(self):
        return len(self.df)
    
    def get_num_features(self):
        return len(self.df.columns) - len(self.extra_cols)

    @staticmethod
    def load_from_file(filepath):
        return FeatureSet(df=pd.read_csv(filepath))
