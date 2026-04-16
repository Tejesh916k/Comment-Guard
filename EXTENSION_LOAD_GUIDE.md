# How to Load the Comment Guard Extension

To use the extension in your browser, you need to load the **`extension/`** folder as an "unpacked" extension.

## Step-by-Step Instructions

1. **Open Google Chrome** (or any Chromium-based browser like Edge or Brave).
2. **Navigate to the Extensions page**:
   - Type `chrome://extensions/` in the address bar and press Enter.
   - Alternatively, click the **Three Dots (⋮) -> Extensions -> Manage Extensions**.
3. **Enable Developer Mode**:
   - In the top right corner, toggle the switch for **Developer mode** to ON.
4. **Extract and Load the Extension**:
   - Extract the `CommentGuard-v2.1.zip` archive (or use the `extension` folder in this repository).
   - Click the **Load unpacked** button that appears in the top left.
   - Select the **`extension`** folder (the folder containing `manifest.json`).
   - Click **Select Folder**.
5. **Verify Installation**:
   - You should now see the "Comment Guard" extension in your list.
   - Make sure the toggle on the extension card is turned ON.

## Using the Extension
- Pin the extension to your toolbar for easy access.
- Click the extension icon to see the popup. The backend connects automatically to the live Hugging Face deployment (`https://tejesh916k-comment-guard-api.hf.space`). You should see a green "Connected to Guard AI" status without running anything locally!
- Navigate to YouTube, Instagram, or Facebook to see it in action!
