#!/bin/bash

function reset_docs_repo() {
    cd pigweed
    git restore .
    git clean -f -d
    cd ..
}

function hack_pigweedai_into_docs_repo() {
    cp src/sphinx/embeddings.py pigweed/pw_docgen/py/pw_docgen/sphinx/embeddings.py
    cp src/sphinx/ask_pigweed_ai.rst pigweed/docs/ask_pigweed_ai.rst
    python3 scripts/hack.py
}

function build_docs() {
    cd pigweed
    source activate.sh
    gn gen out
    ninja -C out docs
    deactivate
    cd ..
}

reset_docs_repo
hack_pigweedai_into_docs_repo
time build_docs
