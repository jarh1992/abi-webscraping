from datetime import datetime

from settings.settings import (
    logger,
    sas_url,
    dest_folder,
    dest_hist_folder,
    output_folder,
    BRANDS
)
from src.utils import upload_blob_file
from src.store_info import stores
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def main():
    str_stores = "\n".join([f"- {f}" for f in stores.keys()])
    description = f"Run scraper for all stores:\n{str_stores}"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-st', '--store', type=str, help="Store name", default="all")
    parser.add_argument('-ns', '--not-send', action='store_true', help="Don't send files")
    args = parser.parse_args()

    dt = datetime.now()
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    file_header = "MARCA|PRODUCTO|PRECIO\n"
    if args.store == "all":
        for st in stores.values():
            data = st.scraper(driver, BRANDS, 'CERVEZA', st.url)
            data += st.scraper(driver, BRANDS, 'OTROS', st.url)
            data = '\n'.join(data)
            file_path = output_folder / f'{st.name}_products.csv'
            file_hist_path = output_folder / dt.strftime(f'{st.name}_products_%Y%m%d.csv')
            with (file_path.open(mode='w', encoding='utf8') as file,
                  file_hist_path.open(mode='w', encoding='utf8') as hist):
                file.write(file_header)
                file.write(data)
                hist.write(file_header)
                hist.write(data)

    else:
        logger.info(f"Running scraping process to a single store")
        if args.store in stores:
            st = stores[args.store]
            data = st.scraper(driver, BRANDS, 'CERVEZA', st.url)
            data += st.scraper(driver, BRANDS, 'OTROS', st.url)
            data = '\n'.join(data)
            file_path = output_folder / f'{st.name}_products.csv'
            file_hist_path = output_folder / dt.strftime(f'{st.name}_products_%Y%m%d.csv')
            with (file_path.open(mode='w', encoding='utf8') as file,
                  file_hist_path.open(mode='w', encoding='utf8') as hist):
                file.write(file_header)
                file.write(data)
                hist.write(file_header)
                hist.write(data)
        else:
            logger.error("Invalid store")

    driver.quit()
    logger.info("Scraping completed")

    if not args.not_send:
        for file in output_folder.glob('*products.csv'):
            hist_file = file.parent / f'{file.stem}_{dt.strftime("%Y%m%d")}{file.suffix}'
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
    main()
