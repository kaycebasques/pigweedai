# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
from json import load

initialize_app()

with open('test.json', 'r') as f:
    data = load(f)

@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    message = data['message']
    return https_fn.Response(message)
