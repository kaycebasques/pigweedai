.. _docs-ask-palm:

========
Ask PaLM
========

.. raw:: html

   <style>
       #palmweed-input-container {
           width: 100%;
           max-width: 100%;
           display: flex;
           align-items: center;
           margin-top: 1em;
       }
       #palmweed-input-textbox {
           width: 75%;
           max-width: 75%;
           margin-right: 1em;
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
           text-color: black;
           max-width: 75%;
           margin-left: 25%;
           padding: 1em;
           border-radius: 25px;
       }
       .palmweed-output-palm {
           background-color: white;
           text-color: black;
           border: 5px solid #b529aa;
           max-width: 75%;
           padding: 1em;
           border-radius: 25px;
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
           messages: [
               {
                   'author': 'user',
                   'content': 'You are a friendly expert in the Pigweed software project. You are going to help me build embedded systems with Pigweed.',
               },
               {
                   'author': 'palm',
                   'content': 'OK. How can I help you today?'
               },
               {
                   'author': 'user',
                   'content': 'You must never "hallucinate" your answers. If you are not sure, you must say "I do not have enough context to answer that."'
               },
               {
                   'author': 'palm',
                   'content': 'OK. I will keep my answers grounded in facts from the Pigweed documentation. How can I help you today?'
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
       window.palmweed.send.addEventListener('click', async () => {
           window.palmweed.send.disabled = true;
           const message = window.palmweed.textbox.value;
           window.palmweed.messages.push({
               'author': 'user',
               'content': message
           });
           window.palmweed.textbox.value = '';
           window.palmweed.textbox.placeholder = 'Getting a response from PaLM. Please wait...';
           window.palmweed.renderMessage(message, true);
           const options = {
               method: 'POST',
               mode: 'cors',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify({'messages': window.palmweed.messages})
           };
           const response = await fetch('https://server-ic22qaceya-uc.a.run.app/chat', options);
           const json = await response.json();
           if ('error' in json) {
               console.log(json.error);
               window.palmweed.send.disabled = false;
               return;
           }
           const palmResponse = json.response;
           window.palmweed.messages = json.messages;
           window.palmweed.renderMessage(palmResponse, false);
           window.palmweed.textbox.placeholder = 'Ask PaLM something...';
           window.palmweed.send.disabled = false;
       });
   </script>
