let running = false;
let rafId = null;

let speed = 120;          // px/sec (changes over time)
let lastTs = 0;
let pausedUntil = 0;

let timer = null;

//Update scrolling time
function frameUpdate(ts){
    if (!running) return;

    if (!lastTs) lastTs = ts;
    const dt = (ts - lastTs) / 1000;//s since previous frame update
    lastTs = ts;

  //Pause randomly
  if (Date.now() < pausedUntil) {
    rafId = requestAnimationFrame(frameUpdate);
    return;
  }
  if (Math.random() < 0.02) { //condition is true about 2% of frames
    pausedUntil = Date.now() + (200 + Math.random() * 800);//pause length: 0.2–1 second
    rafId = requestAnimationFrame(frameUpdate);
    return;
  }

  //Wander speed a bit
  speed += (Math.random() * 2 - 1) * 50 * dt;
  speed = Math.max(60, Math.min(400, speed));  //never above 220 never below 60

  window.scrollBy(0, speed * dt);//scroll down only
  rafId = requestAnimationFrame(frameUpdate);
}

//Listens for messages from background/popup.js
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type == "START_SCROLL"){
    running = true;
    lastTs = 0;
    pausedUntil = 0;
    if (!rafId) rafId = requestAnimationFrame(frameUpdate);
    sendResponse({ ok: true });
  }

  if (msg.type == "STOP_SCROLL") {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
    sendResponse({ ok: true });
    return;
  }
});
