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
           --pigweedai-message-width: 80%;
           --pigweedai-message-margin: 20%;
       }
       #pigweedai-input {
           width: 100%;
           max-width: 100%;
           display: flex;
           align-items: center;
           margin-top: var(--pigweedai-spacing);
       }
       #pigweedai-textbox {
           width: 75%;
           max-width: 75%;
           margin-right: var(--pigweedai-spacing);
           padding: var(--pigweedai-spacing);
           border: var(--pigweedai-border-width) solid var(--pigweedai-neutral-color);
           border-radius: var(--pigweedai-border-radius);
       }
       #pigweedai-send {
           padding: calc(var(--pigweedai-spacing) / 2);
           border-radius: var(--pigweedai-border-radius);
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
           max-width: var(--pigweedai-message-width);
           margin-left: var(--pigweedai-message-margin);
           padding: var(--pigweedai-spacing);
           border-radius: var(--pigweedai-border-radius);
           overflow-x: scroll;
       }
       .pigweedai-output-assistant {
           background-color: white;
           color: black;
           max-width: var(--pigweedai-message-width);
           padding: var(--pigweedai-spacing);
           border: var(--pigweedai-border-width) solid #b529aa;
           border-radius: var(--pigweedai-border-radius);
           overflow-x: scroll;
       }
       .pigweedai-output-assistant {
           background-color: white;
           color: black;
           max-width: var(--pigweedai-message-width);
           padding: var(--pigweedai-spacing);
           border: var(--pigweedai-border-width) solid #b529aa;
           border-radius: var(--pigweedai-border-radius);
           overflow-x: scroll;
       }
   </style>
   <div id="pigweedai-output"></div>
   <div id="pigweedai-input">
       <textarea id="pigweedai-textbox" rows="3" placeholder="Ask PaLM something..."></textarea>
       <button id="pigweedai-send">Send</button>
   </div>
   <script>
       window.pigweedai = {
           uuid: crypto.randomUUID(),
           output: document.querySelector('#pigweedai-output'),
           textbox: document.querySelector('#pigweedai-textbox'),
           send: document.querySelector('#pigweedai-send'),
           history: []
       };
       // TODO: renderSources and renderFeedbackWidgets
       window.pigweedai.renderMessage = (message, role) => {
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
                   label.textContent = 'PaLM said:';
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
           container.innerHTML = message;
           window.pigweedai.output.append(container);
       };
       window.pigweedai.chat = (message) => {
           const body = {
               'message': message,
               'uuid': window.pigweedai.uuid,
               'history': window.pigweedai.history
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
           fetch(url, options).then(response => {
               if (response.ok) {
                   return response.json();
               }
               throw new Error('Something went wrong...');
           }).then(json => {
               if (!('reply' in json)) {
                   window.pigweedai.send.disabled = false;
                   const errorMessage = '(This is a message from the Palmweed code. ' +
                           'This is NOT a message from PaLM. ' +
                           'Some kind of error happened. Sorry about that. ' +
                           'Please try a different question.)';
                   window.pigweedai.renderMessage(errorMessage, 'pigweedai')
                   window.pigweedai.textbox.focus();
                   return;
               }
               const reply = json.reply;
               const links = json.links;
               window.pigweedai.renderMessage(reply, 'assistant', links);
               window.pigweedai.history = json.history;
               window.pigweedai.textbox.placeholder = 'Ask PaLM something...';
               window.pigweedai.send.disabled = false;
               window.pigweedai.textbox.focus();
           }).catch(error => {
               window.pigweedai.send.disabled = false;
               const errorMessage = '(This is a message from the Palmweed code. ' +
                       'This is NOT a message from PaLM. ' +
                       'Some kind of error happened. Sorry about that. ' +
                       'Please try a different prompt.)';
               window.pigweedai.renderMessage(errorMessage, 'pigweedai')
               window.pigweedai.textbox.focus();
           });
       };
       window.pigweedai.send.addEventListener('click', () => {
           window.pigweedai.send.disabled = true;
           const message = window.pigweedai.textbox.value;
           window.pigweedai.textbox.value = '';
           window.pigweedai.textbox.placeholder = 'Getting a response from PaLM. Please wait...';
           window.pigweedai.renderMessage(message, 'user');
           window.pigweedai.chat(message);
       });
   </script>
