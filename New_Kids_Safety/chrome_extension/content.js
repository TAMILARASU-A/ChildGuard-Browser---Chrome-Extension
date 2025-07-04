// content.js

// Send the current page's URL to the background script to check if it's blocked
chrome.runtime.sendMessage({ type: "check_url", url: window.location.href }, (response) => {
  if (response?.block) {
    // If the site is blocked, display a blocking message on the page
    document.body.innerHTML = `<h1 style="text-align:center;margin-top:20%;color:red;">⚠️ This website is blocked for children!</h1>`;
  }
});
