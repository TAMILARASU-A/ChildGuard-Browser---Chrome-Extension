
# ChildGuard-Browser — Chrome Extension

**ChildGuard-Browser** is a Chrome Extension designed to help parents monitor or restrict access to specific websites, providing a safer browsing environment for children.

## 👥 Team

- [kalpana-mk](https://github.com/kalpana-mk)

## 🧩 What It Does

This Chrome Extension allows users to:
- Block specific websites based on a list
- Set browsing time limits
- Monitor and log access attempts
- Provide real-time notifications or alerts

## 📁 Project Structure

```

ChildGuard-Browser---Chrome-Extension/
├── background.js       # Background script for core logic
├── content.js          # Injected into pages to monitor behavior
├── popup.html          # UI shown when clicking the extension icon
├── popup.js            # JavaScript for popup interactions
├── options.html        # Settings/configuration page
├── options.js          # Logic for handling options
├── manifest.json       # Chrome extension manifest file
├── data/
│   └── config.json     # (Optional) Default configuration

````

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/TAMILARASU-A/ChildGuard-Browser---Chrome-Extension.git
cd ChildGuard-Browser---Chrome-Extension
````

### 2. Load the Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** (top right)
3. Click **"Load unpacked"**
4. Select the project directory

## ⚙️ Configuration

You can edit `data/config.json` (if present) or use the **Options page** in the extension to:

* Add/remove blocked sites
* Set custom browsing time restrictions
* Enable logging or alert settings

## 🛡️ Permissions Used

* `tabs`: To monitor and control browser tabs
* `storage`: To store user settings and logs
* `webRequest`: To block or redirect requests to unwanted domains

## 🧪 Testing

Make sure to test:

* Site blocking functionality
* Options saving and restoring
* Popup interface interactions
* Edge cases (like incorrect URLs or rapid tab switching)

## 📄 License

This project is licensed under the MIT License.

## 🙌 Contributions

Pull requests, bug reports, and feature suggestions are welcome!
Check out our teammate’s GitHub: [kalpana-mk](https://github.com/kalpana-mk)

```

Let me know if you'd like to include screenshots or add badges (like "Made with ❤️ in JavaScript" or "Chrome Extension").
```
