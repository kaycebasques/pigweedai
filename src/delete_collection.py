from firebase_admin import initialize_app, firestore as _firestore, credentials
from json import load

with open('firebase/functions/env.json', 'r') as f:
    env = load(f)
with open('firebase/functions/database.json', 'r') as f:
    database = load(f)
service_account_credentials = credentials.Certificate('firebase/functions/service_account.json')
initialize_app(service_account_credentials)
firestore = _firestore.client()

collection_name = input('Enter the name of the collection you want to delete: ')
collection = firestore.collection(collection_name)

doc_refs = collection.stream()
for doc_ref in doc_refs:
    print(doc_ref.id)
    collection.document(doc_ref.id).delete()
