from datetime import datetime

import unicodedata
from azure.storage.blob import ContentSettings
from pathlib import Path
import requests
import mimetypes
from urllib.parse import urlparse


def remove_accents(text):
    # Normaliza el texto en forma NFD (descompone caracteres acentuados)
    nfkd_form = unicodedata.normalize('NFD', text)
    # Filtra los caracteres diacríticos (como los acentos)
    text_without_accents = ''.join([char for char in nfkd_form if not unicodedata.combining(char)])
    # Reemplazar la ñ y Ñ manualmente
    return text_without_accents.replace('ñ', 'n').replace('Ñ', 'N')


def upload_blob_file(storage_sas_url: str, dst_folder: str, file_path: Path):
    url = urlparse(storage_sas_url)
    account_url = url.scheme + "://" + url.netloc + "/"
    container_name = url.path[1:] if url.path[0] == '/' else url.path
    query_string = url.query

    dt = datetime.now()
    file_name = dt.strftime(f'{file_path.stem}_%Y%m%d')
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
