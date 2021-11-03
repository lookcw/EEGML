import hashlib
import json

from EEGML.TransformerInterface import TransformerInterface

def _dict_hash(dictionary: dict) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash

def get_transformer_hash(transformer: TransformerInterface) -> str:
    dhash = _hash_config(transformer.config)
    transformer_names = [t.name for t in transformer.previous_transformers]
    dhash.update(json.dumps(transformer_names).encode())
    return dhash.hexdigest()

def _hash_config(config):
    return _dict_hash(config)    
