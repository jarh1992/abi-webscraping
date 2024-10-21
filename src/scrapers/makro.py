import logging
import re
import time
from urllib.parse import urlparse

from selenium.webdriver.support.wait import WebDriverWait

from src.utils import remove_accents, wait_driver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


logger = logging.getLogger(__name__)


def scraper(driver, locs, brands, store):
    data = []
    # es importante mantener los acentos para encontrar el dpto o ciudad, y en minúsculas
    department, city = [loc.lower() for loc in locs[0].split()]
    department = department.replace('_', ' ')
    city = city.replace('_', ' ')
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

        wait_driver(driver, (By.XPATH, "//button[contains(@class, 'styles__OpModelStyled-sc-8j6wd0-0')]"))
        modal_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'styles__OpModelStyled-sc-8j6wd0-0')]")
        modal_btn.click()

        wait_driver(driver, (By.CLASS_NAME, "ant-modal-content"))
        modal = driver.find_element(By.CLASS_NAME, "ant-modal-content")
        wait_driver(driver, (By.ID, "card-operation-model-PICK_AND_COLLECT"))
        shop_btn = modal.find_element(By.ID, "card-operation-model-PICK_AND_COLLECT")
        shop_btn.click()

        wait_driver(driver, (By.CLASS_NAME, "ant-modal-content"))
        modal = driver.find_element(By.CLASS_NAME, "ant-modal-content")
        wait_driver(modal, (By.TAG_NAME, "input"))
        inputs = modal.find_elements(By.TAG_NAME, "input")
        time.sleep(1)
        inputs[0].send_keys(f'{department}\n')
        wait_driver(modal, (By.TAG_NAME, "input"))
        inputs = modal.find_elements(By.TAG_NAME, "input")
        time.sleep(1)
        inputs[1].send_keys(f'{city}\n')
        btns = modal.find_elements(By.TAG_NAME, "button")
        btns[-1].click()

        wait_driver(driver, (By.CLASS_NAME, "ant-modal-content"))
        modal = driver.find_element(By.CLASS_NAME, "ant-modal-content")
        wait_driver(driver, (By.CLASS_NAME, "CardInfo__StyledCardInfo-sc-pdzb6y-0"))
        shops = modal.find_elements(By.CLASS_NAME, "CardInfo__StyledCardInfo-sc-pdzb6y-0")
        for s in shops:
            shop_name = remove_accents(s.text.split('\n')[0])
            if pos in shop_name:
                s.click()
                break

        time.sleep(2)

        for brand_type, brand_lst in brands.items():
            logger.info(f"Scraping {store.name} {brand_type} in city {city}, POS {pos}.")
            for coproduct in brand_lst:
                driver.get(url_path.format(prod=coproduct))
                time.sleep(2)

                try:
                    wait_driver(driver, (By.CSS_SELECTOR, '.products-container'))
                    html_content = driver.page_source
                    soup = BeautifulSoup(html_content, 'html.parser')
                    elements = soup.find_all('div', class_=re.compile("general__content"))
                    brand = remove_accents(coproduct)
                    for e in elements:
                        description = remove_accents(e.find('p', class_=re.compile("prod__name")).text.strip())
                        price = e.find('p', class_=re.compile("base__price")).text[1:]
                        row = '|'.join([brand, remove_accents(city), pos, description, price])
                        if brand_type == 'CERVEZA':
                            flag = all([i in description for i in [brand_type, 'ML', *brand.split(' ')]])
                        else:
                            flag = all([i in description for i in brand.split(' ')])
                        if not flag:
                            logger.info(f'Product not added: {brand} != {description}')
                            continue

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

                        if row not in data:
                            data.append(row)
                except Exception as e:
                    logger.error(f"Error finding element {coproduct}: {e}")
                    continue
            logger.info(f'Scraped {store.name} {brand_type} in city {city}, POS {pos}.')
    return data
