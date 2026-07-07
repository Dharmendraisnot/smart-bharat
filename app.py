"""
app.py — Smart Bharat Home / Landing Page
Entry point for the Streamlit multi-page application.
"""

import streamlit as st
from utils.styles import GLOBAL_CSS, top_bar, hero_section, feature_card, footer, tricolor_line
from utils.db_utils import init_db

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Bharat – AI Civic Companion",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init session state ─────────────────────────────────────────────────────────
init_db()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "scheme_results" not in st.session_state:
    st.session_state.scheme_results = None

if "doc_result" not in st.session_state:
    st.session_state.doc_result = None

if "last_complaint_id" not in st.session_state:
    st.session_state.last_complaint_id = None

# ── Inject CSS ─────────────────────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
            <div style="font-size:2.5rem;">🇮🇳</div>
            <div style="font-size:1.2rem; font-weight:800; color:#1E3A5F;">Smart Bharat</div>
            <div style="font-size:0.78rem; color:#FF9933; font-weight:600;">AI Civic Companion</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🧭 Navigate")
    st.markdown("""
<nav>
<a href="/"            target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;font-weight:600;">🏠 Home</a>
<a href="/AI_Chatbot"  target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">💬 AI Civic Chatbot</a>
<a href="/Scheme_Finder" target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">🏛️ Government Scheme Finder</a>
<a href="/Grievance_Portal" target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">📣 Grievance Portal</a>
<a href="/Document_Simplifier" target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">📄 Document Simplifier</a>
</nav>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; font-size:0.78rem; color:#888; padding:0.5rem 0;">
            <div style="margin-bottom:0.4rem;">Powered by</div>
            <div style="color:#4285F4; font-weight:700; font-size:0.9rem;">Google Gemini</div>
            <div style="margin-top:0.6rem; color:#aaa;">DEVENGERS PromptWars 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Tricolor top bar ───────────────────────────────────────────────────────────
st.markdown(top_bar(), unsafe_allow_html=True)

# ── Hero Section ───────────────────────────────────────────────────────────────
st.markdown(
    hero_section(
        title="🇮🇳 Smart Bharat",
        subtitle="AI-Powered Civic Companion for Every Indian Citizen",
        tagline="✦  सेवा • सहायता • समाधान  ✦   Service  •  Assistance  •  Solutions",
    ),
    unsafe_allow_html=True,
)

# ── Stats bar ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
stats = [
    ("💬", "AI Chatbot", "English + Hindi"),
    ("🏛️", "10+ Schemes", "Personalised matching"),
    ("📣", "Grievance Portal", "File & track complaints"),
    ("📄", "8 Documents", "Simplified step-by-step"),
]
for col, (icon, title, sub) in zip([c1, c2, c3, c4], stats):
    with col:
        st.markdown(
            f"""
            <div style="background:#f7f9fc; border-radius:10px; padding:1rem;
                        text-align:center; border:1.5px solid #e8edf5;">
                <div style="font-size:1.8rem;">{icon}</div>
                <div style="font-weight:700; color:#1E3A5F; font-size:0.95rem;">{title}</div>
                <div style="font-size:0.8rem; color:#888;">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Section: Features ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; margin-bottom:0.3rem;">
        <span style="font-size:1.6rem; font-weight:800; color:#1E3A5F;">
            Our Features
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(tricolor_line(), unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        feature_card(
            icon="💬",
            title="AI Civic Chatbot",
            desc="Ask anything about government services, documents, rights, and civic issues — in English or Hindi. Powered by Google Gemini.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown('<a href="/AI_Chatbot" target="_self"><button style="width:100%;background:linear-gradient(90deg,#FF9933,#e8821a);color:white;border:none;border-radius:8px;padding:0.45rem 1rem;font-weight:700;font-size:0.95rem;cursor:pointer;">Open Chatbot →</button></a>', unsafe_allow_html=True)

with col2:
    st.markdown(
        feature_card(
            icon="🏛️",
            title="Government Scheme Finder",
            desc="Enter your profile details and instantly discover the government schemes you are eligible for — from health to housing.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown('<a href="/Scheme_Finder" target="_self"><button style="width:100%;background:linear-gradient(90deg,#FF9933,#e8821a);color:white;border:none;border-radius:8px;padding:0.45rem 1rem;font-weight:700;font-size:0.95rem;cursor:pointer;">Find Schemes →</button></a>', unsafe_allow_html=True)

with col3:
    st.markdown(
        feature_card(
            icon="📣",
            title="Grievance Portal",
            desc="Report civic issues like potholes, water supply failures, or power cuts. AI auto-categorizes and prioritizes your complaint.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown('<a href="/Grievance_Portal" target="_self"><button style="width:100%;background:linear-gradient(90deg,#FF9933,#e8821a);color:white;border:none;border-radius:8px;padding:0.45rem 1rem;font-weight:700;font-size:0.95rem;cursor:pointer;">File Complaint →</button></a>', unsafe_allow_html=True)

with col4:
    st.markdown(
        feature_card(
            icon="📄",
            title="Document Simplifier",
            desc="Confused by government document requirements? Get a simple, step-by-step guide in plain language for any official document.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown('<a href="/Document_Simplifier" target="_self"><button style="width:100%;background:linear-gradient(90deg,#FF9933,#e8821a);color:white;border:none;border-radius:8px;padding:0.45rem 1rem;font-weight:700;font-size:0.95rem;cursor:pointer;">Simplify Docs →</button></a>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section: How it works ─────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; margin-bottom:0.3rem;">
        <span style="font-size:1.4rem; font-weight:800; color:#1E3A5F;">
            How Smart Bharat Works
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(tricolor_line(), unsafe_allow_html=True)

h1, h2, h3 = st.columns(3)
steps = [
    ("1️⃣", "Choose a Service",
     "Select from AI Chatbot, Scheme Finder, Grievance Portal, or Document Simplifier from the navigation."),
    ("2️⃣", "Interact with Sahayak",
     "Our AI companion Sahayak, powered by Google Gemini, understands your query in English or Hindi."),
    ("3️⃣", "Get Instant Help",
     "Receive personalised recommendations, simplified explanations, or a complaint ID — instantly."),
]
for col, (num, title, desc) in zip([h1, h2, h3], steps):
    with col:
        st.markdown(
            f"""
            <div style="background:#fff; border-radius:12px; padding:1.4rem;
                        border:1.5px solid #e8edf5; text-align:center; min-height:160px;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">{num}</div>
                <div style="font-weight:700; color:#1E3A5F; font-size:1rem;
                            margin-bottom:0.4rem;">{title}</div>
                <div style="font-size:0.86rem; color:#57606a; line-height:1.5;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Section: About ────────────────────────────────────────────────────────────
with st.expander("📖 About Smart Bharat", expanded=False):
    st.markdown(
        """
        **Smart Bharat – AI-Powered Civic Companion** is a GenAI-powered web platform built to
        bridge the gap between Indian citizens and the complex world of government services.

        ### 🎯 Our Mission
        To promote **transparency, accessibility, and digital inclusion** by making everyday
        civic interactions faster, smarter, and more user-friendly for every Indian citizen —
        regardless of their language, education, or digital literacy.

        ### 🤖 AI Technology
        - **Google Gemini 1.5 Flash** — Fast, multilingual LLM powering all AI features
        - **Retrieval-Augmented Generation (RAG-lite)** — Scheme and document knowledge bases
          injected directly into prompts for grounded, accurate answers
        - **Structured Output** — Grievance classification returns clean JSON (category + priority)

        ### 🌐 Languages Supported
        - **English** — Full support across all features
        - **Hindi (हिंदी)** — Full support in chatbot and document simplifier

        ### 🏛️ Built for DEVENGERS PromptWars 2026
        This project was built as part of the **Smart Bharat** challenge — to demonstrate
        how Generative AI can solve real civic problems for 1.4 billion Indians.
        """,
        unsafe_allow_html=True,
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(footer(), unsafe_allow_html=True)
