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
       .palmweed-output-label {
           font-style: italic;
       }
   </style>
   <div id="palmweed-output"></div>
   <div id="palmweed-input-container">
       <textarea id="palmweed-input-textbox" rows="3" placeholder="Ask PaLM something..."></textarea>
       <button id="palmweed-input-send">Send</button>
   </div>
   <script>
       // TODO: Left-align and right-align messages.
       let output = document.querySelector('#palmweed-output');
       let textbox = document.querySelector('#palmweed-input-textbox');
       document.querySelector('#palmweed-input-send').addEventListener('click', async () => {
           const message = textbox.value;
           let label = document.createElement('p');
           label.textContent = 'You said:';
           label.classList.add('palmweed-output-label');
           output.append(label);
           let messageContainer = document.createElement('div');
           messageContainer.textContent = message;
           output.append(messageContainer);
           const options = {
               method: 'POST',
               mode: 'cors',
               headers: {
                   'Content-Type': 'application/json',
               },
               body: JSON.stringify({message})
           };
           const response = await fetch('https://server-ic22qaceya-uc.a.run.app/chat', options);
           const json = await response.json();
           if ('error' in json) {
               alert('TODO: Update this error message.');
               return;
           }
           const palmResponse = json.response;
           let responseLabel = document.createElement('p');
           responseLabel.textContent = 'PaLM replied:';
           responseLabel.classList.add('palmweed-output-label');
           output.append(responseLabel);
           let responseContainer = document.createElement('div');
           responseContainer.textContent = palmResponse;
           output.append(responseContainer);
           // TODO save convo history
           // response history context
       });
   </script>
