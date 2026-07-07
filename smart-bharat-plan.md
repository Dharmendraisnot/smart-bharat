# Smart Bharat — AI-Powered Civic Companion
## Hackathon Plan (DEVENGERS PromptWars 2026)

---

## Top-Level Overview

**Goal:** Build a GenAI-powered multi-page Streamlit web app that helps Indian citizens access government services, file civic complaints, discover eligible government schemes, and understand complex documents — all via an AI companion named "Sahayak" that speaks English and Hindi.

**Scope:**
- 4 core feature pages + 1 landing page
- Google Gemini 1.5 Flash as the sole LLM
- SQLite for grievance persistence
- JSON files as a lightweight knowledge base (RAG-lite)
- Deploy to Streamlit Community Cloud connected to a public GitHub repo

**Non-Goals:**
- No real user authentication
- No real government API integrations
- No voice/speech input (stretch goal only if time permits)
- No payment or e-governance form submissions

**Approach:**
Build in priority order: scaffold → chatbot → grievances → scheme finder → document simplifier → deploy.

---

## Sub-Task 1 — Project Scaffold and Gemini Client

**Intent:** Create the base project structure, install dependencies, configure secrets, and build the reusable Gemini API wrapper that all feature pages will share.

**Expected Outcomes:**
- All folders and files exist as per the defined folder structure
- `requirements.txt` lists all dependencies
- `utils/gemini_client.py` has a working `chat_with_gemini(query, lang)` function
- `utils/prompts.py` holds all prompt templates as constants
- App runs locally with `streamlit run app.py` without errors

**Todo List:**
1. Create folder structure: `pages/`, `data/`, `db/`, `utils/`, `assets/`
2. Write `requirements.txt` with: `streamlit`, `google-generativeai`, `python-dotenv`
3. Write `.streamlit/secrets.toml` template (with placeholder key)
4. Write `utils/gemini_client.py` — initialise Gemini client from `st.secrets`, expose `chat_with_gemini(prompt, system_prompt)` and `generate_json(prompt)` helpers
5. Write `utils/prompts.py` — define all system prompts as named string constants: `CIVIC_CHATBOT_PROMPT`, `SCHEME_FINDER_PROMPT`, `GRIEVANCE_CLASSIFIER_PROMPT`, `DOCUMENT_SIMPLIFIER_PROMPT`
6. Write `app.py` — Home/landing page with hero section, feature cards, and navigation

**Relevant Context:**
- Google Generative AI Python SDK: `google.generativeai` — use `genai.GenerativeModel("gemini-1.5-flash")`
- Streamlit secrets accessed via `st.secrets["GEMINI_API_KEY"]`
- Streamlit multi-page apps: files in `pages/` are auto-detected as navigation pages

**Status:** [ ] pending

---

## Sub-Task 2 — Knowledge Base (JSON Data Files)

**Intent:** Create the static JSON knowledge bases for government schemes and document requirements. These will be injected directly into Gemini prompts (RAG-lite) so the AI gives grounded, India-specific answers.

**Expected Outcomes:**
- `data/schemes.json` contains at least 10 real government schemes with name, description, eligibility criteria, benefits, and how-to-apply URL
- `data/documents.json` contains at least 8 common government documents with name, purpose, required documents list, and step-by-step process
- Both files are valid JSON and loadable with `json.load()`

**Todo List:**
1. Create `data/schemes.json` with entries for: PM Awas Yojana, Ayushman Bharat, MNREGS, PM Kisan, Sukanya Samriddhi, Pradhan Mantri Mudra Yojana, PM Ujjwala Yojana, PM Jan Dhan Yojana, Beti Bachao Beti Padhao, PM Scholarship Scheme
2. Each scheme entry must include: `id`, `name`, `description`, `eligibility`, `benefits`, `category`, `apply_url`
3. Create `data/documents.json` with entries for: Aadhaar Card, Ration Card, Caste Certificate, Income Certificate, Domicile Certificate, Birth Certificate, Voter ID, Driving Licence
4. Each document entry must include: `id`, `name`, `purpose`, `required_documents`, `steps`, `issuing_authority`
5. Write `utils/scheme_utils.py` — load schemes.json, format schemes as context string for Gemini prompt injection

**Relevant Context:**
- All scheme/doc text will be injected into Gemini's context window (Gemini 1.5 Flash supports 1M token context, so full JSON injection is safe)
- `utils/scheme_utils.py` will be imported by the Scheme Finder page

**Status:** [ ] pending

---

## Sub-Task 3 — SQLite Database Utilities

**Intent:** Set up the SQLite database and all CRUD helper functions needed for grievance filing and tracking.

**Expected Outcomes:**
- `db/grievances.db` is auto-created on first run
- `utils/db_utils.py` exposes: `init_db()`, `file_grievance(...)`, `track_grievance(complaint_id)`, `get_all_grievances()`
- Complaint IDs are human-readable (format: `SB-YYYYMMDD-XXXX`)
- All DB operations are wrapped in try/except for demo stability

**Todo List:**
1. Write `utils/db_utils.py`
2. Implement `init_db()` — creates `grievances` table if not exists with schema: `id TEXT PRIMARY KEY, name TEXT, phone TEXT, category TEXT, description TEXT, location TEXT, priority TEXT, status TEXT, created_at TEXT, updated_at TEXT`
3. Implement `file_grievance(name, phone, description, location, category, priority)` — inserts row, returns generated `SB-YYYYMMDD-XXXX` complaint ID
4. Implement `track_grievance(complaint_id)` — returns dict of grievance or None
5. Call `init_db()` at app startup (in `app.py`)

**Relevant Context:**
- SQLite is built into Python stdlib — no extra install needed
- On Streamlit Cloud, `db/` path must be relative; the DB resets on redeploy (acceptable for hackathon demo)
- Complaint ID format: `SB-` + date string + `-` + 4 random uppercase chars

**Status:** [ ] pending

---

## Sub-Task 4 — AI Civic Chatbot Page

**Intent:** Build the core AI chatbot page where citizens can ask any civic question in English or Hindi and receive grounded, helpful answers from Sahayak (Gemini).

**Expected Outcomes:**
- `pages/1_AI_Chatbot.py` is a fully functional chat UI
- Conversation history is maintained in `st.session_state` for the session
- AI responds in the same language the user writes in (auto-detected by Gemini)
- System prompt establishes Sahayak persona, India context, and language adaptability
- Suggested starter questions are shown to guide new users

**Todo List:**
1. Write `pages/1_AI_Chatbot.py`
2. Use `st.chat_message` and `st.chat_input` for the chat UI
3. Maintain `st.session_state.messages` as list of `{role, content}` dicts
4. On each user message: append to history, call `chat_with_gemini()` with full conversation history + `CIVIC_CHATBOT_PROMPT`, display streaming response
5. Add sidebar with 5 suggested questions in English and Hindi (e.g., "How do I apply for a ration card?", "राशन कार्ड के लिए कैसे आवेदन करें?")
6. Add "Clear Chat" button in sidebar

**Relevant Context:**
- `CIVIC_CHATBOT_PROMPT` in `utils/prompts.py` — persona: "You are Sahayak, a friendly AI civic companion for Indian citizens. Answer in the language the user writes in. Keep answers concise, accurate, and helpful for everyday Indians."
- `chat_with_gemini()` in `utils/gemini_client.py`
- Gemini multi-turn conversation: use `model.start_chat(history=[...])`

**Status:** [ ] pending

---

## Sub-Task 5 — Government Scheme Finder Page

**Intent:** Build an interactive form where a citizen enters their profile (age, income, state, category) and the AI recommends the most relevant government schemes with eligibility reasoning.

**Expected Outcomes:**
- `pages/2_Scheme_Finder.py` has a profile form with: Name, Age, Annual Income, State, Category (General/OBC/SC/ST), Gender, Occupation
- On submit, Gemini is called with the full schemes.json context + user profile
- AI returns top 3–5 matching schemes with: scheme name, why they qualify, key benefits, and apply link
- Results are displayed as attractive cards
- Works in both English and Hindi (language toggle)

**Todo List:**
1. Write `pages/2_Scheme_Finder.py`
2. Build profile form using `st.form` with fields: name, age (slider 0–100), annual income (selectbox ranges), state (dropdown of all Indian states), category (General/OBC/SC/ST/Other), gender, occupation type
3. On form submit: format user profile as a string, load schemes context via `scheme_utils.py`, inject both into `SCHEME_FINDER_PROMPT`, call Gemini
4. Parse and display AI response as styled `st.expander` cards — one per recommended scheme
5. Add language toggle (English / हिंदी) that prepends language instruction to the prompt
6. Add "Start Over" button to reset form

**Relevant Context:**
- `SCHEME_FINDER_PROMPT` — instructs Gemini to act as an eligibility expert, consider the provided scheme database, return structured recommendations
- `utils/scheme_utils.py` — `format_schemes_context()` returns all schemes as a formatted string
- Schemes data: `data/schemes.json`

**Status:** [ ] pending

---

## Sub-Task 6 — Grievance Filing and Tracking Page

**Intent:** Build the civic complaint portal where citizens can file a new grievance with AI-powered auto-categorization and priority assignment, then track existing complaints by ID.

**Expected Outcomes:**
- `pages/3_Grievance_Portal.py` has two tabs: "File a Complaint" and "Track Complaint"
- File tab: form with Name, Phone, Location, Description — AI auto-fills Category and Priority using Gemini
- On submit: grievance saved to SQLite, unique complaint ID shown to user with a success message
- Track tab: input a complaint ID → shows status, category, priority, filed date
- Input validation: phone must be 10 digits, description must be > 20 chars

**Todo List:**
1. Write `pages/3_Grievance_Portal.py`
2. Create two tabs using `st.tabs(["📝 File a Complaint", "🔍 Track Complaint"])`
3. **File tab:** Build form with name, phone (validated), location, description (text area)
4. On submit: call `categorize_and_prioritize(description)` in `gemini_client.py` which calls Gemini with `GRIEVANCE_CLASSIFIER_PROMPT` and returns `{"category": "...", "priority": "..."}` JSON
5. Call `db_utils.file_grievance(...)` with AI-assigned category and priority, display returned complaint ID in a green success box with copy instructions
6. **Track tab:** `st.text_input` for complaint ID, on submit call `db_utils.track_grievance(id)`, display result as a status card with colored status badge (Pending=red, In Progress=orange, Resolved=green)
7. Add a sample complaint ID hint for demo purposes

**Relevant Context:**
- `GRIEVANCE_CLASSIFIER_PROMPT` — "Classify the following civic complaint into one category: Roads, Water Supply, Electricity, Sanitation, Public Safety, Other. Also assign priority: Low, Medium, or High. Return ONLY valid JSON: {category: ..., priority: ...}"
- `utils/db_utils.py` — `file_grievance()`, `track_grievance()`
- `generate_json()` helper in `gemini_client.py` for structured output

**Status:** [ ] pending

---

## Sub-Task 7 — Document Simplifier Page

**Intent:** Build a page where citizens can type a document name (e.g., "ration card") or paste confusing government text, and Sahayak explains the requirements and process in simple, plain language.

**Expected Outcomes:**
- `pages/4_Document_Simplifier.py` has a text input and a dropdown of common documents
- AI response gives: what the document is for, list of required documents, step-by-step process, and estimated time/cost
- Supports English and Hindi output via language toggle
- "Common Documents" quick-select buttons for 8 popular documents

**Todo List:**
1. Write `pages/4_Document_Simplifier.py`
2. Add quick-select buttons for 8 documents: Aadhaar, Ration Card, Caste Certificate, Income Certificate, Voter ID, Birth Certificate, Domicile Certificate, Driving Licence
3. Add a text area for free-form document name or pasted text
4. Language toggle: English / हिंदी
5. On submit: load documents.json context, inject with user query and language into `DOCUMENT_SIMPLIFIER_PROMPT`, call Gemini
6. Display AI response in a clean formatted output with sections: Purpose, Required Documents (bulleted), Step-by-Step Process (numbered), Issuing Authority, Tips
7. Add "Download as Text" button using `st.download_button`

**Relevant Context:**
- `DOCUMENT_SIMPLIFIER_PROMPT` — "You are a helpful government document expert for India. Using the provided document database and the user's query, explain the document process in simple language. Format with clear sections."
- Documents data: `data/documents.json`
- `chat_with_gemini()` in `utils/gemini_client.py`

**Status:** [ ] pending

---

## Sub-Task 8 — UI Polish and Landing Page

**Intent:** Make the app visually presentable for hackathon judges — add branding, consistent styling, a compelling landing page, and a navigation experience that tells the story of Smart Bharat.

**Expected Outcomes:**
- `app.py` landing page has: project title, tagline, feature overview cards, and a "Get Started" CTA
- Consistent color theme (saffron/blue/green — Indian flag inspired)
- Sidebar shows app logo, navigation links, and "About" info
- All pages have consistent page title, icon, and header
- Custom CSS injected via `st.markdown` for card styling

**Todo List:**
1. Update `app.py` with hero section: title "🇮🇳 Smart Bharat", tagline "Your AI-Powered Civic Companion", 4 feature cards with icons and descriptions
2. Add `st.set_page_config(page_title="Smart Bharat", page_icon="🇮🇳", layout="wide")` to all pages
3. Write reusable CSS in `utils/styles.py` — card styles, badge styles, color variables
4. Apply `st.markdown(CSS, unsafe_allow_html=True)` on each page
5. Add sidebar content: logo placeholder, "Powered by Google Gemini" badge, GitHub link placeholder
6. Ensure all pages have a descriptive page header and subtitle

**Relevant Context:**
- Streamlit custom CSS via `st.markdown("<style>...</style>", unsafe_allow_html=True)`
- Indian flag color palette: Saffron `#FF9933`, White `#FFFFFF`, Green `#138808`, Navy `#000080`

**Status:** [ ] pending

---

## Sub-Task 9 — Deployment and GitHub Preparation

**Intent:** Prepare the project for public GitHub and deploy a working instance to Streamlit Community Cloud so submission links are ready.

**Expected Outcomes:**
- Public GitHub repository with all code pushed
- `README.md` with project description, features, setup instructions, and screenshots placeholder
- App deployed and accessible via a public Streamlit URL
- `GEMINI_API_KEY` set in Streamlit Cloud secrets (not in code)
- `.gitignore` excludes `secrets.toml` and `.db` files

**Todo List:**
1. Write `.gitignore` — exclude: `.streamlit/secrets.toml`, `db/*.db`, `__pycache__/`, `.env`, `venv/`
2. Write `README.md` — project title, problem statement, features list, tech stack, how to run locally, deployment link, Gemini prompt strategy section
3. Initialise git repo, commit all files, push to public GitHub repo
4. Go to share.streamlit.io → New app → connect GitHub repo → set `app.py` as entry point
5. Add `GEMINI_API_KEY` in Streamlit Cloud App Settings → Secrets
6. Verify all 4 feature pages work on deployed URL
7. Copy deployed URL and GitHub URL for submission form

**Relevant Context:**
- Streamlit Cloud free tier: 1 app per account, 1GB RAM, public repos only
- SQLite DB will be ephemeral on Streamlit Cloud — reset on each redeploy (fine for demo)
- `requirements.txt` must be in repo root for Streamlit Cloud auto-install

**Status:** [ ] pending

---

## Summary

| Sub-Task | Feature | Priority |
|---|---|---|
| 1 | Scaffold + Gemini Client | P0 — Must Have |
| 2 | Knowledge Base JSON files | P0 — Must Have |
| 3 | SQLite DB Utils | P0 — Must Have |
| 4 | AI Civic Chatbot | P0 — Must Have |
| 5 | Scheme Finder | P1 — Should Have |
| 6 | Grievance Portal | P0 — Must Have |
| 7 | Document Simplifier | P1 — Should Have |
| 8 | UI Polish + Landing Page | P2 — Nice to Have |
| 9 | Deployment + GitHub | P0 — Must Have |

**Recommended build order:** 1 → 3 → 4 → 6 → 2 → 5 → 7 → 8 → 9
