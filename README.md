# Student Assistant Chatbot

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)
![Made by Mo Bialy](https://img.shields.io/badge/Made_by-Mo_Bialy-lightgrey)

A **dual-mode chatbot** with:
1. **Project 1:** Student Management (FAQ mode) — Manage students via predefined commands
2. **Project 2:** RAG Q&A System — Answer questions about PDF documents using AI

---

## 🎯 Projects Overview

### Project 1: Student Management Chatbot
Simple command-based system for managing students.

**Features:**
- View all students
- Search by ID/Name
- Add/Update/Delete students (Admin-only)
- Role-based access (Admin vs User)
- User authentication

**Tech:** Python, Streamlit, MySQL

### Project 2: RAG Q&A Chatbot
Conversational AI that learns from your documents.

**Features:**
- Upload & process PDFs
- Ask questions about documents
- Get answers with source citations
- Seamless fallback to general knowledge
- Multi-factor relevance filtering
- Per-user isolated collections

**Tech:** Python, Streamlit, LangChain, Chroma, OpenAI GPT-5

---

## 🚀 Quick Start

### Setup Both Projects

```bash
# Create main directory
mkdir Student-Assistant-Chatbot
cd Student-Assistant-Chatbot

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Project 1: Run Student Management

```bash
cd "Project 1"
# Setup MySQL database first (see below)
streamlit run app.py
```

### Project 2: Run RAG Chatbot

```bash
cd "Project 2"
# Create .env with OPENAI_API_KEY
streamlit run app.py
```

---

## 🛠️ Setup Details

### Project 1: MySQL Setup

Start XAMPP and create database:

```sql
CREATE DATABASE student_db;
USE student_db;

CREATE TABLE students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  age INT,
  grade VARCHAR(50)
);
```

### Project 2: Environment Setup

Create `.env` in `Project 2/`:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## 📁 Directory Structure

```
Student-Assistant-Chatbot/
├── Project 1/              # Student Management (FAQ)
│   ├── app.py
│   ├── chatbot.py
│   ├── database.py
│   └── requirements.txt
│
├── Project 2/              # RAG Q&A System
│   ├── app.py
│   ├── config.py
│   ├── chatbot.py
│   ├── .env
│   ├── requirements.txt
│   ├── engines/
│   │   ├── simple_faq.py
│   │   └── rag_engine.py
│   └── rag/
│       ├── ingest.py
│       └── pipeline.py
│
└── README.md
```

---

## 💬 Features Comparison

| Feature | Project 1 | Project 2 |
|---------|-----------|----------|
| Student Management | ✅ | ❌ |
| PDF Upload | ❌ | ✅ |
| Document Q&A | ❌ | ✅ |
| User Authentication | ✅ | ✅ |
| Admin Controls | ✅ | ✅ |
| Chat History | ✅ | ✅ |
| AI-Powered | ❌ FAQ only | ✅ GPT-5 |

---

## ✨ Key Highlights

**Project 1:**
- Simple predefined Q&A for student management
- MySQL database integration
- Admin-only operations

**Project 2:**
- Production-grade RAG system
- Multi-factor relevance validation
- Confident, non-cautious AI responses
- Seamless PDF + general knowledge blend
- Source citations with page numbers
- Per-user document isolation

---

## 🔐 Authentication

Both projects include:
- User registration with validation
- Password hashing (SHA256)
- Admin and student roles
- Session management with cleanup

---

## 📚 Dependencies

**Project 1:**
```
streamlit>=1.28.0
mysql-connector-python>=8.0.0
```

**Project 2:**
```
check requirements file in project 2 folder
```

---

## 🐛 Troubleshooting

**Project 1:**
- MySQL not connecting? Ensure XAMPP MySQL is running
- Database not found? Create `student_db` manually

**Project 2:**
- API key error? Check `.env` file
- PDFs not retrieving? Increase `retrieval_k` in config
- Too strict? Lower `similarity_threshold` to 0.55

---

## 🎓 Key Takeaways

- Building Streamlit web applications
- Integrating databases (MySQL) and vector stores (Chroma)
- RAG systems with LangChain
- LLM prompt engineering
- User authentication and role-based access
- PDF processing and text embeddings
- Session management and data isolation

---

## 📌 Roadmap

- ✅ **Project 1:** Basic student management (Complete)
- ✅ **Project 2:** Production RAG system (Complete)
- 🔄 Future: TBA

---

Made with ❤️ by **Mo Bialy**
