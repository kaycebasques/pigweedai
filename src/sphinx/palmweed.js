// Copyright 2023 The Pigweed Authors
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy of
// the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.


const options = {
  method: 'POST',
  mode: 'cors',
  headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
  body: JSON.stringify({'query': 'Explain the Pigweed software project.'})
};

fetch('https://server-ic22qaceya-uc.a.run.app/api/query', options)
    .then(response => response.json())
    .then(json => console.log(json));




// function createBanner() {
//   if (document.querySelector('#palmweed-banner')) {
//     return;
//   }
//   const banner = document.createElement('section');
//   banner.style = 'border: 5px dashed red; padding: 10px;';
//   banner.id = 'palmweed-banner';
//   const message = [
//     'Welcome to the Palmweed demo!',
//     'Enter a query in the site search and see an answer from PaLM on the search results page.',
//     'DO NOT ENTER ANY CONFIDENTIAL OR PERSONAL INFORMATION INTO THE SITE SEARCH BAR!!!',
//   ]
//   banner.textContent = message.join(' ');
//   document.querySelector('article[role="main"]').prepend(banner);
// }
// 
// function createSection() {
//   if (document.querySelector('#palmweed')) {
//     return;
//   }
//   const section = document.createElement('section');
//   section.id = 'palmweed';
//   const title = document.createElement('h2');
//   title.id = 'palmweed-title';
//   title.textContent = 'Ask PaLM';
//   const content = document.createElement('div');
//   content.id = 'palmweed-content';
//   content.style = 'padding: 0.25em;';
//   content.textContent = 'Generating a response. Please wait...';
//   section.appendChild(title);
//   section.appendChild(content);
//   const siblingNode = document.querySelector('#search-results');
//   const parentNode = siblingNode.parentNode;
//   parentNode.insertBefore(section, siblingNode);
// }
// 
// function getQuery() {
//   const params = new URLSearchParams(window.location.search);
//   return params.get('q');
// }
// 
// function generateResponse() {
//   const options = {
//     method: 'POST',
//     mode: 'cors',
//     headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
//     body: JSON.stringify({'query': getQuery()})
//   };
//   fetch('https://server-ic22qaceya-uc.a.run.app/api/query', options)
//       .then(response => response.json())
//       .then(json => render(json));
// }
// 
// function render(data) {
//   document.querySelector('#palmweed-content').innerHTML = data['answer'];
//   const style = 'color: red; font-style: italic; font-size: 2em;';
//   console.log('%cContext', style);
//   console.log(data['context']);
//   console.log('%cVanilla', style);
//   console.log(data['vanilla']);
// }
// 
// window.addEventListener('load', () => {
//   createBanner();
//   // Currently this JS is loaded on every page. This should be fixed
//   // so that this JS is only loaded for search.html. Once that is done this
//   // window.location.pathname check can be removed.
//   if (window.location.pathname != '/search.html') {
//     return;
//   }
//   createSection();
//   generateResponse();
// });
