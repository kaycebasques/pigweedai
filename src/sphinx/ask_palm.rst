.. _docs-ask-palm:

========
Ask PaLM
========

.. raw:: html

   <style>
       :root {
           --palmweed-border-radius: 15px;
           --palmweed-spacing: 1em;
           --palmweed-border-width: 3px;
           --palmweed-neutral-color: lightgrey;
           --palmweed-message-width: 80%;
           --palmweed-message-margin: 20%;
       }
       #palmweed-input {
           width: 100%;
           max-width: 100%;
           display: flex;
           align-items: center;
           margin-top: var(--palmweed-spacing);
       }
       #palmweed-textbox {
           width: 75%;
           max-width: 75%;
           margin-right: var(--palmweed-spacing);
           padding: var(--palmweed-spacing);
           border: var(--palmweed-border-width) solid var(--palmweed-neutral-color);
           border-radius: var(--palmweed-border-radius);
       }
       #palmweed-send {
           padding: calc(var(--palmweed-spacing) / 2);
           border-radius: var(--palmweed-border-radius);
       }
       .palmweed-label {
           font-style: italic;
           background-color: initial;
       }
       .palmweed-label-user {
           text-align: right;
       }
       .palmweed-label-palm {
           text-align: left;
       }
       .palmweed-output-user {
           background-color: #dcf8c6;
           color: black;
           max-width: var(--palmweed-message-width);
           margin-left: var(--palmweed-message-margin);
           padding: var(--palmweed-spacing);
           border-radius: var(--palmweed-border-radius);
           overflow-x: scroll;
       }
       .palmweed-output-palm {
           background-color: white;
           color: black;
           max-width: var(--palmweed-message-width);
           padding: var(--palmweed-spacing);
           border: var(--palmweed-border-width) solid #b529aa;
           border-radius: var(--palmweed-border-radius);
           overflow-x: scroll;
       }
       .palmweed-output-palmweed {
           background-color: white;
           color: black;
           max-width: var(--palmweed-message-width);
           padding: var(--palmweed-spacing);
           border: var(--palmweed-border-width) solid #b529aa;
           border-radius: var(--palmweed-border-radius);
           overflow-x: scroll;
       }
   </style>
   <div id="palmweed-output"></div>
   <div id="palmweed-input">
       <textarea id="palmweed-textbox" rows="3" placeholder="Ask PaLM something..."></textarea>
       <button id="palmweed-send">Send</button>
   </div>
   <script>
       window.palmweed = {
           uuid: crypto.randomUUID(),
           output: document.querySelector('#palmweed-output'),
           textbox: document.querySelector('#palmweed-textbox'),
           send: document.querySelector('#palmweed-send')
       };
       window.palmweed.renderMessage = (message, role) => {
           let label = document.createElement('p');
           let container = document.createElement('div');
           label.classList.add('palmweed-label');
           switch (role) {
               case 'user':
                   label.textContent = 'You said:';
                   label.classList.add('palmweed-label-user');
                   container.classList.add('palmweed-output-user');
                   break;
               case 'palm':
                   label.textContent = 'PaLM said:';
                   label.classList.add('palmweed-label-palm');
                   container.classList.add('palmweed-output-palm');
                   break;
               case 'palmweed':
                   label.textContent = 'Error message from the Palmweed code:';
                   label.classList.add('palmweed-label-palmweed');
                   container.classList.add('palmweed-output-palmweed');
                   break;
           }
           window.palmweed.output.append(label);
           container.innerHTML = message;
           window.palmweed.output.append(container);
       };
       window.palmweed.chat = (message) => {
           const body = {
               'message': message,
               'uuid': window.palmweed.uuid
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
                   window.palmweed.send.disabled = false;
                   const errorMessage = '(This is a message from the Palmweed code. ' +
                           'This is NOT a message from PaLM. ' +
                           'Some kind of error happened. Sorry about that. ' +
                           'Please try a different question.)';
                   window.palmweed.renderMessage(errorMessage, 'palmweed')
                   window.palmweed.textbox.focus();
                   return;
               }
               const reply = json.reply;
               window.palmweed.renderMessage(reply, 'palm');
               window.palmweed.textbox.placeholder = 'Ask PaLM something...';
               window.palmweed.send.disabled = false;
               window.palmweed.textbox.focus();
           }).catch(error => {
               window.palmweed.send.disabled = false;
               const errorMessage = '(This is a message from the Palmweed code. ' +
                       'This is NOT a message from PaLM. ' +
                       'Some kind of error happened. Sorry about that. ' +
                       'Please try a different prompt.)';
               window.palmweed.renderMessage(errorMessage, 'palmweed')
               window.palmweed.textbox.focus();
           });
       };
       window.palmweed.send.addEventListener('click', () => {
           window.palmweed.send.disabled = true;
           const message = window.palmweed.textbox.value;
           window.palmweed.textbox.value = '';
           window.palmweed.textbox.placeholder = 'Getting a response from PaLM. Please wait...';
           window.palmweed.renderMessage(message, 'user');
           window.palmweed.chat(message);
       });
   </script>
