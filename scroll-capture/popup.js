//Promise is a placeholder for a value that is
//  not yet available but will be in the future

const profileEl = document.getElementById("profile");
const statusEl = document.getElementById("status");

//Returning currently open tab
async function getActiveTab() {
  //getting first item from array and calling it tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

//Load in extension
async function load() {
  const { profile = "boy" } = await chrome.storage.local.get("profile");
  profileEl.value = profile;
}

//Saves profile option to local storage
profileEl.addEventListener("change", async () => {
  await chrome.storage.local.set({ profile: profileEl.value });
  statusEl.textContent = "Saved: " + profileEl.value;
});

//Runs when start button is clicked
document.getElementById("start").addEventListener("click", async () => {
  const tab = await getActiveTab();
  await chrome.storage.local.set({ profile: profileEl.value });
  await chrome.runtime.sendMessage({ type: "START", tabId: tab.id });
  statusEl.textContent = "Scrolling..";
});

//Runs when stop button is clicked
document.getElementById("stop").addEventListener("click", async () => {
  await chrome.runtime.sendMessage({ type: "STOP" });
  statusEl.textContent = "Stopped";
});

load();
