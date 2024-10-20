import logging
import time
import re
from urllib.parse import urlparse

from src.utils import remove_accents, wait_driver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


logger = logging.getLogger(__name__)


def scraper(driver, locs, brands, store):
    data = []
    department, city = list(map(remove_accents, locs[0].split()))
    department = department.replace('_', ' ')
    city = city.replace('_', ' ')
    pos = "NA"

    url = urlparse(store.url)
    scheme_netloc = f"{url.scheme}://{url.netloc}"
    url_path = url.geturl()
    driver.get(scheme_netloc)
    time.sleep(5)
    try:
        pop_up = driver.find_element(By.CLASS_NAME, "olimpica-advance-geolocation-0-x-overlayDirection")
        change_btn = pop_up.find_elements(By.TAG_NAME, "button")
        change_btn[1].click()
    except Exception as e:
        logger.info('Popup not found')
        print(e)

    time.sleep(1)

    wait_driver(driver, (By.CLASS_NAME, "vtex-modal__overlay"))
    modal = driver.find_element(By.CLASS_NAME, "vtex-modal__overlay")
    modal_selects = modal.find_element(By.CLASS_NAME, "olimpica-advance-geolocation-0-x-citiesSelectorContainer")
    selects = modal_selects.find_elements(By.CLASS_NAME, "olimpica-advance-geolocation-0-x-selectCity")
    input_dpto = selects[0].find_element(By.TAG_NAME, "input")
    input_dpto.send_keys(f'{department}\n')
    wait_driver(modal_selects, (By.CLASS_NAME, "olimpica-advance-geolocation-0-x-selectCity"))
    selects = modal_selects.find_elements(By.CLASS_NAME, "olimpica-advance-geolocation-0-x-selectCity")
    input_dpto = selects[1].find_element(By.TAG_NAME, "input")
    input_dpto.send_keys(f'{city}\n')

    accept_btn = modal.find_element(By.TAG_NAME, 'button')
    accept_btn.click()
    time.sleep(2)

    for brand_type, brand_lst in brands.items():
        logger.info(f"Scraping {store.name} {brand_type} in city {city}.")
        for coproduct in brand_lst:
            driver.get(url_path.format(prod=coproduct))
            time.sleep(2)

            try:
                wait_driver(driver, (By.XPATH, '//*[@id="gallery-layout-container"]'))
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                elements = soup.find_all('article', class_=re.compile("vtex-product-summary-2-x-element"))
                brand = remove_accents(coproduct)
                for e in elements:
                    description = remove_accents(e.find('span', class_=re.compile("productBrand$")).text.strip()).upper()
                    price = e.find('span', class_=re.compile("olimpica-dinamic-flags-0-x-currencyContainer")).text[2:]
                    row = '|'.join([brand, city, pos, description, price])
                    if brand_type == 'CERVEZA':
                        flag = all([i in description for i in [brand_type, "ML", *brand.split(' ')]])
                    else:
                        flag = all([i in description for i in brand.split(' ')])
                    if not flag:
                        logger.info(f'Product not added: {brand} != {description}')
                        continue

                    row = re.sub(r'\s+ML', 'ML', row)
                    row = re.sub(r'X\s+6\s+UND', 'X6UND', row)
                    row = row.replace('.', ',')
                    row = row.replace('SIXPACK', 'X6UND')
                    row = row.replace('SIX PACK', 'X6UND')
                    row = row.replace('6PACK', 'X6UND')
                    row = row.replace('6 PACK', 'X6UND')
                    if ' 1980ML' in row:
                        row = row.replace('1980ML', '330ML')
                    row = row.replace(' X 6 ', ' X6UND ')

                    if row not in data:
                        data.append(row)
            except Exception as e:
                logger.error(f"Error finding element {coproduct}: {e}")
                continue
        logger.info(f'Scraped {store.name} {brand_type} in city {city}.')
    return data
