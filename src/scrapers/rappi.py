import logging
import re
import time
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
    city = city.replace('_', ' ')
    pos = 'NA'

    url = urlparse(store.url)
    scheme_netloc = f"{url.scheme}://{url.netloc}"
    url_path = url.geturl()
    driver.get(scheme_netloc)

    # close_popup(driver)

    wait_driver(driver, (By.XPATH, "//div[contains(@data-qa, 'address-container')]"))
    address_btn = driver.find_element(By.XPATH, "//div[contains(@data-qa, 'address-container')]")
    address_btn.click()
    time.sleep(2)
    wait_driver(driver, (By.CLASS_NAME, 'chakra-modal__content-container'))
    modal = driver.find_element(By.CLASS_NAME, 'chakra-modal__content-container')
    input = modal.find_element(By.CLASS_NAME, 'chakra-input')
    input.send_keys('bogota')
    time.sleep(2)
    wait_driver(modal, (By.CLASS_NAME, 'chakra-button'))
    options_btn = modal.find_elements(By.CLASS_NAME, 'chakra-button')
    options_btn[2].click()
    time.sleep(2)
    wait_driver(modal, (By.ID, 'confirm-address-button'))
    confirm_btn = modal.find_element(By.ID, 'confirm-address-button')
    confirm_btn.click()
    time.sleep(2)
    wait_driver(modal, (By.ID, 'save-address-button'))
    save_addr_btn = modal.find_element(By.ID, 'save-address-button')
    save_addr_btn.click()

    for brand_type, brand_lst in brands.items():
        logger.info(f"Scraping {store.name} {brand_type} in city {city}.")
        for coproduct in brand_lst:
            driver.get(url_path.format(prod=coproduct))
            time.sleep(2)

            try:
                wait_driver(driver, (By.CSS_SELECTOR, '.chakra-stack'))
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                elements = soup.find_all('div', {'data-qa': re.compile("product-item")})
                brand = remove_accents(coproduct)
                for e in elements:
                    description = remove_accents(e.find('h3', {'data-qa': re.compile('product-name')}).text.strip())
                    price = e.find('span', {'data-qa': re.compile('product-price')}).text[2:]
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
