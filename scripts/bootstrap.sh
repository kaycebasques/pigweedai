#!/bin/bash

function bootstrap_docs_repo() {
    git clone --depth 1 https://pigweed.googlesource.com/pigweed/pigweed
    cd pigweed
    source bootstrap.sh
    deactivate
    cd ..
}

# TODO: This fails because of the local dev checks.
function build_docs() {
    source scripts/build_docs.sh
}

function bootstrap_firebase() {
    cd src/firebase
    npm i
    cd functions
    python3.11 -m venv venv
    source venv/bin/activate
    python3.11 pip install -r requirements.txt
}

bootstrap_docs_repo
build_docs
bootstrap_firebase
