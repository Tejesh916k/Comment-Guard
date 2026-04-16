# Comment Guard — AI-Based Real-Time Comment Moderation

Comment Guard is a full-stack AI-powered comment moderation system that detects and filters toxic, offensive, and hateful comments in real-time, with specialized support for Telugu-English code-mixed text (Tenglish).

## 📖 Documentation

| # | Document | Description |
|---|---|---|
| 01 | [Project Overview](docs/01-project-overview.md) | What is Comment Guard, key features, tech stack, project structure |
| 02 | [System Architecture](docs/02-system-architecture.md) | Architecture diagram, detection pipeline flowchart, request flow |
| 03 | [Datasets](docs/03-datasets.md) | Training data, word lists, augmentation strategy, train/test split |
| 04 | [Preprocessing](docs/04-preprocessing.md) | Text cleaning steps, code-mix filtering, label normalization |
| 05 | [MuRIL BERT Model](docs/05-muril-bert-model.md) | What is MuRIL, why we use it, model specs, language support |
| 06 | [Tokenizer](docs/06-tokenizer.md) | WordPiece tokenization, parameters, visual examples |
| 07 | [Training Pipeline](docs/07-training-pipeline.md) | Training workflow, hyperparameters, overfitting prevention |
| 08 | [Evaluation Metrics](docs/08-evaluation-metrics.md) | Accuracy, precision, recall, F1, confusion matrix explained |
| 09 | [API Reference](docs/09-api-reference.md) | Backend endpoints, request/response formats, setup |
| 10 | [Extension Guide](docs/10-extension-guide.md) | Chrome extension installation, usage, troubleshooting |

## Quick Start

1. **Load the extension**:
   - Open `chrome://extensions/`
   - Enable **Developer Mode**
   - Click **Load Unpacked**
   - Select the `extension/` folder
2. **Test it**: Navigate to YouTube or Instagram and type a comment

> **Note:** The extension connects to the live backend on [Hugging Face Spaces](https://tejesh916k-comment-guard-api.hf.space) — no local server needed.

For detailed instructions, see the [Extension Guide](docs/10-extension-guide.md).

## Running Locally

```bash
# Start the backend
cd backend && python main.py

# Or use Docker
docker-compose up
```

## Project Structure

```
Comment-Guard/
├── backend/          # FastAPI backend + ML model
├── docs/             # Full project documentation (10 chapters)
├── extension/        # Chrome extension (manifest v3)
├── docker-compose.yml
└── README.md
```
