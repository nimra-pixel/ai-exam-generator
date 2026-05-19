# 🎓 AI Exam Question Generator

An AI-powered exam paper generator for university educators.

## Features
- 📎 Upload PDF lecture notes or paste text directly
- 🧠 AI generates MCQs, Short, Long questions & Case Studies
- 🎯 3 difficulty levels: Easy / Medium / Hard
- ✅ Answer keys with model answers & explanations
- 📥 Download Student Copy + Answer Key separately
- 🏫 Course info header (university, semester, instructor)
- ⚙️ Configurable question counts per type

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
```bash
git init && git add . && git commit -m "AI Exam Generator"
git remote add origin https://github.com/nimra-pixel/ai-exam-generator.git
git push -u origin main
```
Streamlit secrets: `GROQ_API_KEY = "gsk_..."`
