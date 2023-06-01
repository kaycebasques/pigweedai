.. _docs-ask-palm:

========
Ask PaLM
========

.. raw:: html

   <style>
       #palmweed-input-container {
           position: fixed;
           bottom: 0;
       }
   </style>
   <div id="palmweed-output"></div>
   <div id="palmweed-input-container">
       <textarea id="palmweed-input-textbox" rows="3" placeholder="Ask PaLM something..."></textarea>
       <button id="palmweed-input-send">Send</button>
   </div>
   <script>
       // See palmweed.js.
       document.querySelector('#palmweed-input-send').addEventListener('click', () => {
           console.log(document.querySelector('#palmweed-input-textbox').value);
       });
   </script>
