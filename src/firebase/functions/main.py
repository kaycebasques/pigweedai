from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore as firestore_init
from json import load
from flask import Flask, request
from flask_cors import CORS
import google.generativeai as palm

with open('env.json', 'r') as f:
    env = load(f)
with open('data.json', 'r') as f:
    data = load(f)

initialize_app()
firestore = firestore_init.client()
embeddings_collection = firestore.collection('embeddings')
app = Flask(__name__)
CORS(app)
palm.configure(api_key=env['palm'])

n = 0
for checksum in data:
    if n > 10:
        continue
    text = data[checksum]['text']
    token_count = palm.count_message_tokens(prompt=text, model='models/text-bison-001')['token_count']
    embedding = palm.generate_embeddings(text=text, model='models/embedding-gecko-001')
    doc = embeddings_collection.document(checksum)
    doc.set({'token_count': token_count, 'embedding': embedding})
    n += 1

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
