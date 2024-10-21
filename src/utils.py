import re

import numpy as np
import pandas as pd
import unicodedata
from azure.storage.blob import ContentSettings
from pathlib import Path
import requests
import mimetypes
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def remove_accents(text):
    # Normaliza el texto en forma NFD (descompone caracteres acentuados)
    nfkd_form = unicodedata.normalize('NFD', text)
    # Filtra los caracteres diacríticos (como los acentos)
    text_without_accents = ''.join([char for char in nfkd_form if not unicodedata.combining(char)])
    text_without_accents = text_without_accents.upper()
    text_without_accents = text_without_accents.replace('Ñ', 'N')
    return text_without_accents


def upload_blob_file(storage_sas_url: str, dst_folder: str, file_path: Path):
    url = urlparse(storage_sas_url)
    account_url = url.scheme + "://" + url.netloc + "/"
    container_name = url.path[1:] if url.path[0] == '/' else url.path
    query_string = url.query

    file_name = file_path.name
    file_ext = file_path.suffix
    content_type_string = ContentSettings(content_type=mimetypes.types_map[file_ext]) if file_ext else None
    with open(file_path, 'rb') as data:
        response = requests.put(
            account_url + container_name + '/' + dst_folder + file_name + '?' + query_string,
            data=data,
            headers={
                'content-type': content_type_string.content_type,
                'x-ms-blob-type': 'BlockBlob'
            },
            params={'file': file_path}
        )
    return response.status_code


def add_sku(data):
    hml = pd.read_excel("docs/Homologacion.xlsx", dtype=str)
    hml['variante'] = hml['variante'].str.upper().replace(",", ".")
    hml['producto'] = hml['producto'].str.upper()
    hml['SKU'] = hml['SKU'].astype(str)
    df = pd.DataFrame(
        data=[item.split("|") for item in data],
        columns=["MARCA", "CIUDAD", "POS", "PRODUCTO", "PRECIO"],
        dtype=str
    )
    df['SKU'] = None
    for i, row in hml.iterrows():
        trademark = remove_accents(row['trademark'])
        variant = row['variante'] if row['variante'] is not np.nan else ' '
        vol = re.search(r"(?<=[(x])\d+\s*ml", row['producto'], re.IGNORECASE)
        vol = vol.group() if vol else ' '
        units = re.search(r"(?<=x)\d+und", row['producto'], re.IGNORECASE)
        units = units.group() if units else ' '

        df['SKU'] = np.where(
            (df['PRODUCTO'].str.contains(trademark))
            & (df['PRODUCTO'].str.contains(variant))
            & (df['PRODUCTO'].str.contains(units))
            & (df['PRODUCTO'].str.contains(vol)),
            row['SKU'],
            df['SKU']
        )
    df['PRECIO'] = df['PRECIO'].str.replace(r',00$', '', regex=True)
    return df


def wait_driver(driver, locator: tuple[str, str], timeout=10):
    WebDriverWait(
        driver, timeout
    ).until(
        ec.presence_of_element_located(
            locator
        )
    )
