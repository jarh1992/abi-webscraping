import time
from datetime import datetime

from settings.settings import (
    logger,
    sas_url,
    dest_folder,
    dest_hist_folder,
    output_folder,
    STORES,
    BRANDS
)
from src.utils import upload_blob_file, add_sku
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def run_scraping(driver, st):
    st_locs = st.locations
    data = []
    for locs in st_locs.items():
        data += st.scraper(driver, locs, BRANDS, st)
    # test
    # with open(output_folder / f'{st.name}_products_cp.csv', 'r', encoding='utf8') as file:
    #     data = file.read().splitlines()
    data = add_sku(data)
    data.to_csv(output_folder / DT.strftime(f'{st.name}_products_%Y%m%d.csv'), index=False, sep='|')
    data.to_csv(output_folder / f'{st.name}_products.csv', index=False, sep='|')
    logger.info(f"Scraping completed - {st.name} Files created")


def main():
    str_stores = "\n".join([f"- {f}" for f in STORES.keys()])
    description = f"Run scraper for all stores:\n{str_stores}"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-st', '--store', type=str, help="Store name", default="all")
    parser.add_argument('-ns', '--not-send', action='store_true', help="Don't send files")
    args = parser.parse_args()

    chrome_options = Options()
    # chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    if args.store == "all":
        logger.info(f"Running scraping process in all stores")
        for st in STORES.values():
            run_scraping(driver, st)
            time.sleep(3)
    elif args.store in STORES:
        logger.info(f"Running scraping process for {args.store} store")
        st = STORES[args.store]
        run_scraping(driver, st)
    else:
        logger.error("Invalid store")
        driver.quit()
        exit(1)

    driver.quit()

    logger.info("Scraping completed")

    if not args.not_send:
        logger.info("Sending files to cloud")
        for file in output_folder.glob('*products.csv'):
            hist_file = file.parent / f'{file.stem}_{DT.strftime("%Y%m%d")}{file.suffix}'
            logger.info(f"Uploading files: {file.name} - {hist_file.name}")
            r = upload_blob_file(sas_url, dest_hist_folder, hist_file)
            logger.info(f"Upload historic file status: {r}")
            r = upload_blob_file(sas_url, dest_folder, file)
            logger.info(f"Upload file status: {r}")
            # 201 status is success.
        logger.info(f"Scraping completed - Files sent")
    else:
        logger.info(f"Scraping completed - Files not sent")


if __name__ == "__main__":
    DT = datetime.now()
    main()
