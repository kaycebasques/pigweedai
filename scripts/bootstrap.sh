#!/bin/bash

function bootstrap_docs_repo() {
    git clone --depth 1 https://pigweed.googlesource.com/pigweed/pigweed
    cd pigweed
    source bootstrap.sh
    deactivate
    cd ..
}

function bootstrap_firebase() {
    cd src/firebase
    npm i
    cd functions
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt
    deactivate
    cd ../../..
}

bootstrap_docs_repo
bootstrap_firebase
