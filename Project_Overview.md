# Comment Guard: AI-Based Real-Time Comment Moderation System

## Project Overview

Comment Guard is a full-stack AI-powered comment moderation system designed to detect and filter toxic, offensive, and hateful comments in real-time. It features specialized support for Telugu-English code-mixed text (Tenglish).

The system combines a Transformer-based machine learning model with rule-based detection to achieve high accuracy across diverse test cases.

### Key Features
* Multi-layered detection: Profanity filter, Keyword regex, Emoji detection, and ML model.
* Telugu-English support: Specialized detection for code-mixed (Tenglish) insults.
* Adjustable strictness: Switch between "High" (celebrity pages) and "Low" (friend chats) modes.
* Real-time analysis: Comments are analyzed and filtered before they are posted.
* Modern Interface: Instagram-style feed with toxicity warnings and visual indicators.

---

## System Architecture

The following detection pipeline ensures high-precision filtering:

1. Profanity Filter: Uses the better-profanity library combined with a custom Telugu badwords list.
2. Keyword Regex: Over 40 compiled regex patterns for insults, threats, and Tenglish slurs.
3. Emoji Check: A dedicated list for detecting offensive or vulgar emojis.
4. ML Model: A fine-tuned **MuRIL BERT** (`google/muril-base-cased`) model for understanding contextual toxicity in Telugu-English code-mixed content.

---

## Datasets Used

### 1. HOLD-Telugu Dataset
* Source: Dravidian Language Technology shared tasks (DravidianLangTech).
* Samples: Approximately 4,000 samples after deduplication.
* Class Distribution: Balanced between toxic and non-toxic labels.
* Content: Telugu-English code-mixed social media comments.

### 2. Telugu-English Test Data
* Samples: 500 labeled test cases (250 toxic + 250 non-toxic).
* Purpose: Evaluation of code-mixed text performance.

### 3. Word Databases
* Telugu Bad Words: Comprehensive list of offensive Telugu terms.
* Secure Vault: Encrypted storage for highly sensitive offensive words.
* Emoji List: Catalog of offensive emoji characters.

---

## Technology Stack

### Backend
* Language: Python 3.12
* Framework: FastAPI (Async REST API)
* Deep Learning: PyTorch and HuggingFace Transformers
* Model: Fine-tuned **MuRIL BERT** (google/muril-base-cased)
* Processing: Pandas and Scikit-learn for data and metrics

### Frontend
* Framework: React 18.2 with Vite
* Styling: Tailwind CSS
* Icons: Lucide React
* API Client: Axios

### DevOps
* Containerization: Docker and Docker Compose
* Analytics: Custom training and evaluation logs

---

## Performance Metrics

* Accuracy: 92.33%
* True Positives: 157
* True Negatives: 120
* False Positives: 0
* False Negatives: 23
* Total Test Cases: 300

---

## Frequently Asked Questions (FAQs)

### Why use a hybrid approach (Rules + ML)?
Pure ML models can sometimes miss explicit profanity or specific cultural insults. The rule-based layers provide immediate, high-precision filtering for known terms, while the ML model handles the subtle, contextual, and novel toxic content.

### How is Telugu-English code-mixed text handled?
The system uses a combination of a Telugu bad words database, regex patterns for Tenglish compound insults (e.g., "[insult] + gadu"), and an ML model fine-tuned on the HOLD-Telugu dataset.

### How are false positives prevented?
We maintain a whitelist of mild terms and safe phrases (e.g., "keep it up"). Additionally, the ML model threshold is adjustable—Celebrity mode uses a stricter threshold, while Friend mode is more lenient.

### What are the future plans for the system?
Future improvements include supporting more Indian languages (Hindi, Tamil), implementing an admin dashboard for moderation analytics, and fine-tuning on even larger datasets or models to handle regional slang. (MuRIL support is already implemented).
