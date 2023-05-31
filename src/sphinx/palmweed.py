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

data_dir = '/tmp/embeddings'

def init(app):
    with open('test.txt', 'w') as f:
        f.write('Hello, world!\n')
    if not exists(data_dir):
        makedirs(data_dir)

def prepare_for_embeddings(app, doctree, docname):
    data = {'docname': docname, 'sections': []}
    clone = deepcopy(doctree)
    text = clone.astext()
    checksum = md5(text.encode('utf-8')).hexdigest()
    with open('test.txt', 'a') as f:
        f.write(f'{docname}\n')
    # for section in clone.traverse(nodes.section):
    #     section_data = {}
    #     text = section.astext()
    #     text = text.replace('\n', ' ')
    #     checksum = md5(text.encode('utf-8')).hexdigest()
    #     section_data = {
    #         'text': text,
    #         'checksum': checksum,
    #     }
    #     data['sections'].append(section_data)
    # docname_checksum = md5(docname.encode('utf-8')).hexdigest()
    # filename = f'{docname_checksum}.json'
    # data_file = join(data_dir, filename)
    # with open(data_file, 'w') as f:
    #     dump(data, f, indent=2)

def setup(app):
    app.connect('builder-inited', init)
    app.connect('doctree-resolved', prepare_for_embeddings)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
