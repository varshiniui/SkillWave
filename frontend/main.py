import streamlit as st
import requests
import io
import re
import plotly.graph_objects as go
from resume_parser import extract_resume_text

st.set_page_config(page_title="SkillWave", layout="wide", initial_sidebar_state="expanded")

# Enhanced Modern UI with Gradients and Glassmorphism
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Page Background */
    .stApp {
        background: linear-gradient(135deg, #16213e 0%, #25395c 50%, #146591 100%);
    }

    /* Default Streamlit header sits ABOVE .stApp's background and is white
       by default — this is the white strip at the top of the page.
       Make it transparent so the gradient shows through, and drop the
       colored decoration bar Streamlit renders just under it. */
    [data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Sidebar collapse/expand arrow — this is a known Streamlit issue
       (github.com/streamlit/streamlit/issues/11449): the button is
       fixed-position but sits BEHIND sidebar content because our custom
       sidebar styling (backdrop-filter, etc.) creates new stacking
       contexts with higher z-index. Force it above everything. */
    [data-testid="stSidebarHeader"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        opacity: 1 !important;
        visibility: visible !important;
        z-index: 999999 !important;
    }

    [data-testid="stSidebarCollapseButton"] button {
        z-index: 999999 !important;
        position: relative !important;
        background: rgba(15, 30, 58, 0.85) !important;
        border-radius: 50% !important;
    }

    /* The icon itself is a Material Symbols font glyph rendered as text,
       not an <svg> — color (not fill) is what actually controls it. */
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="collapsedControl"] * {
        color: #00bcd4 !important;
        fill: #00bcd4 !important;
        stroke: #00bcd4 !important;
        opacity: 1 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2744 0%, #0f1e3a 100%) !important;
        border-right: 1px solid rgba(0, 188, 212, 0.1) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 1.5rem;
    }
    
    /* Header Styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5em;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .sub-header {
        text-align: center;
        color: #9ca3af;
        font-size: 1.1em;
        font-weight: 400;
        margin-bottom: 32px;
        letter-spacing: 0.5px;
    }
    
    /* Section Headers */
    [data-testid="stMarkdownContainer"] h1, 
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Tabs Styling */
    [data-testid="stTabs"] {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 16px;
        padding: 2px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 188, 212, 0.1);
    }
    
    [data-testid="stTabs"] [role="tab"] {
        color: #d1d5db;
        font-weight: 500;
        font-size: 0.95rem;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
        color: white;
        box-shadow: 0 8px 16px rgba(0, 188, 212, 0.3);
    }
    
    [data-testid="stTabs"] [role="tab"]:hover {
        background: rgba(0, 188, 212, 0.1);
        color: #00bcd4;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 76, 117, 0.3));
        border: 1px solid rgba(0, 188, 212, 0.2);
        border-radius: 16px;
        padding: 24px !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetric"]:hover {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 76, 117, 0.5));
        border-color: rgba(0, 188, 212, 0.4);
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(0, 188, 212, 0.2);
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #00bcd4;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.2em !important;
        font-weight: 700;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #9ca3af;
        font-weight: 500;
        font-size: 0.85rem !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 16px rgba(0, 188, 212, 0.3);
        letter-spacing: 0.3px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00acc1 0%, #0097a7 100%);
        box-shadow: 0 12px 32px rgba(0, 188, 212, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    input, select, textarea {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4), rgba(15, 76, 117, 0.2)) !important;
        border: 1px solid rgba(0, 188, 212, 0.2) !important;
        border-radius: 12px !important;
        color: #e5e7eb !important;
        font-size: 0.95rem;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
    }
    
    input:hover, select:hover, textarea:hover {
        border-color: rgba(0, 188, 212, 0.4) !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 76, 117, 0.3)) !important;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: rgba(0, 188, 212, 0.8) !important;
        box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.1);
    }

    /* Streamlit's selectbox/dropdown is a BaseWeb component, not a native
       <select> — the rules above never reach it, which is why it showed
       a plain grey box. Target it directly. */
    [data-baseweb="select"] > div {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 76, 117, 0.3)) !important;
        border: 1px solid rgba(0, 188, 212, 0.3) !important;
        border-radius: 12px !important;
        color: #e5e7eb !important;
    }

    [data-baseweb="select"] svg {
        fill: #00bcd4 !important;
    }

    [data-baseweb="popover"] li {
        background: #16213e !important;
        color: #e5e7eb !important;
    }

    [data-baseweb="popover"] li:hover {
        background: rgba(0, 188, 212, 0.15) !important;
    }
    
    /* Section Tags/Badges */
    .section-tag {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.15), rgba(0, 172, 193, 0.05));
        border-left: 3px solid #00bcd4;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.95em;
        color: #e5e7eb;
        border: 1px solid rgba(0, 188, 212, 0.2);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .section-tag:hover {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.25), rgba(0, 172, 193, 0.15));
        border-left-color: #00acc1;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 188, 212, 0.15);
    }
    
    /* Info/Warning/Success Boxes */
    [data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 76, 117, 0.2)) !important;
        border: 1px solid rgba(0, 188, 212, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Dividers */
    [data-testid="stHorizontalBlock"] hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 188, 212, 0.3), transparent);
        margin: 24px 0;
    }
    
    /* Text Styling */
    [data-testid="stMarkdownContainer"] p {
        color: #d1d5db;
        line-height: 1.6;
    }
    
    [data-testid="stMarkdownContainer"] a {
        color: #00bcd4;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    [data-testid="stMarkdownContainer"] a:hover {
        color: #00acc1;
        text-decoration: underline;
    }
    
    /* Expander */
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4), rgba(15, 76, 117, 0.2));
        border: 1px solid rgba(0, 188, 212, 0.15) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stExpander"]:hover {
        border-color: rgba(0, 188, 212, 0.3) !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 76, 117, 0.3));
    }
    
    /* File Uploader — note the correct testid is "stFileUploaderDropzone"
       (the previous selector had a typo and never matched anything,
       which is why this stayed plain white). */
    [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed rgba(0, 188, 212, 0.3) !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 76, 117, 0.3)) !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(0, 188, 212, 0.6) !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 76, 117, 0.4)) !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #d1d5db !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] svg {
        fill: #00bcd4 !important;
    }

    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.2), rgba(0, 172, 193, 0.1)) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(0, 188, 212, 0.4) !important;
        border-radius: 10px !important;
    }

    /* The "x" button to remove an uploaded file — needs its own rule,
       since it only inherited the generic button background above and
       the icon itself had no contrasting fill set. */
    [data-testid="stFileUploaderDeleteBtn"] {
        background: rgba(15, 30, 58, 0.9) !important;
        border: 1px solid rgba(0, 188, 212, 0.5) !important;
        border-radius: 50% !important;
    }

    [data-testid="stFileUploaderDeleteBtn"] * {
        color: #00bcd4 !important;
        fill: #00bcd4 !important;
        stroke: #00bcd4 !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploaderFile"] {
        color: #e5e7eb !important;
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: 10px !important;
    }
    
    /* Selectbox */
    [data-testid="stSelectbox"] {
        border-radius: 12px;
    }
    
    /* Caption and Labels */
    [data-testid="stMarkdownContainer"] .stCaption {
        color: #9ca3af !important;
    }
    
    /* Plotly Chart */
    [data-testid="stPlotlyChart"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4), rgba(15, 76, 117, 0.2));
        border: 1px solid rgba(0, 188, 212, 0.15);
        border-radius: 16px;
        padding: 8px;
        backdrop-filter: blur(10px);
        overflow: visible !important;
        display: flex !important;
        justify-content: center !important;
    }

    [data-testid="stPlotlyChart"] > div {
        overflow: visible !important;
    }
    
    /* Role Detection Card */
    .role-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5), rgba(15, 76, 117, 0.2)) !important;
        border: 2px solid rgba(0, 188, 212, 0.2) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .role-card:hover {
        border-color: rgba(0, 188, 212, 0.4) !important;
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 188, 212, 0.15) !important;
    }
    
    /* Sidebar Header */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
        color: #00bcd4;
        font-size: 1.3em;
        margin-bottom: 20px;
    }
    
    /* Remove default Streamlit spacing issues */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    /* Smooth transitions everywhere */
    * {
        transition: color 0.2s ease, background 0.2s ease, border-color 0.2s ease;
    }
    
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">SkillWave</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Resume Analyzer & Interview Preparation</div>', unsafe_allow_html=True)

API_URL = "https://skillwave-trnj.onrender.com"


def render_readiness_gauge(readiness):
    """Render readiness score as a circular gauge with enhanced styling."""
    if readiness >= 70:
        bar_color = "#00BCD4"
    elif readiness >= 40:
        bar_color = "#FF9800"
    else:
        bar_color = "#F44336"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness,
        number={'suffix': "%", 'font': {'size': 40, 'color': bar_color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "rgba(0, 188, 212, 0.3)"},
            'bar': {'color': bar_color},
            'bgcolor': "rgba(30, 41, 59, 0.3)",
            'borderwidth': 2,
            'bordercolor': bar_color,
            'steps': [
                {'range': [0, 40], 'color': 'rgba(244, 67, 54, 0.1)'},
                {'range': [40, 70], 'color': 'rgba(255, 152, 0, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(0, 188, 212, 0.1)'},
            ],
        },
    ))
    fig.update_layout(
        height=260,
        width=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "#e5e7eb", 'size': 12},
    )
    return fig


def is_resume_text_valid(text, min_words=30, min_alpha_ratio=0.35):
    """
    Heuristic check to catch scanned/image-based PDFs where text extraction
    returns empty, too short, or garbled (mostly non-alphabetic) content.
    Returns (is_valid, error_message).
    """
    if not text or not text.strip():
        return False, ("No text could be extracted from this PDF. It looks like a scanned "
                        "or image-based document. Please upload a PDF exported directly from "
                        "Word, Google Docs, or a similar tool, with selectable text.")

    words = text.split()
    if len(words) < min_words:
        return False, ("Very little readable text was found in this PDF. It may be a scanned "
                        "image rather than a text-based document. Please upload a PDF with "
                        "selectable text.")

    alpha_chars = len(re.findall(r"[A-Za-z]", text))
    total_chars = len(text.strip())
    alpha_ratio = alpha_chars / total_chars if total_chars else 0

    if alpha_ratio < min_alpha_ratio:
        return False, ("The extracted text looks garbled or mostly non-alphabetic. This usually "
                        "happens with scanned or image-based PDFs. Please upload a text-based PDF.")

    return True, ""


if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'structured_questions' not in st.session_state:
    st.session_state.structured_questions = None
if 'target_role' not in st.session_state:
    st.session_state.target_role = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'auto_detected' not in st.session_state:
    st.session_state.auto_detected = False
if 'suggested_roles' not in st.session_state:
    st.session_state.suggested_roles = None

# Sidebar
with st.sidebar:
    st.header("Resume Analysis")

    try:
        roles_response = requests.get(f"{API_URL}/roles", timeout=5)
        roles_response.raise_for_status()
        available_roles = roles_response.json().get("roles", [])
    except Exception as e:
        st.error(f"Cannot connect to backend. Ensure Flask server is running on {API_URL}")
        st.stop()

    AUTO_DETECT_OPTION = "Not sure — Auto-detect best-fit role"

    resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    role_options = [AUTO_DETECT_OPTION] + available_roles
    target_role_choice = st.selectbox("Select Target Role", role_options)
    st.divider()

    if st.button("Analyze Resume", use_container_width=True, type="primary"):
        if not resume_file:
            st.error("Please upload a resume PDF")
        else:
            with st.spinner("Analyzing resume..."):
                try:
                    resume_text = extract_resume_text(resume_file)

                    is_valid, validation_msg = is_resume_text_valid(resume_text)
                    if not is_valid:
                        st.error(validation_msg)
                        st.stop()

                    print(f"Extracted resume text length: {len(resume_text)}")

                    role_for_api = "" if target_role_choice == AUTO_DETECT_OPTION else target_role_choice

                    response = requests.post(
                        f"{API_URL}/analyze",
                        json={"resume_text": resume_text, "target_role": role_for_api},
                        timeout=60
                    )
                    response.raise_for_status()
                    st.session_state.profile = response.json()
                    st.session_state.resume_text = resume_text

                    resolved_role = st.session_state.profile.get("target_role") or role_for_api
                    st.session_state.target_role = resolved_role
                    st.session_state.auto_detected = st.session_state.profile.get("auto_detected", False)
                    st.session_state.suggested_roles = st.session_state.profile.get("suggested_roles")

                    questions_response = requests.post(
                        f"{API_URL}/questions",
                        json={"profile": st.session_state.profile, "target_role": resolved_role},
                        timeout=60
                    )
                    questions_response.raise_for_status()
                    q_data = questions_response.json()
                    st.session_state.questions = q_data.get("questions", [])
                    st.session_state.structured_questions = q_data.get("structured", {})

                    st.success("Analysis complete!")
                    st.rerun()

                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to backend at {API_URL}")
                except requests.exceptions.Timeout:
                    st.error("Request timeout. Backend took too long to respond.")
                except requests.exceptions.HTTPError as e:
                    try:
                        error_msg = e.response.json().get("error", str(e))
                    except:
                        error_msg = str(e)
                    st.error(f"Error: {error_msg}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")

# Main content
if st.session_state.profile:
    profile = st.session_state.profile
    questions = st.session_state.questions
    structured_questions = st.session_state.structured_questions or {}
    target_role = st.session_state.target_role

    st.markdown(f"#### Currently viewing analysis for: **{target_role}**")

    if st.session_state.auto_detected and st.session_state.suggested_roles:
        st.markdown("### Detected Best-Fit Roles")
        st.caption("Based on your resume profile, SkillWave identified these roles as the best fit. Click any to view detailed analysis.")

        suggestions = st.session_state.suggested_roles
        cols = st.columns(len(suggestions))
        for i, (col, sug) in enumerate(zip(cols, suggestions)):
            with col:
                is_active = sug["role"] == target_role
                accent = "#00BCD4" if is_active else "rgba(0, 188, 212, 0.3)"
                card_bg = "linear-gradient(135deg, rgba(0, 188, 212, 0.15), rgba(0, 172, 193, 0.05))" if is_active else "linear-gradient(135deg, rgba(30, 41, 59, 0.4), rgba(15, 76, 117, 0.2))"
                
                st.markdown(
                    f"""
                    <div style='
                        background: {card_bg};
                        border: 2px solid {accent};
                        border-radius: 16px;
                        padding: 20px;
                        text-align: center;
                        transition: all 0.3s ease;
                        backdrop-filter: blur(10px);
                    '>
                        <div style='font-weight: 700; font-size: 1.1em; color: #e5e7eb; margin-bottom: 12px;'>{sug['role']}</div>
                        <div style='font-size: 2.2em; color: {accent}; font-weight: 800; margin-bottom: 8px;'>{sug['readiness']}%</div>
                        <div style='font-size: 0.85em; color: #9ca3af;'>{sug['matched_count']}/{sug['total_count']} skills matched</div>
                        {f"<div style='font-size: 0.8em; color: #00BCD4; margin-top: 8px; font-weight: 600;'>Currently Selected</div>" if is_active else ""}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if not is_active:
                    if st.button(f"Switch to {sug['role']}", key=f"switch_role_{i}", use_container_width=True):
                        with st.spinner(f"Re-analyzing as {sug['role']}..."):
                            try:
                                resp = requests.post(
                                    f"{API_URL}/analyze",
                                    json={"resume_text": st.session_state.resume_text, "target_role": sug["role"]},
                                    timeout=60
                                )
                                resp.raise_for_status()
                                st.session_state.profile = resp.json()
                                st.session_state.target_role = sug["role"]

                                q_resp = requests.post(
                                    f"{API_URL}/questions",
                                    json={"profile": st.session_state.profile, "target_role": sug["role"]},
                                    timeout=60
                                )
                                q_resp.raise_for_status()
                                q_data = q_resp.json()
                                st.session_state.questions = q_data.get("questions", [])
                                st.session_state.structured_questions = q_data.get("structured", {})
                                st.rerun()
                            except Exception as e:
                                st.error(f"Could not switch role: {str(e)}")
        st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Skill Analysis", "Interview Questions", "Recommendations"])

    with tab1:
        st.subheader("Candidate Profile Summary")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Name**")
            st.markdown(f"### {profile.get('name', 'N/A')}")
        with col2:
            st.markdown("**Education**")
            st.markdown(f"#### {profile.get('education', 'N/A')}")
        with col3:
            st.markdown("**Readiness Score**")
            st.plotly_chart(
                render_readiness_gauge(profile.get('readiness', 0)),
                use_container_width=False,
                config={'displayModeBar': False}
            )

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Skills Found")
            skills = profile.get("skills", [])
            if skills:
                for skill in skills:
                    st.markdown(f'<div class="section-tag">{skill}</div>', unsafe_allow_html=True)
            else:
                st.info("No skills extracted")

        with col2:
            st.subheader("Projects")
            projects = profile.get("projects", [])
            if projects:
                for project in projects:
                    st.markdown(f'<div class="section-tag">{project}</div>', unsafe_allow_html=True)
            else:
                st.info("No projects found")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Internships")
            internships = profile.get("internships", [])
            if internships:
                for internship in internships:
                    st.markdown(f'<div class="section-tag">{internship}</div>', unsafe_allow_html=True)
            else:
                st.info("No internships found")

        with col2:
            st.subheader("Certifications")
            certifications = profile.get("certifications", [])
            if certifications:
                for cert in certifications:
                    st.markdown(f'<div class="section-tag">{cert}</div>', unsafe_allow_html=True)
            else:
                st.info("No certifications found")

        st.divider()

        st.subheader("Work Experience")
        experience = profile.get("experience", [])
        if experience:
            for exp in experience:
                st.markdown(f'<div class="section-tag">{exp}</div>', unsafe_allow_html=True)
        else:
            st.info("No full-time or freelance work experience found — common for students and entry-level candidates.")

    with tab2:
        st.subheader("Skill Gap Analysis")

        readiness = profile.get('readiness', 0)
        bar_color = "#00BCD4" if readiness >= 70 else "#FF9800" if readiness >= 40 else "#F44336"
        st.markdown(f"### Overall Readiness: **{readiness}%**")
        
        # Enhanced progress bar with gradient
        st.markdown(
            f"<div style='background:linear-gradient(90deg, rgba(30,41,59,0.5), rgba(15,76,117,0.3));border-radius:16px;height:32px;width:100%;overflow:hidden;border:1px solid rgba(0,188,212,0.2);'>"
            f"<div style='background:linear-gradient(90deg, {bar_color}, {bar_color}dd);width:{readiness}%;height:32px;border-radius:16px;"
            f"display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:14px;transition:width 0.5s ease;'>"
            f"{readiness}%</div></div>",
            unsafe_allow_html=True
        )
        st.write("")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Your Skills", len(profile.get("skills", [])))
            st.metric("Required Skills", len(profile.get("required_skills", [])))
        with col2:
            st.metric("Missing Skills", len(profile.get("missing_skills", [])))
            st.metric("Matched Skills", len(profile.get("matched_skills", [])))

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your Matched Skills")
            matched = profile.get("matched_skills", [])
            if matched:
                for skill in matched:
                    st.markdown(f'<div class="section-tag">✓ {skill}</div>', unsafe_allow_html=True)
            else:
                st.info("No matched skills")

        with col2:
            st.subheader("Skills to Develop")
            missing = profile.get("missing_skills", [])
            if missing:
                for skill in missing:
                    st.markdown(f'<div class="section-tag">⬆ {skill}</div>', unsafe_allow_html=True)
            else:
                st.success("You have all required skills!")

    with tab3:
        st.subheader("Personalized Interview Questions")

        tech_q = structured_questions.get("technical", [])
        proj_q = structured_questions.get("project", [])
        scene_q = structured_questions.get("scenario", [])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Questions", len(questions))
        col2.metric("Technical", len(tech_q))
        col3.metric("Project-Based", len(proj_q))
        col4.metric("Scenario", len(scene_q))
        st.divider()

        if structured_questions:
            qtab1, qtab2, qtab3 = st.tabs([
                f"Technical ({len(tech_q)})",
                f"Project-Based ({len(proj_q)})",
                f"Scenario-Based ({len(scene_q)})"
            ])

            with qtab1:
                st.markdown("*Questions focused on your technical skills, knowledge, and areas for growth.*")
                st.write("")
                for idx, q in enumerate(tech_q, 1):
                    st.markdown(f"**Q{idx}.** {q}")
                    st.divider()

            with qtab2:
                st.markdown("*Questions about your actual projects and hands-on experience.*")
                st.write("")
                for idx, q in enumerate(proj_q, 1):
                    st.markdown(f"**Q{idx}.** {q}")
                    st.divider()

            with qtab3:
                st.markdown("*Situational and behavioral questions to assess workplace approach.*")
                st.write("")
                for idx, q in enumerate(scene_q, 1):
                    st.markdown(f"**Q{idx}.** {q}")
                    st.divider()
        else:
            for idx, q in enumerate(questions, 1):
                st.markdown(f"**{idx}.** {q}")
                st.divider()

    with tab4:
        st.subheader("Learning Recommendations & Preparation Roadmap")

        recommendations = profile.get("learning_recommendations", [])
        roadmap = profile.get("preparation_roadmap", [])

        if recommendations:
            st.markdown("### Recommended Courses for Missing Skills")
            for rec in recommendations:
                if isinstance(rec, dict):
                    skill = rec.get("skill", "")
                    courses = rec.get("courses", [])
                    with st.expander(f"Learn {skill}", expanded=False):
                        for course in courses:
                            name = course.get("name", "")
                            platform = course.get("platform", "")
                            url = course.get("url", "")
                            duration = course.get("duration", "")
                            price = course.get("price", "")
                            price_label = "Free" if "Free" in price else "Paid"
                            price_color = "#10b981" if "Free" in price else "#f59e0b"
                            
                            st.markdown(
                                f"<div style='margin: 12px 0; padding: 12px; background: rgba(0,188,212,0.05); border-radius: 10px; border-left: 3px solid #00bcd4;'>"
                                f"<div style='font-weight: 600; color: #e5e7eb;'>"
                            )
                            if url:
                                st.markdown(f"[{name}]({url})")
                            else:
                                st.markdown(name)
                            
                            st.markdown(
                                f"<div style='font-size: 0.9em; color: #9ca3af; margin-top: 6px;'>"
                                f"{platform} &nbsp;|&nbsp; {duration} &nbsp;|&nbsp; "
                                f"<span style='color: {price_color}; font-weight: 600;'>{price_label}</span>"
                                f"</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                else:
                    st.info(str(rec))
        else:
            st.success("You already have all the required skills!")

        st.divider()

        if roadmap:
            st.markdown("### Preparation Roadmap")
            for idx, step in enumerate(roadmap, 1):
                if isinstance(step, dict):
                    phase = step.get("phase", f"Phase {idx}")
                    focus = step.get("focus", "")
                    skills_to_learn = step.get("skills_to_learn", step.get("skills", []))
                    
                    st.markdown(
                        f"<div style='background: linear-gradient(135deg, rgba(0,188,212,0.1), rgba(0,172,193,0.05)); border-left: 4px solid #00bcd4; border-radius: 12px; padding: 16px; margin: 12px 0;'>"
                        f"<div style='display: flex; align-items: center;'>"
                        f"<div style='background: linear-gradient(135deg, #00bcd4, #00acc1); color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 16px; flex-shrink: 0;'>{idx}</div>"
                        f"<div>"
                        f"<div style='font-weight: 700; color: #e5e7eb; font-size: 1.05em;'>{phase}</div>"
                        f"<div style='color: #9ca3af; font-size: 0.9em; margin-top: 4px;'>{focus}</div>"
                        f"{'<div style=\"margin-top: 8px; font-size: 0.85em; color: #00bcd4;\">Skills to focus: ' + ', '.join([f'<span style=\"background: rgba(0,188,212,0.15); padding: 2px 8px; border-radius: 6px; margin-right: 4px;\">{s}</span>' for s in skills_to_learn]) + '</div>' if skills_to_learn else ''}"
                        f"</div>"
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
        else:
            st.info("No roadmap available")

    st.divider()
    st.subheader("Export Results")
    col1, col2 = st.columns(2)

    candidate_name = profile.get("name", "Candidate").replace(" ", "_")
    role_name = target_role.replace(" ", "_")
    pdf_filename = f"SkillWave_{candidate_name}_{role_name}.pdf"
    csv_filename = f"SkillWave_{candidate_name}_{role_name}.csv"

    with col1:
        if st.button("Download PDF Report", use_container_width=True):
            try:
                pdf_response = requests.post(
                    f"{API_URL}/export/pdf",
                    json={"profile": profile, "questions": questions, "target_role": target_role},
                    timeout=30
                )
                pdf_response.raise_for_status()
                st.download_button(
                    label="Download PDF",
                    data=pdf_response.content,
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

    with col2:
        if st.button("Download CSV Report", use_container_width=True):
            try:
                csv_response = requests.post(
                    f"{API_URL}/export/csv",
                    json={"profile": profile, "questions": questions, "target_role": target_role},
                    timeout=30
                )
                csv_response.raise_for_status()
                st.download_button(
                    label="Download CSV",
                    data=csv_response.content,
                    file_name=csv_filename,
                    mime="text/csv",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating CSV: {str(e)}")

else:
    st.info("Please upload a resume and click 'Analyze Resume' to get started.")