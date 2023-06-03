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
       }
       #palmweed-input-container {
           width: 100%;
           max-width: 100%;
           display: flex;
           align-items: center;
           margin-top: var(--palmweed-spacing);
       }
       #palmweed-input-textbox {
           width: 75%;
           max-width: 75%;
           margin-right: var(--palmweed-spacing);
           padding: var(--palmweed-spacing);
           border: var(--palmweed-border-width) solid var(--palmweed-neutral-color);
           border-radius: var(--palmweed-border-radius);
       }
       #palmweed-input-send {
           padding: calc(var(--palmweed-spacing) / 2);
           border-radius: var(--palmweed-border-radius);
       }
       .palmweed-output-label-user {
           font-style: italic;
           background-color: initial;
           text-align: right;
       }
       .palmweed-output-label-palm {
           font-style: italic;
           background-color: initial;
           text-align: left;
       }
       .palmweed-output-user {
           background-color: #dcf8c6;
           color: black;
           max-width: 75%;
           margin-left: 25%;
           padding: var(--palmweed-spacing);
           border-radius: var(--palmweed-border-radius);
           overflow-x: scroll;
       }
       .palmweed-output-palm {
           background-color: white;
           color: black;
           max-width: 75%;
           padding: var(--palmweed-spacing);
           border: var(--palmweed-border-width) solid #b529aa;
           border-radius: var(--palmweed-border-radius);
           overflow-x: scroll;
       }
   </style>
   <div id="palmweed-output"></div>
   <div id="palmweed-input-container">
       <textarea id="palmweed-input-textbox" rows="3" placeholder="Ask PaLM something..."></textarea>
       <button id="palmweed-input-send">Send</button>
   </div>
   <script>
       window.palmweed = {
           output: document.querySelector('#palmweed-output'),
           textbox: document.querySelector('#palmweed-input-textbox'),
           send: document.querySelector('#palmweed-input-send'),
           history: [
               {
                   'author': 'user',
                   'content': 'You are a friendly expert in the Pigweed software project. ' +
                              'You are helping me build embedded systems with Pigweed.'
               },
               {
                   'author': 'palm',
                   'content': 'OK. How can I help you?'
               }

           ]
       };
       window.palmweed.renderMessage = (message, isUser) => {
           let label = document.createElement('p');
           label.textContent = isUser ? 'You said:' : 'PaLM replied:';
           label.classList.add(isUser ? 'palmweed-output-label-user' : 'palmweed-output-label-palm');
           window.palmweed.output.append(label);
           let container = document.createElement('div');
           container.innerHTML = message;
           container.classList.add(isUser ? 'palmweed-output-user' : 'palmweed-output-palm');
           window.palmweed.output.append(container);
       };
       window.palmweed.textbox.addEventListener('keypress', e => {
           if (e.ctrlKey && e.keyCode == 13) {
               window.palmweed.send.click();
           }
       });
       window.palmweed.send.addEventListener('click', async () => {
           window.palmweed.send.disabled = true;
           const message = window.palmweed.textbox.value;
           window.palmweed.textbox.value = '';
           window.palmweed.textbox.placeholder = 'Getting a response from PaLM. Please wait...';
           window.palmweed.renderMessage(message, true);
           const options = {
               method: 'POST',
               mode: 'cors',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify({message, 'history': window.palmweed.history})
           };
           const url = (new URLSearchParams(window.location.search)).get('debug') === '1' ?
                   'http://127.0.0.1:5001/palmweed-prototype/us-central1/server/chat' :
                   'https://server-ic22qaceya-uc.a.run.app/chat';
           const response = await fetch(url, options);
           const json = await response.json();
           if ('error' in json) {
               window.palmweed.send.disabled = false;
               console.log(json.error);
               const errorMessage = '(This is an error message from the Palmweed code. ' +
                       'This is NOT a message from PaLM, the LLM. ' +
                       'Some kind of error happened in our prototype code. ' +
                       'Sorry about that. Please try again.)';
               window.palmweed.renderMessage(errorMessage, false)
               window.palmweed.textbox.focus();
               return;
           }
           const reply = json.reply;
           window.palmweed.renderMessage(reply, false);
           window.palmweed.history = json.history;
           console.log(window.palmweed.history);
           window.palmweed.textbox.placeholder = 'Ask PaLM something...';
           window.palmweed.send.disabled = false;
           window.palmweed.textbox.focus();
       });
   </script>
