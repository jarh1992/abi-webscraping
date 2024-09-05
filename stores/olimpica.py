import time
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scraper(driver, brands):

    elements = ''
    for coproduct in brands:

        driver.get(f"https://www.olimpica.com/{coproduct}?_q={coproduct}&map=ft")

        # maximiza la ventana
        #driver.maximize_window()

        # Realiza un pequeño scroll y regresa a su posición para que carguen los productos
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")

        # reduce el tamaño del texto o zoom al 20%
        driver.execute_script('document.body.style.zoom = 0.55')
        # Elimina el modal
        time.sleep(4)

        try:
            # Espera hasta que el elemento esté presente
            elements += WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="gallery-layout-container"]'))
            ).text.replace("\n", " | ").replace("| Agregar |", "\n")
            elements += '\n'
        except Exception as e:
            print(f"Error finding element: {e}")
            continue

    print('Olimpica scraped')
    return elements
