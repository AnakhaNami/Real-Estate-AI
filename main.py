import sys
import os
from datetime import datetime

# ── Path setup — must be before any local imports ─────────────────────────────
ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

import streamlit as st

# ── Page config — must be FIRST streamlit call ────────────────────────────────
st.set_page_config(
    page_title="PropAssist — Kerala Real Estate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "user_id"      not in st.session_state: st.session_state.user_id      = None
if "user_name"    not in st.session_state: st.session_state.user_name    = "Guest"
if "active_tab"   not in st.session_state: st.session_state.active_tab   = "chat"
if "quick_prompt" not in st.session_state: st.session_state.quick_prompt = None

# ── Try importing backend ─────────────────────────────────────────────────────
BACKEND_OK    = False
BACKEND_ERROR = ""
try:
    from src.chatbot     import chat
    from src.firebase_db import (save_user, search_projects,
                                  search_builders, search_agents, init_db)
    init_db()
    BACKEND_OK = True
except Exception as e:
    BACKEND_ERROR = str(e)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
.main .block-container {
    background: #0d1117 !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #e6edf3 !important;
}

.main .block-container {
    padding: 0 2rem 2rem !important;
    max-width: 100% !important;
}

/* hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #010409 !important;
    border-right: 1px solid #21262d !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 2px; }

/* ── All text inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #c9a227 !important;
    box-shadow: 0 0 0 3px rgba(201,162,39,0.15) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}

/* ── All buttons default ── */
[data-testid="stButton"] > button {
    background: transparent !important;
    color: #8b949e !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
    text-align: left !important;
    padding: 8px 12px !important;
}
[data-testid="stButton"] > button:hover {
    background: #161b22 !important;
    color: #e6edf3 !important;
    border-color: #8b949e !important;
}

/* ── Primary buttons (save, search) ── */
button[kind="primary"],
[data-testid="stButton"] > button[kind="primary"] {
    background: #c9a227 !important;
    color: #0d1117 !important;
    border: none !important;
    font-weight: 600 !important;
}
button[kind="primary"]:hover {
    background: #e0b52e !important;
    box-shadow: 0 4px 20px rgba(201,162,39,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e6edf3 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] button {
    background: #c9a227 !important;
    border-radius: 8px !important;
    border: none !important;
    color: #0d1117 !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 14px 16px !important;
}
[data-testid="stMetricLabel"] p {
    color: #8b949e !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
[data-testid="stMetricValue"] {
    color: #c9a227 !important;
    font-size: 20px !important;
    font-weight: 600 !important;
}

/* ── Widget labels ── */
[data-testid="stWidgetLabel"] p,
label, .stSelectbox label {
    color: #8b949e !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* ── Divider ── */
hr { border-color: #21262d !important; margin: 16px 0 !important; }

/* ── Success / warning / error ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 13px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: #c9a227 !important; }

/* ── Section header style ── */
.section-header {
    padding: 28px 0 20px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 24px;
}
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: #e6edf3;
    letter-spacing: -0.3px;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 13px;
    color: #8b949e;
    font-weight: 300;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMPONENT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def user_bubble(content):
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;margin:10px 0">
      <div style="
        background:#1c2333;border:1px solid #30363d;
        border-radius:18px 18px 4px 18px;
        padding:12px 16px;max-width:72%;
        font-size:14px;line-height:1.65;
        color:#e6edf3;font-family:'DM Sans',sans-serif;">
        {content}
      </div>
    </div>""", unsafe_allow_html=True)


def ai_bubble(content, sources=None):
    sources = [str(s) for s in sources] if sources else []
    import re
    # Convert **bold** to <strong>
    content_html = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#e6edf3;font-weight:600">\1</strong>', content)
    # Convert *italic* to <em>
    content_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content_html)
    # Convert newlines to <br>
    content_html = content_html.replace("\n", "<br>")
    src_html = ""
    if sources:
        colors = {
            "PDF Knowledge Base": "#1d4ed8",
            "Project Database":   "#065f46",
            "Builder Database":   "#92400e",
            "Agent Database":     "#581c87",
            "Web Search":         "#7f1d1d",
        }
        for s in sources:
            bg = colors.get(s, "#21262d")
            src_html += (f'<span style="background:{bg};color:#e6edf3;'
                         f'font-size:10px;font-weight:500;padding:3px 8px;'
                         f'border-radius:4px;margin-right:4px;'
                         f'text-transform:uppercase;letter-spacing:0.3px">{s}</span>')

    st.markdown(f"""
    <div style="display:flex;gap:10px;margin:10px 0;align-items:flex-start">
      <div style="width:34px;height:34px;border-radius:9px;flex-shrink:0;
           background:linear-gradient(135deg,#c9a227 0%,#7c5c10 100%);
           display:flex;align-items:center;justify-content:center;
           font-size:16px;margin-top:2px;">🏠</div>
      <div style="flex:1">
        <div style="background:#161b22;border:1px solid #21262d;
             border-radius:4px 18px 18px 18px;padding:14px 18px;
             font-size:14px;line-height:1.75;color:#e6edf3;
             font-family:'DM Sans',sans-serif;max-width:82%;">
          {content_html}
        </div>
        {f'<div style="padding:6px 0 0 4px">{src_html}</div>' if src_html else ''}
      </div>
    </div>""", unsafe_allow_html=True)


def project_card(p):
    is_ready  = "Ready" in p.get("status", "")
    s_color   = "#3fb950" if is_ready else "#e3b341"
    s_bg      = "rgba(63,185,80,0.1)" if is_ready else "rgba(227,179,65,0.1)"
    min_p     = p.get("price_min_lakhs", "?")
    max_p     = p.get("price_max_lakhs", "?")
    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #21262d;border-radius:12px;
         padding:20px;margin-bottom:14px;transition:border-color .2s">
      <div style="display:flex;justify-content:space-between;
           align-items:flex-start;margin-bottom:14px">
        <div>
          <div style="font-family:'DM Serif Display',serif;font-size:18px;
               color:#e6edf3;margin-bottom:3px">{p.get("name","—")}</div>
          <div style="font-size:12px;color:#8b949e">
            {p.get("builder_name","—")} &nbsp;·&nbsp;
            {p.get("locality","")}, {p.get("city","")}
          </div>
        </div>
        <span style="background:{s_bg};color:{s_color};font-size:11px;
              font-weight:600;padding:4px 10px;border-radius:20px;
              border:1px solid {s_color};white-space:nowrap">
          {p.get("status","—")}
        </span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px">
        <div style="background:#0d1117;border-radius:8px;padding:12px">
          <div style="font-size:10px;color:#8b949e;margin-bottom:3px;
               text-transform:uppercase;letter-spacing:.5px">Price</div>
          <div style="font-size:15px;color:#c9a227;font-weight:600">
            ₹{min_p}–{max_p}L
          </div>
        </div>
        <div style="background:#0d1117;border-radius:8px;padding:12px">
          <div style="font-size:10px;color:#8b949e;margin-bottom:3px;
               text-transform:uppercase;letter-spacing:.5px">BHK</div>
          <div style="font-size:13px;color:#e6edf3;font-weight:500">
            {p.get("bhk_options","—")}
          </div>
        </div>
        <div style="background:#0d1117;border-radius:8px;padding:12px">
          <div style="font-size:10px;color:#8b949e;margin-bottom:3px;
               text-transform:uppercase;letter-spacing:.5px">Available</div>
          <div style="font-size:15px;color:#e6edf3;font-weight:600">
            {p.get("available_units","?")}
            <span style="color:#8b949e;font-size:11px">
              /{p.get("total_units","?")}
            </span>
          </div>
        </div>
      </div>
      <div style="font-size:12px;color:#8b949e;border-top:1px solid #21262d;
           padding-top:12px;display:flex;gap:20px;flex-wrap:wrap">
        <span>📅 Possession {p.get("possession_year","—")}</span>
        <span>📐 {p.get("area_sqft_min","?")}–{p.get("area_sqft_max","?")} sqft</span>
        <span style="color:#58a6ff">🔖 {p.get("rera_number","—")}</span>
      </div>
      <div style="font-size:12px;color:#6e7681;margin-top:10px;line-height:1.5">
        {p.get("description","")}
      </div>
    </div>""", unsafe_allow_html=True)


def builder_card(b):
    r      = b.get("rating", 0)
    filled = "★" * int(r)
    empty  = "☆" * (5 - int(r))
    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #21262d;border-radius:12px;
         padding:20px;margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;
           align-items:flex-start;margin-bottom:14px">
        <div>
          <div style="font-family:'DM Serif Display',serif;font-size:18px;
               color:#e6edf3;margin-bottom:3px">{b.get("name","—")}</div>
          <div style="font-size:12px;color:#8b949e">
            {b.get("city","")} &nbsp;·&nbsp; Est. {b.get("established","")}
          </div>
        </div>
        <div style="text-align:right">
          <div style="color:#c9a227;font-size:16px">{filled}<span style="color:#30363d">{empty}</span></div>
          <div style="font-size:11px;color:#8b949e">{r} / 5.0</div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px">
        <div style="background:#0d1117;border-radius:8px;padding:12px;text-align:center">
          <div style="font-size:22px;color:#c9a227;font-weight:700">{b.get("total_projects","—")}</div>
          <div style="font-size:10px;color:#8b949e">Total</div>
        </div>
        <div style="background:#0d1117;border-radius:8px;padding:12px;text-align:center">
          <div style="font-size:22px;color:#3fb950;font-weight:700">{b.get("completed","—")}</div>
          <div style="font-size:10px;color:#8b949e">Completed</div>
        </div>
        <div style="background:#0d1117;border-radius:8px;padding:12px;text-align:center">
          <div style="font-size:22px;color:#e3b341;font-weight:700">{b.get("ongoing","—")}</div>
          <div style="font-size:10px;color:#8b949e">Ongoing</div>
        </div>
      </div>
      <div style="font-size:12px;color:#8b949e;border-top:1px solid #21262d;padding-top:12px">
        <div style="margin-bottom:4px">🏗 {b.get("speciality","—")}</div>
        <div style="margin-bottom:4px">✉ {b.get("contact_email","—")}</div>
        <div>🌐 {b.get("website","—")}</div>
      </div>
      <div style="font-size:12px;color:#6e7681;margin-top:10px;line-height:1.5">
        {b.get("description","")}
      </div>
    </div>""", unsafe_allow_html=True)


def agent_card(a):
    r      = a.get("rating", 0)
    filled = "★" * int(r)
    empty  = "☆" * (5 - int(r))
    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #21262d;border-radius:12px;
         padding:20px;margin-bottom:14px">
      <div style="display:flex;justify-content:space-between;
           align-items:flex-start;margin-bottom:14px">
        <div>
          <div style="font-family:'DM Serif Display',serif;font-size:18px;
               color:#e6edf3;margin-bottom:3px">{a.get("name","—")}</div>
          <div style="font-size:12px;color:#8b949e">
            {a.get("city","")} &nbsp;·&nbsp; {a.get("locality","")}
          </div>
        </div>
        <div style="text-align:right">
          <div style="color:#c9a227;font-size:16px">{filled}<span style="color:#30363d">{empty}</span></div>
          <div style="font-size:11px;color:#8b949e">{r} / 5.0</div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
        <div style="background:#0d1117;border-radius:8px;padding:12px">
          <div style="font-size:10px;color:#8b949e;margin-bottom:3px;
               text-transform:uppercase;letter-spacing:.5px">Experience</div>
          <div style="font-size:15px;color:#e6edf3;font-weight:600">
            {a.get("experience_yrs","—")} yrs
          </div>
        </div>
        <div style="background:#0d1117;border-radius:8px;padding:12px">
          <div style="font-size:10px;color:#8b949e;margin-bottom:3px;
               text-transform:uppercase;letter-spacing:.5px">Deals Closed</div>
          <div style="font-size:15px;color:#c9a227;font-weight:600">
            {a.get("deals_closed","—")}
          </div>
        </div>
      </div>
      <div style="font-size:12px;color:#8b949e;border-top:1px solid #21262d;padding-top:12px">
        <div style="margin-bottom:4px">🗣 {a.get("languages","—")}</div>
        <div style="margin-bottom:4px">🎯 {a.get("speciality","—")}</div>
        <div style="color:#c9a227;font-weight:600;font-size:13px">
          📞 {a.get("phone","—")}
        </div>
      </div>
      <div style="font-size:12px;color:#6e7681;margin-top:10px;line-height:1.5">
        {a.get("description","")}
      </div>
    </div>""", unsafe_allow_html=True)


def section_header(title, subtitle=""):
    st.markdown(f"""
    <div style="padding:28px 0 20px;border-bottom:1px solid #21262d;margin-bottom:24px">
      <div style="font-family:'DM Serif Display',serif;font-size:28px;
           color:#e6edf3;letter-spacing:-0.3px;margin-bottom:4px">{title}</div>
      <div style="font-size:13px;color:#8b949e;font-weight:300">{subtitle}</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Logo ──
    st.markdown("""
    <div style="padding:28px 20px 16px">
      <div style="font-family:'DM Serif Display',serif;font-size:22px;
           color:#e6edf3;margin-bottom:2px">PropAssist</div>
      <div style="font-size:10px;color:#8b949e;letter-spacing:1.5px;
           text-transform:uppercase">Kerala Real Estate AI</div>
      <div style="width:28px;height:2px;background:#c9a227;
           margin-top:10px;border-radius:1px"></div>
    </div>""", unsafe_allow_html=True)

    # ── Backend status ──
    if BACKEND_OK:
        st.markdown('<div style="padding:0 20px 4px"><div style="background:rgba(63,185,80,0.1);'
                    'border:1px solid #238636;border-radius:6px;padding:6px 10px;'
                    'font-size:11px;color:#3fb950">● Backend connected</div></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="padding:0 20px 4px"><div style="background:rgba(248,81,73,0.1);'
                    f'border:1px solid #da3633;border-radius:6px;padding:6px 10px;'
                    f'font-size:11px;color:#f85149">● {BACKEND_ERROR[:60]}</div></div>',
                    unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#21262d;margin:16px 20px">', unsafe_allow_html=True)

    # ── Navigation ──
    st.markdown('<div style="padding:0 20px 8px;font-size:10px;color:#8b949e;'
                'text-transform:uppercase;letter-spacing:1px;font-weight:600">Navigate</div>',
                unsafe_allow_html=True)

    nav_items = [
        ("💬", "Chat",      "chat"),
        ("🏢", "Projects",  "projects"),
        ("🏗",  "Builders",  "builders"),
        ("👤", "Agents",    "agents"),
    ]

    for icon, label, key in nav_items:
        is_active = st.session_state.active_tab == key
        style = ("background:#1f2937;color:#e6edf3;border-color:#c9a227;"
                 if is_active else "")
        # Use columns trick for padding
        pad_l, btn_col, pad_r = st.columns([0.08, 0.84, 0.08])
        with btn_col:
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True):
                st.session_state.active_tab = key
                st.rerun()

    st.markdown('<hr style="border-color:#21262d;margin:16px 20px">', unsafe_allow_html=True)

    # ── User profile ──
    st.markdown('<div style="padding:0 20px 12px;font-size:10px;color:#8b949e;'
                'text-transform:uppercase;letter-spacing:1px;font-weight:600">Your Profile</div>',
                unsafe_allow_html=True)

    with st.container():
        p_l, p_m, p_r = st.columns([0.08, 0.84, 0.08])
        with p_m:
            name   = st.text_input("Name",   value="Rahul Menon",  key="inp_name")
            city   = st.selectbox("City",
                                  ["Kochi", "Kozhikode", "Thrissur",
                                   "Thiruvananthapuram", "Kannur"],
                                  key="inp_city")
            budget = st.number_input("Budget (₹ lakhs)",
                                     min_value=20.0, max_value=500.0,
                                     value=80.0, step=5.0, key="inp_budget")
            bhk    = st.selectbox("BHK needed", [1, 2, 3, 4],
                                  index=1, key="inp_bhk")

            if st.button("💾  Save Profile", key="save_profile",
                         use_container_width=True):
                if BACKEND_OK:
                    try:
                        uid = save_user(name, city, budget, bhk)
                        st.session_state.user_id   = uid
                        st.session_state.user_name = name
                        st.success("Profile saved!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.session_state.user_name = name
                    st.info("Saved locally (no backend)")

    st.markdown('<hr style="border-color:#21262d;margin:16px 20px">', unsafe_allow_html=True)

    # ── Quick prompts ──
    st.markdown('<div style="padding:0 20px 8px;font-size:10px;color:#8b949e;'
                'text-transform:uppercase;letter-spacing:1px;font-weight:600">Quick Questions</div>',
                unsafe_allow_html=True)

    quick_questions = [
        "Show 3BHK flats in Kochi under 100 lakhs",
        "Best rated builders in Kerala",
        "Find NRI specialist agents",
        "What docs to verify before buying?",
        "Ready to move projects in Thrissur",
        "Explain RERA registration",
        "Difference between carpet and built-up area",
        "Affordable flats in Kozhikode",
    ]

    q_l, q_m, q_r = st.columns([0.08, 0.84, 0.08])
    with q_m:
        for q in quick_questions:
            label = (q[:34] + "…") if len(q) > 34 else q
            if st.button(f"→ {label}", key=f"quick_{hash(q)}",
                         use_container_width=True):
                st.session_state.quick_prompt = q
                st.session_state.active_tab   = "chat"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT — switch on active_tab
# ══════════════════════════════════════════════════════════════════════════════
tab = st.session_state.active_tab

# ─────────────────────────────────────────────────────────────────────────────
# CHAT TAB
# ─────────────────────────────────────────────────────────────────────────────
if tab == "chat":

    hour = datetime.now().hour
    greet = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"

    st.markdown(f"""
    <div style="padding:28px 0 20px">
      <div style="font-family:'DM Serif Display',serif;font-size:30px;
           color:#e6edf3;margin-bottom:6px">
        Good {greet},&nbsp;
        <span style="color:#c9a227">{st.session_state.user_name}</span>
      </div>
      <div style="font-size:14px;color:#8b949e;font-weight:300">
        Ask anything about Kerala property — projects, builders, agents, legal guidance
      </div>
    </div>
    <hr style="border-color:#21262d;margin-bottom:20px">
    """, unsafe_allow_html=True)

    # Suggestion chips — only when no messages
    if not st.session_state.messages:
        st.markdown('<div style="margin-bottom:24px">'
                    '<div style="font-size:11px;color:#8b949e;margin-bottom:10px;'
                    'text-transform:uppercase;letter-spacing:.5px">Try asking</div>',
                    unsafe_allow_html=True)
        chips = [
            "What is the minimum budget for 2BHK in Kochi?",
            "Which builders have the best track record?",
            "Explain carpet area vs super built-up area",
            "What is an encumbrance certificate?",
        ]
        c1, c2 = st.columns(2)
        for i, chip in enumerate(chips):
            col = c1 if i % 2 == 0 else c2
            with col:
                if st.button(chip, key=f"chip_{i}", use_container_width=True):
                    st.session_state.quick_prompt = chip
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Render message history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            user_bubble(msg["content"])
        else:
            ai_bubble(msg["content"], msg.get("sources"))

    # Handle quick prompt from sidebar / chips
    user_input = None
    if st.session_state.quick_prompt:
        user_input = st.session_state.quick_prompt
        st.session_state.quick_prompt = None

    # Chat input box
    typed = st.chat_input("Ask about properties, builders, agents, or legal guidance…")
    if typed:
        user_input = typed

    # Process input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        user_bubble(user_input)

        with st.spinner("Searching…"):
            if BACKEND_OK:
                try:
                    answer, sources = chat(
                        user_input,
                        user_id=st.session_state.user_id
                    )
                except Exception as e:
                    answer  = f"Sorry, I hit an error: {e}"
                    sources = []
            else:
                answer  = f"⚠ Backend not connected — {BACKEND_ERROR}"
                sources = []

        st.session_state.messages.append({
            "role": "assistant", "content": answer, "sources": sources
        })
        ai_bubble(answer, sources)
        st.rerun()

    # Clear button
    if st.session_state.messages:
        st.markdown("<br>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([0.7, 0.2, 0.1])
        with btn_col:
            if st.button("Clear chat", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PROJECTS TAB
# ─────────────────────────────────────────────────────────────────────────────
elif tab == "projects":

    section_header(
        "Available Projects",
        "Live data from Firebase · Kerala residential projects"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        f_city   = st.selectbox("City",
                                ["All", "Kochi", "Kozhikode",
                                 "Thrissur", "Thiruvananthapuram"],
                                key="f_city")
    with c2:
        f_bhk    = st.selectbox("BHK type",
                                ["All", "1BHK", "2BHK", "3BHK", "4BHK"],
                                key="f_bhk")
    with c3:
        f_budget = st.number_input("Max budget (₹ L)",
                                   value=200.0, step=10.0, key="f_budget")
    with c4:
        f_status = st.selectbox("Status",
                                ["All", "Ready to move", "Under construction"],
                                key="f_status")

    st.markdown("<br>", unsafe_allow_html=True)
    _, search_col, _ = st.columns([0.01, 0.25, 0.74])
    with search_col:
        do_search = st.button("🔍  Search Projects",
                              key="search_proj", use_container_width=True)

    if do_search:
        if BACKEND_OK:
            with st.spinner("Fetching from Firebase…"):
                try:
                    projects = search_projects(
                        city       = None if f_city   == "All" else f_city,
                        bhk        = None if f_bhk    == "All" else f_bhk,
                        max_budget = f_budget,
                        status     = None if f_status == "All" else f_status,
                    )
                    if projects:
                        st.markdown("<br>", unsafe_allow_html=True)
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Found",          len(projects))
                        m2.metric("Lowest price",   f"₹{min(p.get('price_min_lakhs',0) for p in projects)}L")
                        m3.metric("Highest price",  f"₹{max(p.get('price_max_lakhs',0) for p in projects)}L")
                        m4.metric("Units available",sum(p.get('available_units',0) for p in projects))
                        st.markdown("<br>", unsafe_allow_html=True)
                        for p in projects:
                            project_card(p)
                    else:
                        st.info("No projects match your filters — try relaxing the criteria.")
                except Exception as e:
                    st.error(f"Firebase error: {e}")
        else:
            st.warning(f"Backend not connected: {BACKEND_ERROR}")
    else:
        st.markdown("""
        <div style="text-align:center;padding:70px 0;color:#8b949e">
          <div style="font-size:44px;margin-bottom:14px">🏢</div>
          <div style="font-size:15px;margin-bottom:6px;color:#e6edf3">
            Search Kerala properties
          </div>
          <div style="font-size:13px">
            Set your filters above and click Search Projects
          </div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# BUILDERS TAB
# ─────────────────────────────────────────────────────────────────────────────
elif tab == "builders":

    section_header(
        "Kerala Builders",
        "Verified developers with ratings, project history, and contact details"
    )

    c1, c2, _, load_col = st.columns([0.3, 0.3, 0.2, 0.2])
    with c1:
        b_city = st.selectbox("Filter by city",
                              ["All", "Kochi", "Kozhikode",
                               "Thrissur", "Thiruvananthapuram"],
                              key="b_city")
    with c2:
        b_name = st.text_input("Search by name",
                               placeholder="e.g. Sobha", key="b_name")
    with load_col:
        st.markdown("<br>", unsafe_allow_html=True)
        do_load = st.button("Load Builders",
                            key="load_builders", use_container_width=True)

    if do_load:
        if BACKEND_OK:
            with st.spinner("Fetching from Firebase…"):
                try:
                    builders = search_builders(
                        city = None if b_city == "All" else b_city,
                        name = b_name if b_name.strip() else None,
                    )
                    if builders:
                        st.markdown("<br>", unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Builders found",  len(builders))
                        avg_r = sum(b.get("rating",0) for b in builders) / len(builders)
                        m2.metric("Avg rating",      f"{avg_r:.1f} / 5")
                        m3.metric("Total projects",  sum(b.get("total_projects",0) for b in builders))
                        st.markdown("<br>", unsafe_allow_html=True)
                        for b in builders:
                            builder_card(b)
                    else:
                        st.info("No builders found for that filter.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning(f"Backend not connected: {BACKEND_ERROR}")
    else:
        st.markdown("""
        <div style="text-align:center;padding:70px 0;color:#8b949e">
          <div style="font-size:44px;margin-bottom:14px">🏗</div>
          <div style="font-size:15px;margin-bottom:6px;color:#e6edf3">
            Browse Kerala builders
          </div>
          <div style="font-size:13px">
            Select a city filter and click Load Builders
          </div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AGENTS TAB
# ─────────────────────────────────────────────────────────────────────────────
elif tab == "agents":

    section_header(
        "Verified Agents",
        "RERA-registered agents with ratings, experience, and direct contact numbers"
    )

    c1, c2, c3, load_col = st.columns([0.25, 0.25, 0.25, 0.25])
    with c1:
        a_city = st.selectbox("City",
                              ["All", "Kochi", "Kozhikode",
                               "Thrissur", "Thiruvananthapuram"],
                              key="a_city")
    with c2:
        a_spec = st.selectbox("Speciality",
                              ["All", "NRI", "First-time buyers",
                               "Luxury", "IT corridor", "Gulf NRI"],
                              key="a_spec")
    with c3:
        a_lang = st.selectbox("Language",
                              ["All", "Malayalam", "English",
                               "Hindi", "Arabic", "Tamil"],
                              key="a_lang")
    with load_col:
        st.markdown("<br>", unsafe_allow_html=True)
        do_find = st.button("Find Agents",
                            key="find_agents", use_container_width=True)

    if do_find:
        if BACKEND_OK:
            with st.spinner("Fetching from Firebase…"):
                try:
                    agents = search_agents(
                        city       = None if a_city == "All" else a_city,
                        speciality = None if a_spec == "All" else a_spec,
                        language   = None if a_lang == "All" else a_lang,
                    )
                    if agents:
                        st.markdown("<br>", unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Agents found",  len(agents))
                        avg_r = sum(a.get("rating",0) for a in agents) / len(agents)
                        m2.metric("Avg rating",    f"{avg_r:.1f} / 5")
                        m3.metric("Total deals",   sum(a.get("deals_closed",0) for a in agents))
                        st.markdown("<br>", unsafe_allow_html=True)
                        for a in agents:
                            agent_card(a)
                    else:
                        st.info("No agents match your filters.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning(f"Backend not connected: {BACKEND_ERROR}")
    else:
        st.markdown("""
        <div style="text-align:center;padding:70px 0;color:#8b949e">
          <div style="font-size:44px;margin-bottom:14px">👤</div>
          <div style="font-size:15px;margin-bottom:6px;color:#e6edf3">
            Find a trusted agent
          </div>
          <div style="font-size:13px">
            Filter by city, speciality, or language and click Find Agents
          </div>
        </div>""", unsafe_allow_html=True)