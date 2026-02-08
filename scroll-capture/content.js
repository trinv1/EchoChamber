// content.js runs INSIDE the webpage.
// It can access window/document and can scroll the page smoothly.
//
// It listens for messages:
// - START_SMOOTH_SCROLL: begin scrolling
// - STOP_SMOOTH_SCROLL: stop scrolling
// - GET_SCROLL_STATE: report current status
//
// It notifies background when bottom is reached:
// - sends {type:"REACHED_BOTTOM"}

// ----------------------------
// Runtime state
// ----------------------------
let running = false;           // whether we are currently scrolling
let rafId = null;              // requestAnimationFrame id
let currentSpeedPxPerSec = 0;  // current scroll speed
let pausedUntil = 0;           // timestamp (ms) until which we pause
let lastTs = 0;                // timestamp of last animation frame

// ----------------------------
// Default config
// ----------------------------
// IMPORTANT: cfg MUST exist, because we reference cfg.* in tick().
let cfg = {
  minSpeed: 120,
  maxSpeed: 380,
  speedWander: 60,
  pauseChancePerSec: 0.18,
  pauseMinMs: 250,
  pauseMaxMs: 700,
  bottomPaddingPx: 25
};

// ----------------------------
// Helpers
// ----------------------------
function atBottom(paddingPx = 25) {
  return window.innerHeight + window.scrollY >= document.body.scrollHeight - paddingPx;
}

function clamp(x, a, b) {
  return Math.max(a, Math.min(b, x));
}

function randBetween(a, b) {
  return a + Math.random() * (b - a);
}

// ----------------------------
// Animation loop (runs ~60fps)
// ----------------------------
function tick(ts) {
  if (!running) return;

  // Convert timestamp difference to seconds
  if (!lastTs) lastTs = ts;
  const dt = (ts - lastTs) / 1000;
  lastTs = ts;

  // If we are at bottom, stop and notify background
  if (atBottom(cfg.bottomPaddingPx)) {
    running = false;
    rafId = null;

    chrome.runtime.sendMessage({
      type: "REACHED_BOTTOM",
      url: location.href,
      title: document.title
    });

    return;
  }

  // If paused, do nothing but keep animation going
  if (Date.now() < pausedUntil) {
    rafId = requestAnimationFrame(tick);
    return;
  }

  // Random micro-pause with probability per second
  // Convert chance per second to chance per frame based on dt
  const pauseChanceThisFrame = 1 - Math.pow(1 - cfg.pauseChancePerSec, dt);
  if (Math.random() < pauseChanceThisFrame) {
    const pauseMs = Math.floor(randBetween(cfg.pauseMinMs, cfg.pauseMaxMs));
    pausedUntil = Date.now() + pauseMs;
    rafId = requestAnimationFrame(tick);
    return;
  }

  // Adjust speed gradually (non-uniform drift)
  const wanderDelta = randBetween(-cfg.speedWander, cfg.speedWander) * dt;
  currentSpeedPxPerSec = clamp(
    currentSpeedPxPerSec + wanderDelta,
    cfg.minSpeed,
    cfg.maxSpeed
  );

  // Scroll distance this frame
  const dy = currentSpeedPxPerSec * dt;

  // Scroll smoothly
  window.scrollBy(0, dy);

  // Continue loop
  rafId = requestAnimationFrame(tick);
}

// ----------------------------
// Message listener
// ----------------------------
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    try {
      // START scrolling
      if (msg?.type === "START_SMOOTH_SCROLL") {
        // Merge overrides from background.js (if provided)
        cfg = { ...cfg, ...(msg.config || {}) };

        running = true;
        pausedUntil = 0;
        lastTs = 0;

        // Start speed randomly within range (so runs aren't identical)
        currentSpeedPxPerSec = randBetween(cfg.minSpeed, cfg.maxSpeed);

        // Start animation loop if not already running
        if (!rafId) rafId = requestAnimationFrame(tick);

        // Always respond so message channel doesn't error
        sendResponse({ ok: true, cfg });
        return;
      }

      // STOP scrolling
      if (msg?.type === "STOP_SMOOTH_SCROLL") {
        running = false;

        // Cancel animation frame if active
        if (rafId) cancelAnimationFrame(rafId);
        rafId = null;

        sendResponse({ ok: true });
        return;
      }

      // Debug/status request
      if (msg?.type === "GET_SCROLL_STATE") {
        sendResponse({
          ok: true,
          running,
          url: location.href,
          title: document.title,
          scrollY: window.scrollY,
          scrollHeight: document.body.scrollHeight,
          speedPxPerSec: currentSpeedPxPerSec
        });
        return;
      }

      // Unknown message type but still respond
      sendResponse({ ok: false, error: "unknown message type" });
    } catch (err) {
      // If anything throws, still respond (prevents "channel closed" error)
      sendResponse({ ok: false, error: String(err) });
    }
  })();

  // Tell Chrome: "we will respond asynchronously"
  return true;
});
