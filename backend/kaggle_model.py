"""
Fine-tune for Kaggle environment - ADVANCED 90%+ ACCURACY CONFIGURATION.

KAGLLE SETUP:
1. Upload your data folder as a Kaggle Dataset named 'new-data'.
2. Enable GPU T4 x2 in the notebook settings.
3. Run this script in a notebook cell.
"""

import os
import sys
import json
import base64
import random
from pathlib import Path

# Force unbuffered output 
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

print("DEBUG: Kaggle Training Script started [ADVANCED V2]", flush=True)

# ── Paths ────────────────────────────────────────────────
KAGGLE_INPUT = Path("/kaggle/input")
KAGGLE_OUTPUT = Path("/kaggle/working")

DATA_DIR = None
available_inputs = list(KAGGLE_INPUT.glob("*"))

for p in available_inputs:
    if p.is_dir() and any(p.glob("*training_data*")):
        DATA_DIR = p
        break

if not DATA_DIR:
    for p in KAGGLE_INPUT.rglob("*training_data*"):
        DATA_DIR = p.parent
        break

if not DATA_DIR:
    DATA_DIR = KAGGLE_INPUT / "new-data"

OUTPUT_DIR = KAGGLE_OUTPUT / "model_output"

print(f"DEBUG: Using DATA_DIR: {DATA_DIR}", flush=True)
print(f"DEBUG: Using OUTPUT_DIR: {OUTPUT_DIR}", flush=True)

# ── Dependencies ─────────────────────────────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    import transformers
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        TrainingArguments,
        Trainer,
        EarlyStoppingCallback
    )
    import pandas as pd
    import openpyxl
    import sklearn
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    import numpy as np
    from torch.utils.data import Dataset as TorchDataset
    from sklearn.model_selection import train_test_split
    from sklearn.utils.class_weight import compute_class_weight
except ImportError:
    print("DEBUG: Installing missing dependencies...", flush=True)
    os.system("pip install -q transformers torch scikit-learn accelerate openpyxl pandas")
    print("⚠ Please run: !pip install transformers torch scikit-learn accelerate openpyxl pandas")

# ── Setup Seeds for Reproducibility & Better Initialization ──────────────────
def set_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seeds(100) # Changed seed to shake model out of local minimum

# ── Config ────────────────────────────────────────────────────────────────────
BASE_MODEL    = "google/muril-base-cased" 
MAX_LENGTH    = 256  
EPOCHS        = 5    
LEARNING_RATE = 2e-5 

def is_code_mixed(text):
    text = str(text)
    has_latin = any('\u0041' <= c <= '\u007A' for c in text)
    total = len([c for c in text if c.strip()])
    telugu = len([c for c in text if '\u0C00' <= c <= '\u0C7F'])
    if total == 0 or not has_latin: return False
    if telugu / total > 0.8: return False
    return True

def load_data(files):
    hate_labels_set = {'hate', 'offensive', 'hof', '1', 'yes', 'toxic'}
    frames = []
    TEXT_NAMES  = {'text', 'comment', 'comments', 'sentence', 'tweet', 'content', 'data'}
    LABEL_NAMES = {'label', 'labels', 'category', 'class', 'tag', 'hate', 'annotation'}

    for excel_file in files:
        if excel_file.suffix == '.csv':
            df = pd.read_csv(excel_file)
            sheets_data = [('csv', df)]
        else:
            xl = pd.ExcelFile(excel_file)
            sheets_data = [(sheet, xl.parse(sheet)) for sheet in xl.sheet_names]
        
        for sheet, df in sheets_data:
            text_col = next((c for c in df.columns if str(c).lower() in TEXT_NAMES or any(t in str(c).lower() for t in ['text', 'comment', 'sentence'])), None)
            label_col = next((c for c in df.columns if str(c).lower() in LABEL_NAMES or any(t in str(c).lower() for t in ['label', 'categor', 'class'])), None)

            if text_col and label_col:
                sub = df[[text_col, label_col]].copy()
                sub.columns = ['text', 'label']
                sub = sub.dropna()
                sub['text'] = sub['text'].astype(str).str.lower().str.strip() # Enforce lowercase for consistency
                sub['label_int'] = sub['label'].astype(str).str.strip().str.lower().apply(lambda x: 1 if x in hate_labels_set else 0)
                sub = sub[sub['text'].apply(is_code_mixed)].reset_index(drop=True)
                frames.append(sub)
            
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=['text', 'label', 'label_int'])

def load_badwords_as_training_data():
    toxic_words = []
    p1 = DATA_DIR / "telugu_badwords.txt"
    if p1.exists():
        with open(p1, "r", encoding="utf-8") as f:
            toxic_words.extend([l.strip().lower() for l in f if l.strip()])
            
    p2 = DATA_DIR / "secure_words.bin"
    if p2.exists():
        with open(p2, "rb") as f:
            decoded = base64.b64decode(f.read()).decode("utf-8")
            toxic_words.extend([l.strip().lower() for l in decoded.splitlines() if l.strip()])
            
    p3 = DATA_DIR / "bad_emojis.txt"
    if p3.exists():
        with open(p3, "r", encoding="utf-8") as f:
            toxic_words.extend([l.strip() for l in f if l.strip() and not l.strip().startswith("#")])
    
    if not toxic_words: return pd.DataFrame()
    
    toxic_templates = ["{word}", "nuvvu pedda {word}", "rey {word} nayala", "ni mokam chudu {word} la undi", "tuppas {word}"]
    safe_phrases = ["good morning", "chala bagundi anna", "keep it up brother", "super editing", "edo oka roju sadhistavu", "very helpful video", "amazing efforts", "congratulations macha", "proud of you"]
    
    rows = []
    for word in list(set(toxic_words)):
        for t in random.sample(toxic_templates, min(3, len(toxic_templates))): # Increased augments
            rows.append({'text': t.format(word=word), 'label_int': 1})
            rows.append({'text': random.choice(safe_phrases), 'label_int': 0})
    
    return pd.DataFrame(rows)

# ── Main Execution ───────────────────────────────────────────────────────────

if not DATA_DIR.exists():
    print(f"✗ ERROR: DATA_DIR {DATA_DIR} does not exist. Did you add the data to the Kaggle notebook?")
    sys.exit(1)

train_files = [f for f in DATA_DIR.iterdir() if 'training_data' in f.name.lower() and f.suffix in ['.xlsx', '.xls', '.csv']]
all_data = load_data(train_files)
badwords_data = load_badwords_as_training_data()
if not badwords_data.empty:
    all_data = pd.concat([all_data, badwords_data], ignore_index=True)

all_data = all_data.drop_duplicates(subset='text')

# ── Advanced Data Handling ───────────────────────────────────────────────────
# Extra aggressive Shuffle
all_data = all_data.sample(frac=1, random_state=100).reset_index(drop=True)

# Train/Test Split (stratified)
train_df, test_df = train_test_split(all_data, test_size=0.10, random_state=100, stratify=all_data['label_int'])

# Calculate Class Weights to force model to pay attention to minority classes
class_weights = compute_class_weight('balanced', classes=np.unique(train_df['label_int']), y=train_df['label_int'])
class_weights_tensor = torch.tensor(class_weights, dtype=torch.float)

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL, 
    num_labels=2, 
    ignore_mismatched_sizes=True,
    problem_type="single_label_classification"
)

class CommentDataset(TorchDataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=MAX_LENGTH, return_tensors='pt')
        self.labels = labels
    def __len__(self): return len(self.labels)
    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

train_dataset = CommentDataset(train_df['text'].tolist(), train_df['label_int'].tolist())
test_dataset  = CommentDataset(test_df['text'].tolist(), test_df['label_int'].tolist())

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        'accuracy': accuracy_score(labels, preds),
        'f1': f1_score(labels, preds, zero_division=0),
    }

# ── Custom Trainer for Class Weights ─────────────────────────────────────────
device = 'cuda' if torch.cuda.is_available() else 'cpu'
class_weights_tensor = class_weights_tensor.to(device)

class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = nn.CrossEntropyLoss(weight=class_weights_tensor)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
batch_size = 16 if device == 'cuda' else 8
total_steps = (len(train_dataset) // batch_size) * EPOCHS
warmup_steps = int(total_steps * 0.15)  

training_args = TrainingArguments(
    output_dir=str(OUTPUT_DIR),
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=64, 
    learning_rate=LEARNING_RATE,
    weight_decay=0.015, # Increased weight decay
    warmup_steps=warmup_steps, 
    eval_strategy="epoch",
    save_strategy="no", # <--- PREVENTS KAGGLE STORAGE OVERFLOW BY NEVER SAVING CHECKPOINTS
    save_total_limit=0, 
    load_best_model_at_end=False, # Must be false if we don't save checkpoints
    metric_for_best_model="accuracy", # Optimizing strictly for accuracy
    report_to="none",
    fp16=(device == 'cuda'),
)

trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
)

print(f"Starting training on {device} using {BASE_MODEL}...")
print(f"Dataset Size: {len(all_data)} (Train: {len(train_df)}, Test: {len(test_df)})")
print(f"Class Weights applied: {class_weights}")
trainer.train()

# --- EVALUATION ---
print("\n📊 Evaluating on test set...")
results = trainer.evaluate()
print(f"\n{'='*50}")
print("🏆 FINAL RESULTS:")
print(f"  Accuracy:  {results.get('eval_accuracy', 0)*100:.2f}%")
print(f"  F1 Score:  {results.get('eval_f1', 0):.4f}")
print(f"{'='*50}")

trainer.save_model(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))
print(f"✅ Done! Model saved to: {OUTPUT_DIR}")
