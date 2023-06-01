from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore as firestore_init, credentials
from json import load
from flask import Flask, request
from flask_cors import CORS
import google.generativeai as palm
from datetime import datetime

with open('env.json', 'r') as f:
    env = load(f)
with open('data.json', 'r') as f:
    data = load(f)

# palm.list_models() shows that this is the limit for models/embedding-gecko-001.
token_limit = 1024

service_account_credentials = credentials.Certificate('service_account.json')
initialize_app(service_account_credentials)
firestore = firestore_init.client()
embeddings_collection = firestore.collection('embeddings')
app = Flask(__name__)
CORS(app)
palm.configure(api_key=env['palm'])

@app.get('/batch_generate_embeddings')
def batch_generate_embeddings():
    n = 0
    for checksum in data:
        if n > 300:
            continue
        # TODO: Check if data already exists for this section.
        text = data[checksum]['text']
        token_count = palm.count_message_tokens(prompt=text)['token_count']
        firebase_data = {'token_count': token_count}
        if token_count < token_limit:
            embedding = palm.generate_embeddings(text=text, model='models/embedding-gecko-001')
            firebase_data['data'] = embedding
        doc = embeddings_collection.document(checksum)
        doc.set(firebase_data)
        n += 1
    return datetime.now()

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

# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     message = data['message']
#     return https_fn.Response(message)
