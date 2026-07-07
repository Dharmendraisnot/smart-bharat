"""
utils/styles.py
Reusable CSS and HTML component helpers for Smart Bharat UI.
Indian flag colour palette:
  Saffron  #FF9933
  White    #FFFFFF
  Green    #138808
  Navy     #000080
  Accent   #1E3A5F  (deep blue)
"""

# ── Global CSS ─────────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Fonts & base ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
}

/* ── Hide Streamlit default chrome ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ── Top colour bar (saffron → green) ── */
.top-bar {
    height: 5px;
    background: linear-gradient(90deg, #FF9933 33%, #FFFFFF 33% 66%, #138808 66%);
    margin-bottom: 0.5rem;
}

/* ── Hero section ── */
.hero-section {
    background: linear-gradient(135deg, #1E3A5F 0%, #0d2137 100%);
    border-radius: 16px;
    padding: 3rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    border-top: 5px solid #FF9933;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #c9d8e8;
    margin: 0 0 0.25rem 0;
}
.hero-tagline {
    font-size: 0.95rem;
    color: #FF9933;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── Feature card ── */
.feature-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1.6rem 1.4rem;
    border: 1.5px solid #e8edf5;
    border-top: 4px solid #FF9933;
    min-height: 220px;
    transition: box-shadow 0.2s;
    text-align: center;
}
.feature-card:hover {
    box-shadow: 0 8px 24px rgba(30,58,95,0.12);
}
.feature-card .card-icon {
    font-size: 2.4rem;
    margin-bottom: 0.6rem;
}
.feature-card .card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1E3A5F;
    margin-bottom: 0.4rem;
}
.feature-card .card-desc {
    font-size: 0.88rem;
    color: #57606a;
    line-height: 1.5;
}

/* ── Section header ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.3rem;
}
.section-header h2 {
    font-size: 1.7rem;
    font-weight: 800;
    color: #1E3A5F;
    margin: 0;
}
.section-divider {
    height: 3px;
    background: linear-gradient(90deg, #FF9933, #138808);
    border-radius: 2px;
    margin-bottom: 1.5rem;
}

/* ── Page title bar ── */
.page-title-bar {
    background: linear-gradient(90deg, #1E3A5F, #2a4f7c);
    border-radius: 12px;
    padding: 1.2rem 1.8rem;
    margin-bottom: 1.5rem;
    border-left: 6px solid #FF9933;
}
.page-title-bar h1 {
    color: #FFFFFF;
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
}
.page-title-bar p {
    color: #c9d8e8;
    margin: 0.3rem 0 0 0;
    font-size: 0.92rem;
}

/* ── Scheme result card ── */
.scheme-card {
    background: #f8fbff;
    border-radius: 12px;
    padding: 1.3rem 1.4rem;
    border: 1.5px solid #d0e4f7;
    border-left: 5px solid #138808;
    margin-bottom: 1rem;
}
.scheme-card h3 {
    color: #1E3A5F;
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
}
.scheme-card p {
    color: #444;
    font-size: 0.88rem;
    margin: 0;
    line-height: 1.55;
}

/* ── Status badge ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.badge-pending    { background: #fff3cd; color: #856404; }
.badge-progress   { background: #cff4fc; color: #055160; }
.badge-resolved   { background: #d1e7dd; color: #0a3622; }

/* ── Info box ── */
.info-box {
    background: #f0f7ff;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    border-left: 4px solid #1E3A5F;
    font-size: 0.9rem;
    color: #1E3A5F;
    margin-bottom: 1rem;
}

/* ── Success box ── */
.success-box {
    background: #d4edda;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    border-left: 4px solid #138808;
    font-size: 0.92rem;
    color: #155724;
    margin-bottom: 1rem;
}

/* ── Complaint ID display ── */
.complaint-id-box {
    background: linear-gradient(135deg, #1E3A5F, #2a4f7c);
    border-radius: 12px;
    padding: 1.4rem 1.8rem;
    text-align: center;
    margin: 1rem 0;
}
.complaint-id-box .id-label {
    color: #c9d8e8;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.complaint-id-box .id-value {
    color: #FF9933;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 0.3rem 0;
}
.complaint-id-box .id-hint {
    color: #c9d8e8;
    font-size: 0.8rem;
}

/* ── Chat bubbles ── */
.chat-container {
    max-height: 480px;
    overflow-y: auto;
    padding: 0.5rem 0;
}
.chat-bubble-user {
    background: #1E3A5F;
    color: #FFFFFF;
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.1rem;
    margin: 0.5rem 0 0.5rem 15%;
    font-size: 0.92rem;
    line-height: 1.5;
}
.chat-bubble-bot {
    background: #f0f7ff;
    color: #1E3A5F;
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem;
    margin: 0.5rem 15% 0.5rem 0;
    font-size: 0.92rem;
    line-height: 1.5;
    border: 1.5px solid #d0e4f7;
}
.chat-bubble-bot .bot-name {
    font-weight: 700;
    color: #FF9933;
    font-size: 0.78rem;
    margin-bottom: 0.3rem;
}

/* ── Quick action button strip ── */
.quick-btn-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
    border-top: 1.5px solid #e8edf5;
    margin-top: 3rem;
    color: #888;
    font-size: 0.82rem;
}
.footer span { color: #FF9933; font-weight: 600; }

/* ── Tricolor accent line ── */
.tricolor-line {
    height: 4px;
    background: linear-gradient(90deg, #FF9933 33%, #FFFFFF 33% 66%, #138808 66%);
    border-radius: 2px;
    margin: 0.5rem 0 1.5rem 0;
}

/* ── Form styling ── */
.stTextInput > label, .stSelectbox > label,
.stTextArea > label, .stSlider > label {
    font-weight: 600 !important;
    color: #1E3A5F !important;
}
.stButton > button {
    background: linear-gradient(90deg, #FF9933, #e8821a) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}
</style>
"""

# ── Component helpers ──────────────────────────────────────────────────────────

def top_bar() -> str:
    return '<div class="top-bar"></div>'


def hero_section(title: str, subtitle: str, tagline: str) -> str:
    return f"""
<div class="hero-section">
    <div class="hero-title">{title}</div>
    <div class="hero-subtitle">{subtitle}</div>
    <div class="hero-tagline">{tagline}</div>
</div>
"""


def feature_card(icon: str, title: str, desc: str) -> str:
    return f"""
<div class="feature-card">
    <div class="card-icon">{icon}</div>
    <div class="card-title">{title}</div>
    <div class="card-desc">{desc}</div>
</div>
"""


def page_title_bar(icon: str, title: str, subtitle: str) -> str:
    return f"""
<div class="page-title-bar">
    <h1>{icon} {title}</h1>
    <p>{subtitle}</p>
</div>
"""


def section_header(title: str) -> str:
    return f"""
<div class="section-header"><h2>{title}</h2></div>
<div class="section-divider"></div>
"""


def scheme_card(name: str, desc: str, benefits: str, apply_url: str = "#") -> str:
    return f"""
<div class="scheme-card">
    <h3>✅ {name}</h3>
    <p><strong>Why you qualify:</strong> {desc}</p>
    <p style="margin-top:0.4rem"><strong>Benefits:</strong> {benefits}</p>
    <p style="margin-top:0.4rem"><a href="{apply_url}" target="_blank"
       style="color:#138808;font-weight:600;font-size:0.85rem;">🔗 Apply Now →</a></p>
</div>
"""


def badge(status: str) -> str:
    mapping = {
        "Pending":     "badge-pending",
        "In Progress": "badge-progress",
        "Resolved":    "badge-resolved",
    }
    css_class = mapping.get(status, "badge-pending")
    return f'<span class="badge {css_class}">{status}</span>'


def complaint_id_box(complaint_id: str) -> str:
    return f"""
<div class="complaint-id-box">
    <div class="id-label">Your Complaint ID</div>
    <div class="id-value">{complaint_id}</div>
    <div class="id-hint">📋 Save this ID to track your complaint status</div>
</div>
"""


def info_box(text: str) -> str:
    return f'<div class="info-box">ℹ️ {text}</div>'


def success_box(text: str) -> str:
    return f'<div class="success-box">✅ {text}</div>'


def tricolor_line() -> str:
    return '<div class="tricolor-line"></div>'


def footer() -> str:
    return """
<div class="footer">
    🇮🇳 <span>Smart Bharat</span> — AI-Powered Civic Companion &nbsp;|&nbsp;
    Built with ❤️ for DEVENGERS PromptWars 2026 &nbsp;|&nbsp;
    Powered by <span>Google Gemini</span>
</div>
"""
