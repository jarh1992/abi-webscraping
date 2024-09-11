import json
from datetime import datetime
from pathlib import Path
import sys
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR.as_posix())
import logging


# Define the log file path
LOGS_DIR = BASE_DIR / 'logs'
LOG_FILE = LOGS_DIR / datetime.today().strftime("app_%Y%m%d.log")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Define the logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),    # Log to file
        logging.StreamHandler()           # Log to console
    ]
)

# Create a logger object that can be imported and used in other files
logger = logging.getLogger(__name__)
