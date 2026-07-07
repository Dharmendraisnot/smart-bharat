"""
pages/3_Grievance_Portal.py — Civic Grievance Filing and Tracking Portal
AI auto-categorization and priority assignment with SQLite persistence.
"""

import re
import streamlit as st
from utils.styles import (
    GLOBAL_CSS, top_bar, page_title_bar, footer, tricolor_line,
    complaint_id_box, badge, success_box, info_box,
)
from utils.gemini_client import categorize_and_prioritize
from utils.db_utils import init_db, file_grievance, track_grievance

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grievance Portal – Smart Bharat",
    page_icon="📣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Init DB + session state ────────────────────────────────────────────────────
init_db()

if "last_complaint_id" not in st.session_state:
    st.session_state.last_complaint_id = None

if "grievance_submitted" not in st.session_state:
    st.session_state.grievance_submitted = False

if "track_result" not in st.session_state:
    st.session_state.track_result = None

if "track_not_found" not in st.session_state:
    st.session_state.track_not_found = False

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
<a href="/Grievance_Portal"    target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;font-weight:700;background:#f0f7ff;">📣 Grievance Portal</a>
<a href="/Document_Simplifier" target="_self" style="display:block;padding:0.35rem 0.5rem;border-radius:6px;color:#1E3A5F;text-decoration:none;font-size:0.92rem;">📄 Document Simplifier</a>
</nav>
""", unsafe_allow_html=True)
    st.markdown("---")

    # ── Complaint categories reference ─────────────────────────────────────────
    st.markdown(
        """
        <div style="background:#fff3cd; border-radius:10px; padding:0.8rem;
                    border-left:3px solid #856404; font-size:0.82rem; color:#533f03;">
            <strong>📋 Complaint Categories</strong><br><br>
            🛣️ Roads &amp; Infrastructure<br>
            💧 Water Supply<br>
            ⚡ Electricity<br>
            🗑️ Sanitation &amp; Waste<br>
            🚨 Public Safety<br>
            🏥 Healthcare<br>
            🎓 Education<br>
            📌 Other
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:0.78rem; color:#888; text-align:center;">
            Demo IDs for tracking:<br>
            <code>SB-20240115-DEMO</code><br>
            <code>SB-20240116-SAMP</code><br>
            <code>SB-20240110-TEST</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Top bar + Page header ──────────────────────────────────────────────────────
st.markdown(top_bar(), unsafe_allow_html=True)
st.markdown(
    page_title_bar(
        icon="📣",
        title="Grievance Portal",
        subtitle="Report civic issues and track your complaints. AI automatically categorizes and prioritizes every complaint.",
    ),
    unsafe_allow_html=True,
)
st.markdown(tricolor_line(), unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_file, tab_track = st.tabs(["📝  File a New Complaint", "🔍  Track Existing Complaint"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FILE A COMPLAINT
# ══════════════════════════════════════════════════════════════════════════════
with tab_file:
    st.markdown("<br>", unsafe_allow_html=True)

    # Show success state if just filed ─────────────────────────────────────────
    if st.session_state.grievance_submitted and st.session_state.last_complaint_id:
        cid = st.session_state.last_complaint_id
        st.markdown(complaint_id_box(cid), unsafe_allow_html=True)
        st.markdown(
            success_box(
                f"Your complaint has been filed successfully! "
                f"Reference ID: <strong>{cid}</strong>. "
                f"Use this ID to track your complaint status."
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            info_box(
                "Our team will review your complaint and update the status within 2–5 working days. "
                "You can track progress using the 'Track Complaint' tab."
            ),
            unsafe_allow_html=True,
        )
        if st.button("📝 File Another Complaint", use_container_width=False):
            st.session_state.grievance_submitted = False
            st.session_state.last_complaint_id = None
            st.rerun()
        st.stop()

    # ── Filing form ────────────────────────────────────────────────────────────
    left_col, right_col = st.columns([1.2, 1], gap="large")

    with left_col:
        st.markdown(
            """
            <div style="font-size:1rem; font-weight:700; color:#1E3A5F; margin-bottom:0.8rem;">
                📝 Complaint Details
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form(key="grievance_form"):
            # Personal info ────────────────────────────────────────────────────
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input(
                    "Full Name *",
                    placeholder="e.g. Ramesh Kumar",
                )
            with col_b:
                phone = st.text_input(
                    "Phone Number *",
                    placeholder="10-digit mobile number",
                    max_chars=10,
                )

            location = st.text_input(
                "Location / Area *",
                placeholder="e.g. Sector 12, Noida, Uttar Pradesh",
            )

            description = st.text_area(
                "Describe Your Complaint *",
                placeholder=(
                    "Describe the civic issue in detail. Include:\n"
                    "• What is the problem?\n"
                    "• Where exactly is it located?\n"
                    "• How long has it been an issue?\n"
                    "• How is it affecting citizens?"
                ),
                height=160,
                max_chars=1000,
            )

            char_count = len(description)
            st.caption(f"{'✅' if char_count >= 20 else '⚠️'} {char_count}/1000 characters "
                       f"{'(minimum 20 required)' if char_count < 20 else ''}")

            # Optional image note ──────────────────────────────────────────────
            st.markdown(
                """
                <div style="font-size:0.8rem; color:#888; margin-top:0.2rem;">
                    📸 Photo upload support coming soon
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "📣 Submit Complaint",
                use_container_width=True,
            )

        # ── Validation + submit ────────────────────────────────────────────────
        if submitted:
            errors = []
            if not name.strip():
                errors.append("Please enter your full name.")
            if not phone.strip() or not re.fullmatch(r"\d{10}", phone.strip()):
                errors.append("Please enter a valid 10-digit phone number.")
            if not location.strip():
                errors.append("Please enter the location of the issue.")
            if len(description.strip()) < 20:
                errors.append("Please describe the complaint in at least 20 characters.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                with st.spinner("🤖 Sahayak is analysing and categorizing your complaint..."):
                    classified = categorize_and_prioritize(description)

                category = classified.get("category", "Other")
                priority = classified.get("priority", "Medium")
                summary  = classified.get("summary", "")

                complaint_id = file_grievance(
                    name=name.strip(),
                    phone=phone.strip(),
                    description=description.strip(),
                    location=location.strip(),
                    category=category,
                    priority=priority,
                    summary=summary,
                )

                st.session_state.last_complaint_id = complaint_id
                st.session_state.grievance_submitted = True
                st.rerun()

    with right_col:
        st.markdown(
            """
            <div style="background:#f7f9fc; border-radius:14px; padding:1.4rem;
                        border:1.5px solid #e8edf5;">
                <div style="font-weight:700; color:#1E3A5F; font-size:0.95rem;
                            margin-bottom:0.8rem;">🤖 How AI Helps Your Complaint</div>
                <div style="font-size:0.85rem; color:#57606a; line-height:1.8;">
                    <strong style="color:#FF9933;">Step 1 — Auto-Categorisation</strong><br>
                    Sahayak reads your complaint and assigns it to the correct department
                    (Roads, Water, Electricity, etc.)<br><br>
                    <strong style="color:#FF9933;">Step 2 — Priority Assignment</strong><br>
                    Based on urgency and public impact, your complaint is assigned
                    <em>High</em>, <em>Medium</em>, or <em>Low</em> priority.<br><br>
                    <strong style="color:#FF9933;">Step 3 — Unique ID</strong><br>
                    A trackable complaint ID (e.g., <code>SB-20240120-AB3X</code>)
                    is instantly generated.<br><br>
                    <strong style="color:#FF9933;">Step 4 — Status Tracking</strong><br>
                    Use the Track tab to check Pending → In Progress → Resolved status.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background:#fff0f0; border-radius:10px; padding:1rem;
                        border-left:4px solid #c0392b; font-size:0.82rem; color:#7b2020;">
                <strong>⚠️ Important</strong><br>
                For emergencies (fire, medical, crime), please call:<br>
                🚒 Fire: <strong>101</strong><br>
                🚑 Ambulance: <strong>108</strong><br>
                🚔 Police: <strong>100</strong><br>
                📞 Emergency: <strong>112</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TRACK COMPLAINT
# ══════════════════════════════════════════════════════════════════════════════
with tab_track:
    st.markdown("<br>", unsafe_allow_html=True)

    track_left, track_right = st.columns([1, 1.4], gap="large")

    with track_left:
        st.markdown(
            """
            <div style="font-size:1rem; font-weight:700; color:#1E3A5F; margin-bottom:0.8rem;">
                🔍 Track Your Complaint
            </div>
            """,
            unsafe_allow_html=True,
        )

        complaint_id_input = st.text_input(
            "Enter Complaint ID",
            placeholder="e.g. SB-20240115-DEMO",
            help="The ID you received when you filed your complaint.",
        ).strip().upper()

        st.caption("💡 Demo IDs: SB-20240115-DEMO  |  SB-20240116-SAMP  |  SB-20240110-TEST")

        if st.button("🔍 Track Complaint", use_container_width=True, key="track_btn"):
            if not complaint_id_input:
                st.error("Please enter a complaint ID.")
            else:
                result = track_grievance(complaint_id_input)
                if result:
                    st.session_state.track_result = result
                    st.session_state.track_not_found = False
                else:
                    st.session_state.track_result = None
                    st.session_state.track_not_found = True
                st.rerun()

        # ── Pre-fill from last filed complaint ─────────────────────────────────
        if st.session_state.last_complaint_id:
            st.markdown(
                f"""
                <div style="margin-top:0.5rem; font-size:0.82rem; color:#555;">
                    ℹ️ Your last filed complaint:
                    <strong style="color:#FF9933;">{st.session_state.last_complaint_id}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with track_right:
        if st.session_state.track_result:
            g = st.session_state.track_result
            status = g.get("status", "Pending")
            priority = g.get("priority", "Medium")

            priority_color = {"High": "#c0392b", "Medium": "#e67e22", "Low": "#27ae60"}.get(priority, "#888")

            st.markdown(
                f"""
                <div style="background:#fff; border-radius:14px; padding:1.6rem;
                            border:1.5px solid #d0e4f7; border-top:5px solid #1E3A5F;">
                    <div style="font-weight:800; color:#1E3A5F; font-size:1.05rem;
                                margin-bottom:1rem;">
                        📋 Complaint Details
                    </div>

                    <table style="width:100%; border-collapse:collapse; font-size:0.88rem;">
                        <tr>
                            <td style="color:#888; padding:0.4rem 0; width:40%;">Complaint ID</td>
                            <td style="color:#FF9933; font-weight:700; font-size:1rem;">
                                {g.get('id', 'N/A')}
                            </td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0;">Status</td>
                            <td>{badge(status)}</td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0;">Category</td>
                            <td style="color:#1E3A5F; font-weight:600;">{g.get('category', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0;">Priority</td>
                            <td style="color:{priority_color}; font-weight:700;">{priority}</td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0;">Filed By</td>
                            <td style="color:#444;">{g.get('name', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0;">Location</td>
                            <td style="color:#444;">{g.get('location', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0; vertical-align:top;">Description</td>
                            <td style="color:#444; line-height:1.5;">{g.get('description', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0;">Filed On</td>
                            <td style="color:#666;">{g.get('created_at', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="color:#888; padding:0.4rem 0;">Last Updated</td>
                            <td style="color:#666;">{g.get('updated_at', 'N/A')}</td>
                        </tr>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Status progress bar ──────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            progress_map = {"Pending": 15, "In Progress": 55, "Resolved": 100}
            progress_val = progress_map.get(status, 15)
            st.markdown(f"**📊 Resolution Progress: {status}**")
            st.progress(progress_val / 100)

        elif st.session_state.track_not_found:
            st.markdown(
                """
                <div style="background:#fff0f0; border-radius:12px; padding:2rem;
                            text-align:center; border:1.5px solid #f5c6cb; margin-top:1rem;">
                    <div style="font-size:2rem; margin-bottom:0.5rem;">❌</div>
                    <div style="font-weight:700; color:#721c24; margin-bottom:0.4rem;">
                        Complaint Not Found
                    </div>
                    <div style="font-size:0.88rem; color:#856404;">
                        No complaint found with this ID.<br>
                        Please check the ID and try again.<br><br>
                        <strong>Demo IDs:</strong> SB-20240115-DEMO, SB-20240116-SAMP, SB-20240110-TEST
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # ── Empty track state ──────────────────────────────────────────────
            st.markdown(
                """
                <div style="background:#f7f9fc; border-radius:14px; padding:2.5rem 2rem;
                            text-align:center; border:2px dashed #d0dae8; margin-top:0.5rem;">
                    <div style="font-size:2.5rem; margin-bottom:0.8rem;">🔍</div>
                    <div style="font-size:1rem; font-weight:700; color:#1E3A5F; margin-bottom:0.4rem;">
                        Enter your Complaint ID
                    </div>
                    <div style="font-size:0.86rem; color:#888; line-height:1.6;">
                        Paste the ID you received when filing your complaint
                        (format: SB-YYYYMMDD-XXXX).<br><br>
                        Try demo ID: <strong>SB-20240115-DEMO</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(footer(), unsafe_allow_html=True)
