from firebase_functions import https_fn
from firebase_functions.options import MemoryOption
from firebase_admin import initialize_app, firestore as firestore_init, credentials
from firebase_admin.exceptions import FirebaseError
from json import load
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as palm
from datetime import datetime
from time import sleep, time
import numpy as np
from traceback import print_exc
from markdown import markdown
from hashlib import md5
from math import ceil

database = {}
embedding_model = 'models/embedding-gecko-001'
chat_model = 'models/text-bison-001'
# palm.list_models() shows that this is the limit for models/embedding-gecko-001.
token_limit = 1024 # TODO: Is this needed anymore?
with open('env.json', 'r') as f:
    env = load(f)
service_account_credentials = credentials.Certificate('service_account.json')
initialize_app(service_account_credentials)
firestore = firestore_init.client()
embeddings = firestore.collection('embeddings')
app = Flask(__name__)
CORS(app)
palm.configure(api_key=env['palm'])
# Load the Firestore embeddings data to the in-memory "database".
docs = embeddings.stream()
for doc in docs:
    doc_data = doc.to_dict()
    checksum = doc.id
    database[checksum] = doc_data
# TODO: Create logic to remove entries that have not been timestamped for one month.
# TODO: Call the retry function.

# General utility functions.
def handle_exception(exception):
    print(f'Exception: {exception}')
    print('Exception stack trace:')
    print_exc()
    return {'error': exception}

def get_timestamp():
    return ceil(time())

def retry_embedding_generation():
    pass

def closest(target):
    # Calculate how far each docs section is from the target query.
    calculations = []
    for checksum in database:
        section = database[checksum]
        if 'embedding' not in section:
            continue
        candidate = section['embedding']
        distance = np.dot(target, candidate)
        calculations.append({
            'distance': distance,
            'text': section['text'],
            'token_count': section['token_count'],
            'path': section['path']
        })
    calculations = sorted(calculations, key=lambda item: item['distance'])
    calculations.reverse()
    tokens = 0
    # Keep this below the model's maximum limit so that there is space for the user's
    # query and for the prompt instructions.
    limit = 4000
    matches = []
    for item in calculations:
        if tokens > limit:
            continue
        if tokens + item['token_count'] > limit:
            continue
        matches.append(item)
        tokens += item['token_count']
    # TODO: Return all matches, not just the first one.
    return matches

@app.get('/debug')
def debug():
    response = palm.chat(messages='Hello!')
    return response.last

def get_context_and_paths(message):
    embedding = palm.generate_embeddings(text=message,
            model=embedding_model)['embedding']
    data = closest(embedding)
    paths = [item['path'] for item in data]
    documentation = '<documentation>'
    for item in data:
        text = item['text']
        path = item['path']
        documentation += f'<document><excerpt>{text}</excerpt><path>{path}</path></document>'
    documentation += '</documentation>'
    context = [
        'You are a friendly expert in developing embedded systems with Pigweed modules and tools.',
        'Answer this question from a Pigweed user:',
        f'<question>{message}</question>',
        "Summarize this documentation and use your summary in your answer:",
        documentation
    ]
    context = ' '.join(context)
    context = context.replace('\n', ' ')
    return {'context': context, 'paths': paths}

def update_chat_logs(uuid, author, message, context=None):
    # author message timestamp for user messages
    # author message timestamp context paths for palm
    pass

@app.post('/chat')
def chat():
    try:
        request_data = request.get_json()
        message = request_data['message']
        uuid = request_data['uuid']
        data = get_context_and_paths(message)
        context = data['context']
        paths = data['paths']
        response = palm.generate_text(prompt=context, temperature=0)
        reply = response.result
        html = markdown(reply, extensions=['markdown.extensions.fenced_code'])
        return {
            'reply': html,
            'paths': paths
        }
    except Exception as e:
        print(locals()) # TODO: Always pass locals to exception handler?
        return handle_exception(e)

def embed(text):
    response = palm.generate_embeddings(text=text, model=embedding_model)
    embedding = response['embedding']
    return response['embedding']

@app.post('/generate_embedding')
def generate_embedding():
    try:
        print('/generate_embedding')
        request_data = request.get_json()
        text = request_data['text']
        token_count = request_data['token_count']
        path = request_data['path']
        checksum = md5(text.encode('utf-8')).hexdigest()
        print(checksum)
        print(path)
        firebase_ref = embeddings.document(checksum)
        firebase_doc = firebase_ref.get()
        if firebase_doc.exists and 'embedding' in firebase_doc.to_dict():
            firebase_data = firebase_doc.to_dict()
            # Refresh the timestamp to indicate that this text is still fresh.
            firebase_data['timestamp'] = get_timestamp()
            firebase_ref.set(firebase_data)
            return {'embedding': firebase_doc.to_dict()['embedding']}
        new_data = {
            'text': text,
            'token_count': token_count,
            'path': path,
            'timestamp': get_timestamp()
        }
        # Save early because the the embedding API often fails.
        # Other parts of the server codebase try to complete the embedding
        # process later.
        firebase_ref.set(new_data)
        embedding = embed(text)
        new_data['embedding'] = embedding
        firebase_ref.set(new_data)
        return {'embedding': embedding}
    except Exception as e:
        return handle_exception(e)

@app.post('/count_tokens')
def count_tokens():
    try:
        print('/count_tokens')
        body = request.get_json()
        text = body['text']
        response = palm.count_message_tokens(prompt=text)
        return {'token_count': response['token_count']}
    except Exception as e:
        return handle_exception(e)
 
@https_fn.on_request(timeout_sec=120, memory=MemoryOption.MB_512)
def server(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
