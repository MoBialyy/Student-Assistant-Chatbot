# Project 2: RAG Q&A Chatbot

A Streamlit-based conversational RAG system that answers questions about uploaded PDFs with document grounding and general knowledge fallback.

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **RAG Framework:** LangChain
- **Vector Store:** Chroma (persistent local)
- **Embeddings:** OpenAI text-embedding-3-small
- **LLM:** OpenAI GPT-5
- **PDF Processing:** PyPDF (text extraction)

## 🚀 Quick Start

### 1. Setup
```bash
mkdir "Project 2"
cd "Project 2"
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Environment
Create `.env`:
```env
OPENAI_API_KEY=your_api_key_here
```


### 3. Run
```bash
streamlit run app.py
```

## 📁 Project Structure

```
Project 2/
├── app.py                    # Main Streamlit app
├── config.py                 # Configuration settings
├── chatbot.py               # Chatbot orchestrator
├── .env                     # API keys
├── .chroma_v7/              # Vector database
├── engines/
│   ├── simple_faq.py
│   └── rag_engine.py
└── rag/
    ├── ingest.py           # PDF processing
    └── pipeline.py         # RAG pipeline
```

## ⚙️ Key Configuration

```python
# config.py
chunk_size: int = 1000
chunk_overlap: int = 200
retrieval_k: int = 8
similarity_threshold: float = 0.60
min_context_length: int = 200
```

**Tuning:**
- Increase `retrieval_k` (5→10) for comprehensive answers
- Lower `similarity_threshold` (0.60→0.55) if too strict
- Raise `similarity_threshold` (0.60→0.70) if irrelevant results

## 💬 Features

✅ **PDF Upload & Processing** - Automatic text extraction, chunking, embedding
✅ **Multi-Factor Relevance Filtering** - Similarity scores + context length validation
✅ **Smart Session Management** - Per-user isolated collections, no re-processing
✅ **Confident Responses** - Uses PDFs when relevant, general knowledge otherwise
✅ **Source Citations** - Shows document + page number
✅ **Chat History** - Preserved across uploads, downloadable
✅ **Dual Engines** - Switch between Simple FAQ and RAG modes
✅ **User Authentication** - SHA256 hashed passwords, admin/user roles

## 📊 How It Works

```
Question → Retrieve Similar Chunks → Relevance Check
  ↓
  ├─ Relevant? → RAG Chain (GPT-5 + context) → Answer + Sources
  └─ Not relevant? → General Chat (GPT-5 only) → Answer
```

## 🔐 Authentication

- **Admin:** Auto-created in `credentials.json`
- **Users:** Self-register with validation (8+ char pwd, mixed case + digit + special)
- **Hashing:** SHA256

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| API key not found | Check `.env`, restart app, you can add it in your system path |
| PDFs not retrieving | Increase `retrieval_k` to 10 |
| Too many irrelevant results | Raise `similarity_threshold` to 0.70 |
| Too strict filtering | Lower `similarity_threshold` to 0.55 |

## ✨ Highlights

- **Intelligent Fallback** - Never stuck on PDFs; uses general knowledge seamlessly
- **Non-Cautious Assistant** - Confident answers, no excessive disclaimers
- **Persistent Storage** - Collections saved locally, survives restarts
- **Smart PDF Management** - Tracks processed files, adds new ones without re-processing
- **Production-Ready** - Multi-factor validation, error handling, session cleanup