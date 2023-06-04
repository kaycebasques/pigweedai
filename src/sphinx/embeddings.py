# Copyright 2023 The Pigweed Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from docutils import nodes
from hashlib import md5
from json import dump, load, dumps
from copy import deepcopy
from os.path import exists, join
from os import makedirs, remove
from glob import glob
from requests import post
from math import floor, ceil
from time import sleep

# TODO: Explain how this relates to the embedding model and chunking logic.
token_limit = 500
server = 'http://127.0.0.1:5001/palmweed-prototype/us-central1/server'

def split_doc_into_embeddable_chunks(doc, doc_size_in_tokens):
    num_of_chunks = ceil(doc_size_in_tokens / token_limit)
    chunk_size_in_tokens = ceil(doc_size_in_tokens / num_of_chunks)
    len_of_doc_in_chars = len(doc)
    chunk_size_in_chars = floor(len_of_doc_in_chars / num_of_chunks)
    chunk_start_index = 0
    chunk_end_index = chunk_size_in_chars
    chunks = []
    while chunk_end_index < len_of_doc_in_chars:
        chunk = doc[chunk_start_index:chunk_end_index]
        token_count = get_token_count(chunk)
        chunks.append({
            'text': chunk,
            'token_count': token_count
        })
        chunk_start_index += chunk_size_in_chars
        chunk_end_index += chunk_size_in_chars
        # Termination case.
        if chunk_end_index > len_of_doc_in_chars:
            chunk = doc[chunk_start_index:chunk_end_index]
            token_count = get_token_count(chunk)
            chunks.append({
                'text': chunk,
                'token_count': token_count
            })
    return chunks

def get_token_count(text):
    try:
        url = f'{server}/count_tokens'
        data = {'text': text}
        headers = {'Content-Type': 'application/json'}
        response = post(url, data=dumps(data), headers=headers)
        return response.json()['token_count']
    except Exception as e:
        return None

def generate_embeddings_for_docs(app, doctree, docname):
    clone = deepcopy(doctree)
    doc_text = clone.astext()
    # if 'pw_rpc' not in doc_text:
    #     return
    doc_token_count = get_token_count(doc_text)
    if doc_token_count is None:
        return
    chunks = split_doc_into_embeddable_chunks(doc_text, doc_token_count)
    url = f'{server}/generate_embedding'
    for chunk in chunks:
        headers = {'Content-Type': 'application/json'}
        data = {
            'text': chunk['text'],
            'path': app.builder.get_target_uri(docname),
            'token_count': chunk['token_count']
        }
        # This is a blocking call. We don't care about the response so maybe
        # we should use a non-blocking alternative in the future. It would have
        # to be another library because requests only offers the blocking API.
        # For now, it's probably good to slow down these requests because the
        # embedding API has a rate limit of 300 requests per minute.
        post(url, data=dumps(data), headers=headers)
        sleep(1) # Also to help stay within the rate limits.

def generate_embeddings_for_headers(app, exception):
    # This is a silly hack to reach allllllllll the way back to the real
    # Pigweed repo root directory and find the headers there.
    headers = glob(f'{app.srcdir}/../../../../../pw_*/public/**/*.h', recursive=True)
    # with open(f'{app.outdir}/headers.json', 'w') as f:
    #     dump({'headers': headers}, f, indent=4)
    url = f'{server}/generate_embedding'
    for header in headers:
        if 'internal' in header:
            continue
        with open(header, 'r') as f:
            doc_text = f.read()
        # if 'pw_rpc' not in doc_text:
        #     continue
        doc_token_count = get_token_count(doc_text)
        if doc_token_count is None:
            return
        chunks = split_doc_into_embeddable_chunks(doc_text, doc_token_count)
        for chunk in chunks:
            headers = {'Content-Type': 'application/json'}
            target = '/../../../../..'
            index = header.index(target) + len(target)
            path = header[index:]
            data = {
                'text': chunk['text'],
                'path': path,
                'token_count': chunk['token_count']
            }
            post(url, data=dumps(data), headers=headers)

def setup(app):
    app.connect('doctree-resolved', generate_embeddings_for_docs)
    app.connect('build-finished', generate_embeddings_for_headers)
    return {
        'version': '0.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
