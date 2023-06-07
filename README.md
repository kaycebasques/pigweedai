# pigweedai

An experimental prototype of a retrieval-augmented generation search experience
for the [Pigweed](https://pigweed.dev) docs.

## Setup

Assumptions: I've only developed/tested this project on Debian-flavored Linux computers.

TODO: There is a little logic in a couple of the files that essentially makes
the local development only work on my computers. When this TODO is removed, it
means that you should be able to run everything yourself.

Create `//src/firebase/functions/env.json` and put your OpenAI API key there:

```
{
    "openai": "..."
}
```

Create `//src/firebase/functions/service_account.json` and put your Firebase
service account there:

```

{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "...",
  "universe_domain": "..."
}

Run the bootstrap script from the root directory of this repo:

```
source scripts/bootstrap.sh
```

All scripts should be run from this repo's root directory.

Emulate Firebase Functions locally:

```
source scripts/emulate_firebase_functions.sh
```

In a separate terminal tab/window, build the docs to kick off the embedding
generation process:

```
source scripts/build_docs.sh
```

The Sphinx extension basically just parses each doc into sections
and sends off a request to the Firebase Functions server to generate
an embedding for each section.

At this point you should be good to go!
