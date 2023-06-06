from firebase_functions import https_fn
from firebase_functions.options import MemoryOption
from firebase_admin import initialize_app, firestore, credentials
from json import load, dumps
from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
from time import time
import numpy as np
from markdown import markdown
from hashlib import md5
from math import ceil
import openai
from tiktoken import get_encoding

database = {}
with open('env.json', 'r') as f:
    env = load(f)
service_account_credentials = credentials.Certificate('service_account.json')
initialize_app(service_account_credentials)
firestore_client = firestore.client()
embeddings = firestore_client.collection('embeddings')
chats = firestore_client.collection('chats')
app = Flask(__name__)
CORS(app)
openai.api_key = env['openai']
openai_embedding_model = 'text-embedding-ada-002'
openai_encoder = get_encoding('cl100k_base')
# Load the Firestore embeddings data to the in-memory "database".
docs = embeddings.stream()
for doc in docs:
    data = doc.to_dict()
    checksum = doc.id
    if 'openai' not in data or 'openai_token_count' not in data:
        continue
    if data['openai'] is None or data['openai_token_count'] is None:
        continue
    # Don't load the other data until it's needed.
    database[checksum] = {
        'openai': data['openai'],
        'openai_token_count': data['openai_token_count']
    }

def get_timestamp():
    return ceil(time())

def find_relevant_docs(target):
    distances = []
    for checksum in database:
        doc = database[checksum]
        candidate = doc['openai']
        token_count = doc['openai_token_count']
        distance = np.dot(target, candidate)
        distances.append({
            'checksum': checksum,
            'distance': distance,
            'token_count': token_count
        })
    distances = sorted(distances, key=lambda item: item['distance'])
    distances.reverse()
    current_token_count = 0
    token_limit = 1000
    results = []
    for item in distances:
        checksum = item['checksum']
        if current_token_count > token_limit:
            continue
        if current_token_count + item['token_count'] > token_limit:
            continue
        if 'text' not in database[checksum]:
            ref = embeddings.document(checksum)
            doc = ref.get()
            data = doc.to_dict()
            database[checksum] = data
        clone = dict(database[checksum])
        clone.pop('openai')
        results.append(clone)
        current_token_count += item['token_count']
    return results

@app.get('/debug')
def debug():
    print(database)
    return {'ok': True}

def update_chat_logs(uuid, author, message, context=None):
    ref = chats.document(uuid)
    doc = ref.get()
    data = doc.to_dict()
    if data is None:
        data = {'convo': []}
    data['convo'].append({'author': 'user', 'message': message, 'timestamp': get_timestamp()})
    ref.set(data)
    data['convo'].append({'author': 'palm', 'message': reply, 'context': context, 'timestamp': get_timestamp()})
    ref.set(data)

    # author message timestamp for user messages
    # author message timestamp context paths for palm
    pass

def create_context(message):
    embedding = create_openai_embedding(message)
    data = find_relevant_docs(embedding)
    sections = [item['text'] for item in data]
    sections = ''.join(sections)
    document = f'<document>{sections}</document>'
    question = f'<question>{message}</question>'
    instructions = [
        'Help the user develop an embedded system with Pigweed.',
        'Answer the following question:',
        question,
        'Use information from the following Docutils document tree in your answer.',
        document
    ]
    context = ' '.join(instructions)
    return context

@app.post('/chat')
def chat():
    try:
        data = request.get_json()
        message = data['message']
        uuid = data['uuid']
        # context = create_context(message)
        # TODO: Escape the JSON string.
        # response = palm.generate_text(prompt=dumps(context), temperature=0)
        # reply = response.result
        model = 'models/chat-bison-001'
        # response = palm.chat(messages=message, context=context, temperature=0, model=model)
        response = palm.chat(messages=message, temperature=0, model=chat_model)
        reply = response.last
        html = markdown(reply, extensions=['markdown.extensions.fenced_code'])
        return {
            'reply': html
        }
    except Exception as e:
        return {'ok': False}

def create_openai_embedding(text):
    response = openai.Embedding.create(input=[text], model=openai_embedding_model)
    return response['data'][0]['embedding']

def get_openai_token_count(text):
    return len(openai_encoder.encode(text))

@app.post('/create_embedding')
def create_embedding():
    print('POST /create_embedding')
    data = request.get_json()
    text = data['text']
    checksum = md5(text.encode('utf-8')).hexdigest()
    data['timestamp'] = get_timestamp()
    ref = embeddings.document(checksum)
    firestore_doc = ref.get()
    firestore_data = firestore_doc.to_dict() if firestore_doc.exists else None
    openai_embedding = None
    openai_token_count = None
    ok = firestore_data is None or \
            firestore_data['openai'] is None or \
            firestore_data['openai_token_count'] is None
    if not ok:
        openai_embedding = create_openai_embedding(text)
        openai_token_count = get_openai_token_count(text)
    data['openai_token_count'] = openai_token_count
    data['openai'] = openai_embedding
    ref.set(data)
    return {'ok': True}

@https_fn.on_request(timeout_sec=120, memory=MemoryOption.MB_512)
def server(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
