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
embeddings = firestore.collection('embeddings')
data = {}
url = 'http://127.0.0.1:5001/palmweed-prototype/us-central1/server'
version_url = f'{url}/version'
unescaped_version = get(version_url).json()['version']
version = unescaped_version.replace('.', '_')
data_dir = f'src/eval/{version}'
# mkdir(data_dir)

questions = []

for doc in firestore.collection('chats').stream():
    chat = doc.to_dict()
    for message in chat['history']:
        if message['role'] != 'user':
            continue
        context = message['content']
        start_pattern = '</question>.<question>'
        start = context.index(start_pattern) + len(start_pattern)
        end_pattern = '</question>'
        substring = context[start:]
        end = substring.index(end_pattern)
        question = substring[0:end]
        questions.append(question)

with open('questions.json', 'w') as f:
    dump({'questions': questions}, f, indent=4)
