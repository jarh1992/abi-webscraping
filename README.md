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
│	 ├── input.json
│	 └── input_test.json
├── logs
│	 └── app_YYYYMMDD.log
├── output
│	 ├── store_products_YYYYMMDD.csv
│	 └── store_products.csv
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
├── .env
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
````
- **docs**: documentos/información para la lógica de negocio y de programación. 
  **IMPORTANTE**: el archivo de [homologacion.xlsx](docs/Homologacion.xlsx) debe tener una estructura especial en la
    columna producto:
  - primero los productos individuales, primero poner botella y debajo poner lata.
  - seguidos de los productos en packs (x4 o x6 unidades), primero poner botella y debajo poner lata.
- **input**: contiene los archivos (no credenciales) de entrada necesarios para la correcta ejecución
del aplicativo:
  - **[input.json](input/input.json)**: Contiene información de los comercios y productos/marcas.
    - STORES: Contienen nombre de comercios en mayúsculas y opcionalmente con tildes, a su vez tienen:
      - URL: con ruta con parametros en formato "{prod}"
      - LOCATIONS: compuestos por la llave "NOMBRE_DEPARTAMENTO NOMBRE_CIUDAD", con sus respectivos valores en formato
      de lista y conformados por los nombres de los puntos de venta. Las palabras que conformen el nombre del 
      departamento (e igual para ciudad), deben estar separadas por guion bajo ("_"). Para separar departamento y ciudad se
      debe usar espacio (" ").
    - BRANDS: organizadas según dos categorías: CERVEZA y OTROS. **Nuevos productos/marcas** deben ser agregados en
    mayúsculas. Estos pueden incluir tildes o 'Ñ'.  
  
  Este archivo es invocado en **[settings.py](settings/settings.py)**.
  
  - **[input_test.json](input/input_test.json)**: Archivo similar a **[input.json](input/input.json)**, pero para realizar
  pruebas cortas. Este archivo puede ser invocado en **[settings.py](settings/settings.py)**.
- **logs**: Contiene los logs generados en la ejecución de los scrapers de cada comercio. Pueden ser configurados
  desde el archivo **[settings.json](settings/settings.py)**.
- **output**: Aquí se guardan los CSV con la información obtenida de los comercios.
- **settings**:
  - **[settings.py](settings/settings.py)**: Configuración inicial para:
    - Invocar y cargar las variables de entorno (archivo **[.env](.env)** en la raíz) necesarias para el funcionamiento
    del programa.
    - Configurar sistema de logs.
    - Cargar o declarar variables globales.
- **src**: Contiene el código fuente entre las siguientes carpetas:
  - **models**
    - **[models.py](src/models/models.py)**: Contiene el modelo/clase principal _Stores_, para organizar la información principal de los
    comercios.
  - **scrapers**: Scripts que realizan el scraping y el formateo de los datos recolectados **por cada comercio** a 
  inspeccionar.
  - **[utils.py](src/utils.py)**: Contiene **funciones** para **normalizar la información recolectada** y para **enviar datos a Azure
  Blob Storage**.
- **[.env](.env)**: Archivo con las variables de entorno (credenciales para enviar datos a Azure Blob Storage) 
necesarias para la ejecución de la aplicación. **DEBE SER CREADO MANUALMENTE y NO SE PUEDE SUBIR AL REPOSITORIO** como
lo establece el archivo **[.gitignore](.gitignore)**.
- **[.gitignore](.gitignore)**: Archivo git con la lista de folders/archivos que no deben ser subidos al repositorio.
- **[main.py](main.py)**: Script principal de la aplicación.
- **README.md**: El presente archivo de documentación.
- **[requirements.txt](requirements.txt.cp)**: Archivo con la lista de librerias requeridas para el funcionamiento de la aplicación.

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
3. Activar el entorno virtual e instalar los requerimientos usando el archivo **[requirements.txt](requirements.txt.cp)**:

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

4. Crear archivo **.env** y agregarle el contenido requerido
````text
STORAGE_SAS_URL=https://<url>
STORAGE_DEST_FOLDER=<azure_blob_storage_path>
STORAGE_DEST_FOLDER_HIST=<azure_blob_storage_path>
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
````
- Para ver en el navegador la ejecucion (puede servir para debugging) usar la bandera "-v" o "--verbose":
````shell
python main.py -v
python main.py --verbose
````
- Para consultar la ayuda:
````shell
python main.py -h
python main.py --help
````
Obtendrá la salida:
````shell
usage: main.py [-h] [-st STORE] [-ns] [-v]

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
  -v, --verbose         Show browser
````
### Anomalías
- Makro: hay que estar atentos con algunos nombres de departamentos y de ciudades, los cuales en el diccionario pueden
  llevar tilde, pero en la lista de makro es algo arbitrario, tendrán o no tendrán tildes. Esto se ve reflejado en
  cómo están escritos estos dos elementos dentro del archivo [input.json](input/input.json). En el codigo es
  **importante** cargarlos en **minúsculas**.
- **Todos los comercios** deben ser ejecutados con la ventana maximizada, independientemente de si se visualiza o no el
  navegador, por eso se pone en [main.py](main.py):

````
chrome_options.add_argument("start-maximized")
````
- Es aconsejable, con el código actual, ejecutar puntualmente cada comercio por separado, puesto que si se corren en
  línea tomaría mucho tiempo. Esto se puede solucionar si se implementan hilos, ejecutando cada comercio en uno de 
  estos.
