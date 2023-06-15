from firebase_admin import initialize_app, firestore as _firestore, credentials
from json import load, dump, dumps
from pprint import pprint
from requests import get, post
from os import mkdir
from zipfile import ZipFile
from shutil import rmtree

# General setup stuff
service_account_credentials = credentials.Certificate('src/firebase/functions/service_account.json')
initialize_app(service_account_credentials)
firestore = _firestore.client()
embeddings = firestore.collection('embeddings')
data = {}
url = 'http://127.0.0.1:5001/palmweed-prototype/us-central1/server'
version_url = f'{url}/version'
chat_url = f'{url}/chat'
unescaped_version = get(version_url).json()['version']
version = unescaped_version.replace('.', '_')
data_dir = f'eval-{version}'
mkdir(data_dir)

# Save the embeddings database
docs = embeddings.stream()
for doc in docs:
    checksum = doc.id
    data[checksum] = doc.to_dict()
with open(f'{data_dir}/embeddings.json', 'w') as f:
    dump(data, f, indent=4)

# Run the eval tests and save the results
questions = None
results = {}
with open('src/eval/questions.json', 'r') as f:
    questions = load(f)
headers = {'Content-Type': 'application/json'}
for category in questions:
    for question in questions[category]['questions']:
        print(question)
        print()
        data = {
            'message': question,
            'uuid': f'eval-{version}',
            'history': [],
            'mode': None,
        }
        retries = 0
        reply = None
        while retries < 5:
            try:
                response = post(chat_url, data=dumps(data), headers=headers)
                json = response.json()
                if 'reply' not in json:
                    raise ValueError('Not a usable response from OpenAI...')
                reply = json['reply']
            except Exception as e:
                retries += 1
                continue
            break
        if reply is None:
            raise ValueError('OpenAI did not provide a usable response even after retries...')
        print(reply)
        print()
        results[question] = reply
        with open(f'{data_dir}/eval.json', 'w') as f:
            dump(results, f, indent=4)

# Cleanup
with ZipFile(f'{version}.zip', 'w') as z:
    z.write(data_dir)
# rmtree(data_dir)
