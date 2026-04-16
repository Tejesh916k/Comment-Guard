/* background.js */

console.log("Comment Guard Background Service Worker started.");

// Default settings
const defaultSettings = {
    backendUrl: "https://tejesh916k-comment-guard-api.hf.space",
    strictness: "low"
};

// Initialize settings on install
chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.get(['backendUrl', 'strictness'], (result) => {
        if (!result.backendUrl) {
            chrome.storage.local.set(defaultSettings);
        }
    });
});

// Handle messages from content.js OR popup.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "checkComment") {
        // Fetch current backend URL from storage
        chrome.storage.local.get(['backendUrl'], (result) => {
            const apiUrl = result.backendUrl || defaultSettings.backendUrl;
            console.log(`Checking text length: ${request.text.length} at URL: ${apiUrl}`);

            // Call the FastAPI Backend
            fetch(`${apiUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: request.text })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Prediction result:", data);
                // Return result to content script
                sendResponse({ success: true, data: data });
                
                // Update stats
                updateStats(data.is_toxic);
            })
            .catch(error => {
                console.error("Error communicating with Comment Guard backend:", error);
                sendResponse({ success: false, error: error.message });
            });
        });
        
        // Return true to indicate we will respond asynchronously
        return true; 
    }
    
    if (request.action === "getStats") {
        chrome.storage.local.get(['scannedCount', 'toxicCount', 'safeCount'], (result) => {
            sendResponse({
                scannedCount: result.scannedCount || 0,
                toxicCount: result.toxicCount || 0,
                safeCount: result.safeCount || 0
            });
        });
        return true;
    }
});

function updateStats(isToxic) {
    chrome.storage.local.get(['scannedCount', 'toxicCount', 'safeCount'], (result) => {
        const stats = {
            scannedCount: (result.scannedCount || 0) + 1,
            toxicCount: (result.toxicCount || 0) + (isToxic ? 1 : 0),
            safeCount: (result.safeCount || 0) + (!isToxic ? 1 : 0)
        };
        chrome.storage.local.set(stats);
    });
}
