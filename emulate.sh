#!/bin/bash

function emulate_firebase_functions() {
    cd src/firebase
    npx firebase emulators:start --only functions
    cd ../..
}

emulate_firebase_functions
