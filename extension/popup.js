/* popup.js */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const backendUrlInput = document.getElementById('backendUrl');
    const strictnessSelect = document.getElementById('strictness');
    const saveBtn = document.getElementById('saveBtn');
    const resetBtn = document.getElementById('resetBtn');
    
    const scannedCount = document.getElementById('scannedCount');
    const toxicCount = document.getElementById('toxicCount');
    const safeCount = document.getElementById('safeCount');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    // Load initial data
    loadSettings();
    updateStatsUI();

    // Event Listeners
    saveBtn.addEventListener('click', saveSettings);
    resetBtn.addEventListener('click', resetStats);

    // Refresh stats periodically while popup is open
    setInterval(updateStatsUI, 2000);
    
    // Check backend connection
    checkConnection();

    function loadSettings() {
        chrome.storage.local.get(['backendUrl', 'strictness'], (result) => {
            if (result.backendUrl) backendUrlInput.value = result.backendUrl;
            if (result.strictness) strictnessSelect.value = result.strictness;
        });
    }

    function saveSettings() {
        const settings = {
            backendUrl: backendUrlInput.value.trim(),
            strictness: strictnessSelect.value
        };

        chrome.storage.local.set(settings, () => {
            saveBtn.textContent = 'Saved!';
            saveBtn.style.backgroundColor = '#4CAF50';
            
            checkConnection(); // Recheck on save
            
            setTimeout(() => {
                saveBtn.textContent = 'Save Settings';
                saveBtn.style.backgroundColor = ''; // Reset to CSS default
            }, 2000);
        });
    }

    function updateStatsUI() {
        chrome.runtime.sendMessage({ action: "getStats" }, (response) => {
            if (response) {
                scannedCount.textContent = response.scannedCount;
                toxicCount.textContent = response.toxicCount;
                safeCount.textContent = response.safeCount;
            }
        });
    }

    function resetStats() {
        if (confirm("Are you sure you want to reset your moderation stats?")) {
            chrome.storage.local.set({ scannedCount: 0, toxicCount: 0, safeCount: 0 }, () => {
                updateStatsUI();
            });
        }
    }

    function checkConnection() {
        statusDot.className = 'status-dot'; // Remove connected/disconnected classes
        statusText.textContent = 'Checking connection...';

        chrome.storage.local.get(['backendUrl'], (result) => {
            const url = result.backendUrl || "https://tejesh916k-comment-guard-api.hf.space";
            
            // Just ping the root to see if server is alive
            fetch(`${url}/`)
                .then(response => {
                    if (response.ok) {
                        statusDot.classList.add('connected');
                        statusText.textContent = 'Connected to Guard AI';
                    } else {
                        throw new Error('Server returned error');
                    }
                })
                .catch(error => {
                    statusDot.classList.add('disconnected');
                    statusText.textContent = 'Offline (Check Backend URL)';
                });
        });
    }
});
