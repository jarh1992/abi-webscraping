import os

import unicodedata
from azure.storage.blob import BlobServiceClient
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(override=True)


def remove_accents(text):
    # Normaliza el texto en forma NFD (descompone caracteres acentuados)
    nfkd_form = unicodedata.normalize('NFD', text)
    # Filtra los caracteres diacríticos (como los acentos)
    text_without_accents = ''.join([char for char in nfkd_form if not unicodedata.combining(char)])
    # Reemplazar la ñ y Ñ manualmente
    return text_without_accents.replace('ñ', 'n').replace('Ñ', 'N')


def upload_blob_file(conn_str: str, container_name: str, filepath: str):
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_str)
    file = Path(filepath)
    with file.open('rb') as data:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.name)
        blob_client.upload_blob(data)


# storage_account_key = os.getenv('STORAGE_ACCOUNT_KEY')
# storage_account_name = os.getenv('STORAGE_ACCOUNT_NAME')
# connection_string = os.getenv('CONNECTION_STRING')
# ctr_name = os.getenv('CTR_NAME')
# account_url = f"https://{storage_account_name}.blob.core.windows.net"
# upload_blob_file(conn_str=connection_string, container_name=ctr_name, filepath='Jumbo/output/xxx.txt')
