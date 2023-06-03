from firebase_functions import https_fn
from firebase_functions.options import MemoryOption
from firebase_admin import initialize_app, firestore as firestore_init, credentials
from firebase_admin.exceptions import FirebaseError
from json import load
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as palm
from datetime import datetime
from time import sleep
import numpy as np
from traceback import print_exc
from markdown import markdown

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
embedding_model = 'models/embedding-gecko-001'
chat_model = 'models/text-bison-001'

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
    checksum = doc.id
    if checksum not in database:
        continue
    if 'token_count' in doc_data:
        database[checksum]['token_count'] = doc_data['token_count']
    if 'embedding' in doc_data:
        database[checksum]['embedding'] = doc_data['embedding']

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
    limit = 2000
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

def get_docs_context(message):
    # TODO: Return the context string AND paths.
    pass

def markdown_to_html(markdown):
    pass

def normalize_text(text):
    return text.replace('\n', ' ')

def generate_summary(prompt):
    response = palm.generate_text(model='models/text-bison-001',
            prompt=prompt, temperature=0)
    if response.result is None:
        return 'PaLM was unable to generate a summary.'
    return response.result

@app.post('/chat')
def chat():
    try:
        print('Chat request received')
        message = request.get_json()['message']
        print(f'Message from user: {message}')
        history = request.get_json()['history']
        embedding = palm.generate_embeddings(text=message,
                model=embedding_model)['embedding']
        data = closest(embedding)
        paths = [item['path'] for item in data]
        print('Semantic search done')
        docs = [item['text'] for item in data]
        docs = ' '.join(docs)
        docs = normalize_text(docs)
        summary_prompt = f'Summarize the following documentation. Use complete sentences. {docs}'
        history.append({
            'author': 'user',
            'content': summary_prompt
        })
        history.append({
            'author': 'palm',
            'content': generate_summary(summary_prompt)
        })
        history.append({
            'author': 'user',
            'content': f'Use the summary from your last reply to respond to this prompt: {message}'
        })
        response = palm.chat(messages=history, temperature=0)
        print('Response from PaLM:')
        print(response)
        reply = response.last
        if reply is None:
            reply = 'PaLM was unable to answer that.'
        history.append({
            'author': 'palm',
            'content': reply
        })
        html = markdown(reply,
                extensions=['markdown.extensions.fenced_code'])
        print('HTML generated')
        return {
            'reply': html,
            'history': history,
            'paths': paths
        }
    except Exception as e:
        print(f'Exception: {e}')
        print('Exception stack trace:')
        print_exc()
        return {
            'error': str(e)
        }

@app.post('/count_tokens')
def count_tokens():
    try:
        body = request.get_json()
        print(body)
        text = body['text']
        response = palm.count_message_tokens(prompt=text)
        print(response)
        return {'token_count': response['token_count']}
    except Exception as e:
        print(e)
        return {'token_count': None}
 
@https_fn.on_request(timeout_sec=120, memory=MemoryOption.MB_512)
def server(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
