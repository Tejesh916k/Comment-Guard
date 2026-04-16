# Tokenizer

## What Is a Tokenizer?

A tokenizer converts human-readable text into **numerical tokens** that a machine learning model can process. It is the bridge between raw text and the model.

```
"nuvvu waste fellow" → [1234, 5678, 9012] → Model → Prediction
```

## Tokenizer Used

Comment Guard uses the **MuRIL tokenizer** (`google/muril-base-cased`), which comes bundled with the MuRIL BERT model.

| Property | Value |
|---|---|
| **Type** | WordPiece (same as standard BERT) |
| **Source** | `google/muril-base-cased` |
| **Vocabulary Size** | 197,285 tokens |
| **Case Sensitive** | Yes (cased model) |
| **Special Tokens** | `[CLS]`, `[SEP]`, `[PAD]`, `[UNK]`, `[MASK]` |

## How WordPiece Tokenization Works

WordPiece splits text into **subword units**. If a word exists in the vocabulary, it stays as one token. If not, it is split into smaller known pieces.

### Example with English Text
```
Input:    "unhappiness"
Tokens:   ["un", "##happiness"]
```

### Example with Telugu-English Code-Mixed Text
```
Input:    "nuvvu waste fellow"
Tokens:   ["nu", "##vvu", "waste", "fellow"]
```

The `##` prefix means _"this token continues the previous word"_. This allows the model to handle words it has never seen before by breaking them into known subwords.

## Tokenization Parameters

| Parameter | Value | Purpose |
|---|---|---|
| **max_length** | 128 | Maximum number of tokens per input |
| **truncation** | True | Cuts text longer than 128 tokens |
| **padding** | True | Pads shorter texts to the same length |
| **return_tensors** | `"pt"` | Returns PyTorch tensors |

### Why max_length = 128?

- Social media comments are typically **short** (10–50 words)
- MuRIL supports up to 512 tokens, but 128 is sufficient for comments
- Shorter sequences = **faster training** and **faster inference**
- Longer sequences would waste memory with padding for no benefit

## Tokenization Output

For each input text, the tokenizer produces three tensors:

| Tensor | Description |
|---|---|
| **input_ids** | Numerical IDs of each token from the vocabulary |
| **attention_mask** | Binary mask — `1` for real tokens, `0` for padding |
| **token_type_ids** | Segment IDs (always `0` for single-sentence classification) |

### Visual Example

```
Text: "waste fellow"

input_ids:      [101, 5765, 12345, 102, 0, 0, 0, ...]
attention_mask: [  1,    1,     1,   1, 0, 0, 0, ...]
token_type_ids: [  0,    0,     0,   0, 0, 0, 0, ...]
                 ↑CLS            ↑SEP  ↑ Padding
```

- `101` = `[CLS]` token (marks the start of input)
- `102` = `[SEP]` token (marks the end of input)
- `0` values in `attention_mask` = padding (ignored by the model)

## Why the MuRIL Tokenizer Matters

The MuRIL tokenizer has a **much larger vocabulary** (197K tokens) compared to standard BERT (30K tokens). This large vocabulary includes:

- English words and subwords
- Telugu script characters and words
- Transliterated Indian language tokens
- Devanagari, Kannada, Tamil, and other Indian script tokens

This means Telugu-English code-mixed text gets **better tokenization** — fewer `[UNK]` (unknown) tokens and more meaningful subword splits compared to a standard English tokenizer.
