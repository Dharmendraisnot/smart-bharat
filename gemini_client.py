"""
utils/gemini_client.py
Google Gemini 1.5 Flash API client for Smart Bharat.
Uses google-generativeai >= 0.8.0 (google.generativeai SDK).

Public API:
    is_api_configured() -> bool
    chat_with_gemini(user_message, conversation_history, system_prompt) -> str
    find_schemes_with_gemini(user_profile, scheme_context, language) -> str
    simplify_document(user_query, doc_context, language) -> str
    categorize_and_prioritize(description) -> dict

All functions fall back to rich mock responses when GEMINI_API_KEY is absent,
so the UI is fully navigable without credentials.
"""

from __future__ import annotations

import json
import logging
import re
import time

import streamlit as st

logger = logging.getLogger(__name__)

_MODEL_NAME = "gemini-1.5-flash"


# ── Gemini client — cached once per process ────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _build_model():
    """
    Configure google-generativeai and return a GenerativeModel.
    Returns None when the API key is absent or invalid.
    """
    try:
        import google.generativeai as genai  # type: ignore

        api_key: str = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key or api_key.strip() in ("", "your-gemini-api-key-here"):
            logger.warning("GEMINI_API_KEY not set — running in demo mode.")
            return None

        genai.configure(api_key=api_key.strip())
        model = genai.GenerativeModel(
            model_name=_MODEL_NAME,
            generation_config={
                "temperature": 0.4,
                "top_p": 0.95,
                "max_output_tokens": 1024,
            },
        )
        logger.info("Gemini model '%s' ready.", _MODEL_NAME)
        return model

    except Exception as exc:
        logger.error("Gemini init failed: %s", exc)
        return None


def _model():
    return _build_model()


def is_api_configured() -> bool:
    """True when a live Gemini model is available."""
    return _model() is not None


# ── 1. Civic chatbot ───────────────────────────────────────────────────────────

def chat_with_gemini(
    user_message: str,
    conversation_history: list[dict],
    system_prompt: str = "",
) -> str:
    """
    Multi-turn civic Q&A via Gemini.

    Args:
        user_message: Latest user input (already appended to history by caller).
        conversation_history: Full list of {role, content} dicts.
        system_prompt: System instruction; sent once as the first exchange.

    Returns:
        AI reply string.
    """
    model = _model()
    if model is None:
        time.sleep(0.5)
        return _mock_chatbot_response(user_message)

    try:
        # Build Gemini conversation history
        gemini_history: list[dict] = []

        if system_prompt.strip():
            gemini_history.append({"role": "user",  "parts": [system_prompt.strip()]})
            gemini_history.append({"role": "model", "parts": [
                "Understood. I am Sahayak, your Smart Bharat AI civic companion. "
                "I will answer all civic questions accurately in the language the citizen uses."
            ]})

        for msg in conversation_history[:-1]:      # exclude the latest user message
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_message)
        return response.text.strip()

    except Exception as exc:
        logger.error("chat_with_gemini: %s", exc)
        return (
            "⚠️ Sahayak is temporarily unavailable. "
            f"Please try again in a moment.\n\n*(Error: {exc})*"
        )


# ── 2. Structured JSON output ──────────────────────────────────────────────────

def _generate_json(prompt: str, fallback: dict) -> dict:
    """
    Call Gemini and parse the response as a JSON dict.
    Strips markdown fences; corrects trailing commas.
    """
    model = _model()
    if model is None:
        time.sleep(0.3)
        return _mock_classify_complaint(prompt)

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        raw = re.sub(r",\s*([}\]])", r"\1", raw)
        return json.loads(raw.strip())

    except json.JSONDecodeError:
        logger.warning("JSON parse failed. Raw: %.200s", raw)
        return fallback
    except Exception as exc:
        logger.error("_generate_json: %s", exc)
        return fallback


# ── 3. Scheme finder ───────────────────────────────────────────────────────────

def find_schemes_with_gemini(
    user_profile: dict,
    scheme_context: str,
    language: str = "English",
) -> str:
    """
    Recommend top 3–5 government schemes based on user profile.
    Grounded in the provided scheme knowledge base (RAG-lite).
    """
    from utils.prompts import SCHEME_FINDER_PROMPT

    model = _model()
    if model is None:
        time.sleep(0.8)
        return _mock_scheme_recommendations(user_profile)

    profile_lines = "\n".join(
        f"- {k.replace('_', ' ').title()}: {v}" for k, v in user_profile.items()
    )
    prompt = SCHEME_FINDER_PROMPT.format(
        scheme_context=scheme_context,
        user_profile=profile_lines,
        language=language,
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("find_schemes_with_gemini: %s", exc)
        return (
            "⚠️ Unable to fetch scheme recommendations right now. "
            f"Please try again shortly.\n\n*(Error: {exc})*"
        )


# ── 4. Document simplifier ─────────────────────────────────────────────────────

def simplify_document(
    user_query: str,
    doc_context: str,
    language: str = "English",
) -> str:
    """
    Explain a government document in plain language.
    """
    from utils.prompts import DOCUMENT_SIMPLIFIER_PROMPT

    model = _model()
    if model is None:
        time.sleep(0.5)
        return _mock_document_explanation(user_query)

    prompt = DOCUMENT_SIMPLIFIER_PROMPT.format(
        doc_context=doc_context,
        user_query=user_query,
        language=language,
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("simplify_document: %s", exc)
        return (
            "⚠️ Unable to simplify the document right now. "
            f"Please try again shortly.\n\n*(Error: {exc})*"
        )


# ── 5. Grievance classifier ────────────────────────────────────────────────────

def categorize_and_prioritize(description: str) -> dict:
    """
    Auto-classify a civic complaint → {category, priority, summary}.
    """
    from utils.prompts import GRIEVANCE_CLASSIFIER_PROMPT

    prompt = GRIEVANCE_CLASSIFIER_PROMPT.format(complaint_text=description)
    return _generate_json(
        prompt,
        fallback={
            "category": "Other",
            "priority": "Medium",
            "summary": description[:120],
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# Demo / fallback helpers  (invoked only when GEMINI_API_KEY is absent)
# ══════════════════════════════════════════════════════════════════════════════

def _mock_chatbot_response(user_message: str) -> str:  # noqa: C901
    msg = user_message.lower()

    if any(w in msg for w in ["ration", "राशन"]):
        return (
            "**Ration Card** (राशन कार्ड) is issued by the State Food Department.\n\n"
            "**Steps to apply:**\n"
            "1. Visit your nearest **Food & Civil Supplies** office or apply at your state portal.\n"
            "2. Fill **Form 1** (application for new ration card).\n"
            "3. Attach: Aadhaar, residence proof, passport-size photo, income certificate.\n"
            "4. Submit and collect the acknowledgment slip.\n"
            "5. Card issued within **15–30 working days**.\n\n"
            "💡 *Tip: Apply via the **mRation** mobile app in supported states.*"
        )

    if any(w in msg for w in ["aadhaar", "aadhar", "आधार"]):
        return (
            "**Aadhaar Card** is issued by **UIDAI** (Unique Identification Authority of India).\n\n"
            "**To apply or update Aadhaar:**\n"
            "1. Visit the nearest **Aadhaar Seva Kendra** or **Common Service Centre (CSC)**.\n"
            "2. Fill the enrolment form and provide biometrics.\n"
            "3. Update address online at **ssup.uidai.gov.in**.\n\n"
            "📞 UIDAI Helpline: **1947** (toll-free, 24×7)"
        )

    if any(w in msg for w in ["pan", "पैन"]):
        return (
            "**PAN Card** is issued by the **Income Tax Department** via NSDL / UTIITSL.\n\n"
            "**How to apply:**\n"
            "1. Apply online at **onlineservices.tin.egov-nsdl.com** or **www.utiitsl.com**.\n"
            "2. Fill Form 49A and upload identity + address proof.\n"
            "3. Pay ₹107 (physical) or ₹72 (e-PAN).\n"
            "4. PAN issued within **15 working days**.\n\n"
            "💡 *Link your Aadhaar for a free **instant e-PAN** at incometax.gov.in.*"
        )

    if any(w in msg for w in ["scheme", "yojana", "योजना"]):
        return (
            "India has many government schemes:\n\n"
            "🌾 **Agriculture:** PM Kisan, PM Fasal Bima Yojana\n"
            "🏠 **Housing:** PM Awas Yojana (Rural & Urban)\n"
            "🏥 **Health:** Ayushman Bharat – PM Jan Arogya Yojana\n"
            "💼 **Employment:** MGNREGS, PM Mudra Yojana\n"
            "👧 **Women & Children:** Sukanya Samriddhi, Beti Bachao Beti Padhao\n\n"
            "👉 Use the **Scheme Finder** page to check your personal eligibility!"
        )

    if any(w in msg for w in ["rti", "right to information", "सूचना का अधिकार"]):
        return (
            "**RTI – Right to Information Act, 2005** allows every citizen to request "
            "information from any public authority.\n\n"
            "**How to file:**\n"
            "1. Write to the **Public Information Officer (PIO)** of the concerned department.\n"
            "2. State the information you need clearly.\n"
            "3. Pay ₹10 fee (waived for BPL card holders).\n"
            "4. Submit at the office or via **rtionline.gov.in**.\n"
            "5. Response must come within **30 days**.\n\n"
            "📞 RTI Helpline: **011-24622461**"
        )

    if any(w in msg for w in ["hello", "hi", "नमस्ते", "नमस्कार", "hey"]):
        return (
            "नमस्ते! 🙏 मैं **सहायक** हूँ — आपका AI नागरिक सहायक।\n\n"
            "Hello! I'm **Sahayak**, your Smart Bharat AI companion.\n\n"
            "I can help you with:\n"
            "- 📋 **Government documents** — Aadhaar, Ration Card, PAN, Voter ID, etc.\n"
            "- 🏛️ **Government schemes** — eligibility, benefits, how to apply\n"
            "- 📣 **Civic complaints** — how to file and track\n"
            "- ℹ️ **Any civic question** — in English or Hindi\n\n"
            "What can I help you with today? / आज मैं आपकी क्या सहायता कर सकता हूँ?"
        )

    return (
        f"Thank you for your question about **\"{user_message}\"**.\n\n"
        "I'm **Sahayak**, your Smart Bharat AI civic companion. "
        "I can answer questions about government services, documents, schemes, and civic rights.\n\n"
        "⚡ *Connect your Gemini API key for live AI-powered answers.*\n\n"
        "Or try one of these:\n"
        "- 🔍 **Scheme Finder** — find eligible government schemes\n"
        "- 📣 **Grievance Portal** — report civic issues\n"
        "- 📄 **Document Simplifier** — understand government documents"
    )


def _mock_classify_complaint(prompt: str) -> dict:
    # Scan only the complaint text portion so the category list above it
    # does not cause false-positive keyword matches.
    marker = "COMPLAINT TEXT:"
    complaint_section = prompt[prompt.find(marker) + len(marker):] if marker in prompt else prompt
    p = complaint_section.lower()
    if any(w in p for w in ["road", "pothole", "sarak", "highway", "bridge", "footpath"]):
        return {"category": "Roads & Infrastructure", "priority": "High",
                "summary": "Road damage or pothole causing inconvenience to commuters."}
    if any(w in p for w in ["water", "paani", "पानी", "pipeline", "tap", "supply"]):
        return {"category": "Water Supply", "priority": "High",
                "summary": "Water supply disruption affecting residential area."}
    if any(w in p for w in ["light", "electricity", "bijli", "power", "voltage", "transformer", "street light"]):
        return {"category": "Electricity", "priority": "Medium",
                "summary": "Electricity supply issue reported in the area."}
    if any(w in p for w in ["garbage", "waste", "sanitation", "drain", "sewage", "clean"]):
        return {"category": "Sanitation & Waste", "priority": "Medium",
                "summary": "Sanitation or waste management issue reported."}
    if any(w in p for w in ["hospital", "doctor", "medicine", "health", "clinic", "ambulance"]):
        return {"category": "Healthcare", "priority": "High",
                "summary": "Healthcare service issue reported."}
    if any(w in p for w in ["school", "teacher", "education", "college"]):
        return {"category": "Education", "priority": "Medium",
                "summary": "Education-related civic issue reported."}
    if any(w in p for w in ["crime", "theft", "safety", "police", "violence", "harassment"]):
        return {"category": "Public Safety", "priority": "High",
                "summary": "Public safety issue requiring urgent attention."}
    return {"category": "Other", "priority": "Medium",
            "summary": "General civic complaint filed by citizen."}


def _mock_scheme_recommendations(user_profile: dict) -> str:
    age       = int(user_profile.get("age", 30))
    income    = user_profile.get("annual_income", "Below ₹1 Lakh")
    gender    = user_profile.get("gender", "Male")
    is_low    = any(k in income for k in ["Below", "1 Lakh", "2 Lakh", "2.5"])
    is_farmer = "farm" in user_profile.get("occupation", "").lower()

    recs: list[str] = []

    recs.append(
        "### ✅ PM Jan Dhan Yojana\n"
        "**Why you qualify:** Available to all Indian citizens regardless of income.\n"
        "**Benefits:** Zero-balance savings account, RuPay debit card, ₹2 lakh accident insurance, ₹30,000 life insurance.\n"
        "**How to Apply:** Visit any nationalised bank with Aadhaar + photo.\n"
        "🔗 [Apply Now →](https://pmjdy.gov.in)"
    )

    if is_low:
        recs.append(
            "### ✅ Ayushman Bharat – PM Jan Arogya Yojana\n"
            "**Why you qualify:** Your income falls within the BPL/low-income bracket.\n"
            "**Benefits:** Health coverage up to ₹5 lakh per family per year. Cashless treatment at 25,000+ empanelled hospitals.\n"
            "**How to Apply:** Visit empanelled hospital → show Aadhaar → get Ayushman card issued.\n"
            "🔗 [Apply Now →](https://pmjay.gov.in)"
        )
        recs.append(
            "### ✅ PM Ujjwala Yojana\n"
            "**Why you qualify:** Available to BPL households.\n"
            "**Benefits:** Free LPG connection + first refill subsidy.\n"
            "**How to Apply:** Visit nearest LPG distributor with BPL certificate + Aadhaar.\n"
            "🔗 [Apply Now →](https://pmuy.gov.in)"
        )

    if is_farmer:
        recs.append(
            "### ✅ PM Kisan Samman Nidhi\n"
            "**Why you qualify:** You are a farmer/agricultural labourer.\n"
            "**Benefits:** ₹6,000 per year (₹2,000 every 4 months) credited directly to bank account.\n"
            "**How to Apply:** Register at pmkisan.gov.in or nearest CSC with land records + Aadhaar.\n"
            "🔗 [Apply Now →](https://pmkisan.gov.in)"
        )

    if gender == "Female" and age < 45:
        recs.append(
            "### ✅ Sukanya Samriddhi Yojana\n"
            "**Why you qualify:** Available for girl children and women investors.\n"
            "**Benefits:** 8.2% p.a. interest, tax exemption under Section 80C.\n"
            "**How to Apply:** Visit Post Office or nationalised bank with birth certificate + Aadhaar.\n"
            "🔗 [Apply Now →](https://nsiindia.gov.in)"
        )

    if 18 <= age <= 55:
        recs.append(
            "### ✅ PM Mudra Yojana\n"
            "**Why you qualify:** Working-age citizen eligible for micro-enterprise loans.\n"
            "**Benefits:** Collateral-free loans up to ₹10 lakh for small businesses.\n"
            "**How to Apply:** Approach any bank/NBFC with business plan + KYC documents.\n"
            "🔗 [Apply Now →](https://mudra.org.in)"
        )

    result  = "## 🏛️ Recommended Government Schemes\n\n"
    result += "Based on your profile, here are the schemes you are most likely eligible for:\n\n"
    result += "\n\n---\n\n".join(recs)
    result += (
        "\n\n---\n\n"
        "*⚡ Demo recommendations — add `GEMINI_API_KEY` for live AI-powered personalised eligibility analysis.*"
    )
    return result


def _mock_document_explanation(user_query: str) -> str:
    q = user_query.lower()

    if "ration" in q:
        return (
            "## 📄 What is this document?\n"
            "A **Ration Card** is issued by the State Government to buy subsidised food grains "
            "(rice, wheat, sugar) from Fair Price Shops under the Public Distribution System (PDS).\n\n"
            "## 🎯 Why do you need it?\n"
            "- Purchase subsidised food grains at ration shops\n"
            "- Accepted as proof of residence and family identity\n"
            "- Required for many government scheme applications\n"
            "- Free food grains under PM Garib Kalyan Anna Yojana\n\n"
            "## 📋 Documents Required\n"
            "1. Aadhaar card (all family members)\n"
            "2. Proof of residence (electricity bill / rent agreement)\n"
            "3. Passport-size photographs of all members\n"
            "4. Income certificate (for BPL card)\n\n"
            "## 🔄 Step-by-Step Process\n"
            "1. Visit State Food & Civil Supplies portal or nearest tehsil office\n"
            "2. Fill Form-1 (new ration card application)\n"
            "3. Attach all documents and submit\n"
            "4. Receive acknowledgment slip with application number\n"
            "5. Card issued within **15–30 working days** after verification\n\n"
            "## 🏛️ Issuing Authority\nState Food & Civil Supplies Department\n\n"
            "## ⏱️ Time & Cost\n- 15–30 working days · Free of cost\n\n"
            "## 💡 Tips\n"
            "- Link Aadhaar with ration card for uninterrupted subsidy\n"
            "- Apply via **mRation** app in supported states\n"
            "- Check application status using your acknowledgment number"
        )

    if any(w in q for w in ["aadhaar", "aadhar"]):
        return (
            "## 📄 What is this document?\n"
            "**Aadhaar** is a 12-digit unique identity number issued by **UIDAI** "
            "to every Indian resident, based on biometric and demographic data.\n\n"
            "## 🎯 Why do you need it?\n"
            "- Primary identity proof for all government services\n"
            "- Bank account KYC, mobile SIM activation, PAN linking\n"
            "- Access to Direct Benefit Transfers (DBT) and subsidies\n"
            "- Required for income tax filing\n\n"
            "## 📋 Documents Required\n"
            "1. Proof of Identity: Passport / Voter ID / PAN Card\n"
            "2. Proof of Address: Utility bill / Bank passbook / Rent agreement\n"
            "3. Date of Birth proof: Birth certificate / School certificate\n\n"
            "## 🔄 Step-by-Step Process\n"
            "1. Visit nearest **Aadhaar Seva Kendra** or Common Service Centre (CSC)\n"
            "2. Fill the Enrolment Form and provide biometrics (fingerprints + iris + photo)\n"
            "3. Collect your **14-digit Enrolment ID** on the acknowledgment slip\n"
            "4. Download **e-Aadhaar** from uidai.gov.in within 2–3 days\n"
            "5. Physical Aadhaar card delivered to your address in 60–90 days\n\n"
            "## 🏛️ Issuing Authority\nUIDAI – Unique Identification Authority of India\n\n"
            "## ⏱️ Time & Cost\n"
            "- e-Aadhaar: 2–3 days after enrolment · Physical card: 60–90 days · **Free**\n\n"
            "## 💡 Tips\n"
            "- Update your address online at **ssup.uidai.gov.in** (no centre visit needed)\n"
            "- Lock your biometrics at **myaadhaar.uidai.gov.in** for security\n"
            "- UIDAI Helpline: **1947** (toll-free, 24×7)"
        )

    return (
        f"## 📄 About: {user_query}\n\n"
        "This appears to be a government document or process query.\n\n"
        "## 📋 General Steps to Obtain Government Documents\n"
        "1. Identify the **issuing authority** (district/state level office)\n"
        "2. Visit the official state portal or nearest government office / CSC\n"
        "3. Fill the application form and attach Aadhaar + address proof + photo\n"
        "4. Pay any applicable fees and collect the acknowledgment slip\n"
        "5. Track application status and collect your document within the stipulated time\n\n"
        "## 💡 Tips\n"
        "- Store all documents digitally on **DigiLocker** (digilocker.gov.in) — free & official\n"
        "- Most documents are also available at **Common Service Centres (CSC)**\n"
        "- For urgent needs, use the **Tatkal** scheme where available\n\n"
        "*⚡ Add your `GEMINI_API_KEY` to get a detailed, accurate explanation for any government document.*"
    )
