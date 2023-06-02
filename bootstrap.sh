#!/bin/bash

function bootstrap_docs_repo() {
    git clone --depth 1 https://pigweed.googlesource.com/pigweed/pigweed
    cd pigweed
    source bootstrap.sh
    deactivate
    cd ..
}

function build_docs() {
    source build_docs.sh
}

bootstrap_docs_repo
build_docs
