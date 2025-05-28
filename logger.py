import logging
from pathlib import Path
import datetime as dt

from config import get_config

log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / "blitz.log"

# need to rotate logs, if file already exists, rename it with a timestamp then create a new file
if log_file.exists():
    log_file.rename(log_dir / f"blitz-{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
    log_file = log_dir / "blitz.log"

logger = logging.getLogger("blitz")
logger.setLevel(logging.getLevelNamesMapping().get(get_config("logLevel"), logging.INFO))
logger.addHandler(logging.FileHandler(log_file))

def log(log_level: int, msg: str, command=None, payload=None) -> None:
    logger.log(log_level, msg, extra={"command": command, "payload": payload})

debug = lambda msg, command=None, payload=None: log(logging.DEBUG, msg, command, payload)
info = lambda msg, command=None, payload=None: log(logging.INFO, msg, command, payload)
warning = lambda msg, command=None, payload=None: log(logging.WARNING, msg, command, payload)
error = lambda msg, command=None, payload=None: log(logging.ERROR, msg, command, payload)
