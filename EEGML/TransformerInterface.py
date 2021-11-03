from abc import ABCMeta, abstractmethod

class TransformerInterface:

    def set_config(self, config: dict):
        self.config = config

    def set_previous_transformers(self, previous_transformers):
        self.previous_transformers = previous_transformers
    
    def set_pipeline_name(self, pipeline_name):
        self.pipeline_name = pipeline_name