import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import json
import logging
import sys


load_dotenv(override=True)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR.as_posix())


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

# Set vars to send files to azure blob storage
sas_url = os.getenv('STORAGE_SAS_URL')
dest_folder = os.getenv('STORAGE_DEST_FOLDER')
dest_hist_folder = os.getenv('STORAGE_DEST_FOLDER_HIST')
output_folder = BASE_DIR / 'output'
