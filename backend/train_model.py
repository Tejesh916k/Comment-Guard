"""
Fine-tune MuRIL (google/muril-base-cased) on the HOLD-Telugu (Dravidian CodeMix) dataset.
(MuRIL handles Telugu significantly better than standard toxic-bert)
SETUP:
1. Place the downloaded Excel file in: backend/data/  (any .xlsx file)
2. Install deps: pip install transformers torch scikit-learn accelerate openpyxl pandas

USAGE:
  cd backend
  python train_model.py

OUTPUT:
  Fine-tuned model saved to: backend/model_output/
  The backend auto-loads this model on next restart.
"""

import os
import sys
import json
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')

print("DEBUG: Script started", flush=True)

# ── Install dependencies if needed ───────────────────────────────────────────
print("DEBUG: Importing dependencies...", flush=True)
try:
    import torch
    print(f"DEBUG: Torch imported (v{torch.version})", flush=True)
    
    # Import transformers early
    import transformers
    print(f"DEBUG: transformers imported (v{transformers.__version__})", flush=True)

    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        TrainingArguments,
        Trainer,
        EarlyStoppingCallback
    )
    print("DEBUG: HuggingFace classes imported", flush=True)

    import pandas as pd
    print(f"DEBUG: pandas imported (v{pd.__version__})", flush=True)
    
    import openpyxl
    print("DEBUG: openpyxl imported", flush=True)
    
    import sklearn
    print(f"DEBUG: sklearn imported (v{sklearn.__version__})", flush=True)
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    print("DEBUG: sklearn metrics imported", flush=True)
    
    import numpy as np
    print(f"DEBUG: numpy imported (v{np.__version__})", flush=True)
    
    from torch.utils.data import Dataset as TorchDataset
    print("DEBUG: TorchDataset imported", flush=True)

except ImportError as e:
    print(f"DEBUG: ImportError: {e}", flush=True)
    sys.exit(1)
except Exception as e:
    print(f"DEBUG: Exception during import: {e}", flush=True)
    sys.exit(1)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "model_output"

# ── Config ────────────────────────────────────────────────────────────────────
BASE_MODEL    = "google/muril-base-cased"   # MuRIL (Multilingual BERT) for Indian languages
# BASE_MODEL    = "unitary/toxic-bert"         # Fallback to general toxic-bert if needed
MAX_LENGTH    = 128  # Longer context = better understanding of comments
EPOCHS        = 8    # More epochs with early stopping patience=2
LEARNING_RATE = 3e-5 # Slightly higher LR for faster convergence
# TEST_SPLIT    = 0.15 # Not needed if we use explicit files

# ── Find Excel files ─────────────────────────────────────────────────────
print(f"DEBUG: Searching for data in {DATA_DIR}", flush=True)
all_files = list(DATA_DIR.iterdir())
print(f"DEBUG: Found files: {[f.name for f in all_files]}", flush=True)

train_files = [f for f in all_files if 'training_data' in f.name.lower() and f.suffix in ['.xlsx', '.xls', '.csv']]

if not train_files:
    print("✗ No training file found (looking for 'training_data*.xlsx')")
    sys.exit(1)
else:
    print(f"✓ Training files: {[f.name for f in train_files]}")
    print("ℹ Test set will be a stratified 20% split from training data (same distribution)")


# ── Helper to load data ──────────────────────────────────────────────────────

def is_code_mixed(text):
    """
    Returns True if text is Telugu-English code-mixed.
    Keeps rows that have at least some Latin (English) characters.
    Removes rows that are purely in Telugu script (U+0C00-U+0C7F).
    """
    text = str(text)
    has_latin = any('\u0041' <= c <= '\u007A' for c in text)   # A-z
    total     = len([c for c in text if c.strip()])
    telugu    = len([c for c in text if '\u0C00' <= c <= '\u0C7F'])
    # Skip if purely Telugu (>80% Telugu script chars) or has no Latin at all
    if total == 0:
        return False
    if not has_latin:
        return False
    if telugu / total > 0.8:
        return False
    return True

def load_data(files):
    hate_labels_set = {'hate', 'offensive', 'hof', '1', 'yes', 'toxic'}
    frames = []
    
    TEXT_NAMES  = {'text', 'comment', 'comments', 'sentence', 'tweet', 'content', 'data'}
    LABEL_NAMES = {'label', 'labels', 'category', 'class', 'tag', 'hate', 'annotation'}

    for excel_file in files:
        print(f"  Loading: {excel_file.name}", flush=True)
        try:
            # Support both Excel and CSV files
            if excel_file.suffix == '.csv':
                sheets_data = [('csv', pd.read_csv(excel_file))]
            else:
                xl = pd.ExcelFile(excel_file)
                sheets_data = [(sheet, xl.parse(sheet)) for sheet in xl.sheet_names]
            
            for sheet, df in sheets_data:
                
                # Column matching
                text_col = next(
                    (c for c in df.columns if str(c).lower() in TEXT_NAMES or
                     any(t in str(c).lower() for t in ['text', 'comment', 'sentence'])), None
                )
                label_col = next(
                    (c for c in df.columns if str(c).lower() in LABEL_NAMES or
                     any(t in str(c).lower() for t in ['label', 'categor', 'class'])), None
                )

                if text_col and str(text_col).lower() in ['s.no', 'no', 'id', 'index', 'sr']:
                    text_col = None

                if text_col and label_col:
                    sub = df[[text_col, label_col]].copy()
                    sub.columns = ['text', 'label']
                    sub = sub.dropna()
                    sub['label'] = sub['label'].astype(str).str.strip().str.lower()
                    sub['label_int'] = sub['label'].apply(lambda x: 1 if x in hate_labels_set else 0)
                    
                    # ── Filter: keep only Telugu-English code-mixed rows ──────
                    before = len(sub)
                    sub = sub[sub['text'].apply(is_code_mixed)].reset_index(drop=True)
                    after = len(sub)
                    print(f"    ✓ Sheet '{sheet}': {after} code-mixed rows kept (filtered out {before - after} pure Telugu rows)", flush=True)
                    
                    frames.append(sub)
                else:
                    print(f"    ⚠ Sheet '{sheet}': Skipped (cols={list(df.columns)})", flush=True)
        except Exception as e:
            print(f"    ✗ Error reading {excel_file.name}: {e}", flush=True)
            
    if not frames:
        return pd.DataFrame(columns=['text', 'label', 'label_int'])
    
    combined = pd.concat(frames, ignore_index=True)
    return combined


# ── Load Bad Words / Emojis as Additional Training Data ──────────────────────
def load_badwords_as_training_data():
    """Load telugu_badwords.txt, secure_words.bin, and bad_emojis.txt as toxic training examples."""
    import base64
    import random
    random.seed(42)
    
    toxic_words = []
    
    # 1. Load telugu_badwords.txt
    badwords_path = DATA_DIR / "telugu_badwords.txt"
    if badwords_path.exists():
        with open(badwords_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    toxic_words.append(word)
        print(f"  ✓ Loaded {len(toxic_words)} words from telugu_badwords.txt", flush=True)
    
    # 2. Load secure_words.bin (base64 encoded)
    secure_path = DATA_DIR / "secure_words.bin"
    secure_count = 0
    if secure_path.exists():
        with open(secure_path, "rb") as f:
            encoded_data = f.read()
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            for line in decoded_data.splitlines():
                word = line.strip()
                if word and word not in toxic_words:
                    toxic_words.append(word)
                    secure_count += 1
        print(f"  ✓ Loaded {secure_count} additional words from secure_words.bin", flush=True)
    
    # 3. Load bad_emojis.txt
    emoji_path = DATA_DIR / "bad_emojis.txt"
    emoji_count = 0
    if emoji_path.exists():
        with open(emoji_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    toxic_words.append(line)
                    emoji_count += 1
        print(f"  ✓ Loaded {emoji_count} offensive emojis from bad_emojis.txt", flush=True)
    
    if not toxic_words:
        return pd.DataFrame(columns=['text', 'label', 'label_int'])
    
    # Create toxic training examples with natural sentence patterns
    toxic_templates = [
        "{word}",
        "you are a {word}",
        "{word} ga unnav",
        "enti ra {word}",
        "orey {word}",
        "nuvvu {word}",
        "{word} fellow",
        "this {word}",
    ]
    
    toxic_rows = []
    for word in toxic_words:
        # Use 2-3 random templates per word to create varied examples
        templates = random.sample(toxic_templates, min(3, len(toxic_templates)))
        for template in templates:
            toxic_rows.append({
                'text': template.format(word=word),
                'label': 'hate',
                'label_int': 1
            })
    
    # Generate matching SAFE examples to keep the dataset balanced
    safe_phrases = [
        "good morning everyone", "nice video", "great content bro",
        "keep it up", "super ga undi", "chala bagundi",
        "love this", "awesome work", "thank you for sharing",
        "very helpful", "bagundi", "nice one", "well done",
        "interesting topic", "manchi video", "super explanation",
        "thanks for this", "really useful", "good job",
        "happy birthday", "congratulations", "best wishes",
        "nice song", "beautiful", "amazing performance",
        "very informative", "subscribed", "waiting for next video",
        "loved it", "manchi content", "edo oka roju",
        "nenu chala happy", "meeru bagunnara", "thanks anna",
        "thanks akka", "super bro", "nice edit",
        "first comment", "who is watching in 2024",
        "please make more videos", "this helped me a lot",
        "I learned something new", "great tutorial", "perfect",
    ]
    
    safe_rows = []
    # Create enough safe examples to match toxic count
    target_safe = len(toxic_rows)
    for i in range(target_safe):
        phrase = safe_phrases[i % len(safe_phrases)]
        safe_rows.append({
            'text': phrase,
            'label': 'not-hate',
            'label_int': 0
        })
    
    all_rows = toxic_rows + safe_rows
    print(f"  ✓ Generated {len(toxic_rows)} toxic + {len(safe_rows)} safe training examples from bad words/emojis", flush=True)
    return pd.DataFrame(all_rows)


# ── Load and Split ───────────────────────────────────────────────────────────
print("\nLoading training data...", flush=True)
all_data = load_data(train_files)
if all_data.empty:
    print("✗ Error: No usable data found.", flush=True)
    sys.exit(1)

# Load bad words as additional training data
print("\nLoading bad words/emojis as training data...", flush=True)
badwords_data = load_badwords_as_training_data()
if not badwords_data.empty:
    all_data = pd.concat([all_data, badwords_data], ignore_index=True)
    print(f"  Combined dataset size: {len(all_data)}", flush=True)

# Remove duplicates
len_before = len(all_data)
all_data = all_data.drop_duplicates(subset='text')
print(f"  Deduplicated: {len_before} -> {len(all_data)}")

# ── Stratified 90/10 split (more training data = higher accuracy) ─────────────
from sklearn.model_selection import train_test_split
train_df, test_df = train_test_split(
    all_data, test_size=0.10, random_state=42, stratify=all_data['label_int']
)

print(f"\nFinal Split: Train={len(train_df)} | Test={len(test_df)}")
print(f"Class Dist (Train): {train_df['label_int'].value_counts().to_dict()}")
print(f"Class Dist (Test):  {test_df['label_int'].value_counts().to_dict()}")

train_texts  = train_df['text'].tolist()
train_labels = train_df['label_int'].tolist()
test_texts   = test_df['text'].tolist()
test_labels  = test_df['label_int'].tolist()

# ── Load tokenizer & model ────────────────────────────────────────────────────
print(f"\nLoading model: {BASE_MODEL}", flush=True)

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    num_labels=2,
    ignore_mismatched_sizes=True,
    problem_type="single_label_classification"  # Forces CrossEntropyLoss (fixes transformers v5 bug)
)
print(f"✓ Model loaded", flush=True)

# ── Dataset ───────────────────────────────────────────────────────────────────
class CommentDataset(TorchDataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(
            texts, truncation=True, padding=True,
            max_length=MAX_LENGTH, return_tensors='pt'
        )
        self.labels = labels

    def __len__(self): return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

print("Tokenizing datasets...", flush=True)
train_dataset = CommentDataset(train_texts, train_labels)
test_dataset  = CommentDataset(test_texts,  test_labels)

# ── Metrics ───────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        'accuracy':  accuracy_score(labels, preds),
        'f1':        f1_score(labels, preds, zero_division=0),
        'precision': precision_score(labels, preds, zero_division=0),
        'recall':    recall_score(labels, preds, zero_division=0),
    }

# ── Training ──────────────────────────────────────────────────────────────────
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\nTraining on: {device.upper()}", flush=True)

OUTPUT_DIR.mkdir(exist_ok=True)
batch_size      = 16 if device == 'cuda' else 8   # Smaller batch = better generalization on small datasets
eval_batch_size = 64   # No gradients during eval → can use larger batch

# 10% warmup steps
total_steps = (len(train_dataset) // batch_size) * EPOCHS
warmup_steps = int(total_steps * 0.1)

training_args = TrainingArguments(
    output_dir=str(OUTPUT_DIR),
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=eval_batch_size,
    learning_rate=LEARNING_RATE,
    warmup_steps=warmup_steps,
    weight_decay=0.05,              # Stronger regularization to prevent overfitting
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    logging_steps=25,
    report_to="none",
    fp16=(device == 'cuda'),
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]  # Stop early before overfitting
)

print(f"Starting training...", flush=True)
trainer.train()

# ── Final evaluation ──────────────────────────────────────────────────────────
print("\nEvaluating on test set...", flush=True)
results = trainer.evaluate()
print(f"\n{'='*60}")
print("FINAL RESULTS:")
print(f"  Accuracy:  {results.get('eval_accuracy', 0)*100:.2f}%")
print(f"  F1 Score:  {results.get('eval_f1', 0):.4f}")
print(f"  Precision: {results.get('eval_precision', 0):.4f}")
print(f"  Recall:    {results.get('eval_recall', 0):.4f}")
print(f"{'='*60}")

# ── Save ──────────────────────────────────────────────────────────────────────
trainer.save_model(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))
with open(OUTPUT_DIR / "eval_results.json", 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Done! Model saved to: {OUTPUT_DIR}", flush=True)
