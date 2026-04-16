# System Architecture

## Overview

Comment Guard follows a **client-server** architecture. The Chrome extension acts as the client, and a FastAPI server acts as the backend. The backend runs a multi-layer detection pipeline to classify comments.

## Architecture Diagram

```mermaid
flowchart LR
    subgraph Browser["Chrome Browser"]
        CS[content.js\nDOM Monitor]
        BG[background.js\nService Worker]
        PU[popup.html\nSettings UI]
    end

    subgraph Backend["FastAPI Server"]
        API["/analyze Endpoint"]
        L1["Layer 1\nProfanity Filter"]
        L2["Layer 2\nKeyword Regex"]
        L3["Layer 3\nEmoji Check"]
        L4["Layer 4\nMuRIL BERT Model"]
    end

    CS -->|"sendMessage(text)"| BG
    PU -->|"getStats"| BG
    BG -->|"POST /analyze"| API
    API --> L1 --> L2 --> L3 --> L4
    API -->|"{ is_toxic, results }"| BG
    BG -->|"response"| CS
```

## Detection Pipeline — Detailed Flow

The backend processes each comment through **four layers** in sequence. If any layer flags the comment as toxic, it short-circuits and returns immediately without running the remaining layers.

```mermaid
flowchart TD
    A["Incoming Comment"] --> B{"Layer 1: Profanity Filter\n(better_profanity + Telugu bad words)"}
    B -->|"Profanity Found"| TOXIC["🔴 Return: TOXIC"]
    B -->|"Clean"| C{"Layer 1b: Keyword Regex\n(40+ insult/threat patterns)"}
    C -->|"Match Found"| TOXIC
    C -->|"No Match"| D{"Layer 2: Emoji Check\n(offensive emoji list)"}
    D -->|"Offensive Emoji"| TOXIC
    D -->|"Clean"| E{"Text < 5 chars?"}
    E -->|"Yes"| SAFE["🟢 Return: SAFE"]
    E -->|"No"| F{"Layer 3: MuRIL BERT\n(ML Classification)"}
    F -->|"Score > Threshold"| TOXIC
    F -->|"Score ≤ Threshold"| SAFE
```

## Why a Multi-Layer Approach?

| Layer | Strengths | Limitations |
|---|---|---|
| **Profanity Filter** | Instant, zero false negatives on known words | Cannot catch new or misspelled slurs |
| **Keyword Regex** | Catches compound insults (e.g., "waste fellow") | Cannot understand context or sarcasm |
| **Emoji Check** | Catches visual toxicity | Limited to known offensive emojis |
| **MuRIL BERT** | Understands context, tone, and novel insults | Requires GPU for fast inference; may miss rare slang |

The rule-based layers act as a **fast first line of defense**. The ML model handles the **nuanced, context-dependent cases** that rules cannot cover.

## End-to-End Request Flow

1. **User types** in any text input on any website
2. **`content.js`** detects the input via event listeners and a MutationObserver
3. After **800ms of inactivity** (debounce), the text is sent to `background.js`
4. **`background.js`** forwards it as `POST /analyze` to the FastAPI backend
5. **`main.py`** runs the 4-layer detection pipeline
6. The result (`is_toxic: true/false`) is returned to the extension
7. **`content.js`** applies visual feedback:
   - **Toxic** → orange-red text, tooltip warning, Send button disabled, Enter key blocked
   - **Safe** → all warnings cleared

## Strictness Modes

| Mode | Threshold | Use Case |
|---|---|---|
| **High** (Strict) | 0.4 | Celebrity pages, public forums — catches more borderline cases |
| **Low** (Balanced) | 0.7 | Friend chats, private groups — allows casual language |

The threshold applies only to the ML model layer. Rule-based layers always trigger regardless of the strictness setting.
