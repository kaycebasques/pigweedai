cd src/firebase
source functions/venv/bin/activate
npx firebase deploy --only functions
deactivate
cd ../..
