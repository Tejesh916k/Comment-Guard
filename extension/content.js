/* content.js - Keystroke Monitoring Script */

console.log("Comment Guard: Input monitor initialized.");

let typingTimer;
const doneTypingInterval = 800; // Time in ms (0.8 seconds) to wait after user stops typing
let currentTarget = null;

// Instagram and other React apps often use contenteditable divs that don't always fire 'input' normally, 
// or they capture the event differently. We listen to both 'input' and 'keyup' to be safe.

function handleInputEvent(event) {
    let target = event.target || event; // handle both events and elements directly
    if (!target) return;
    
    // Safely handle text nodes
    if (target.nodeType === 3) {
        target = target.parentNode;
    }
    
    // Find the actual editable container
    let editableContainer = target;
    if (editableContainer && !editableContainer.isContentEditable && typeof editableContainer.closest === 'function') {
        // Look for standard inputs OR WhatsApp/Facebook/YouTube specialized editors
        const closestContentEditable = editableContainer.closest(
            '[contenteditable="true"], [contenteditable="plaintext-only"], textarea, input[type="text"], div[data-lexical-editor="true"], div[title="Type a message"], yt-formatted-string#contenteditable-root, div#contenteditable-root'
        );
        if (closestContentEditable) {
            editableContainer = closestContentEditable;
        }
    }

    if (!editableContainer) return;

    // Check if valid input
    const isTextInput = editableContainer.tagName === 'INPUT' && (editableContainer.type === 'text' || editableContainer.type === 'search');
    const isTextArea = editableContainer.tagName === 'TEXTAREA';
    const isContentEditable = editableContainer.isContentEditable || 
                              editableContainer.getAttribute('contenteditable') === 'true' || 
                              editableContainer.getAttribute('contenteditable') === 'plaintext-only';

    if (isTextInput || isTextArea || isContentEditable) {
        clearTimeout(typingTimer);
        currentTarget = editableContainer;
        
        let text = "";
        if (isTextInput || isTextArea) {
            text = editableContainer.value;
        } else if (isContentEditable) {
            // Instagram/Facebook use Draft.js/Lexical which heavily nests text.
            // InnerText is actually better here because it preserves spaces/newlines.
            text = editableContainer.innerText || editableContainer.textContent || "";
        }

        if (text.trim().length > 0) {
            showScanningIndicator(editableContainer);
            
            typingTimer = setTimeout(() => {
                checkTextToxicity(text, editableContainer);
            }, doneTypingInterval);
        } else {
            clearWarning(editableContainer);
        }
    }
}

// 1. Standard event listeners
document.addEventListener('input', handleInputEvent, true);
document.addEventListener('keyup', handleInputEvent, true);
document.addEventListener('paste', handleInputEvent, true);

// 2. MutationObserver (Critical for React/Instagram)
// React often updates the DOM directly without firing standard input events that bubble up
const observer = new MutationObserver((mutations) => {
    for (let mutation of mutations) {
        if (mutation.type === 'characterData' || mutation.type === 'childList') {
            // If text changed inside a contenteditable, trigger our handler
            let target = mutation.target;
            if (target.nodeType === 3) target = target.parentNode; // Get element from text node
            
            if (target && typeof target.closest === 'function' && target.closest('[contenteditable="true"], [contenteditable="plaintext-only"]')) {
                handleInputEvent({ target: target });
                break; // Only need to trigger once per batch of mutations
            }
        }
    }
});

// Start observing the entire body for changes
observer.observe(document.body, { 
    characterData: true, 
    childList: true, 
    subtree: true 
});

// Removed yellow border, just set the flag so we know it's scanning internally
function showScanningIndicator(element) {
    if (!element.dataset.cgScanning) {
        element.dataset.cgScanning = "true";
    }
}


function checkTextToxicity(text, element) {
    // Send message to background script to check the text
    try {
        chrome.runtime.sendMessage(
            { action: "checkComment", text: text },
            (response) => {
                if (chrome.runtime.lastError) {
                    console.error("Comment Guard Error:", chrome.runtime.lastError.message);
                    return;
                }

                if (response && response.success) {
                    if (response.data.is_toxic) {
                        showWarning(element);
                    } else {
                        clearWarning(element);
                    }
                }
            }
        );
    } catch (e) {
        // Suppress "Extension context invalidated" uncaught errors.
        // This only happens when the developer reloads the extension but forgets to refresh the page.
        if (e.message && e.message.includes("Extension context invalidated")) {
            console.warn("Comment Guard: Extension was reloaded. Please refresh this page (F5) to restore functionality.");
        } else {
            console.error("Comment Guard Error:", e);
        }
    }
}

function showWarning(element) {
    // Apply inline styles to turn text red/orange
    element.style.setProperty('color', '#ff4500', 'important'); // Orange-red text
    element.style.setProperty('font-weight', 'bold', 'important');
    
    // Mark element as toxic so we can block the Enter key
    element.dataset.cgToxic = "true";
    
    // Find and disable the "Send" button on Instagram
    // Instagram's Send button is usually a nearby div with role="button" containing "Send"
    disableSendButton(element);
    
    // Check if warning tooltip already exists
    let tooltipId = "cg-warning-" + Math.random().toString(36).substr(2, 9);
    if (!element.dataset.cgTooltip) {
        element.dataset.cgTooltip = tooltipId;
        
        const tooltip = document.createElement("div");
        tooltip.id = tooltipId;
        tooltip.className = "comment-guard-tooltip";
        tooltip.innerText = "🚨 Toxic content detected! Please edit your message.";
        
        // Position it right above the input
        const rect = element.getBoundingClientRect();
        tooltip.style.position = "absolute";
        // Put it slightly above and to the left
        tooltip.style.top = Math.max(0, (window.scrollY + rect.top - 35)) + "px";
        tooltip.style.left = (window.scrollX + rect.left) + "px";
        tooltip.style.zIndex = "999999999";
        
        document.body.appendChild(tooltip);
    }
}

function disableSendButton(inputElement) {
    // Traverse up to find the common chat/comment container
    const container = inputElement.closest('form') || 
                      inputElement.closest('ytd-commentbox') || // YouTube comment box
                      inputElement.closest('div[style*="border"], div[role="button"]')?.parentElement?.parentElement || 
                      inputElement.closest('footer') || // WhatsApp Web usually puts chat in a footer
                      document.body;
    
    // Look for generic send/post/reply buttons and platform-specific icons
    const sendButtons = Array.from(container.querySelectorAll('div[role="button"], button, span[data-icon="send"], ytd-button-renderer#submit-button')).filter(btn => {
        const text = btn.textContent.trim().toLowerCase();
        const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
        const dataIcon = (btn.getAttribute('data-icon') || '').toLowerCase();
        const id = (btn.id || '').toLowerCase();
        
        return text === 'send' || text === 'post' || text === 'reply' || text === 'comment' || 
               ariaLabel === 'send' || ariaLabel === 'post' || ariaLabel === 'reply' || ariaLabel === 'comment' ||
               dataIcon === 'send' || id === 'submit-button';
    });
    
    sendButtons.forEach(btn => {
        // If it's a span (like WhatsApp's icon), disable its parent button/div
        const targetBtn = btn.tagName === 'SPAN' ? btn.parentElement : btn;
        
        targetBtn.dataset.cgDisabledBtn = "true";
        targetBtn.style.setProperty('pointer-events', 'none', 'important');
        targetBtn.style.setProperty('opacity', '0.2', 'important'); // Make it very obvious it's disabled
        targetBtn.style.setProperty('cursor', 'not-allowed', 'important');
    });
}

function clearWarning(element) {
    // Remove text coloring
    element.style.removeProperty('color');
    element.style.removeProperty('font-weight');
    
    if (element.dataset.cgToxic) {
        delete element.dataset.cgToxic;
    }
    
    // Re-enable Send buttons
    enableSendButtons();
    
    if (element.dataset.cgScanning) {
        delete element.dataset.cgScanning;
    }
    
    if (element.dataset.cgTooltip) {
        const tooltip = document.getElementById(element.dataset.cgTooltip);
        if (tooltip) {
            tooltip.remove();
        }
        delete element.dataset.cgTooltip;
    }
}

function enableSendButtons() {
    const disabledButtons = document.querySelectorAll('[data-cg-disabled-btn="true"]');
    disabledButtons.forEach(btn => {
        btn.style.removeProperty('pointer-events');
        btn.style.removeProperty('opacity');
        btn.style.removeProperty('cursor');
        delete btn.dataset.cgDisabledBtn;
    });
}

// Block the Enter key if the input is marked as toxic
document.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        let target = event.target || event;
        // Find the editable container
        if (target.nodeType === 3) target = target.parentNode;
        let editableContainer = target;
        if (editableContainer && typeof editableContainer.closest === 'function') {
            const closestContentEditable = editableContainer.closest('[contenteditable="true"], [contenteditable="plaintext-only"], textarea, input[type="text"]');
            if (closestContentEditable) {
                editableContainer = closestContentEditable;
            }
        }
        
        // If it's a toxic container, prevent the Enter key from submitting
        if (editableContainer && editableContainer.dataset.cgToxic === "true") {
            // Allow shift+enter for newlines, but block bare enter for submission
            if (!event.shiftKey) {
                event.preventDefault();
                event.stopPropagation();
                
                // Shake the element to indicate it's blocked
                editableContainer.style.setProperty('transform', 'translateX(5px)', 'important');
                setTimeout(() => {
                    editableContainer.style.setProperty('transform', 'translateX(-5px)', 'important');
                    setTimeout(() => {
                        editableContainer.style.removeProperty('transform');
                    }, 50);
                }, 50);
            }
        }
    }
}, true); // Use capture phase to intercept before React handles it

