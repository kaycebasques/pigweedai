from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore as firestore_init, credentials
from json import load
from flask import Flask, request
from flask_cors import CORS
import google.generativeai as palm
from datetime import datetime
from time import sleep

# Load PaLM API key. env.json is not checked into the repo. It needs
# to be in the same directory as this main.py file when the Firebase
# Functions are deployed.
with open('env.json', 'r') as f:
    env = load(f)
# At this point the database only has: the full text of each section,
# the URL of the doc that each section is a part of, and the checksum
# for each section.
with open('database.json', 'r') as f:
    database = load(f)

# palm.list_models() shows that this is the limit for models/embedding-gecko-001.
token_limit = 1024

# service_account.json has the Firebase service account credentials.
# It is not checked into this repo and needs to be in the same directory
# as this main.py file when the Firebase Functions are deployed.
service_account_credentials = credentials.Certificate('service_account.json')
initialize_app(service_account_credentials)
firestore = firestore_init.client()
embeddings = firestore.collection('embeddings')
app = Flask(__name__)
CORS(app)
palm.configure(api_key=env['palm'])

# Load the token count and embedding data from Firebase into the local database.
docs = embeddings.stream()
for doc in docs:
    doc_data = doc.to_dict()
    checksum = doc_data['checksum']
    if checksum not in database:
        continue
    if 'token_count' in doc_data:
        database[checksum]['token_count'] = doc_data['token_count']
    if 'embedding' in doc_data:
        database[checksum]['embedding'] = doc_data['embedding']

# Generate token counts and embeddings for any remaining sections that
# don't have them yet.
n = 0
for checksum in database:
    # Rate limit is 300 requests per minute.
    if n > 250:
        sleep(65)
        n = 0
        continue
    section = database[checksum]
    if 'embedding' in section and 'token_count' in section:
        continue
    text = section['text']
    token_count = palm.count_message_tokens(prompt=text)['token_count']
    new_data = {'token_count': token_count}
    # There's no point in generating an embedding if the token size of
    # the section's text is larger than the model's token limit.
    if token_count < token_limit:
        embedding = palm.generate_embeddings(text=text, model='models/embedding-gecko-001')
        new_data['embedding'] = embedding
    doc = embeddings.document(checksum)
    doc.set(new_data)
    n += 1

@app.post('/count_tokens')
def count_tokens():
    text = request.get_json()['text']
    token_count = palm.count_message_tokens(prompt=text)['token_count']
    return {'token_count': token_count}

@app.post('/api/query')
def chat():
    message = request.get_json()['query']
    response = palm.chat(messages=message)
    return {
        'answer': response.last,
        'context': 'N/A',
        'vanilla': 'N/A'
    }

@https_fn.on_request()
def server(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
