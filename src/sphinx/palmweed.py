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
from os import makedirs
from glob import glob

def get_data_dir(app):
    return f'{app.outdir}/embeddings'

def init(app):
    data_dir = get_data_dir(app)
    if not exists(data_dir):
        makedirs(data_dir)

def prepare_for_embeddings(app, doctree, docname):
    clone = deepcopy(doctree)
    for section in clone.traverse(nodes.section):
        text = section.astext()
        checksum = md5(text.encode('utf-8')).hexdigest()
        data = {
            'text': text,
            'docname': docname,
            'checksum': checksum,
            'path': app.builder.get_target_uri(docname),
        }
        name = f'{checksum}.json'
        path = f'{get_data_dir(app)}/{name}'
        with open(path, 'w') as f:
            dump(data, f, indent=4)

def setup(app):
    app.connect('builder-inited', init)
    app.connect('doctree-resolved', prepare_for_embeddings)
    return {
        'version': '0.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
