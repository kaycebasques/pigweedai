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

from docutils.nodes import section
from hashlib import md5
from json import dumps
from copy import deepcopy
from os import getcwd
from requests import post, get

server = 'https://server-ic22qaceya-uc.a.run.app'
if 'kayce' in getcwd():
    server = 'http://127.0.0.1:5001/palmweed-prototype/us-central1/server'
create_embedding_url = f'{server}/create_embedding'

def init(app):
    # Throws an unhandled exception if the server isn't available.
    get(server)

def find_title(doctree):
    for node in doctree.traverse():
        if node.tagname == 'title':
            return node.astext()

def create_embedding(text, token_count, title, url):
    headers = {'Content-Type': 'application/json'}
    data = {
        'text': text,
        'title': title,
        'url': url
    }
    post(create_embedding_url, data=dumps(data), headers=headers)

def create_embeddings(app, doctree, docname):
    if 'pw_rpc' not in docname:
        return
    clone = deepcopy(doctree)
    title = find_title(clone)
    url = f'https://pigweed.dev/{app.builder.get_target_uri(docname)}'
    for node in clone.traverse(section):
        try:
            xml = node.asdom().toxml()
            create_embedding(xml, title, url)
        except Exception as e:
            continue

def setup(app):
    app.connect('builder-inited', init)
    app.connect('doctree-resolved', create_embeddings)
    return {
        'version': '0.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
