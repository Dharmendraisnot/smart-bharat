"""
pages/2_Scheme_Finder.py — Government Scheme Finder
AI-powered personalised eligibility matching for Indian government schemes.
"""

import streamlit as st
from utils.styles import (
    GLOBAL_CSS, top_bar, page_title_bar, footer, tricolor_line, info_box,
)
from utils.gemini_client import find_schemes_with_gemini
from utils.scheme_utils import (
    format_schemes_context, INDIAN_STATES, INCOME_RANGES, CATEGORIES, OCCUPATIONS,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scheme Finder – Smart Bharat",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "scheme_results" not in st.session_state:
    st.session_state.scheme_results = None

if "scheme_profile" not in st.session_state:
    st.session_state.scheme_profile = {}

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
    st.page_link("app.py",                            label="🏠 Home")
    st.page_link("pages/1_AI_Chatbot.py",             label="💬 AI Civic Chatbot")
    st.page_link("pages/2_Scheme_Finder.py",          label="🏛️ Government Scheme Finder")
    st.page_link("pages/3_Grievance_Portal.py",       label="📣 Grievance Portal")
    st.page_link("pages/4_Document_Simplifier.py",    label="📄 Document Simplifier")
    st.markdown("---")
    st.markdown(
        """
        <div style="background:#f0fdf4; border-radius:10px; padding:0.8rem;
                    border-left:3px solid #138808; font-size:0.82rem; color:#155724;">
            <strong>🏛️ Database</strong><br>
            10+ government schemes across categories:<br><br>
            🏠 Housing &nbsp;&nbsp; 🏥 Health<br>
            🌾 Agriculture &nbsp; 💼 Employment<br>
            👧 Women &amp; Child &nbsp; 🎓 Education<br>
            💰 Finance &nbsp;&nbsp;&nbsp; ⚡ Energy
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    if st.button("🔄 Reset Form", use_container_width=True):
        st.session_state.scheme_results = None
        st.session_state.scheme_profile = {}
        st.rerun()

# ── Top bar + Page header ──────────────────────────────────────────────────────
st.markdown(top_bar(), unsafe_allow_html=True)
st.markdown(
    page_title_bar(
        icon="🏛️",
        title="Government Scheme Finder",
        subtitle="Enter your profile to discover all government schemes you are eligible for — AI-powered personalised matching.",
    ),
    unsafe_allow_html=True,
)

# ── Language toggle ────────────────────────────────────────────────────────────
lang_col, _ = st.columns([1, 3])
with lang_col:
    language = st.radio(
        "🌐 Response Language",
        options=["English", "हिंदी (Hindi)"],
        horizontal=True,
        key="scheme_language",
    )
lang = "Hindi" if "हिंदी" in language else "English"

st.markdown(tricolor_line(), unsafe_allow_html=True)

# ── Layout: form on left, results on right ────────────────────────────────────
form_col, result_col = st.columns([1, 1.6], gap="large")

with form_col:
    st.markdown(
        """
        <div style="font-size:1.05rem; font-weight:700; color:#1E3A5F; margin-bottom:0.8rem;">
            👤 Your Profile
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(key="scheme_form"):
        name = st.text_input(
            "Full Name",
            placeholder="e.g. Ramesh Kumar",
            help="Your name (used only for personalisation)",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            age = st.slider("Age", min_value=1, max_value=100, value=30, step=1)
        with col_b:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        state = st.selectbox(
            "State / Union Territory",
            options=["Select your state…"] + INDIAN_STATES,
        )

        category = st.selectbox(
            "Social Category",
            options=CATEGORIES,
            help="General, OBC, SC, ST, or EWS",
        )

        annual_income = st.selectbox(
            "Annual Household Income",
            options=INCOME_RANGES,
        )

        occupation = st.selectbox(
            "Occupation Type",
            options=OCCUPATIONS,
        )

        col_c, col_d = st.columns(2)
        with col_c:
            has_land = st.checkbox("Owns agricultural land")
        with col_d:
            is_bpl = st.checkbox("BPL card holder")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "🔍 Find Eligible Schemes",
            use_container_width=True,
        )

    # ── Validation + AI call ───────────────────────────────────────────────────
    if submitted:
        errors = []
        if not name.strip():
            errors.append("Please enter your name.")
        if state == "Select your state…":
            errors.append("Please select your state.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            profile = {
                "name": name.strip(),
                "age": age,
                "gender": gender,
                "state": state,
                "category": category,
                "annual_income": annual_income,
                "occupation": occupation,
                "owns_agricultural_land": "Yes" if has_land else "No",
                "bpl_card_holder": "Yes" if is_bpl else "No",
            }
            st.session_state.scheme_profile = profile

            with st.spinner("🤖 Sahayak is analysing your eligibility..."):
                scheme_context = format_schemes_context()
                results = find_schemes_with_gemini(
                    user_profile=profile,
                    scheme_context=scheme_context,
                    language=lang,
                )
            st.session_state.scheme_results = results
            st.rerun()

# ── Results panel ──────────────────────────────────────────────────────────────
with result_col:
    if st.session_state.scheme_results is None:
        # ── Empty state ────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="background:#f7f9fc; border-radius:14px; padding:3rem 2rem;
                        text-align:center; border:2px dashed #d0dae8; margin-top:2.5rem;">
                <div style="font-size:3rem; margin-bottom:1rem;">🏛️</div>
                <div style="font-size:1.1rem; font-weight:700; color:#1E3A5F;
                            margin-bottom:0.5rem;">
                    Fill your profile to discover schemes
                </div>
                <div style="font-size:0.88rem; color:#888; line-height:1.6;">
                    Our AI will analyse your age, income, category, state, and occupation
                    to find the most relevant government schemes for you.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Sample scheme categories ───────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            info_box(
                "This tool covers schemes from PM Awas Yojana, Ayushman Bharat, PM Kisan, "
                "PM Mudra Yojana, PM Jan Dhan, Sukanya Samriddhi, PM Ujjwala, MGNREGS, "
                "Beti Bachao Beti Padhao, PM Scholarship, and more."
            ),
            unsafe_allow_html=True,
        )
    else:
        # ── Populated results ──────────────────────────────────────────────────
        profile = st.session_state.scheme_profile
        st.markdown(
            f"""
            <div style="background:#f0fdf4; border-radius:12px; padding:1rem 1.4rem;
                        border-left:5px solid #138808; margin-bottom:1.2rem;">
                <div style="font-weight:700; color:#0a3622; font-size:0.95rem;">
                    ✅ Eligibility results for <em>{profile.get('name', 'Citizen')}</em>
                </div>
                <div style="font-size:0.82rem; color:#155724; margin-top:0.3rem;">
                    Age: {profile.get('age')} &nbsp;|&nbsp;
                    State: {profile.get('state')} &nbsp;|&nbsp;
                    Category: {profile.get('category')} &nbsp;|&nbsp;
                    Income: {profile.get('annual_income')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(st.session_state.scheme_results)

        st.markdown("<br>", unsafe_allow_html=True)
        dl_col, reset_col = st.columns(2)
        with dl_col:
            st.download_button(
                label="⬇️ Download Results",
                data=st.session_state.scheme_results,
                file_name=f"scheme_recommendations_{profile.get('name', 'citizen').replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with reset_col:
            if st.button("🔄 Search Again", use_container_width=True, key="reset_from_results"):
                st.session_state.scheme_results = None
                st.session_state.scheme_profile = {}
                st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(footer(), unsafe_allow_html=True)
