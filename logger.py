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
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(log_file, 'a', 'utf-8')
handler.setLevel(logging.getLevelNamesMapping().get(get_config("logLevel"), logging.INFO))
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
logger.addHandler(handler)

debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
