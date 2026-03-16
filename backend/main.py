from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from better_profanity import profanity
from typing import List, Dict
import re

# Mild/acceptable words that better_profanity should NOT flag.
# Using the library's built-in whitelist_words param is the most reliable fix.
MILD_WORDS_WHITELIST = [
    "damn", "hell", "crap", "dang", "heck", "shoot", "frick", "freaking",
    "sucks", "suck", "bloody", "piss", "pissed",
]

# Initialize profanity filter with whitelisted mild words so they never trigger
profanity.load_censor_words(whitelist_words=MILD_WORDS_WHITELIST)

# Keep a set for the manual cleanup fallback (covers multi-word phrases)
PROFANITY_WHITELIST = set(MILD_WORDS_WHITELIST) | {"keep it up", "great post"}

# Pre-compiled regex patterns for profanity whitelist
PROFANITY_WHITELIST_PATTERNS = {word: re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE) for word in PROFANITY_WHITELIST}

def is_whitelisted(text: str) -> bool:
    """Check if the text only triggers profanity due to whitelisted mild words."""
    cleaned = text.lower()
    for pattern in PROFANITY_WHITELIST_PATTERNS.values():
        cleaned = pattern.sub("", cleaned)
    return not profanity.contains_profanity(cleaned)

# Keyword-based insult/threat detector to catch what the ML model misses.
# Unicode apostrophe class ['‘’] handles both ASCII (') and curly (’) apostrophes.
INSULT_KEYWORDS = [
    # --- English insults / threats ---
    r"\byou['‘’]?re so dumb\b",
    r"\bwhat a loser\b",
    r"\bi will find you\b",
    r"\byou deserve to die\b",
    r"\bi hate you\b",
    r"\byou['‘’]?re disgusting\b",
    r"\bnobody likes you\b",
    r"\byou['‘’]?re pathetic\b",
    r"\bget lost\b",
    r"\bnobody asked\b",
    r"\byou['‘’]?re worthless\b",
    r"\byou['‘’]?re trash\b",
    r"\bkill yourself\b",
    r"\bgo kill yourself\b",
    r"\byou['‘’]?re ugly\b",
    r"\bshut up\b",
    r"\byou['‘’]?re annoying\b",
    r"\bgo to hell\b",
    r"\bstupid ga\b",
    r"\bwaste fellow\b",
    r"\byou['‘’]?re an idiot\b",
    r"\bthis is garbage\b",
    r"\byou are stupid\b",
    r"\byou are an idiot\b",
    r"\byou['‘’]?re dumb\b",
    r"\bstupid idiot\b",
    r"\bbloody fool\b",
    # --- Telugu-English compound insults: [insult word] + gadu/fellow/vaadu ---
    r"\b(?:buffalo|monkey|mental|psycho|cheap|nasty|dirty|useless|worst|scoundrel)"
    r"\s+(?:gadu|fellow|vaadu|ra)\b",
    r"\b(?:rascal|buffoon|loafer|fraud|basthi|chapri|local|rowdy|420|kothi|waste)"
    r"\s+(?:gadu|fellow|vaadu|ra)\b",
    r"\b(?:third\s+class|low\s+class|third-class|low-class)\s+(?:gadu|fellow|vaadu)\b",
    r"\b(?:buffalo|monkey|mental|psycho|cheap|nasty|dirty|useless|worst|scoundrel|rascal|buffoon|loafer|fraud)\s+fellow\b",
    # --- Telugu standalone insult suffixes ---
    r"\bkothi\s+vedhava\b",
]
INSULT_PATTERN = re.compile("|".join(INSULT_KEYWORDS), re.IGNORECASE | re.UNICODE)

def contains_insult_keyword(text: str) -> bool:
    """Check if text contains known insult/threat patterns."""
    return bool(INSULT_PATTERN.search(text))

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
# However, for toxicity detection in Telugu-English code-mixed content, MuRIL (Multilingual 
# Representations for Indian Languages) BERT is preferred over standard DistilBERT or toxic-bert.
# MuRIL is specifically trained on Indian languages and handles code-switching much better.
# Current production model: google/muril-base-cased (fine-tuned)
import torch

# Optimizatons to prevent PyTorch from lagging the entire OS when running on CPU
try:
    if torch.cuda.is_available():
        device = 0 # Use GPU
        print("✓ CUDA GPU detected, running models on GPU for faster inference.")
    else:
        device = -1 # Use CPU
        torch.set_num_threads(config.get("cpu_threads", 4)) # Limit to 4 threads rather than maxing out CPU
        print(f"✓ CPU detected, limited PyTorch to {torch.get_num_threads()} threads to prevent system lag.")
except Exception as e:
    device = -1
    pass

try:
    # Use fine-tuned model if available (produced by train_model.py)
    fine_tuned_path = os.path.join(os.path.dirname(__file__), "model_output")
    if os.path.exists(fine_tuned_path) and os.path.exists(os.path.join(fine_tuned_path, "config.json")):
        print(f"✓ Loading fine-tuned model from: {fine_tuned_path}")
        classifier = pipeline("text-classification", model=fine_tuned_path, top_k=None, device=device)
    else:
        print("Loading default model: google/muril-base-cased (Fallback)")
        print("Note: MuRIL is highly recommended for Telugu-English code-mixed content.")
        classifier = pipeline("text-classification", model="google/muril-base-cased", top_k=None, device=device)
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
    # MILD_WORDS_WHITELIST is already removed from the profanity library's censor list,
    # so only genuine profanity (slurs, explicit words) will be flagged here.
    if profanity.contains_profanity(text):
        # Extra safety: remove any remaining multi-word safe phrases and re-check using PRECOMPILED regex
        cleaned_text = text.lower()
        for pattern in PROFANITY_WHITELIST_PATTERNS.values():
            cleaned_text = pattern.sub("", cleaned_text)
            
        if profanity.contains_profanity(cleaned_text):
            return AnalysisResponse(
                text=request.text,
                results=[Score(label="profanity_strict", score=1.0)],
                is_toxic=True
            )
        # Only multi-word mild phrase triggered it — continue to deeper checks

    # 1b. Keyword-based insult/threat detector (catches ML model blind spots)
    if contains_insult_keyword(text):
        return AnalysisResponse(
            text=request.text,
            results=[Score(label="insult_keyword", score=1.0)],
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
    # High (Celeb) = 0.4 (Strict)
    # Low (Friend) = 0.7 (Balanced)
    threshold = 0.4 if request.strictness == "high" else 0.7

    # Labels that indicate toxicity. Ignores 'LABEL_0', 'non-toxic', 'neutral', etc.
    TOXIC_LABELS = {"toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate", "LABEL_1"}

    for item in scores:
        label = item['label']
        score = item['score']
        formatted_scores.append(Score(label=label, score=score))
        
        # Only mark as toxic if the label is in our toxic set AND exceeds threshold
        if label in TOXIC_LABELS and score > threshold: 
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
    is_toxic = any(item['score'] > 0.5 for item in results)
    
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
