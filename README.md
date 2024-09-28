# Aplicación ABI Web scraping

## Estructura
````
abi-webscraping
├── docs
│	 ├── Catálogo Maestro Fabricantes - ABI nuevo (1).xlsx
│	 ├── Homologacion.xlsx
│	 ├── Marcas ABI.xlsx
│	 ├── rvwebscrappingka.zip
│	 └── Seguimiento web scrapping.entregables.xlsx
├── input
│	 ├── brands.json
│	 ├── brands_test.json
│	 └── store_info.py
├── logs
│	 └── app_20240926.log
├── output
│	 ├── rappi_products_20240926.csv
│	 └── rappi_products.csv
├── settings
│	 └── settings.py
├── src
│	 ├── models
│	 │	 └── models.py
│	 ├── scrapers
│	 │	 ├── carulla.py
│	 │	 ├── exito.py
│	 │	 ├── jumbo.py
│	 │	 ├── makro.py
│	 │	 ├── metro.py
│	 │	 ├── olimpica.py
│	 │	 └── rappi.py
│	 └── utils.py
├── main.py
├── README.md
└── requirements.txt
````
- **docs**: documentos/información para la lógica de negocio. 

- **input**: contiene los archivos (no credenciales) de entrada necesarios para la correcta ejecución
del aplicativo:
  - **[brands.json](input/brands.json)**: Contiene el nombre de los productos/marcas organizados según dos tipos: cerveza
  y otros. **Nuevos productos/marcas** deben ser agregados en mayúsculas y entre comillas dobles. Estos pueden incluir
  tildes o 'Ñ'. Este archivo es invocado en **[store_info.py](input/store_info.py)**, línea 53.
  - **[store_info.py](input/store_info.py)**: En este archivo son organizados como estructuras de datos (Clases) los
  comercios. **Nuevos comercios** deben ser agregados siguiendo la estructura encontrada en este mismo archivo; la
  estructura es basada en la clase **Store** ubicada en el archivo **[models.py](src/models/models.py)**.
  - **[brands_test.json](input/brands_test.json)**: Archivo similar a **[brands.json](input/brands.json)**, pero para realizar
  pruebas cortas. Este archivo puede ser invocado en **[store_info.py](input/store_info.py)**, línea 53.
- **logs**: Contiene los logs generados en la ejecución de los scrapers de cada comercio. Pueden ser configurados
  desde el archivo **[settings.json](settings/settings.py)**.
- **output**: Aquí se guardan los CSV con la información obtenida de los comercios.
- **settings**:
  - **[settings.py](settings/settings.py)**: Configuración inicial para:
    - Invocar y cargar las variables de entorno (archivo **[.env](.env)** en la raíz) necesarias para el funcionamiento del
    programa.
    - Configurar sistema de logs.
- **src**: Contiene el código fuente entre las siguientes carpetas:
  - **models**
    - **models.py**: Contiene el modelo/clase principal _Stores_, para organizar la información principal de los
    comercios.
  - **scrapers**: Scripts que realizan el scraping y el formateo de los datos recolectados **por cada comercio** a 
  inspeccionar.
  - **utils.py**: Contiene **funciones** para **normalizar la información recolectada** y para **enviar datos a Azure
  Blob Storage**.
- **README.md**: El presente archivo de documentación.
- **[main.py](main.py)**: Script principal de la aplicación.
- **[.env](.env)**: Archivo con las variables de entorno (credenciales para enviar datos a Azure Blob Storage) 
necesarias para la ejecución de la aplicación. **DEBE SER CREADO MANUALMENTE y NO SE PUEDE SUBIR AL REPOSITORIO** como
lo establece el archivo **[.gitignore](.gitignore)**.
- **[.gitignore](.gitignore)**: Archivo git con la lista de folders/archivos que no deben ser subidos al repositorio.
- **[requirements.txt](requirements.txt)**: Archivo con la lista de librerias requeridas para el funcionamiento de la aplicación.

## Despliegue
1. Clonar el repositorio en la ruta deseada:
````shell
cd <path>
git clone https://github.com/jarh1992/abi-webscraping.git
````
2. Entrar al repositorio y crear el entorno virtual (Se necesita previamente tener instalado Python >= v3.9):
````shell
cd abi-webscraping
python -m venv venv
````
3. Activar el entorno virtual e instalar los requerimientos usando el archivo **[requirements.txt](requirements.txt)**:

Linux
````shell
source venv/bin/activate
pip install -r requirements.txt
````
Windows
````shell
.\venv\Scripts\activate
pip install -r requirements.txt
````

## Ejecución
Ubicarse en la raíz de la aplicación y luego:
- Ejecutar el scraper en todos los comercios:
````shell
python main.py
````
- Ejecutar el scraper para un comercio en específico:
````shell
python main.py -st COMERCIO
python main.py -st comercio
````
(_\<comercio\>_ no distingue entre mayúsculas y minúsculas).
- Para no enviar archivos a Azure Blob Storage se puede usar la bandera "-ns" o "--not-send":
````shell
python main.py -ns
python main.py --not-send
python main.py -st comercio -ns
python main.py -st comercio --not-send
````
- Para consultar la ayuda:
````shell
python main.py -h
python main.py --help
````
Obtendrá la salida:
````shell
usage: main.py [-h] [-st STORE] [-ns]

Run scraper for all stores:
- carulla
- exito
- jumbo
- makro
- metro
- olimpica
- rappi

options:
  -h, --help            show this help message and exit
  -st STORE, --store STORE
                        Store name
  -ns, --not-send       Don't send files
````
