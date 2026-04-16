# API Reference

## Base URL

```
http://localhost:8000
```

## Endpoints

### GET `/`

Health check endpoint. Returns a simple message confirming the server is running.

**Response:**
```json
{
  "message": "AI Comment Moderation API is running"
}
```

---

### POST `/analyze`

Analyzes a comment and returns whether it is toxic or safe. This is the primary endpoint used by the Chrome extension.

**Request Body:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | ✅ Yes | — | The comment text to analyze |
| `strictness` | string | No | `"high"` | `"high"` (strict) or `"low"` (balanced) |

**Example Request:**
```json
{
  "text": "nuvvu waste fellow ra",
  "strictness": "high"
}
```

**Response:**

| Field | Type | Description |
|---|---|---|
| `text` | string | The original input text |
| `results` | array | List of scores from the ML model |
| `is_toxic` | boolean | `true` if the comment is toxic |

**Example Response (Toxic):**
```json
{
  "text": "nuvvu waste fellow ra",
  "results": [
    { "label": "insult_keyword", "score": 1.0 }
  ],
  "is_toxic": true
}
```

**Example Response (Safe):**
```json
{
  "text": "super ga undi bro",
  "results": [
    { "label": "toxic", "score": 0.05 },
    { "label": "severe_toxic", "score": 0.01 },
    { "label": "obscene", "score": 0.03 },
    { "label": "threat", "score": 0.01 },
    { "label": "insult", "score": 0.02 },
    { "label": "identity_hate", "score": 0.01 }
  ],
  "is_toxic": false
}
```

**Detection Labels Returned:**

| Label | Source | Description |
|---|---|---|
| `profanity_strict` | Rule-based | Triggered by the profanity filter |
| `insult_keyword` | Rule-based | Triggered by regex insult patterns |
| `offensive_emoji` | Rule-based | Triggered by offensive emoji detection |
| `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate` | ML Model | Scores from the MuRIL BERT classifier |

---

### POST `/submit`

Mock endpoint for posting a comment (simulates saving to a database). Rejects toxic comments.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `text` | string | ✅ Yes | The comment text to post |

**Success Response:**
```json
{
  "message": "Comment posted successfully",
  "text": "Great video, keep it up!"
}
```

**Error Response (Toxic Comment):**
```json
{
  "detail": "Comment rejected due to toxicity."
}
```
Status Code: `400`

---

## Running the Server

### Local Development
```bash
cd backend
pip install -r requirements.txt
python main.py
```

The server starts at `http://localhost:8000` with auto-reload enabled.

### Docker
```bash
docker-compose up backend
```

### SSL/HTTPS (Optional)
Place `cert.pem` and `key.pem` in the `backend/data/` directory. The server will automatically detect and use them for HTTPS.
