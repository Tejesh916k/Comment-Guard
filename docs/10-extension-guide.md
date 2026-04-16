# Chrome Extension Guide

## Overview

The Comment Guard Chrome extension monitors text input fields on all websites. When it detects toxic content, it warns the user and prevents submission.

## Installation

### Step 1 — Open Chrome Extensions Page
- Open **Google Chrome** (or any Chromium-based browser like Edge or Brave)
- Navigate to `chrome://extensions/`

### Step 2 — Enable Developer Mode
- Toggle the **Developer mode** switch in the top right corner to **ON**

### Step 3 — Load the Extension
- Click **Load unpacked**
- Navigate to the project folder and select the **`extension/`** folder (the one containing `manifest.json`)
- Click **Select Folder**

### Step 4 — Verify Installation
- "Comment Guard" should appear in your extensions list
- Pin it to the toolbar by clicking the puzzle piece icon → Pin

### Step 5 — Ensure Backend Is Running
- The extension requires the FastAPI backend server to be running
- Start it with: `cd backend && python main.py`
- The extension popup will show a **green dot** when connected

## How It Works

### Input Monitoring

The extension watches for text input on every webpage using three methods:

| Method | What It Catches |
|---|---|
| `input` / `keyup` / `paste` events | Standard text fields and textareas |
| `MutationObserver` | React/SPA apps that update the DOM directly |
| DOM tree traversal | Nested contenteditable elements |

### Supported Platforms

| Platform | Input Type Detected |
|---|---|
| **YouTube** | Comment boxes (`ytd-commentbox`) |
| **Instagram** | Direct message and comment fields (Draft.js/Lexical editors) |
| **WhatsApp Web** | Message input box (`div[title="Type a message"]`) |
| **Facebook** | Comment and post fields |
| **Generic Websites** | Any `<input>`, `<textarea>`, or `contenteditable` div |

### Toxic Content Feedback

When toxic content is detected, three things happen:

1. **Visual Warning**: Text turns orange-red and bold
2. **Tooltip**: A red floating badge appears — "🚨 Toxic content detected!"
3. **Submission Blocked**:
   - Send/Post/Reply buttons are visually disabled (faded, unclickable)
   - Enter key is intercepted and blocked (with a shake animation)
   - Shift+Enter still works for adding new lines

When the user edits the comment to remove toxic content, all warnings are removed.

## Popup Settings

Click the extension icon to open the popup. It provides:

### Connection Status
- **Green dot** = Connected to backend
- **Red dot** = Backend unreachable (check URL and server)

### Statistics
- **Scanned**: Total comments analyzed
- **Toxic**: Comments flagged as toxic
- **Safe**: Comments that passed all checks

### Configuration

| Setting | Options | Description |
|---|---|---|
| **Backend URL** | Any URL | Where the FastAPI server is running |
| **Strictness** | High / Low | Controls ML model sensitivity |

### Buttons
- **Save Settings** — Saves the backend URL and strictness
- **Reset Stats** — Clears all scanned/toxic/safe counters

## File Structure

```
extension/
├── manifest.json     # Chrome Extension configuration
├── background.js     # Service worker (API communication)
├── content.js        # DOM monitoring & toxic feedback
├── content.css       # Warning tooltip styles
├── popup.html        # Popup UI markup
├── popup.js          # Popup logic
├── popup.css         # Popup styles
└── icons/            # Extension icons (16, 48, 128 px)
```

## Troubleshooting

| Issue | Solution |
|---|---|
| Red dot in popup | Ensure backend is running (`python main.py`) and URL is correct |
| Extension not detecting typing | Refresh the webpage (`F5`) after installing or updating the extension |
| "Extension context invalidated" in console | The extension was reloaded — refresh the page |
| No warnings on typed text | Check that the strictness is set and backend URL is correct |
