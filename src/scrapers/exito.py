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


def close_popup(driver):
    try:
        wait_driver(driver, (By.ID, "wps_popup"), timeout=15)
        pop_up = driver.find_element(By.ID, "wps_popup")
        close_btn = pop_up.find_element(By.ID, "wps-overlay-close-button")
        close_btn.click()
    except Exception as e:
        pass


def scraper(driver, locs, brands, store):
    data = []
    department, city = list(map(remove_accents, locs[0].split()))
    city = city.replace('_', ' ')
    points_of_sale = locs[1]

    url = urlparse(store.url)
    scheme_netloc = f"{url.scheme}://{url.netloc}"
    url_path = url.geturl()
    driver.get(scheme_netloc)

    # close_popup(driver)

    for pos in points_of_sale:
        pos = remove_accents(pos)

        wait_driver(driver, (By.XPATH, "//button[contains(@class, 'button_fs-button__v6Toy')]"))
        modal_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'button_fs-button__v6Toy')]")
        modal_btn.click()
        wait_driver(driver, (By.CLASS_NAME, "modal_fs-modal__zQHxL"))
        modal = driver.find_element(By.CLASS_NAME, "modal_fs-modal__zQHxL")

        wait_driver(
            modal,
            (By.XPATH, "//div[contains(@data-fs-pickup-point-city-select-city, 'true')]"),
            timeout=15
        )
        select_city = modal.find_element(
            By.XPATH, "//div[contains(@data-fs-pickup-point-city-select-city, 'true')]")
        time.sleep(2)
        inputs = select_city.find_element(By.TAG_NAME, 'input')
        time.sleep(2)
        try:
            inputs.send_keys(f'{city}\n')
        except Exception as e:
            logger.error(f"Cannot be introduced the city {city}")
            print(e)
            time.sleep(2)
            close_popup(driver)
            inputs.send_keys(f'{city}\n')

        wait_driver(
            modal,
            (By.XPATH, "//div[contains(@data-fs-pickup-point-city-select-dependency, 'true')]"),
            timeout=15
        )
        select_city = modal.find_element(
            By.XPATH, "//div[contains(@data-fs-pickup-point-city-select-dependency, 'true')]")
        time.sleep(2)

        inputs = select_city.find_element(By.TAG_NAME, 'input')
        time.sleep(2)
        try:
            inputs.send_keys(f'{pos}\n')
        except Exception as e:
            logger.error(f"Cannot be introduced the city {city}")
            print(e)
            time.sleep(2)
            inputs.send_keys(f'{pos}\n')

        try:
            wait_driver(modal, (By.CLASS_NAME, 'PickupPoint_primaryButtonEnable__vh9yw'))
        except Exception as e:
            logger.info('Confirmar button not activated')
            print(e)

        confirm_btn = modal.find_element(By.CLASS_NAME, 'PickupPoint_primaryButtonEnable__vh9yw')
        confirm_btn.click()

        for brand_type, brand_lst in brands.items():
            logger.info(f"Scraping {store.name} {brand_type} in city {city}, POS {pos}.")
            for coproduct in brand_lst:
                driver.get(url_path.format(prod=coproduct))
                time.sleep(2)

                try:
                    wait_driver(driver, (By.XPATH, '//div[@data-fs-product-listing-results="true"]'))
                    html_content = driver.page_source
                    soup = BeautifulSoup(html_content, 'html.parser')
                    elements = soup.find_all(class_=re.compile("productCard_contentInfo__CBBA7"))
                    brand = remove_accents(coproduct)
                    for e in elements:
                        description = remove_accents(e.find('p', class_=re.compile("styles_name")).text.strip())
                        price = e.find('p', class_=re.compile("ProductPrice_container__price")).text[2:]
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
            logger.info(f'Scraped {store.name} {brand_type} in city {city}, POS {pos}.')
    return data
