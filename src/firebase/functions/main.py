from firebase_functions import https_fn
from firebase_functions.options import MemoryOption
from firebase_admin import initialize_app, firestore, credentials
from json import load, dumps, dump
from flask import Flask, request
from flask_cors import CORS
from time import time
import numpy as np
from markdown import markdown
from hashlib import md5
from math import ceil
import openai
from tiktoken import get_encoding

################
# Initialization
################

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
openai_chat_model = 'gpt-3.5-turbo'
openai_total_token_limit = 4096
openai_input_token_limit = 2800
openai_output_token_limit = 1000
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

###################
# General utilities
###################

def get_timestamp():
    return ceil(time())

################
# Business logic
################

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
    results = []
    for item in distances:
        checksum = item['checksum']
        if current_token_count > openai_input_token_limit:
            continue
        if current_token_count + item['token_count'] > openai_input_token_limit:
            continue
        if 'text' not in database[checksum]:
            ref = embeddings.document(checksum)
            doc = ref.get()
            data = doc.to_dict()
            database[checksum] = data
        clone = dict(database[checksum])
        clone.pop('openai')
        clone.pop('openai_token_count')
        results.append(clone)
        current_token_count += item['token_count']
    return results

def create_context(message):
    embedding = create_openai_embedding(message)
    data = find_relevant_docs(embedding)
    links = []
    unique_urls = set()
    for item in data:
        if item['url'] in unique_urls:
            continue
        links.append({'title': item['title'], 'url': item['url']})
        unique_urls.add(item['url'])
    # TODO: Should we add links into the context that the LLM sees?
    sections = ''.join([item['text'] for item in data])
    document = f'<document>{sections}</document>'
    question = f'<question>{message}</question>'
    context = (
        'The user is developing an embedded system with Pigweed, the software project.'
        'Answer the following question about Pigweed. The question is everything between <question> and </question>.'
       f'{question}'
        'Answer in Markdown.'
        'Parse the following Docutils document and use its information in your answer. Do not mention Docutils.'
       f'{document}'
    )
    return {'context': context, 'links': links}

def create_openai_embedding(text):
    response = openai.Embedding.create(input=[text], model=openai_embedding_model)
    return response['data'][0]['embedding']

def get_openai_token_count(text):
    return len(openai_encoder.encode(text))

# TODO: This is probably not getting saved because earlier in the process
# all the data is getting clobbered.
def create_summary(checksum, text):
    print('create_summary()')
    print(checksum)
    try:
        ref = embeddings.document(checksum)
        doc = ref.get()
        data = {}
        if doc.exists:
            print('doc found')
            data = doc.to_dict()
            print(data.keys())
            if 'summary' in data:
                print('summary found')
                return data['summary']
        print('generating summary')
        instruction = f'Output a single plain text paragraph. Summarize this: {text}'
        messages = [{
            'role': 'user',
            'content': instruction
        }]
        model = 'gpt-3.5-turbo'
        response = openai.ChatCompletion.create(model=model, messages=messages,
                temperature=0, max_tokens=100)
        summary = response['choices'][0]['message']['content']
        data['summary'] = summary
        ref.set({'summary': summary}, merge=True)
        return summary
    except Exception as e:
        print(e)
        return None

##############
# URL handlers
##############

@app.post('/chat')
def chat():
    print('POST /chat')
    try:
        data = request.get_json()
        message = data['message']
        response = openai.Moderation.create(input=message)
        if response['results'][0]['flagged']:
            return {'ok': False}
        uuid = data['uuid']
        history = data['history']
        context_data = create_context(message)
        context = context_data['context']
        links = context_data['links']
        messages = {'role': 'user', 'content': context}
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[messages],
                temperature=0, max_tokens=openai_output_token_limit)
        question_id = f'question{get_timestamp()}'
        messages['question_id'] = question_id
        # The history is only logged for our own analysis. It's not
        # sent to the LLM. I.e. the LLM has no knowledge of the convo history.
        history.append(messages)
        reply = response.choices[0].message.content
        reply_id = f'reply{get_timestamp()}'
        history.append({'role': 'assistant', 'content': reply, 'question_id': question_id, 'reply_id': reply_id})
        ref = chats.document(uuid)
        ref.set({'history': history})
        mode = data['mode']
        if mode == 'html':
            reply = markdown(reply, extensions=['markdown.extensions.fenced_code'])
        return {'reply': reply, 'history': history, 'links': links, 'id': reply_id}
    except Exception as e:
        print(e)
        return {'ok': False}

@app.post('/create_embedding')
def create_embedding():
    print('POST /create_embedding')
    try:
        data = request.get_json()
        print(data['title'])
        print(data['url'])
        text = data['text']
        checksum = md5(text.encode('utf-8')).hexdigest()
        ref = embeddings.document(checksum)
        firestore_doc = ref.get()
        if firestore_doc.exists:
            print('Doc found')
            firestore_data = firestore_doc.to_dict()
            if not 'openai' in firestore_data or firestore_data['openai'] is None:
                print('Embeddings data was missing...')
                data['openai'] = create_openai_embedding(text)
                data['openai_token_count'] = get_openai_token_count(text)
            else:
                print('Embeddings data OK...')
                data['openai'] = firestore_data['openai']
                data['openai_token_count'] = firestore_data['openai_token_count']
            # TODO: Refactor this.
            if 'summary' in firestore_data:
                data['summary'] = firestore_data['summary']
        else:
            print('Doc did not exist...')
            data['openai'] = create_openai_embedding(text)
            data['openai_token_count'] = get_openai_token_count(text)
        data['timestamp'] = get_timestamp()
        ref.set(data)
        summary = create_summary(checksum, text)
        print(f'Summary: {summary}')
        return {'summary': summary}
    except Exception as e:
        print(e)
        return {'ok': False}

@app.post('/send_feedback')
def send_feedback():
    print('POST /send_feedback')
    try:
        data = request.get_json()
        message_id = data['message_id']
        uuid = data['uuid']
        feedback = data['feedback']
        ref = chats.document(uuid)
        doc = ref.get()
        if not doc.exists:
            return {'ok': False}
        doc_data = doc.to_dict()
        for message in doc_data['history']:
            if message['role'] != 'assistant':
                continue
            if message['reply_id'] != message_id:
                continue
            message['feedback'] = feedback
            ref.set(doc_data)
        return {'ok': True}
    except Exception as e:
        return {'ok': False}

@app.post('/debug')
def post_debug():
    print('POST /debug')
    data = request.get_json()
    print(data)
    return {'ok': True}

@app.get('/debug')
def debug():
    print('GET /debug')
    create_context('Hello, world!')
    return {'ok': True}

@app.get('/ping')
def ping():
    print('GET /ping')
    return {'ok': True}

@app.get('/version')
def version():
    return {'version': '0.0.0'}

@https_fn.on_request(timeout_sec=90, memory=MemoryOption.GB_1)
def server(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()
