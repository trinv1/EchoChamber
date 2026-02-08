// popup.js runs ONLY inside the popup window (UI).
// It does NOT scroll or screenshot.
// It only:
// 1) stores profile (boy/girl) in chrome.storage
// 2) finds current active tab
// 3) tells background.js to start/stop the loop

const profileEl = document.getElementById("profile");
const statusEl = document.getElementById("status");

// Helper: get the active tab (the tab you’re currently viewing)
async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

// Load saved profile from extension storage and set dropdown value
async function loadProfile() {
  const { profile = "boy" } = await chrome.storage.local.get("profile");
  profileEl.value = profile;
}

// Save profile whenever the dropdown changes
profileEl.addEventListener("change", async () => {
  await chrome.storage.local.set({ profile: profileEl.value });
});

// Start button: save profile and tell background to start loop on current tab
document.getElementById("start").addEventListener("click", async () => {
  const tab = await getActiveTab();
  if (!tab?.id) return;

  // Save the selected profile so background can read it
  await chrome.storage.local.set({ profile: profileEl.value });

  // Tell background to start scrolling+capturing on this tab
  await chrome.runtime.sendMessage({ type: "START_LOOP", tabId: tab.id });

  // Update UI
  statusEl.textContent = `Running (${profileEl.value})`;
});

// Stop button: tell background to stop
document.getElementById("stop").addEventListener("click", async () => {
  await chrome.runtime.sendMessage({ type: "STOP_LOOP" });
  statusEl.textContent = "Stopped";
});

// When popup opens, sync dropdown to saved profile
loadProfile();
