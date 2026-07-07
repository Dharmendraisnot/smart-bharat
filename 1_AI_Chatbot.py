"""
pages/1_AI_Chatbot.py — Smart Bharat AI Civic Chatbot
Multilingual civic Q&A powered by Google Gemini (Sahayak persona).
"""

import streamlit as st
from utils.styles import GLOBAL_CSS, top_bar, page_title_bar, footer, tricolor_line
from utils.gemini_client import chat_with_gemini
from utils.prompts import CIVIC_CHATBOT_PROMPT

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chatbot – Smart Bharat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_processing" not in st.session_state:
    st.session_state.chat_processing = False

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 0.8rem 0 0.5rem 0;">
            <div style="font-size:2rem;">🇮🇳</div>
            <div style="font-size:1.1rem; font-weight:800; color:#1E3A5F;">Smart Bharat</div>
            <div style="font-size:0.75rem; color:#FF9933; font-weight:600;">AI Civic Companion</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🧭 Navigate")
    st.page_link("app.py",                            label="🏠 Home")
    st.page_link("pages/1_AI_Chatbot.py",             label="💬 AI Civic Chatbot")
    st.page_link("pages/2_Scheme_Finder.py",          label="🏛️ Government Scheme Finder")
    st.page_link("pages/3_Grievance_Portal.py",       label="📣 Grievance Portal")
    st.page_link("pages/4_Document_Simplifier.py",    label="📄 Document Simplifier")
    st.markdown("---")

    # ── Suggested questions ────────────────────────────────────────────────────
    st.markdown("### 💡 Suggested Questions")
    suggestions = [
        "How do I apply for a ration card?",
        "राशन कार्ड के लिए कैसे आवेदन करें?",
        "What is Ayushman Bharat scheme?",
        "How to file an RTI application?",
        "मेरे लिए कौन सी सरकारी योजनाएं हैं?",
        "How do I get a caste certificate?",
        "What documents are needed for Aadhaar?",
    ]
    for q in suggestions:
        if st.button(q, key=f"sugg_{q[:15]}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": q})
            st.session_state.chat_processing = True
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown(
        """
        <div style="text-align:center; font-size:0.75rem; color:#aaa; padding-top:0.5rem;">
            Sahayak speaks English & Hindi
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Top bar + Page header ──────────────────────────────────────────────────────
st.markdown(top_bar(), unsafe_allow_html=True)
st.markdown(
    page_title_bar(
        icon="💬",
        title="AI Civic Chatbot",
        subtitle="Ask Sahayak anything about government services, schemes, and civic processes — in English or Hindi.",
    ),
    unsafe_allow_html=True,
)

# ── Welcome message ────────────────────────────────────────────────────────────
if not st.session_state.chat_history:
    st.markdown(
        """
        <div style="background:#f0f7ff; border-radius:14px; padding:1.4rem 1.8rem;
                    border-left:5px solid #FF9933; margin-bottom:1rem;">
            <div style="font-size:1rem; font-weight:700; color:#1E3A5F; margin-bottom:0.4rem;">
                🙏 Namaste! I'm Sahayak — your Smart Bharat AI Companion.
            </div>
            <div style="font-size:0.9rem; color:#444; line-height:1.6;">
                I can help you with:<br>
                &nbsp;&nbsp;📋 <strong>Government Documents</strong> — Aadhaar, Ration Card, PAN, Voter ID, and more<br>
                &nbsp;&nbsp;🏛️ <strong>Government Schemes</strong> — eligibility, benefits, and how to apply<br>
                &nbsp;&nbsp;📣 <strong>Civic Complaints</strong> — how to file and track grievances<br>
                &nbsp;&nbsp;ℹ️ <strong>Any civic question</strong> — in English or Hindi<br><br>
                <em>नमस्ते! मैं हिंदी में भी आपकी सहायता कर सकता हूँ।</em>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Process pending AI response ────────────────────────────────────────────────
if st.session_state.chat_processing and st.session_state.chat_history:
    last_user_msg = st.session_state.chat_history[-1]["content"]
    with st.spinner("🤔 Sahayak is thinking..."):
        response = chat_with_gemini(
            user_message=last_user_msg,
            conversation_history=st.session_state.chat_history,
            system_prompt=CIVIC_CHATBOT_PROMPT,
        )
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.chat_processing = False

# ── Chat display ───────────────────────────────────────────────────────────────
chat_col, _ = st.columns([3, 1])

with chat_col:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(
                    "<div style='font-size:0.78rem; font-weight:700; "
                    "color:#FF9933; margin-bottom:0.2rem;'>🤖 SAHAYAK</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(msg["content"])

    # ── Chat input ─────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(tricolor_line(), unsafe_allow_html=True)

    user_input = st.chat_input(
        "Ask your civic question in English or Hindi... / हिंदी या अंग्रेज़ी में पूछें...",
    )

    if user_input and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_processing = True
        st.rerun()

# ── Info panel ─────────────────────────────────────────────────────────────────
with _:
    st.markdown(
        """
        <div style="background:#f7f9fc; border-radius:12px; padding:1.2rem;
                    border:1.5px solid #e8edf5; margin-top:0.2rem;">
            <div style="font-weight:700; color:#1E3A5F; margin-bottom:0.6rem; font-size:0.9rem;">
                ℹ️ Quick Tips
            </div>
            <div style="font-size:0.82rem; color:#57606a; line-height:1.7;">
                • Type in <strong>English</strong> or <strong>Hindi</strong><br>
                • Use the suggestion buttons in the sidebar<br>
                • Ask follow-up questions naturally<br>
                • Ask about <strong>schemes, documents, RTI, complaints</strong>, and more<br><br>
                <strong style="color:#FF9933;">Sample Questions:</strong><br>
                <em>"Ayushman Bharat ke liye kaise apply karen?"</em><br>
                <em>"What is PM Kisan Yojana?"</em><br>
                <em>"How to update Aadhaar address?"</em>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:#fff3e0; border-radius:10px; padding:1rem;
                    border-left:4px solid #FF9933; font-size:0.8rem; color:#7a4400;">
            <strong>🔑 API Status</strong><br>
            Demo mode active.<br>Set <code>GEMINI_API_KEY</code> in
            <code>.streamlit/secrets.toml</code> to enable real AI responses.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(footer(), unsafe_allow_html=True)
