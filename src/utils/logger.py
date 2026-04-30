import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "portfolio_risk.log")

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class SafeTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Skip rollover if Windows has the log file locked elsewhere."""

    def doRollover(self):
        try:
            super().doRollover()
        except PermissionError:
            self.rolloverAt = self.computeRollover(int(datetime.now().timestamp()))


file_handler = SafeTimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

def get_logger(name):
    """Get a logger instance."""
    return logging.getLogger(name)

