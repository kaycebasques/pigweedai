#!/bin/bash

cd src/firebase
npx firebase emulators:start --only functions
cd ../..
