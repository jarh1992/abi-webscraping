from settings.settings import *
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from settings.stores_info import stores


def main():
    str_stores = "\n".join([f"- {f}" for f in stores.keys()])
    description = f"Run scraper for all stores:\n{str_stores}"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--store', type=str, help="Store name", default="all")
    args = parser.parse_args()

    in_file = BASE_DIR / "input/brands.csv"
    with in_file.open(encoding='utf8') as f:
        brands = [line.rstrip('\n') for line in f]

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if args.store == "all":
        for st in stores.values():
            data = st.scraper(driver, brands, st.url)
            file_path = BASE_DIR / f'output/{st.store_name}_products_out.txt'
            with file_path.open(mode='w', encoding='utf8') as file:
                file.write(data)
    else:
        if args.store in stores:
            st = stores[args.store]
            data = st.scraper(driver, brands, st.url)
            file_path = BASE_DIR / f'output/{args.store}_products_out.txt'
            with file_path.open(mode='w', encoding='utf8') as file:
                file.write(data)
        else:
            ValueError("Invalid store")
    driver.quit()


if __name__ == "__main__":
    main()
