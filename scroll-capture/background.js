let currentTabId = null;

//Injecting content.js into current tab
async function ensureContentScript(tabId) {
  await chrome.scripting.executeScript({
    target: { tabId },
    files: ["content.js"]
  });
}

//Listening for message to start or stop scrolling from popup.js
chrome.runtime.onMessage.addListener((msg) => {
  (async () => {
    if (msg.type == "START") {
      currentTabId = msg.tabId;
      await ensureContentScript(currentTabId);
      await chrome.tabs.sendMessage(currentTabId, { type: "START_SCROLL" });
    }
    if (msg.type == "STOP") {
      if (!currentTabId) return; 
     await chrome.tabs.sendMessage(currentTabId, { type: "STOP_SCROLL" });
    }
  })();
});
