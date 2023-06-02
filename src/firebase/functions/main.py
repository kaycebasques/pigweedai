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

def generate_summary(context):
    print('Summary generation request received')
    instructions = [
        'The user is trying to develop embedded systems with the Pigweed software project.',
        'Generate a summary of the following Pigweed documentation: ',
        context
    ]
    prompt = ' '.join(instructions)
    response = palm.generate_text(model='models/text-bison-001',
            prompt=prompt, temperature=0)
    print(f'Generated summary: {response.result}')
    return response.result

@app.post('/chat')
def chat():
    try:
        print('Chat request received')
        messages = request.get_json()['messages']
        last_message = messages[-1]['content']
        print(f'Message from user: {last_message}')
        embedding = palm.generate_embeddings(text=last_message,
                model=embedding_model)['embedding']
        data = closest(embedding)
        print('Semantic search done')
        information = [item['text'] for item in data]
        information = ' '.join(information)
        information = normalize_text(information)
        information = generate_summary(information)
        paths = [item['path'] for item in data]
        context = [
            'Use the following Pigweed information in your answer:',
            information
        ]
        context = ' '.join(context)
        response = palm.chat(messages=messages, context=context, temperature=0)
        print('Response from PaLM:')
        print(response)
        html = markdown(response.last, extensions=['markdown.extensions.fenced_code'])
        print('HTML generated')
        return {
            'response': html,
            'messages': response.messages,
            'paths': paths
        }
    except Exception as e:
        print(f'Exception: {e}')
        print('Exception stack trace:')
        print_exc()
        return {
            'error': str(e)
        }

@https_fn.on_request(timeout_sec=120, memory=MemoryOption.MB_512)
def server(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
