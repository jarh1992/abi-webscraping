import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import json
import logging
import sys
from src.models.models import Store
from src.scrapers.carulla import scraper as carulla_scraper
from src.scrapers.exito import scraper as exito_scraper
from src.scrapers.jumbo import scraper as jumbo_scraper
from src.scrapers.makro import scraper as makro_scraper
from src.scrapers.metro import scraper as metro_scraper
from src.scrapers.olimpica import scraper as olimpica_scraper
from src.scrapers.rappi import scraper as rappi_scraper


load_dotenv(override=True)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR.as_posix())


# Define the log file path
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
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


def set_scraper(store_name: str):
    if store_name == 'carulla':
        return carulla_scraper
    elif store_name == 'exito':
        return exito_scraper
    elif store_name == 'jumbo':
        return jumbo_scraper
    elif store_name == 'makro':
        return makro_scraper
    elif store_name == 'metro':
        return metro_scraper
    elif store_name == 'olimpica':
        return olimpica_scraper
    elif store_name == 'rappi':
        return rappi_scraper


# Set vars to send files to azure blob storage
sas_url = os.getenv('STORAGE_SAS_URL')
dest_folder = os.getenv('STORAGE_DEST_FOLDER')
dest_hist_folder = os.getenv('STORAGE_DEST_FOLDER_HIST')
output_folder = BASE_DIR / 'output'
output_folder.mkdir(parents=True, exist_ok=True)
input_path = BASE_DIR / "input/input.json"
logger.info(f"Loaded input file.")
with input_path.open(encoding='utf8') as f:
    input = json.load(f)
    STORES = dict()
    STORES_DATA = input['STORES']
    for k, v in STORES_DATA.items():
        STORES[k.lower()] = Store(
            name=k.lower(),
            url=v['URL'],
            locations=v['LOCATIONS'],
            scraper=set_scraper(k.lower())
        )
    BRANDS = input['BRANDS']
