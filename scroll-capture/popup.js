const profileEl = document.getElementById("profile");
const statusEl = document.getElementById("status");

//Load in extension
async function load() {
  const { profile = "boy" } = await chrome.storage.local.get("profile");
  profileEl.value = profile;
  statusEl.textContent = "Saved: " + profile;
}

//Saves profile option to local storage
profileEl.addEventListener("change", async () => {
  await chrome.storage.local.set({ profile: profileEl.value });
  statusEl.textContent = "Saved: " + profileEl;
});

load();
