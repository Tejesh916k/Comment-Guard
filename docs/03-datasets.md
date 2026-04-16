# Datasets

## Overview

Comment Guard uses multiple data sources for training, augmentation, and rule-based detection. The primary focus is **Telugu-English code-mixed** (Tenglish) social media comments.

## 1. HOLD-Telugu Dataset (Primary Training Data)

| Property | Details |
|---|---|
| **Source** | Dravidian Language Technology (DravidianLangTech) shared tasks |
| **File** | `data/training_data_telugu-hate.xlsx` |
| **Format** | Excel (.xlsx) with columns: `Comments`, `Label` |
| **Total Samples** | ~4,000 (after deduplication) |
| **Labels** | `hate` and `non-hate` |
| **Content** | Telugu-English code-mixed social media comments |

This dataset contains real-world comments from platforms like YouTube and Twitter, labeled by human annotators for hate speech detection in Dravidian languages.

## 2. Telugu Bad Words List

| Property | Details |
|---|---|
| **File** | `data/telugu_badwords.txt` |
| **Format** | Plain text, one word per line |
| **Purpose** | Rule-based profanity detection + training augmentation |

Contains Telugu-script and transliterated Telugu offensive words. These are loaded into the `better_profanity` library at runtime and also used to generate synthetic training examples.

## 3. Secure Word Vault

| Property | Details |
|---|---|
| **File** | `data/secure_words.bin` |
| **Format** | Base64-encoded text |
| **Purpose** | Stores highly sensitive offensive terms separately |
| **Management** | CLI tool: `admin_manager.py` (add, remove, view, migrate) |

This file stores the most explicit offensive words in an encoded format to keep them out of plain-text source control. These words are decoded at runtime and added to the profanity filter.

## 4. Offensive Emoji List

| Property | Details |
|---|---|
| **File** | `data/bad_emojis.txt` |
| **Format** | UTF-8 text, one emoji per line |
| **Purpose** | Catches visual toxicity (e.g., 🖕, vulgar emoji combinations) |

## 5. Data Augmentation (Synthetic Training Data)

To increase dataset size and diversity, the training pipeline generates **synthetic examples** from the word lists above:

- **Toxic examples**: Each bad word is placed into multiple sentence templates  
  - Templates: `"{word}"`, `"you are a {word}"`, `"{word} ga unnav"`, `"enti ra {word}"`, etc.
  - **14 templates** in V3, generating **4 examples per word**

- **Safe examples**: A curated list of positive Telugu-English phrases  
  - Examples: `"bagundi bro"`, `"keep it up"`, `"super explanation"`, etc.
  - **Matched 1:1** against toxic examples to maintain class balance

## Dataset Split

| Split | Percentage | Purpose |
|---|---|---|
| **Training** | 90% | Model learning (with class balancing via oversampling) |
| **Testing** | 10% | Final evaluation (stratified, same class distribution) |

The split is **stratified** — both training and testing sets maintain the same ratio of toxic to non-toxic samples. This prevents the model from being evaluated on a skewed distribution.

## Class Balancing

The V3 training pipeline uses **dynamic oversampling**:
1. Count samples in each class (toxic vs. non-toxic)
2. Identify the minority class
3. Randomly oversample (with replacement) the minority class to match the majority
4. Shuffle the final balanced dataset

This ensures the model does not develop a bias toward predicting the majority class.
