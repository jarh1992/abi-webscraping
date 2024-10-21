import logging
import os
import re
import time
from urllib.parse import urlparse

from src.utils import remove_accents, wait_driver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv


load_dotenv(override=True)
logger = logging.getLogger(__name__)
EMAIL = os.getenv('TEST_EMAIL')


def scraper(driver, locs, brands, store):
    data = []
    department, city = list(map(remove_accents, locs[0].split()))
    department = department.replace('_', ' ')
    city = city.replace('_', ' ')
    points_of_sale = locs[1]

    url = urlparse(store.url)
    scheme_netloc = f"{url.scheme}://{url.netloc}"
    url_path = url.geturl()
    driver.get(scheme_netloc)
    try:
        wait_driver(driver, (By.ID, "evg-popup"), timeout=15)
        pop_up = driver.find_element(By.ID, "evg-popup")
        close_btn = pop_up.find_element(By.XPATH, "//button[contains(@class, 'evg-btn-dismissal')]")
        close_btn.click()
    except Exception as e:
        pass

    for i, pos in enumerate(points_of_sale):
        pos = remove_accents(pos)

        wait_driver(
            driver,
            (By.XPATH, "//div[contains(@class, 'tiendasjumboqaio-delivery-modal-3-x-containerTrigger')]")
        )
        modal_btn = driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'tiendasjumboqaio-delivery-modal-3-x-containerTrigger')]"
        )
        modal_btn.click()

        wait_driver(driver, (By.CLASS_NAME, "vtex-modal-layout-0-x-container"))
        modal = driver.find_element(By.CLASS_NAME, "vtex-modal-layout-0-x-container")

        try:
            wait_driver(modal, (By.XPATH, "//input[contains(@placeholder, 'Ingresa aquí tu correo')]"))
            email_input = modal.find_element(By.XPATH, "//input[@placeholder='Ingresa aquí tu correo']")
            email_input.send_keys(f'{EMAIL}')
        except Exception as exc:
            email_change = modal.find_element(By.XPATH, '//button[normalize-space()="Cambiar"]')
            email_change.click()

        wait_driver(modal, (By.XPATH, '//button[normalize-space()="Enviar"]'))
        email_send = modal.find_element(By.XPATH, '//button[normalize-space()="Enviar"]')
        email_send.click()

        wait_driver(modal, (By.XPATH, '//div[contains(@class, "tiendasjumboqaio-delivery-modal-3-x-ButtonPlain")]'))
        delivery_btns = modal.find_elements(By.XPATH, '//div[contains(@class, "tiendasjumboqaio-delivery-modal-3-x-ButtonPlain")]')
        delivery_btns[1].click()

        time.sleep(1)
        wait_driver(modal, (By.TAG_NAME, 'select'))
        selects = modal.find_elements(By.TAG_NAME, 'select')
        dept_select = Select(selects[0])
        for e, option in enumerate(dept_select.options):
            if department in remove_accents(option.text):
                time.sleep(1)
                dept_select.select_by_visible_text(option.text)
                dept_select.select_by_index(e)
                break

        time.sleep(1)
        wait_driver(modal, (By.TAG_NAME, 'select'))
        selects = modal.find_elements(By.TAG_NAME, 'select')
        city_select = Select(selects[1])
        for e, option in enumerate(city_select.options):
            if city in remove_accents(option.text):
                time.sleep(1)
                city_select.select_by_visible_text(option.text)
                city_select.select_by_index(e)
                break

        time.sleep(1)
        wait_driver(modal, (By.TAG_NAME, 'select'))
        selects = modal.find_elements(By.TAG_NAME, 'select')
        pos_select = Select(selects[2])
        for e, option in enumerate(pos_select.options):
            if pos in remove_accents(option.text):
                time.sleep(1)
                pos_select.select_by_visible_text(option.text)
                pos_select.select_by_index(e)
                break

        confirm_btn = modal.find_element(By.XPATH, '//button[normalize-space()="Confirmar"]')
        confirm_btn.click()
        time.sleep(10)

        for brand_type, brand_lst in brands.items():
            for coproduct in brand_lst:
                logger.info(f"Scraping {store.name} {brand_type} in city {city}, POS {pos}.")
                driver.get(url_path.format(prod=coproduct))
                time.sleep(2)

                try:
                    wait_driver(driver, (By.XPATH, '//*[@id="gallery-layout-container"]'))
                    html_content = driver.page_source
                    soup = BeautifulSoup(html_content, 'html.parser')
                    elements = soup.find_all('article', class_=re.compile("product-summary"))
                    brand = remove_accents(coproduct)
                    for e in elements:
                        description = remove_accents(e.find('span', class_=re.compile("productBrand$")).text.strip())
                        price = e.find('div', id='items-price').text[2:]
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
                        row = row. replace('.', ',')
                        row = row.replace(',00|', '|')
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
            logger.info(f'Scraped {store.name} {brand_type} in city {city}, POS {pos}.')
    return data
