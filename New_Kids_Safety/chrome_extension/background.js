chrome.webNavigation.onBeforeNavigate.addListener(async function (details) {
  if (!details.url.startsWith("http")) return;

  console.log("Checking URL:", details.url);

  try {
    const response = await fetch("http://127.0.0.1:5000/check_site", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: details.url })
    });

    const data = await response.json();

    if (data.blocked) {
      console.warn("⚠️ Site blocked by backend. Redirecting to about:blank");
      chrome.tabs.update(details.tabId, { url: "about:blank" });
    }
  } catch (error) {
    console.error("❌ Error contacting Flask server:", error);
  }
}, { url: [{ urlMatches: ".*" }] });
