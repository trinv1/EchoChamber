// background.js runs as a MV3 service worker.
// Think of it as the "brain":
// - Injects content.js into the page
// - Tells content.js to start smooth scrolling
// - Captures screenshots at a fixed interval while scrolling
// - Sends screenshots to your FastAPI endpoint
// - Stops when user presses stop OR content script says bottom reached

// ----------------------------
// Global state variables
// ----------------------------

// Is the system running right now?
let isOn = false;

// Which tab we are controlling
let runningTabId = null;

// Timer reference for repeated screenshots
let captureTimer = null;

// ----------------------------
// API endpoint
// ----------------------------
// If FastAPI is on Render, replace this with your Render URL:
// const API_ENDPOINT = "https://YOUR-APP.onrender.com/ingest-screenshot";
const API_ENDPOINT = "https://echochamber-q214.onrender.com/ingest-screenshot";

// Screenshot frequency while scrolling
const CAPTURE_EVERY_MS = 700; // adjust to 1000-2000ms if too many requests

// ----------------------------
// Stop everything cleanly
// ----------------------------
function stopAll() {
  // turn off running state
  isOn = false;
  runningTabId = null;

  // stop screenshot timer if it exists
  if (captureTimer) {
    clearInterval(captureTimer);
    captureTimer = null;
  }
}

// ----------------------------
// Inject content.js into tab
// ----------------------------
async function ensureContentScript(tabId) {
  // Injects content.js into the current page.
  // content.js is the only script that can reliably scroll the DOM.
  await chrome.scripting.executeScript({
    target: { tabId },
    files: ["content.js"]
  });
}

// ----------------------------
// Safe messaging to content.js
// ----------------------------
// On X.com, the DOM/navigation can change and content scripts can "disappear".
// This helper attempts to send a message.
// If it fails, it reinjects content.js and retries once.
async function safeSendMessage(tabId, message) {
  try {
    return await chrome.tabs.sendMessage(tabId, message);
  } catch (e) {
    // Reinject and retry once
    await ensureContentScript(tabId);
    return await chrome.tabs.sendMessage(tabId, message);
  }
}

// ----------------------------
// Capture screenshot and send to FastAPI
// ----------------------------
async function captureAndSend(tab, profile) {
  // Capture visible portion of the current tab as a PNG data URL
  const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, { format: "png" });

  // Convert data URL to Blob bytes
  const res = await fetch(dataUrl);
  const blob = await res.blob();

  // Build multipart form payload
  const form = new FormData();
  form.append("image", blob, `capture-${profile}-${Date.now()}.png`);
  form.append("profile", profile);
  form.append("url", tab.url ?? "");
  form.append("title", tab.title ?? "");

  // POST to FastAPI endpoint
  const apiRes = await fetch(API_ENDPOINT, { method: "POST", body: form });

  // Throw if server returns error (helps you see issues in service worker console)
  if (!apiRes.ok) {
    const text = await apiRes.text().catch(() => "");
    throw new Error(`API error ${apiRes.status}: ${text}`);
  }
}

// ----------------------------
// Start screenshot loop (runs in parallel with scrolling)
// ----------------------------
async function startCaptureLoop(tabId) {
  // Read profile (boy/girl) from extension storage
  const { profile = "boy" } = await chrome.storage.local.get("profile");

  // Set up a repeating timer
  captureTimer = setInterval(async () => {
    // Only capture if we are still running and still on the same tab
    if (!isOn || runningTabId !== tabId) return;

    try {
      // Grab latest tab info each time
      const latestTab = await chrome.tabs.get(tabId);

      // Take screenshot and upload
      await captureAndSend(latestTab, profile);
    } catch (e) {
      console.error("Capture failed:", e);
      // Optional: if you want to stop on repeated failures, call stopAll()
    }
  }, CAPTURE_EVERY_MS);
}

// ----------------------------
// Start smooth scrolling (content.js does the scrolling)
// ----------------------------
async function startSmoothScroll(tabId) {
  // Ensure content.js is present
  await ensureContentScript(tabId);

  // Tell content.js to start smooth scrolling.
  // This config controls the "feel" and speed.
  await safeSendMessage(tabId, {
    type: "START_SMOOTH_SCROLL",
    config: {
      // Speed range (px/sec). Lower = slower.
      minSpeed: 60,
      maxSpeed: 220,

      // How much the speed can drift each second
      speedWander: 40,

      // Micro pauses to make it non-uniform
      pauseChancePerSec: 0.20,
      pauseMinMs: 250,
      pauseMaxMs: 900,

      // Consider page "done" near bottom
      bottomPaddingPx: 25
    }
  });
}

// ----------------------------
// Listen for messages from popup.js and content.js
// ----------------------------
chrome.runtime.onMessage.addListener((msg) => {
  (async () => {
    // START from popup
    if (msg?.type === "START_LOOP") {
      // Reset any existing run
      stopAll();

      // Mark running
      isOn = true;
      runningTabId = msg.tabId;

      // Start scrolling and capturing simultaneously
      await startSmoothScroll(msg.tabId);
      await startCaptureLoop(msg.tabId);
      return;
    }

    // STOP from popup
    if (msg?.type === "STOP_LOOP") {
      if (runningTabId) {
        // Tell content.js to stop scrolling (ignore failures)
        try {
          await safeSendMessage(runningTabId, { type: "STOP_SMOOTH_SCROLL" });
        } catch {}
      }
      stopAll();
      return;
    }

    // Message from content.js when bottom is reached
    if (msg?.type === "REACHED_BOTTOM") {
      if (runningTabId) {
        try {
          await safeSendMessage(runningTabId, { type: "STOP_SMOOTH_SCROLL" });
        } catch {}
      }
      stopAll();
      return;
    }
  })();
});
