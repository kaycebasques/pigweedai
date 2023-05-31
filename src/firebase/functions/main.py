from firebase_functions import https_fn
from firebase_admin import initialize_app
from json import load
from flask import Flask

initialize_app()
app = Flask(__name__)

with open('data.json', 'r') as f:
    data = load(f)

@app.get('/data')
def get_data():
    return 'Hello, data!'

@https_fn.on_request()
def server(req: https_fn.Request) -> https_fn.Response:
    with app.request_context(req.environ):
        return app.full_dispatch_request()

# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     message = data['message']
#     return https_fn.Response(message)
