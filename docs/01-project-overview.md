# Comment Guard — Project Overview

## What Is Comment Guard?

Comment Guard is an AI-powered real-time comment moderation system. It detects **toxic, offensive, and hateful comments** before they are posted on social media platforms.

It is built specifically to handle **Telugu-English code-mixed text** (commonly called "Tenglish") — a style of writing widely used across Indian social media.

## How It Works

Comment Guard runs as a **Chrome browser extension** that silently monitors text input fields on any website. When a user types a comment, the extension sends the text to a backend server that uses a **four-layer detection pipeline** to classify it as safe or toxic.

If the comment is toxic:
- The text turns **orange-red** as a visual warning
- A **tooltip** appears: "🚨 Toxic content detected!"
- The **Send/Post button** is disabled
- The **Enter key** is blocked to prevent submission

If the user edits the comment to remove toxic content, everything returns to normal.

## Key Features

| Feature | Description |
|---|---|
| **Multi-Layer Detection** | Combines rule-based filtering with ML for high accuracy |
| **Telugu-English Support** | Handles code-mixed Tenglish insults and slang |
| **MuRIL BERT Model** | Uses Google's Indian-language-optimized Transformer model |
| **Adjustable Strictness** | Two modes — High (strict) and Low (balanced) |
| **Real-Time Analysis** | Comments are checked as the user types |
| **Cross-Platform** | Works on YouTube, Instagram, WhatsApp Web, Facebook, and more |

## Technology Stack

| Layer | Technology |
|---|---|
| **Browser Extension** | Chrome Extension (Manifest V3), JavaScript |
| **Backend API** | Python, FastAPI, Uvicorn |
| **ML Framework** | PyTorch, HuggingFace Transformers |
| **ML Model** | `google/muril-base-cased` (fine-tuned) |
| **Data Processing** | Pandas, Scikit-learn |
| **Containerization** | Docker, Docker Compose |

## Project Structure

```
Comment-Guard/
├── backend/                  # Python backend server
│   ├── main.py               # FastAPI application & detection pipeline
│   ├── train_model.py        # Local model training script
│   ├── kaggle_training_v3.py # Kaggle-optimized training (MuRIL BERT)
│   ├── admin_manager.py      # Secure word list management CLI
│   ├── verify_model.py       # Interactive model testing tool
│   ├── data/                 # Training data & word lists
│   ├── model_output/         # Fine-tuned model files
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile            # Container image definition
├── extension/                # Chrome browser extension
│   ├── manifest.json         # Extension configuration (MV3)
│   ├── content.js            # DOM monitoring & toxic feedback
│   ├── background.js         # Service worker (API communication)
│   ├── popup.html/js/css     # Extension popup UI
│   └── content.css           # Warning tooltip styles
├── docs/                     # Project documentation
└── docker-compose.yml        # Multi-container orchestration
```
