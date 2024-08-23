import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

# crea un objeto webdriver para usar chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

f = open("in.csv")
reader = csv.reader(f)
for wild_products in reader:
    coproduct = wild_products[0]
    driver.get(f"https://www.tiendasjumbo.co/{coproduct}?_q={coproduct}&map=ft")

    # maximiza la ventana
    #driver.maximize_window()

    # Realiza un pequeño scroll y regresa a su posicion para que carguen los productos
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 0);")

    # reduce el tamaño del texto o zoom al 20%
    driver.execute_script('document.body.style.zoom = 0.55')
    # Elimina el modal
    time.sleep(4)
    elements = None

    try:
        # Espera hasta que el elemento esté presente
        elements = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="gallery-layout-container"]'))
        ).text.replace("\n", " | ").replace("| Agregar |", "\n")
    except Exception as e:
        print(f"Error al encontrar el elemento: {e}")
        continue

    brand_names = []
    brand_name_text = elements
    brand_names.append(brand_name_text)
    print(elements)

    #csv_file = open(f'{coproduct}_brand_names.csv', mode='w')  # open csv file
    #csv_writer = csv.writer(csv_file, delimiter='|')  # objeto para escribir
    #csv_writer.writerow(brand_name_text)  # escribir los elementos
    #csv_file

    file = open(f'{coproduct}_out.txt', "w", encoding="utf-8")
    file.write(elements + os.linesep)
    file.close()

print('Proceso Finalizado')






