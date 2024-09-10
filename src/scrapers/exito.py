import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scraper(driver, brands, url):

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
                EC.presence_of_element_located((By.XPATH, '//div[@data-fs-product-listing-results="true"]'))
            )
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            elements = soup.find_all(class_=re.compile("productCard_contentInfo__CBBA7"))
            for i in elements:
                # 1) in exito brand name is not specified
                brand = coproduct.upper().replace('CERVEZA ', '').replace('Ñ', 'N')
                description = i.find('p', class_=re.compile("styles_name")).text.strip()
                price = i.find('p', class_=re.compile("ProductPrice_container__price")).text[2:]
                print(brand, description, price)
                # 2) then we need find it in description
                if not ('cerveza' in description.lower() and brand.lower() in description.lower()):
                    continue
                row = '|'.join([brand, description, price])
                if row not in data:
                    data.append(row)
        except Exception as e:
            print(f"Error finding element {coproduct}: {e}")
            continue

    data = '\n'.join(data)
    print('Exito scraped')
    return data
