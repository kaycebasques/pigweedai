# palmweed

https://firebase.google.com/docs/functions/get-started?gen=2nd#python-preview

https://github.com/firebase/firebase-functions-python

https://github.com/firebase/functions-samples/tree/main/Python

Maybe just upload the embeddings manually to Google Cloud and make that file public? Or just upload the embeddings alongside the functions. Uploading alongside the function will be better for debugging. Presumably you can download everything and see the exact embeddings data that was used.

## Notes

* database.json with "all docs" is 5.6MB
* "all docs" is in quotes because I need to do something about the
  possibility of missing sections because they're too large
