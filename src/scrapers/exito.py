import logging
import re
import time

from src.utils import remove_accents
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


logger = logging.getLogger(__name__)


def scraper(driver, brands, brand_type, url):
    logger.info(f"Scraping Exito {brand_type}")
    brands = brands[brand_type]
    data = []
    for coproduct in brands:

        driver.get(url.format(prod=coproduct))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")

        driver.execute_script('document.body.style.zoom = 0.55')
        time.sleep(4)

        try:
            WebDriverWait(
                driver,
                10
            ).until(
                ec.presence_of_element_located((By.XPATH, '//div[@data-fs-product-listing-results="true"]'))
            )
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            elements = soup.find_all(class_=re.compile("productCard_contentInfo__CBBA7"))
            for i in elements:
                brand = coproduct.upper().replace('Ñ', 'N')
                description = remove_accents(i.find('p', class_=re.compile("styles_name")).text.strip()).upper()
                price = i.find('p', class_=re.compile("ProductPrice_container__price")).text[2:]
                row = '|'.join([brand, description, price])
                if brand_type == 'CERVEZA':
                    flag = all([i in description for i in [brand_type, *brand.split(' ')]])
                else:
                    flag = all([i in description for i in brand.split(' ')])
                if not flag:
                    logger.info(f'Product not added: {row}')
                    continue
                if row not in data:
                    data.append(row)
        except Exception as e:
            logger.error(f"Error finding element {coproduct}: {e}")
            continue

    logger.info(f'Exito {brand_type} scraped')
    return data
