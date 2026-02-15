let timer = null;

//Starts scrolling
function startScroll() { 
  if (timer) return; 
  //every 16ms (~60fps) run function and scroll down page by 10 px
  timer = setInterval(() => {window.scrollBy(0, 10)}, 16);  
}

//Stops scroll and repeating loop
function stopScroll() { 
  if (!timer) return; 
  clearInterval(timer); 
  timer = null; 
}

//Listens for messages from background/popup.js
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type == "START_SCROLL") startScroll();
  if (msg.type == "STOP_SCROLL") stopScroll();
  sendResponse({ ok: true });
});
