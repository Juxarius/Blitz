import json
from functools import cache
from pathlib import Path

config_file = Path(__file__).parent / 'config.json'
cert_file = Path(__file__).parent.parent / 'certs' / 'blitz.pem'

with open(config_file) as f:
    data = json.load(f)

@cache
def get_config(kw: str=None):
    if not kw: return data
    return data[kw]
