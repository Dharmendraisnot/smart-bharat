# 🇮🇳 Smart Bharat — AI-Powered Civic Companion

> **Built for DEVENGERS PromptWars 2026** · Powered by Google Gemini · Deployed on Streamlit Cloud

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 Problem Statement

Indian citizens face significant friction when accessing government services — complex paperwork, language barriers, lack of awareness about eligible schemes, and no easy way to report civic issues. **Smart Bharat** bridges this gap using Generative AI.

---

## 🚀 What is Smart Bharat?

**Smart Bharat** is a GenAI-powered multi-page web platform that helps Indian citizens:

- 💬 **Ask civic questions** in English or Hindi via an AI companion named **Sahayak**
- 🏛️ **Discover government schemes** they are eligible for (PM Kisan, Ayushman Bharat, MGNREGS, and more)
- 📣 **File and track civic complaints** (potholes, water supply, electricity, sanitation) with AI auto-categorization
- 📄 **Understand complex government documents** in plain, simple language

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 💬 **AI Civic Chatbot** | Multilingual Q&A powered by Gemini 1.5 Flash. Answers questions about Aadhaar, PAN, RTI, ration cards, and more in English & Hindi |
| 🏛️ **Government Scheme Finder** | Profile-based eligibility matching across 10+ real schemes. Returns top 3–5 matches with reasoning and apply links |
| 📣 **Grievance Portal** | File civic complaints with name + phone. AI auto-assigns category & priority. Generates trackable complaint ID (`SB-YYYYMMDD-XXXX`) |
| 🔍 **Complaint Tracking** | Real SQLite persistence. Track any complaint by ID — see status (Pending / In Progress / Resolved) |
| 📄 **Document Simplifier** | Explains government documents (Aadhaar, Ration Card, Caste Certificate, Driving Licence, etc.) in plain language with step-by-step guide |
| 🌐 **Bilingual** | Full English + Hindi support across all AI features |
| 🎨 **Indian Government Theme** | Saffron (#FF9933) · White · Green (#138808) · Navy (#1E3A5F) colour palette |

---

## 🏗️ Architecture

```
smart-bharat/
├── app.py                         ← Home / Landing page (entry point)
├── requirements.txt
├── .streamlit/
│   └── secrets.toml               ← GEMINI_API_KEY (not committed to git)
├── pages/
│   ├── 1_AI_Chatbot.py            ← Multilingual civic Q&A
│   ├── 2_Scheme_Finder.py         ← AI eligibility matching
│   ├── 3_Grievance_Portal.py      ← File + Track complaints
│   └── 4_Document_Simplifier.py   ← Plain-language doc explainer
├── data/
│   ├── schemes.json               ← 10 government schemes knowledge base
│   └── documents.json             ← 8 document requirement guides
├── db/
│   └── grievances.db              ← SQLite (auto-created on first run)
└── utils/
    ├── gemini_client.py            ← Gemini API wrapper (all AI functions)
    ├── db_utils.py                 ← SQLite CRUD helpers
    ├── scheme_utils.py             ← JSON loaders + Indian states list
    ├── prompts.py                  ← All Gemini prompt templates
    └── styles.py                  ← CSS + HTML component helpers
```

---

## 🤖 AI Workflow (Prompt Strategy)

### 1. Civic Chatbot — Multi-turn Conversation
```
System Prompt → Sahayak persona + language rule (respond in user's language)
     ↓
Conversation History → all prior turns injected into Gemini context
     ↓
User Message → Gemini 1.5 Flash → Response in detected language
```

### 2. Scheme Finder — RAG-lite
```
User Profile (age, income, state, category, gender, occupation)
     +
Scheme Knowledge Base (schemes.json → formatted context string)
     ↓
SCHEME_FINDER_PROMPT → Gemini → Top 3–5 matching schemes with eligibility reasoning
```

### 3. Grievance Classifier — Structured Output
```
Raw complaint text
     ↓
GRIEVANCE_CLASSIFIER_PROMPT → Gemini → {"category": "...", "priority": "...", "summary": "..."}
     ↓
JSON parsed + saved to SQLite with auto-generated SB-YYYYMMDD-XXXX ID
```

### 4. Document Simplifier — RAG-lite
```
Document name or pasted text
     +
Document Knowledge Base (documents.json → formatted context string)
     ↓
DOCUMENT_SIMPLIFIER_PROMPT → Gemini → Structured markdown guide
(What is it · Why needed · Documents required · Steps · Issuing authority · Tips)
```

### Prompt Design Principles
- **Language awareness**: System prompt instructs Gemini to respond in the user's language
- **Grounding**: All AI answers are anchored to the provided JSON knowledge base (no hallucinations)
- **Structured output**: Grievance classifier uses strict JSON format instruction with fence stripping
- **Temperature = 0.4**: Balanced for accuracy + natural language (not too creative, not too rigid)
- **Graceful fallback**: All functions return rich mock responses when no API key is set

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit 1.32+ (multi-page app) |
| **AI / LLM** | Google Gemini 1.5 Flash via `google-generativeai` |
| **Database** | SQLite (stdlib — zero config, auto-created) |
| **Knowledge Base** | JSON files (RAG-lite, injected into Gemini context) |
| **Languages** | Python 3.10+ |
| **Deployment** | Streamlit Community Cloud (free) |
| **Secrets** | `st.secrets` — API key never in code |

---

## ⚡ Quick Start (Local)

### Prerequisites
- Python 3.10 or higher
- A free Google Gemini API key → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/smart-bharat.git
cd smart-bharat

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Gemini API key
# Edit .streamlit/secrets.toml:
# GEMINI_API_KEY = "AIza..."

# 4. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**

> **No API key?** The app works in demo mode with intelligent mock responses. You can navigate all pages, file complaints, track them, and use every feature.

---

## ☁️ Deploy to Streamlit Community Cloud

1. **Fork / push** this repo to your public GitHub account
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → New app
3. Select your GitHub repo → set main file to `app.py`
4. Go to **App Settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "AIza..."
   ```
5. Click **Deploy** — live URL generated in ~2 minutes

> ⚠️ The `db/` folder is ephemeral on Streamlit Cloud (resets on redeploy). This is fine for demo purposes. For production, replace SQLite with a cloud database.

---

## 🎭 Demo Complaint IDs (for Tracking)

These IDs are pre-seeded in the database for instant demo:

| Complaint ID | Status | Category |
|---|---|---|
| `SB-20240115-DEMO` | In Progress | Roads & Infrastructure |
| `SB-20240116-SAMP` | Pending | Water Supply |
| `SB-20240110-TEST` | Resolved | Sanitation & Waste |

---

## 📋 Government Schemes Covered

| Scheme | Category |
|---|---|
| PM Awas Yojana (Urban) | Housing |
| Ayushman Bharat – PM Jan Arogya Yojana | Health |
| PM Kisan Samman Nidhi | Agriculture |
| PM Jan Dhan Yojana | Finance |
| Sukanya Samriddhi Yojana | Women & Child |
| PM Mudra Yojana | Employment |
| PM Ujjwala Yojana | Energy |
| MGNREGS | Employment |
| Beti Bachao Beti Padhao | Women & Child |
| PM Scholarship Scheme | Education |

---

## 📄 Documents Supported

Aadhaar Card · Ration Card · Caste Certificate · Income Certificate · Voter ID · Birth Certificate · Domicile Certificate · Driving Licence

---

## 🔐 Security

- **API key** is never hard-coded. Always read from `st.secrets["GEMINI_API_KEY"]`
- **secrets.toml** is in `.gitignore` and never committed
- **SQLite** path is relative — no absolute system paths exposed
- **Error handling** wraps all Gemini API calls — failures never crash the UI

---

## 📁 Project Description (Submission)

**Smart Bharat – AI-Powered Civic Companion** is a GenAI-powered web platform built for the DEVENGERS PromptWars 2026 hackathon. It uses Google Gemini 1.5 Flash to help Indian citizens access government services, discover eligible schemes, file civic complaints, and understand complex documents — all in English and Hindi.

The platform promotes **transparency, accessibility, and digital inclusion** by making everyday civic interactions faster, smarter, and more user-friendly. Citizens with limited digital literacy can type a question in Hindi or English and immediately receive accurate, grounded information about their rights and available services.

**Key innovation:** The RAG-lite architecture injects a curated knowledge base (10 schemes + 8 documents) directly into Gemini's 1M-token context window, ensuring all AI responses are grounded in real government data — no hallucinations, no made-up scheme names.

---

## 🏆 Hackathon Submission Checklist

- [x] Public GitHub Repository
- [x] Working Deployed Web App (Streamlit Cloud)
- [x] Project Description (see above)
- [x] Prompt Workflow / Strategy (see AI Workflow section)
- [x] All 4 features functional (Chatbot, Scheme Finder, Grievance Portal, Document Simplifier)
- [x] English + Hindi multilingual support
- [x] Real SQLite persistence for grievances
- [x] Graceful demo mode (works without API key)

---

## 👨‍💻 Built With

- [Streamlit](https://streamlit.io) — UI framework
- [Google Gemini](https://ai.google.dev) — Generative AI
- [google-generativeai](https://pypi.org/project/google-generativeai/) — Python SDK
- Python 3.10+ Standard Library (sqlite3, json, re, logging)

---

*🇮🇳 Smart Bharat — सेवा • सहायता • समाधान · Built with ❤️ for DEVENGERS PromptWars 2026*
