.. _docs-ask-pigweed-ai:

==============
Ask Pigweed AI
==============

.. raw:: html

   <style>
       :root {
           --pigweedai-border-radius: 15px;
           --pigweedai-spacing: 1em;
           --pigweedai-border-width: 3px;
           --pigweedai-neutral-color: lightgrey;
       }
       #pigweedai-input {
           width: 100%;
           margin-top: var(--pigweedai-spacing);
       }
       #pigweedai-textbox {
           padding: var(--pigweedai-spacing);
           border: var(--pigweedai-border-width) solid var(--pigweedai-neutral-color);
           border-radius: var(--pigweedai-border-radius);
           width: 100%;
           box-sizing: border-box;
           display: block;
       }
       #pigweedai-send {
           margin: var(--pigweedai-border-radius) 0 0 auto;
           padding: var(--pigweedai-spacing);
           border-radius: var(--pigweedai-border-radius);
           display: block;
       }
       .pigweedai-label {
           font-style: italic;
           background-color: initial;
       }
       .pigweedai-label-user {
           text-align: right;
       }
       .pigweedai-label-assistant {
           text-align: left;
       }
       .pigweedai-output-user {
           background-color: #dcf8c6;
           color: black;
           max-width: 100%;
           padding: var(--pigweedai-spacing);
           border-radius: var(--pigweedai-border-radius);
           overflow-x: scroll;
       }
       .pigweedai-output-assistant {
           background-color: white;
           color: black;
           max-width: 100%;
           padding: var(--pigweedai-spacing);
           border: var(--pigweedai-border-width) solid #b529aa;
           border-radius: var(--pigweedai-border-radius);
           overflow-x: scroll;
       }
       .pigweedai-feedback-textbox {
           border-radius: var(--pigweedai-border-radius);
           padding: var(--pigweedai-spacing);
           width: 100%;
           box-sizing: border-box;
           display: block;
       }
       .pigweedai-feedback-button {
           border-radius: var(--pigweedai-border-radius);
           padding: var(--pigweedai-spacing);
           margin: var(--pigweedai-border-radius) 0 0 auto;
           display: block;
       }
   </style>
   <p>
       Welcome! This is a prototype of a
       <a href="https://developers.google.com/machine-learning/glossary#retrieval-augmented-generation">retrieval-augmented
       generation</a> search experience for the <a href="https://pigweed.dev">Pigweed</a> docs. Here's the
       <a href="https://github.com/kaycebasques/pigweedai">source code</a>. Important notes:
   </p>
   <ul>
       <li>
           <b>This is not an official Google product.</b> This is a personal prototype by Kayce Basques.
           All responsibility my own.
       </li>
       <li>
           <b>DO NOT ENTER PERSONAL OR CONFIDENTIAL INFORMATION!!!</b>
           Your messages are sent to OpenAI. They're also logged in Firestore for
           quality assurance.
       </li>
       <li>
           The <s>cake</s> chat UI is a lie! <b>The LLM won't remember your conversation
           history.</b> It's a known limitation.
       </li>
   </ul>
   <p>Thanks for trying it out! Please <b>leave feedback with the in-message widget</b>.</p>
   <div id="pigweedai-output"></div>
   <div id="pigweedai-input">
       <textarea id="pigweedai-textbox" rows="5" placeholder="Ask Pigweed AI something..."></textarea>
       <button id="pigweedai-send">Ask Pigweed AI</button>
   </div>
   <script>
       window.pigweedai = {
           uuid: crypto.randomUUID(),
           output: document.querySelector('#pigweedai-output'),
           textbox: document.querySelector('#pigweedai-textbox'),
           send: document.querySelector('#pigweedai-send'),
           history: [],
       };
       window.pigweedai.renderMessage = (message, role, links, id) => {
           let label = document.createElement('p');
           let container = document.createElement('div');
           let reply = document.createElement('div');
           label.classList.add('pigweedai-label');
           switch (role) {
               case 'user':
                   label.textContent = 'You said:';
                   label.classList.add('pigweedai-label-user');
                   container.classList.add('pigweedai-output-user');
                   break;
               case 'assistant':
                   label.textContent = 'Pigweed AI said:';
                   label.classList.add('pigweedai-label-assistant');
                   container.classList.add('pigweedai-output-assistant');
                   break;
               case 'pigweedai':
                   label.textContent = 'Error message from the Palmweed code:';
                   label.classList.add('pigweedai-label-assistant');
                   container.classList.add('pigweedai-output-assistant');
                   break;
           }
           window.pigweedai.output.append(label);
           reply.innerHTML = message;
           container.append(reply);
           if (links) {
               let sourcesContainer = document.createElement('ul');
               let html = '<p>Sources:</p>';
               links.forEach(link => {
                   const anchor = `<li><a href="${link.url}" target="_blank">${link.title}</a></li>`;
                   html += anchor;
               });
               sourcesContainer.innerHTML = html;
               container.append(sourcesContainer);
           }
           if (id) {
               let idContainer = document.createElement('div');
               let textbox = document.createElement('textarea');
               textbox.rows = 3;
               textbox.type = 'text';
               textbox.id = id;
               textbox.placeholder = 'Leave feedback on this reply...';
               textbox.classList.add('pigweedai-feedback-textbox');
               let button = document.createElement('button');
               button.textContent = 'Send Feedback';
               button.classList.add('pigweedai-feedback-button');
               button.addEventListener('click', () => {
                   const body = {
                       'message_id': id,
                       'feedback': document.querySelector(`#${id}`).value,
                       'uuid': window.pigweedai.uuid
                   };
                   const options = {
                       method: 'POST',
                       mode: 'cors',
                       headers: {
                           'Content-Type': 'application/json',
                       },
                       body: JSON.stringify(body)
                   };
                   const debug = (new URLSearchParams(window.location.search)).get('debug') === '1';
                   const url = debug ?
                           'http://127.0.0.1:5001/palmweed-prototype/us-central1/server/send_feedback' :
                           'https://server-ic22qaceya-uc.a.run.app/send_feedback';
                   fetch(url, options).catch(error => console.log(error));
                   document.querySelector(`#${id}`).value = '';
                   document.querySelector(`#${id}`).placeholder = 'Feedback sent! You can send again, but it will overwrite your previous comment.';
               });
               idContainer.append(textbox);
               idContainer.append(button);
               container.append(idContainer);
           }
           window.pigweedai.output.append(container);
       };
       window.pigweedai.renderErrorMessage = () => {
           const errorMessage = '(This is a message from the prototype code. ' +
                   'This is NOT a message from an LLM. Some kind of error happened ' +
                   'in the prototype code. Sorry about that. Please try a different ' +
                   'question.)';
           window.pigweedai.send.disabled = false;
           window.pigweedai.renderMessage(errorMessage, 'pigweedai', null, null);
           window.pigweedai.textbox.focus();
       };
       window.pigweedai.chat = (message) => {
           const body = {
               'message': message,
               'uuid': window.pigweedai.uuid,
               'history': window.pigweedai.history,
               'mode': 'html',
           };
           const options = {
               method: 'POST',
               mode: 'cors',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify(body)
           };
           const debug = (new URLSearchParams(window.location.search)).get('debug') === '1';
           const url = debug ?
                   'http://127.0.0.1:5001/palmweed-prototype/us-central1/server/chat' :
                   'https://server-ic22qaceya-uc.a.run.app/chat';
           // Using traditional, nested promises because it was too hard to
           // reason about correct try/catch logic for async code.
           fetch(url, options).then(response => {
               if (response.ok) {
                   return response.json();
               }
               throw new Error('Something went wrong...');
           }).then(json => {
               if (!('reply' in json)) {
                   window.pigweedai.renderErrorMessage();
                   return;
               }
               const reply = json.reply;
               const links = json.links;
               const id = json.id;
               window.pigweedai.renderMessage(reply, 'assistant', links, id);
               window.pigweedai.history = json.history;
               window.pigweedai.textbox.placeholder = 'Ask Pigweed AI something...';
               window.pigweedai.send.disabled = false;
               window.pigweedai.textbox.focus();
           }).catch(error => {
               window.pigweedai.renderErrorMessage();
               return;
           });
       };
       window.pigweedai.send.addEventListener('click', () => {
           window.pigweedai.send.disabled = true;
           const message = window.pigweedai.textbox.value;
           window.pigweedai.textbox.value = '';
           window.pigweedai.textbox.placeholder =
                   'Getting a response from Pigweed AI. It usually takes 10-60 seconds. Please wait...';
           window.pigweedai.renderMessage(message, 'user', null, null);
           window.pigweedai.chat(message);
       });
   </script>
