from settings.settings import BASE_DIR, logger
from input.store_info import STORES, BRANDS
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def main():
    str_stores = "\n".join([f"- {f}" for f in STORES.keys()])
    description = f"Run scraper for all stores:\n{str_stores}"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--store', type=str, help="Store name", default="all")
    args = parser.parse_args()

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    if args.store == "all":
        for st in STORES.values():
            data = st.scraper(driver, BRANDS, 'CERVEZA', st.url)
            data += st.scraper(driver, BRANDS, 'OTROS', st.url)
            data = '\n'.join(data)
            file_path = BASE_DIR / f'output/{st.store_name}_products_out.txt'
            with file_path.open(mode='w', encoding='utf8') as file:
                file.write(data)
    else:
        if args.store in STORES:
            st = STORES[args.store]
            data = st.scraper(driver, BRANDS, 'CERVEZA', st.url)
            data += st.scraper(driver, BRANDS, 'OTROS', st.url)
            data = '\n'.join(data)
            file_path = BASE_DIR / f'output/{args.store}_products_out.txt'
            with file_path.open(mode='w', encoding='utf8') as file:
                file.write(data)
        else:
            logger.error("Invalid store")
    driver.quit()
    logger.info("Finished")


if __name__ == "__main__":
    main()
