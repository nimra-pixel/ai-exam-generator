# 🎓 AI Exam Question Generator

> An AI-powered exam paper generator for university educators — powered by **Groq (free) + Llama 3 + Streamlit**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-000000?style=flat&logo=groq&logoColor=white)](https://groq.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)

---

## ✨ Features

| Feature | Details |
|---|---|
| 📎 **PDF Upload** | Upload lecture notes, slides or textbook chapters |
| 📝 **Text Paste** | Directly paste any course content |
| 🧠 **AI Generation** | Groq + Llama 3.3 70B reads and understands material |
| 📝 **MCQs** | 4-option questions with answer + explanation |
| ✏️ **Short Questions** | With model answers and marks |
| 📖 **Long Questions** | Detailed model answers |
| 🔬 **Case Studies** | Scenario + sub-questions + full answers |
| 🎯 **Difficulty Levels** | Easy / Medium / Hard per question type |
| 🏫 **Course Info** | University, course code, instructor, semester |
| 📥 **Two Downloads** | Student Copy (no answers) + Answer Key |
| 🌑 **Dark Academic UI** | Clean, professional interface |

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone the repo
git clone https://github.com/nimra-pixel/ai-exam-generator.git
cd ai-exam-generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Then paste your **free Groq API key** in the sidebar → [console.groq.com](https://console.groq.com)

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Go to **[share.streamlit.io](https://share.streamlit.io)** → New app
2. Select this repo, set main file: `app.py`
3. Under **Settings → Secrets**, add:
```toml
GROQ_API_KEY = "gsk_..."
```
4. Click **Deploy** ✅

---

## 🛠️ How It Works

```
Professor uploads PDF / pastes lecture notes
              │
              ▼
    AI (Groq + Llama 3) reads material
              │
              ├── Generates MCQs (Easy / Medium / Hard)
              ├── Generates Short Questions
              ├── Generates Long Questions
              └── Generates Case Studies
                          │
                          ▼
            Student Copy (.txt) — no answers
            Answer Key  (.txt) — full model answers
```

---

## 📁 Files

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app — UI + AI generation + export |
| `requirements.txt` | Dependencies |
| `README.md` | This file |

---

## 🧰 Tech Stack

- **[Groq](https://groq.com)** — Free ultra-fast LLM API
- **[Llama 3.3 70B](https://llama.meta.com)** — AI model for question generation
- **[Streamlit](https://streamlit.io)** — Web UI framework
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** — PDF text extraction
- **Python** — Core language

---

## 👩‍🏫 Built By

**Nimra** — AI Engineer & Assistant Professor, Superior University  
🔗 [GitHub](https://github.com/nimra-pixel)

---

## 📄 License

MIT License — free to use, modify, and distribute.
