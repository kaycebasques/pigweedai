from firebase_admin import initialize_app, firestore as _firestore, credentials
from json import load, dump
from pprint import pprint
from requests import get
from os import mkdir
from zipfile import ZipFile
from shutil import rmtree

service_account_credentials = credentials.Certificate('src/firebase/functions/service_account.json')
initialize_app(service_account_credentials)
firestore = _firestore.client()
collection = firestore.collection('embeddings')
embeddings_data = {}
web_service = 'http://127.0.0.1:5001/palmweed-prototype/us-central1/server'
version_url = f'{web_service}/version'
version = get(version_url).json()['version']
escaped_version = version.replace('.', '_')
data_dir = f'src/eval/{escaped_version}'
mkdir(data_dir)
docs = collection.stream()
for doc in docs:
    checksum = doc.id
    embeddings_data[checksum] = doc.to_dict()
with open(f'{data_dir}/embeddings.json', 'w') as f:
    dump(embeddings_data, f)
with ZipFile(f'{escaped_version}.zip', 'w') as z:
    z.write(data_dir)
rmtree(data_dir)
