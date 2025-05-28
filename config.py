from pathlib import Path
import json
from functools import cache

config_file = Path(__file__).parent / 'config.json'

with open(config_file) as f:
    data: dict = json.load(f)

@cache
def get_config(kw: str=None):
    if not kw: return data
    return data[kw]