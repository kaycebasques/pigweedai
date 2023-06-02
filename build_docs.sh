#!/bin/bash

function reset_docs_repo() {
    cd pigweed
    git restore .
    git clean -f -d
    cd ..
}

function hack_palmweed_into_docs_repo() {
    cp src/sphinx/palmweed.js pigweed/docs/_static/palmweed.js
    cp src/sphinx/palmweed.py pigweed/pw_docgen/py/pw_docgen/sphinx/palmweed.py
    cp src/sphinx/ask_palm.rst pigweed/docs/ask_palm.rst
    python3 hack.py
}

function build_docs() {
    cd pigweed
    source activate.sh
    gn gen out
    ninja -C out docs
    deactivate
    cd ..
    mv pigweed/out/docs/gen/docs/html/embeddings/database.json \
            src/firebase/functions/database.json
}

reset_docs_repo
hack_palmweed_into_docs_repo
build_docs