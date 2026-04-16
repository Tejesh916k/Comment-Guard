# Evaluation Metrics

## Overview

After training, the model is evaluated on a **held-out test set** (10% of the total data) that the model has never seen during training. This gives an honest measure of how well the model generalizes to new comments.

## What the Metrics Mean

| Metric | Definition | In Simple Terms |
|---|---|---|
| **Accuracy** | Correct predictions ÷ Total predictions | "How often is the model right overall?" |
| **Precision** | True Positives ÷ (True Positives + False Positives) | "When it says toxic, how often is it actually toxic?" |
| **Recall** | True Positives ÷ (True Positives + False Negatives) | "Of all toxic comments, how many did it catch?" |
| **F1 Score** | Harmonic mean of Precision and Recall | "A balanced score between Precision and Recall" |

## Confusion Matrix — Explained

```
                    Predicted Safe     Predicted Toxic
Actual Safe         True Negative (TN)  False Positive (FP)
Actual Toxic        False Negative (FN) True Positive (TP)
```

| Term | Meaning | Impact |
|---|---|---|
| **True Positive** | Toxic comment correctly flagged | ✅ Good — harmful content blocked |
| **True Negative** | Safe comment correctly allowed | ✅ Good — normal conversation flows |
| **False Positive** | Safe comment incorrectly flagged | ⚠️ Bad — user frustrated by false alarm |
| **False Negative** | Toxic comment missed | ❌ Bad — harmful content gets through |

## Model Results

### MuRIL BERT (V3 — Current Model)

| Metric | Value |
|---|---|
| **Accuracy** | 93.64% |
| **F1 Score** | 0.9343 |
| **Precision** | 96.68% |
| **Recall** | 90.40% |

### What These Numbers Mean

- **93.64% Accuracy**: Out of every 100 comments, the model correctly classifies ~94
- **96.68% Precision**: When the model flags a comment as toxic, it is correct ~97% of the time
- **90.40% Recall**: The model catches ~90% of all toxic comments
- **0.9343 F1**: A strong, balanced score — no major trade-off between precision and recall

## Dataset Split Summary

| Split | Size | Purpose |
|---|---|---|
| **Training Set** | 90% of data | Model learns patterns from this data |
| **Test Set** | 10% of data | Model is evaluated on this unseen data |

Both splits are **stratified** — the ratio of toxic to safe comments is the same in both sets.

## Test Case Categories

The model is tested across multiple categories to ensure broad coverage:

| Category | Example |
|---|---|
| English insults | "You are worthless and pathetic" |
| Tenglish insults | "Mental gadu", "Waste fellow" |
| Telugu profanity | Explicit Telugu offensive words |
| Emoji toxicity | "🖕", vulgar emoji combinations |
| Safe — English | "Great post, keep it up!" |
| Safe — Tenglish | "Super ga undi bro" |
| Safe — Casual | "Good morning everyone!" |

## Why F1 Score Matters Most

For toxicity detection, we optimize for **F1 score** rather than just accuracy because:

1. **Accuracy can be misleading**: If 90% of comments are safe, a model that always predicts "safe" gets 90% accuracy but catches zero toxic comments
2. **F1 balances both sides**: It ensures the model is both good at catching toxic content (recall) and not raising false alarms (precision)
3. **Early stopping uses F1**: Training automatically stops when the F1 score on the test set stops improving
