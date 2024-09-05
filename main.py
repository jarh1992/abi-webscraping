# coding: utf8
import argparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from stores.carulla import scraper as carulla_scraper
from stores.exito import scraper as exito_scraper
from stores.jumbo import scraper as jumbo_scraper
from stores.makro import scraper as makro_scraper
from stores.metro import scraper as metro_scraper
from stores.olimpica import scraper as olimpica_scraper
from stores.rappi import scraper as rappi_scraper
from webdriver_manager.chrome import ChromeDriverManager


BASE_DIR = Path(__file__).resolve().parent
stores = {
    # 'carulla': carulla_scraper,
    # 'exito': exito_scraper,
    'jumbo': jumbo_scraper,
    'makro': makro_scraper,
    # 'metro': metro_scraper,
    'olimpica': olimpica_scraper,
    # 'rappi': rappi_scraper,
}
str_stores = "\n".join([f"- {f}" for i, f in enumerate(stores.keys(), start=1)])
description = f"""
Run scraper for all stores:
{str_stores}
"""


def main():
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--store', type=str, help="Store name", default="all")
    args = parser.parse_args()

    in_file = BASE_DIR / "input/in.csv"
    with in_file.open(encoding='cp1252') as f:
        brands = [line.rstrip('\n') for line in f]

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if args.store == "all":
        for store, scraper in stores.items():
            data = scraper(driver, brands)
            file_path = BASE_DIR / f'output/{store}_products_out.txt'
            with file_path.open(mode='w', encoding='utf8') as file:
                file.write(data)
    else:
        if args.store in stores:
            data = stores[args.store](driver, brands)
            file_path = BASE_DIR / f'output/{args.store}_products_out.txt'
            with file_path.open(mode='w', encoding='cp1252') as file:
                file.write(data)
        else:
            ValueError("Invalid store")


if __name__ == "__main__":
    main()
