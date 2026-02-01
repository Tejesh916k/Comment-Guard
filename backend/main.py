from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from better_profanity import profanity
from typing import List, Dict

# Initialize strict profanity filter with default words
profanity.load_censor_words()

# Load Custom Telugu-English Bad Words (Secure)
import base64
import os

try:
    secure_file_path = "data/secure_words.bin"
    if os.path.exists(secure_file_path):
        with open(secure_file_path, "rb") as f:
            encoded_data = f.read()
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            custom_words = [line.strip() for line in decoded_data.splitlines() if line.strip()]
            profanity.add_censor_words(custom_words)
        print(f"Loaded {len(custom_words)} custom bad words from secure storage.")
    else:
        print("Warning: Secure bad words file not found.")
except Exception as e:
    print(f"Warning: Could not load custom bad words: {e}")

# Load Offensive Emojis
offensive_emojis = set()
try:
    emoji_file_path = "data/bad_emojis.txt"
    if os.path.exists(emoji_file_path):
        with open(emoji_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    offensive_emojis.add(line)
        print(f"Loaded {len(offensive_emojis)} offensive emojis.")
    else:
        print("Warning: Offensive emojis file not found.")
except Exception as e:
    print(f"Warning: Could not load offensive emojis: {e}")

def contains_offensive_emoji(text: str) -> bool:
    """Check if text contains any offensive emojis"""
    for emoji in offensive_emojis:
        if emoji in text:
            return True
    return False


app = FastAPI(title="AI Comment Moderation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the toxicity classification pipeline
# We use 'original' to keep the original distilbert-base-uncased-finetuned-sst-2-english if we wanted simple sentiment
# But for toxicity, 'unitary/toxic-bert' is preferred. 
# However, to avoid huge downloads during a demo, we can use a smaller model or just 'text-classification'.
# Let's stick to the plan: DistilBERT fine-tuned on toxic comments.
# 'unitary/toxic-bert' is excellent but might be large.
# 'martin-haas/toxic-comment-model' is a distilbert version.
# Let's use a standard pipeline that is robust.
try:
    classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)
except Exception as e:
    print(f"Error loading model: {e}")
    classifier = None

class CommentRequest(BaseModel):
    text: str
    strictness: str = "high" # "high" (Celeb) or "low" (Friend)

class Score(BaseModel):
    label: str
    score: float

class AnalysisResponse(BaseModel):
    text: str
    results: List[Score]
    is_toxic: bool

@app.get("/")
def read_root():
    return {"message": "AI Comment Moderation API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_comment(request: CommentRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # 1. Strict "Bad Word" Check (Rule-based)
    # catches "complete bad words" instantly - ALWAYS APPLIES
    if profanity.contains_profanity(text):
        return AnalysisResponse(
            text=request.text,
            results=[Score(label="profanity_strict", score=1.0)],
            is_toxic=True
        )
    
    # 2. Offensive Emoji Check
    if contains_offensive_emoji(text):
        return AnalysisResponse(
            text=request.text,
            results=[Score(label="offensive_emoji", score=1.0)],
            is_toxic=True
        )


    # 2. Short Text Heuristic
    if len(text) < 5:
        return AnalysisResponse(
            text=request.text,
            results=[],
            is_toxic=False
        )
    
    # 3. ML Model Check (Context-based)
    if not classifier:
         print("Classifier not loaded, skipping ML check.")
         return AnalysisResponse(text=request.text, results=[], is_toxic=False)

    results = classifier(text)
    scores = results[0]
    
    is_toxic = False
    formatted_scores = []
    
    # Define Threshold based on Strictness
    # High (Celeb) = 0.6 (Sensitive but allows mild slang like 'crazy')
    # Low (Friend) = 0.85 (Allows banter)
    threshold = 0.6 if request.strictness == "high" else 0.85

    for item in scores:
        formatted_scores.append(Score(label=item['label'], score=item['score']))
        if item['score'] > threshold: 
            is_toxic = True
            
    return AnalysisResponse(
        text=request.text,
        results=formatted_scores,
        is_toxic=is_toxic
    )

@app.post("/submit")
def submit_comment(request: CommentRequest):
    # This is a mock endpoint. In a real app, this would save to DB.
    # We re-check toxicity here to prevent bypassing frontend
    if not classifier:
         raise HTTPException(status_code=500, detail="Model not loaded")
         
    results = classifier(request.text)[0]
    is_toxic = any(item['score'] > 0.7 for item in results)
    
    if is_toxic:
        raise HTTPException(status_code=400, detail="Comment rejected due to toxicity.")
        
    return {"message": "Comment posted successfully", "text": request.text}

if __name__ == "__main__":
    import uvicorn
    import os

    # Check for SSL certificates in data directory or root
    key_file = "data/key.pem" if os.path.exists("data/key.pem") else "key.pem"
    cert_file = "data/cert.pem" if os.path.exists("data/cert.pem") else "cert.pem"

    if os.path.exists(key_file) and os.path.exists(cert_file):
        print(f"Starting server with SSL/HTTPS enabled using {cert_file} and {key_file}...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, ssl_keyfile=key_file, ssl_certfile=cert_file)
    else:
        print("SSL certificates not found. Starting server in HTTP mode.")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
