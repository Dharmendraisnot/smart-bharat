"""
pages/4_Document_Simplifier.py — Government Document Simplifier
Explains complex government document requirements in plain language using Gemini.
"""

import streamlit as st
from utils.styles import (
    GLOBAL_CSS, top_bar, page_title_bar, footer, tricolor_line, info_box,
)
from utils.gemini_client import simplify_document
from utils.scheme_utils import format_documents_context, get_document_names

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Document Simplifier – Smart Bharat",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "doc_result" not in st.session_state:
    st.session_state.doc_result = None

if "doc_query" not in st.session_state:
    st.session_state.doc_query = ""

if "doc_quick_select" not in st.session_state:
    st.session_state.doc_quick_select = ""

# ── Quick-select documents ─────────────────────────────────────────────────────
QUICK_DOCS = [
    ("🪪", "Aadhaar Card"),
    ("🍚", "Ration Card"),
    ("📜", "Caste Certificate"),
    ("💰", "Income Certificate"),
    ("🗳️", "Voter ID"),
    ("👶", "Birth Certificate"),
    ("🏠", "Domicile Certificate"),
    ("🚗", "Driving Licence"),
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:0.8rem 0 0.5rem 0;">
            <div style="font-size:2rem;">🇮🇳</div>
            <div style="font-size:1.1rem; font-weight:800; color:#1E3A5F;">Smart Bharat</div>
            <div style="font-size:0.75rem; color:#FF9933; font-weight:600;">AI Civic Companion</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 🧭 Navigate")
    st.markdown("""
<nav>
<a href="/"                    target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">🏠 Home</a>
<a href="/AI_Chatbot"          target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">💬 AI Civic Chatbot</a>
<a href="/Scheme_Finder"       target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">🏛️ Government Scheme Finder</a>
<a href="/Grievance_Portal"    target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">📣 Grievance Portal</a>
<a href="/Document_Simplifier" target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;font-weight:700;background:#f0f7ff;">📄 Document Simplifier</a>
</nav>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📄 Quick Select")
    for icon, doc_name in QUICK_DOCS:
        if st.button(f"{icon} {doc_name}", key=f"sidebar_{doc_name}", use_container_width=True):
            st.session_state.doc_quick_select = doc_name
            st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.78rem; color:#888; padding:0.4rem 0;">
            📂 Documents covered:<br>
            Aadhaar, Ration Card, PAN, Voter ID,
            Caste/Income/Domicile Certificate,
            Birth Certificate, Driving Licence,
            Passport, and more.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Top bar + Page header ──────────────────────────────────────────────────────
st.markdown(top_bar(), unsafe_allow_html=True)
st.markdown(
    page_title_bar(
        icon="📄",
        title="Document Simplifier",
        subtitle="Enter any government document name and Sahayak will explain the requirements and process in plain, simple language.",
    ),
    unsafe_allow_html=True,
)
st.markdown(tricolor_line(), unsafe_allow_html=True)

# ── Language toggle ────────────────────────────────────────────────────────────
lang_col, _ = st.columns([1, 3])
with lang_col:
    language = st.radio(
        "🌐 Output Language",
        options=["English", "हिंदी (Hindi)"],
        horizontal=True,
        key="doc_language",
    )
lang = "Hindi" if "हिंदी" in language else "English"

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick-select buttons ───────────────────────────────────────────────────────
st.markdown(
    """
    <div style="font-size:0.92rem; font-weight:700; color:#1E3A5F; margin-bottom:0.6rem;">
        ⚡ Common Documents — Quick Select
    </div>
    """,
    unsafe_allow_html=True,
)

# Render quick-select buttons in a row
btn_cols = st.columns(len(QUICK_DOCS))
for col, (icon, doc_name) in zip(btn_cols, QUICK_DOCS):
    with col:
        if st.button(
            f"{icon}\n{doc_name}",
            key=f"quick_{doc_name}",
            use_container_width=True,
        ):
            st.session_state.doc_quick_select = doc_name
            st.session_state.doc_result = None
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Main layout: input + output ────────────────────────────────────────────────
input_col, output_col = st.columns([1, 1.5], gap="large")

# ── Resolve query from quick-select or text input ─────────────────────────────
prefill_query = st.session_state.doc_quick_select or st.session_state.doc_query

with input_col:
    st.markdown(
        """
        <div style="font-size:1rem; font-weight:700; color:#1E3A5F; margin-bottom:0.6rem;">
            📝 Enter Document Query
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(key="doc_form"):
        doc_query = st.text_area(
            "Document name or paste text here",
            value=prefill_query,
            placeholder=(
                "Examples:\n"
                "• Ration Card\n"
                "• Caste Certificate\n"
                "• How to get an income certificate in Bihar?\n"
                "• Paste any confusing government document text here..."
            ),
            height=200,
            key="doc_text_area",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            simplify_btn = st.form_submit_button(
                "🔍 Simplify Document",
                use_container_width=True,
            )
        with col_b:
            clear_btn = st.form_submit_button(
                "🗑️ Clear",
                use_container_width=True,
            )

    if clear_btn:
        st.session_state.doc_result = None
        st.session_state.doc_query = ""
        st.session_state.doc_quick_select = ""
        st.rerun()

    if simplify_btn:
        if not doc_query.strip():
            st.error("Please enter a document name or paste document text.")
        else:
            st.session_state.doc_query = doc_query.strip()
            st.session_state.doc_quick_select = ""
            with st.spinner("📚 Sahayak is looking up the requirements..."):
                doc_context = format_documents_context()
                result = simplify_document(
                    user_query=doc_query.strip(),
                    doc_context=doc_context,
                    language=lang,
                )
            st.session_state.doc_result = result
            st.rerun()

    # ── Tips box ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        info_box(
            "You can type a document name like <strong>'Ration Card'</strong>, ask a specific question "
            "like <strong>'How to update Aadhaar address?'</strong>, or paste a confusing "
            "government notice to get a plain-language explanation."
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="background:#f0f7ff; border-radius:10px; padding:1rem;
                    border-left:4px solid #4285F4; font-size:0.82rem; color:#0d2137;
                    margin-top:0.8rem;">
            <strong>📱 DigiLocker Tip</strong><br>
            Did you know? You can store and share all your government documents
            digitally using the <strong>DigiLocker</strong> app (digilocker.gov.in).
            It's free and officially recognised by the Government of India.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Output panel ───────────────────────────────────────────────────────────────
with output_col:
    if st.session_state.doc_result:
        query_display = st.session_state.doc_query or "Document"

        st.markdown(
            f"""
            <div style="background:#f0fdf4; border-radius:12px; padding:0.8rem 1.2rem;
                        border-left:5px solid #138808; margin-bottom:1rem;">
                <div style="font-weight:700; color:#0a3622; font-size:0.9rem;">
                    📄 Simplified explanation for: <em>{query_display}</em>
                </div>
                <div style="font-size:0.78rem; color:#155724; margin-top:0.2rem;">
                    Language: {lang} &nbsp;|&nbsp; Powered by Google Gemini
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Render the markdown result in a styled container
        with st.container():
            st.markdown(
                '<div style="background:#fff; border-radius:12px; padding:1.4rem; '
                'border:1.5px solid #d0e4f7;">',
                unsafe_allow_html=True,
            )
            st.markdown(st.session_state.doc_result)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        dl_col, copy_col = st.columns(2)
        with dl_col:
            filename = query_display.replace(" ", "_").lower()[:30]
            st.download_button(
                label="⬇️ Download as Text",
                data=st.session_state.doc_result,
                file_name=f"smart_bharat_{filename}_guide.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with copy_col:
            if st.button("🔄 Ask Another Document", use_container_width=True):
                st.session_state.doc_result = None
                st.session_state.doc_query = ""
                st.session_state.doc_quick_select = ""
                st.rerun()

    else:
        # ── Empty state ────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="background:#f7f9fc; border-radius:14px; padding:3rem 2rem;
                        text-align:center; border:2px dashed #d0dae8; margin-top:1rem;">
                <div style="font-size:3rem; margin-bottom:1rem;">📄</div>
                <div style="font-size:1.1rem; font-weight:700; color:#1E3A5F;
                            margin-bottom:0.5rem;">
                    Select or type a document name
                </div>
                <div style="font-size:0.88rem; color:#888; line-height:1.7;">
                    Click any <strong>quick-select button</strong> above, or type
                    a document name in the input box and click
                    <strong>Simplify Document</strong>.<br><br>
                    Sahayak will explain what the document is, what you need,
                    and how to get it — in simple language.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Sample output preview ──────────────────────────────────────────────
        st.markdown(
            """
            <div style="background:#fff; border-radius:12px; padding:1.4rem;
                        border:1.5px solid #e8edf5;">
                <div style="font-weight:700; color:#1E3A5F; margin-bottom:0.6rem; font-size:0.9rem;">
                    👀 Sample Output Preview
                </div>
                <div style="font-size:0.84rem; color:#444; line-height:1.8;">
                    <strong style="color:#138808;">📄 What is this document?</strong><br>
                    A plain-language explanation of the document...<br><br>
                    <strong style="color:#138808;">📋 Documents Required</strong><br>
                    1. Aadhaar Card<br>
                    2. Proof of residence<br>
                    3. Passport-size photograph<br><br>
                    <strong style="color:#138808;">🔄 Step-by-Step Process</strong><br>
                    1. Visit your nearest government office<br>
                    2. Fill the application form<br>
                    3. Submit documents and receive acknowledgment<br><br>
                    <em style="color:#aaa; font-size:0.78rem;">
                        Real output generated by Google Gemini AI
                    </em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(footer(), unsafe_allow_html=True)
