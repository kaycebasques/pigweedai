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
```

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

## Software architecture

This section is a general overview of how this project works end-to-end.
If you are familiar with [retrieval-augmented generation] (RAG) then you
can probably skim this section. `pigweedai` is a textbook RAG architecture.

Note: `//` means the root directory of this repository.

1. The bootstrap script (`//scripts/bootstrap.sh`) clones the Pigweed docs repo to
   `//pigweed` and installs Firebase dependencies (`//src/firebase/node_modules` and
   `//src/firebase/functions/venv`).
2. Before building the docs, the Firebase Functions server needs to be deployed or
   spun up locally. It handles a lot of the embedding generation logic that occurs
   during the docs build.
3. The build script (`//scripts/build_docs.sh`) copies the Sphinx extension 
   (`//src/sphinx/embeddings.py`) and frontend web UI (`//src/sphinx/ask_pigweed_ai.rst`)
   to the Pigweed docs repo. The build script kicks off the Pigweed docs build.
4. During the docs build, the Sphinx extension hooks into the Sphinx build lifecycle.
   The Sphinx build system calls the extension every time that it processes a doc
   into HTML. The Sphinx extension is able to parse each doc into sections. The
   extension sends a request to the Firebase Functions server to generate an embedding
   for each section. In other words, the extension is a [thin client]. The server is
   doing the heavy lifting. The embeddings and section text are stored in Firestore. An
   MD5 hash is generated for each section based on the section's text. This hash
   is essentially the [unique key](https://www.javatpoint.com/primary-key-vs-unique-key).
5. There is a separate, manual process for deploying the web frontend to GitHub Pages.
   This deployment is based on GitHub Actions.
6. When the generative search experience is running on GitHub Pages, user queries
   are sent to the Firebase Functions server. The server performs a semantic search
   of the user query against the embeddings database, assembles the documentation
   context, interacts with the LLM, and sends the response back to the web UI.
7. The web UI just renders the data from the Firebase Functions server. It is
   also a [thin client].

[retrieval-augmented generation]: https://developers.google.com/machine-learning/glossary#retrieval-augmented-generation
[thin client]: https://en.wikipedia.org/wiki/Thin_client
