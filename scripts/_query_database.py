from firebase_admin import initialize_app, firestore as _firestore, credentials
from json import load
from pprint import pprint

service_account_credentials = credentials.Certificate('src/firebase/functions/service_account.json')
initialize_app(service_account_credentials)
firestore = _firestore.client()

collection = firestore.collection('embeddings')

count = 0
docs = collection.stream()
for doc in docs:
    data = doc.to_dict()
    if 'openai' not in data or data['openai'] is None:
        print(data['title'])
        print(data['url'])
        count += 1
print(count)


