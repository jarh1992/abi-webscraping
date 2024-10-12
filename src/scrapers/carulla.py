import logging
import re
import time
from urllib.parse import urlparse

from src.utils import remove_accents, wait_driver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


logger = logging.getLogger(__name__)


def scraper(driver, locs, brands, store):
    data = []
    department, city = list(map(remove_accents, locs[0].split()))
    points_of_sale = locs[1]

    url = urlparse(store.url)
    scheme_netloc = f"{url.scheme}://{url.netloc}"
    url_path = url.geturl()
    driver.get(scheme_netloc)
    try:
        wait_driver(driver, (By.ID, "wps_popup"), timeout=15)
        pop_up = driver.find_element(By.ID, "wps_popup")
        close_btn = pop_up.find_element(By.ID, "wps-overlay-close-button")
        close_btn.click()
    except Exception as e:
        pass

    for pos in points_of_sale:
        pos = remove_accents(pos)

        try:
            modal = driver.find_element(By.ID, "exito-geolocation-3-x-modalContainer")
        except Exception as e:
            wait_driver(driver, (By.XPATH, "//div[contains(@class, 'exito-geolocation-3-x-addressResultFirst')]"))
            modal_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'exito-geolocation-3-x-addressResultFirst')]")
            modal_btn.click()
            wait_driver(driver, (By.ID, "exito-geolocation-3-x-modalContainer"))
            modal = driver.find_element(By.ID, "exito-geolocation-3-x-modalContainer")

        wait_driver(modal, (By.XPATH, "//div[contains(@class, 'shippingaddress-lista-ciudad')]"), timeout=15)
        select_city = modal.find_element(By.XPATH, "//div[contains(@class, 'shippingaddress-lista-ciudad')]")
        time.sleep(2)
        inputs = select_city.find_element(By.TAG_NAME, 'input')
        inputs.send_keys(f'{city}\n')

        wait_driver(modal, (By.XPATH, "//div[contains(@class, 'buycollect-lista-almacen')]"), timeout=15)
        select_shop = modal.find_element(By.XPATH, "//div[contains(@class, 'buycollect-lista-almacen')]")
        time.sleep(2)
        inputs = select_shop.find_element(By.TAG_NAME, 'input')
        inputs.send_keys(f'{pos}\n')

        wait_driver(modal, (By.CLASS_NAME, 'exito-geolocation-3-x-primaryButtonEnable'))
        confirm_btn = modal.find_element(By.CLASS_NAME, 'exito-geolocation-3-x-primaryButtonEnable')
        confirm_btn.click()

        for brand_type, brand_lst in brands.items():
            for coproduct in brand_lst:
                logger.info(f"Scraping {store.name} {brand_type} in city {city}, POS {pos}.")
                driver.get(url_path.format(prod=coproduct))
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                # driver.execute_script("window.scrollTo(0, 0);")

                # driver.execute_script('document.body.style.zoom = 0.55')
                # time.sleep(4)

                try:
                    wait_driver(driver, (By.XPATH, '//*[@id="gallery-layout-container"]'))
                    html_content = driver.page_source
                    soup = BeautifulSoup(html_content, 'html.parser')
                    elements = soup.find_all(class_=re.compile("flexRowContent--product-info-container"))
                    brand = remove_accents(coproduct)
                    for i in elements:
                        description = remove_accents(i.find('span', class_=re.compile("productBrand$")).text.strip())
                        price = i.find('div', class_=re.compile("exito-vtex-components-4-x-PricePDP")).text[2:]
                        row = '|'.join([brand, city, pos, description, price])
                        if brand_type == 'CERVEZA':
                            flag = all([i in description for i in [brand_type, "ML", *brand.split(' ')]])
                        else:
                            flag = all([i in description for i in brand.split(' ')])
                        if not flag:
                            logger.info(f'Product not added: {brand} != {description}')
                            continue
                        if row not in data:
                            row = re.sub(r'\s+ML', 'ML', row)
                            row = re.sub(r'X\s+6\s+UND', 'X6UND', row)
                            row = row. replace('.', ',')
                            row = row.replace('SIXPACK', 'X6UND')
                            row = row.replace('SIX PACK', 'X6UND')
                            row = row.replace('6PACK', 'X6UND')
                            row = row.replace('6 PACK', 'X6UND')
                            if ' 1980ML' in row:
                                row = row.replace('1980ML', '330ML')
                            row = row.replace(' X 6 ', ' X6UND ')
                            data.append(row)
                except Exception as e:
                    logger.error(f"Error finding element {coproduct}: {e}")
                    continue
            logger.info(f'Scraped {store.name} {brand_type} in city {city}, POS {pos}.')
    return data
