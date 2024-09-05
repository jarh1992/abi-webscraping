import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).resolve().parent


def scraper(driver, brands):

    elements = ''
    for coproduct in brands:

        driver.get(f"https://tienda.makro.com.co/search?name={coproduct}")

        # maximiza la ventana
        #driver.maximize_window()

        # Realiza un pequeño scroll y regresa a su posicion para que carguen los productos
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")

        # reduce el tamaño del texto o zoom al 20%
        driver.execute_script('document.body.style.zoom = 0.55')
        # Elimina el modal
        time.sleep(5)

        try:
            time.sleep(2)
            elements += driver.find_element(
                By.XPATH,
                '/html/body/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div'
            ).text.replace("\n", " | ").replace("Agregar | ", "\n").replace("Nacionales | ", "")
        except:
            time.sleep(5)
            elements += driver.find_element(
                By.XPATH,
                '/html/body/div/div/div[2]/div/div/div'
            ).text.replace("\n", " | ").replace("Agregar | ", "\n")
        elements += '\n'
        wait = WebDriverWait(driver, 5)
        print(elements)

    print('Makro scraped')
    return elements
