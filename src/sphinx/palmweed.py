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
from json import dump, load
from copy import deepcopy
from os.path import exists, join
from os import makedirs, remove
from glob import glob
from requests import post

def get_data_dir(app):
    return f'{app.outdir}/embeddings'

def init(app):
    data_dir = get_data_dir(app)
    if not exists(data_dir):
        makedirs(data_dir)

def prepare_database(app, doctree, docname):
    clone = deepcopy(doctree)
    text = clone.astext()
    # Only covering RPC docs for now.
    if 'pw_rpc' not in text:
        return
    checksum = md5(text.encode('utf-8')).hexdigest()
    url = 'https://server-ic22qaceya-uc.a.run.app/count_tokens'
    body = {
        'text': text
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = post(url, data=body, headers=headers)
    token_count = response.json()['token_count']
    data = {
        # 'text': text,
        'checksum': checksum,
        'path': app.builder.get_target_uri(docname),
    }
    name = f'{checksum}.json'
    path = f'{get_data_dir(app)}/{name}'
    with open(path, 'w') as f:
        dump(data, f, indent=4)


    # # Remove code blocks because PaLM does not like them.
    # for node in clone.traverse(nodes.literal_block):
    #     if 'code' in node['classes']:
    #         node.parent.remove(node)
    # for section in clone.traverse(nodes.section):
    #     text = section.astext()
    #     checksum = md5(text.encode('utf-8')).hexdigest()
    #     data = {
    #         'text': text,
    #         'checksum': checksum,
    #         'path': app.builder.get_target_uri(docname),
    #     }
    #     name = f'{checksum}.json'
    #     path = f'{get_data_dir(app)}/{name}'
    #     with open(path, 'w') as f:
    #         dump(data, f, indent=4)

def merge(app, exception):
    data = {}
    for file_path in glob(f'{get_data_dir(app)}/*.json'):
        with open(file_path, 'r') as f:
            file_data = load(f)
        checksum = file_data['checksum']
        data[checksum] = file_data
        remove(file_path)
    with open(f'{get_data_dir(app)}/database.json', 'w') as f:
        dump(data, f, indent=4)

def setup(app):
    app.connect('builder-inited', init)
    app.connect('doctree-resolved', prepare_database)
    app.connect('build-finished', merge)
    return {
        'version': '0.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
