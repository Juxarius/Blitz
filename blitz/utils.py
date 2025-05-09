import json
from functools import cache
from pathlib import Path
import logging
from telegram import Update

from .models import MongoHandler

config_file = Path(__file__).parent / 'config.json'

with open(config_file) as f:
    data: dict = json.load(f)

@cache
def get_config(kw: str=None):
    if not kw: return data
    return data[kw]

logger = logging.getLogger("blitz")
logger.setLevel(logging.getLevelNamesMapping().get(get_config("loggingLevel"), logging.INFO))

mongo_handler = MongoHandler(
    mongo_uri=f"mongodb://{get_config('mongoDbHostname')}:{get_config('mongoDbPort')}",
    db_name="blitz",
    collection_name="logs"
)
print("DB successfully connected!")
logger.addHandler(mongo_handler)

def log(log_level: int, msg: str, command=None, payload=None) -> None:
    logger.log(log_level, msg, extra={"command": command, "payload": payload})

debug = lambda msg, command=None, payload=None: log(logging.DEBUG, msg, command, payload)
info = lambda msg, command=None, payload=None: log(logging.INFO, msg, command, payload)
warning = lambda msg, command=None, payload=None: log(logging.WARNING, msg, command, payload)
error = lambda msg, command=None, payload=None: log(logging.ERROR, msg, command, payload)

def update_identifier(update: Update) -> str:
    return f"{update.message.chat.full_name} ({update.message.chat.id})"

up_id = update_identifier
