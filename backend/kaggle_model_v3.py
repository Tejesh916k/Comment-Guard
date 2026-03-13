"""
KAGGLE MODEL V3: Aiming for 90%+ Accuracy without Overfitting
Optimizations:
1. Increased Dataset Size: More diverse templates and safe phrases for data augmentation.
2. Data Text Cleaning: Removed URLs, extra spaces, and user mentions to reduce noise.
3. Class Balancing: Automatically oversamples the minority class to perfectly balance the dataset.
4. Overfitting Prevention: Added Label Smoothing, Cosine Learning Rate Scheduler, 
   Warmup steps, and appropriate Weight Decay.
5. Model: Using 'google/muril-base-cased' which is highly optimized for Indian languages 
   including Telugu, better for code-mixed text. Added custom dropout to config.
"""

import os
import sys
import json
import base64
import random
import re
from pathlib import Path

# Force unbuffered output
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

print("DEBUG: Kaggle V3 Training Script started", flush=True)

# ── Paths ────────────────────────────────────────────────────────────────────
KAGGLE_INPUT = Path("/kaggle/input")
KAGGLE_OUTPUT = Path("/kaggle/working")

DATA_DIR = None
print(f"DEBUG: Checking for data in {KAGGLE_INPUT}...", flush=True)

for p in KAGGLE_INPUT.glob("*"):
    if p.is_dir() and any(p.glob("*training_data*")):
        DATA_DIR = p
        break

if not DATA_DIR:
    for p in KAGGLE_INPUT.rglob("*training_data*"):
        DATA_DIR = p.parent
        break

if not DATA_DIR:
    DATA_DIR = KAGGLE_INPUT / "comment-guard-data"

OUTPUT_DIR = KAGGLE_OUTPUT / "model_output_v3"

# ── Dependencies ─────────────────────────────────────────────────────────────
try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        AutoConfig,
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
except ImportError:
    print("⚠ Please run: !pip install transformers torch scikit-learn accelerate openpyxl pandas -q")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
BASE_MODEL    = "google/muril-base-cased" # Great for Telugu/Code-mixed
MAX_LENGTH    = 128
EPOCHS        = 10      # High max epochs, relying on early stopping
LEARNING_RATE = 2e-5    
WEIGHT_DECAY  = 0.05    
LABEL_SMOOTHING = 0.1   # Helps prevent overfitting by softening labels
WARMUP_RATIO  = 0.1     # Gradual learning rate increase

# ── Functions ────────────────────────────────────────────────────────────────

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text) # Remove URLs
    text = re.sub(r'@\w+', '', text) # Remove mentions
    text = re.sub(r'#\w+', '', text) # Remove hashtags
    text = re.sub(r'\s+', ' ', text) # Remove extra whitespace
    return text.strip()

def is_code_mixed(text):
    text = str(text)
    has_latin = any('\u0041' <= c <= '\u007A' for c in text)
    total = len([c for c in text if c.strip()])
    # Simply require that it has some Latin characters (English alphabet)
    if total == 0 or not has_latin: return False
    return True

def load_data(files):
    hate_labels_set = {'hate', 'offensive', 'hof', '1', 'yes', 'toxic'}
    frames = []
    TEXT_NAMES  = {'text', 'comment', 'comments', 'sentence', 'tweet', 'content', 'data'}
    LABEL_NAMES = {'label', 'labels', 'category', 'class', 'tag', 'hate', 'annotation'}

    for excel_file in files:
        try:
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
                    sub['text'] = sub['text'].apply(clean_text)
                    sub['label_int'] = sub['label'].astype(str).str.strip().str.lower().apply(lambda x: 1 if x in hate_labels_set else 0)
                    sub = sub[sub['text'].apply(is_code_mixed)].reset_index(drop=True)
                    frames.append(sub)
        except Exception as e:
            print(f"Error loading {excel_file}: {e}")
            pass
            
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=['text', 'label', 'label_int'])

def load_badwords_augmented():
    """V3: Massively expanded safe phrases and toxic templates to increase dataset robustness."""
    toxic_words = []
    p1, p2, p3 = DATA_DIR / "telugu_badwords.txt", DATA_DIR / "secure_words.bin", DATA_DIR / "bad_emojis.txt"
    if p1.exists():
        with open(p1, "r", encoding="utf-8") as f: toxic_words.extend([l.strip() for l in f if l.strip()])
    if p2.exists():
        with open(p2, "rb") as f: toxic_words.extend([l.strip() for l in base64.b64decode(f.read()).decode("utf-8").splitlines() if l.strip()])
    if p3.exists():
        with open(p3, "r", encoding="utf-8") as f: toxic_words.extend([l.strip() for l in f if l.strip() and not l.strip().startswith("#")])
    
    if not toxic_words: return pd.DataFrame()
    
    random.seed(42)
    # Increased variety
    toxic_templates = [
        "{word}", "you are a {word}", "{word} ga unnav", "enti ra {word}", 
        "nuvvu {word}", "{word} fellow", "worst {word}", "rey {word}",
        "ni yamma {word} nayala", "nuvvu pedda {word}", "chi {word} badava",
        "endira ee {word} panulu", "tuppas {word} mokam", "nee lanti {word} inka evaru leru"
    ]
    
    safe_phrases = [
        "bagundi bro", "keep it up", "manchi video", "super explanation", "thanks for sharing", 
        "helpful information", "nice edit", "waiting for next video", "super ga undi", 
        "love from ap", "good job", "congratulations brother", "beautiful video", "awesome music",
        "next video eppudu?", "very interesting topic", "I learned a lot today", "nice talk",
        "informative content", "meeru chala baga chepparu", "meeru chala handsome", "super anna",
        "daily chustanu mee videos", "proud of you", "all the best for your future", "fantastic editing",
        "thank you so much", "very nice presentation", "please upload more", "hello everyone",
        "good morning brother", "have a great day ahead", "chala upayoga padindi", "excellent work"
    ]
    
    rows = []
    for word in list(set(toxic_words)):
        # Generate 4 toxic examples per word
        for t in random.sample(toxic_templates, min(4, len(toxic_templates))):
            rows.append({'text': t.format(word=word), 'label_int': 1})
        # Generate 4 safe examples to match
        for _ in range(4):
            rows.append({'text': random.choice(safe_phrases), 'label_int': 0})
    
    return pd.DataFrame(rows)

# ── Main Execution ───────────────────────────────────────────────────────────

if not DATA_DIR.exists():
    print(f"✗ ERROR: DATA_DIR {DATA_DIR} not found. Ensure dataset is added to notebook.")
    sys.exit(1)

train_files = [f for f in DATA_DIR.iterdir() if 'training_data' in f.name.lower() and f.suffix in ['.xlsx', '.xls', '.csv']]
all_data = load_data(train_files)
aug_data = load_badwords_augmented()
if not aug_data.empty:
    all_data = pd.concat([all_data, aug_data], ignore_index=True)

all_data = all_data.drop_duplicates(subset='text').reset_index(drop=True)

# V3: DYNAMIC OVERSAMPLING & BALANCING
counts = all_data['label_int'].value_counts()
if len(counts) == 2:
    majority_class = counts.idxmax()
    minority_class = counts.idxmin()
    majority_count = counts[majority_class]
    minority_count = counts[minority_class]
    
    if minority_count < majority_count:
        df_majority = all_data[all_data['label_int'] == majority_class]
        df_minority = all_data[all_data['label_int'] == minority_class]
        
        # Oversample minority
        df_minority_over = df_minority.sample(majority_count, replace=True, random_state=42)
        all_data = pd.concat([df_majority, df_minority_over], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"DEBUG: Oversampled class {minority_class} to {majority_count}. Total rows symmetrically balanced: {len(all_data)}")

# Train/Test Split
train_df, test_df = train_test_split(all_data, test_size=0.10, random_state=42, stratify=all_data['label_int'])

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

# Incorporating Dropout into config to prevent overfitting
config = AutoConfig.from_pretrained(BASE_MODEL, num_labels=2, problem_type="single_label_classification")
config.hidden_dropout_prob = 0.2
config.attention_probs_dropout_prob = 0.2

model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL, 
    config=config,
    ignore_mismatched_sizes=True
)

class CommentDataset(TorchDataset):
    def __init__(self, texts, labels):
        self.texts = texts # Store raw texts as well
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
        'precision': precision_score(labels, preds, zero_division=0),
        'recall': recall_score(labels, preds, zero_division=0),
    }

device = 'cuda' if torch.cuda.is_available() else 'cpu'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

training_args = TrainingArguments(
    output_dir=str(OUTPUT_DIR),
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=16 if device == 'cuda' else 8,
    per_device_eval_batch_size=32 if device == 'cuda' else 8,
    learning_rate=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY,
    warmup_ratio=WARMUP_RATIO,
    lr_scheduler_type='cosine', # Cosine learning rate scheduler helps avoid overfitting and local minima
    label_smoothing_factor=LABEL_SMOOTHING, # Distributes a bit of probability mass to other classes, reducing overconfidence
    eval_strategy="epoch",
    save_strategy="no",          # CHANGED: Don't save checkpoints to prevent KAGGLE STORAGE OVERFLOW
    load_best_model_at_end=False, # CHANGED: Must be false if we aren't saving checkpoints
    metric_for_best_model="f1",
    report_to="none",
    fp16=(device == 'cuda'),
    logging_steps=50,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)

print(f"Starting V3 training on {device}...")
trainer.train()

# Evaluate & Print Results
print("\n📊 EVALUATING MODEL V3...")
results = trainer.evaluate()
print(f"\n{'='*50}\n🏆 V3 FINAL ACCURACY: {results.get('eval_accuracy', 0)*100:.2f}%\n{'='*50}")

# --- CRITICAL KAGGLE STORAGE FIX ---
# Free up disk space before saving by clearing the HuggingFace cache and previous runs
print("\n🧹 Clearing disk space...")
import shutil
import gc

# 1. Clear large dataframes and run garbage collection
del all_data, train_df, test_df, train_dataset, test_dataset
gc.collect()

# 2. Clear known cache directories
for cache_path in [".cache/huggingface", ".cache/torch"]:
    cache_dir = Path.home() / cache_path
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Cleared {cache_dir}")
        except Exception as e:
            pass

# 3. Aggressively delete OLD model outputs in /kaggle/working to free up 100s of MBs
for old_dir in ["model_output", "model_output_v2", "wandb"]:
    old_path = KAGGLE_OUTPUT / old_dir
    if old_path.exists():
        try:
            shutil.rmtree(old_path)
            print(f"✅ Deleted old directory: {old_path}")
        except Exception as e:
            pass

# Save
try:
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    with open(OUTPUT_DIR / "eval_results.json", 'w') as f: json.dump(results, f, indent=2)
    print(f"✅ Model saved successfully to: {OUTPUT_DIR}")
except OSError as e:
    print(f"\n❌ FATAL SAVING ERROR: {e}")
    print("Kaggle ran out of disk space again! Try restarting your session or using a smaller BASE_MODEL.")
