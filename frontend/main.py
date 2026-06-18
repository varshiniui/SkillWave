import streamlit as st
import requests
import io
import re
import plotly.graph_objects as go
from resume_parser import extract_resume_text

st.set_page_config(page_title="SkillWave", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #00BCD4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .section-tag {
        background-color: #e8f4fd;
        border-left: 4px solid #00BCD4;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 4px;
        font-size: 0.95em;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">SkillWave</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Resume Analyzer & Interview Preparation</div>', unsafe_allow_html=True)

API_URL = "https://skillwave-trnj.onrender.com"


def render_readiness_gauge(readiness):
    """Render readiness score as a circular gauge instead of a plain number metric."""
    if readiness >= 70:
        bar_color = "#00BCD4"
    elif readiness >= 40:
        bar_color = "#FF9800"
    else:
        bar_color = "#F44336"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness,
        number={'suffix': "%", 'font': {'size': 32}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#999999"},
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': '#fdecea'},
                {'range': [40, 70], 'color': '#fff3e0'},
                {'range': [70, 100], 'color': '#e0f7fa'},
            ],
        },
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#333333", 'family': "Arial"}
    )
    return fig


def is_resume_text_valid(text, min_words=30, min_alpha_ratio=0.35):
    """
    Heuristic check to catch scanned/image-based PDFs where text extraction
    returns empty, too short, or garbled (mostly non-alphabetic) content.
    Returns (is_valid, error_message).
    
    min_alpha_ratio=0.35 allows formatted resumes with tables, symbols, and special characters.
    Still catches truly scanned/image PDFs which typically have much lower ratios (<0.20).
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

                    # Empty string tells the backend to auto-detect the best role
                    role_for_api = "" if target_role_choice == AUTO_DETECT_OPTION else target_role_choice

                    response = requests.post(
                        f"{API_URL}/analyze",
                        json={"resume_text": resume_text, "target_role": role_for_api},
                        timeout=60
                    )
                    response.raise_for_status()
                    st.session_state.profile = response.json()
                    st.session_state.resume_text = resume_text

                    # Backend returns the role it actually used (auto-detected or chosen)
                    resolved_role = st.session_state.profile.get("target_role") or role_for_api
                    st.session_state.target_role = resolved_role

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

    if profile.get("auto_detected") and profile.get("suggested_roles"):
        st.markdown("### 🎯 Role Detected from Resume")
        st.caption("No target role was specified, so SkillWave identified the best-fitting roles for this candidate. The report below is based on the top match.")

        suggestions = profile["suggested_roles"]
        cols = st.columns(len(suggestions))
        for i, (col, sug) in enumerate(zip(cols, suggestions)):
            with col:
                is_active = sug["role"] == target_role
                accent = "#00BCD4" if is_active else "#cccccc"
                st.markdown(
                    f"<div style='border:2px solid {accent};border-radius:10px;padding:14px;text-align:center;'>"
                    f"<div style='font-weight:bold;font-size:1.05em;'>{sug['role']}</div>"
                    f"<div style='font-size:1.8em;color:{accent};font-weight:bold;'>{sug['readiness']}%</div>"
                    f"<div style='font-size:0.85em;color:#666;'>{sug['matched_count']}/{sug['total_count']} skills matched</div>"
                    + ("<div style='font-size:0.8em;color:#00BCD4;margin-top:4px;'>★ Shown below</div>" if is_active else "")
                    + "</div>",
                    unsafe_allow_html=True
                )
                if not is_active:
                    if st.button(f"View as {sug['role']}", key=f"switch_role_{i}", use_container_width=True):
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
                use_container_width=True,
                config={'displayModeBar': False}
            )

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Skills Found")
            skills = profile.get("skills", [])
            if skills:
                for skill in skills:
                    st.write(f"• {skill}")
            else:
                st.info("No skills extracted")

        with col2:
            st.subheader("Projects")
            projects = profile.get("projects", [])
            if projects:
                for project in projects:
                    st.write(f"• {project}")
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
        st.markdown(
            f"<div style='background:#e0e0e0;border-radius:10px;height:24px;width:100%;'>"
            f"<div style='background:{bar_color};width:{readiness}%;height:24px;border-radius:10px;"
            f"display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:13px;'>"
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
                    st.write(f"✓ {skill}")
            else:
                st.info("No matched skills")

        with col2:
            st.subheader("Skills to Develop")
            missing = profile.get("missing_skills", [])
            if missing:
                for skill in missing:
                    st.write(f"⚠ {skill}")
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
                st.markdown("*Questions based on your technical skills and knowledge gaps.*")
                st.write("")
                for idx, q in enumerate(tech_q, 1):
                    st.markdown(f"**Q{idx}.** {q}")
                    st.divider()

            with qtab2:
                st.markdown("*Questions based on your actual projects and work experience.*")
                st.write("")
                for idx, q in enumerate(proj_q, 1):
                    st.markdown(f"**Q{idx}.** {q}")
                    st.divider()

            with qtab3:
                st.markdown("*Situational questions to test how you handle real workplace scenarios.*")
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
                    with st.expander(f"{skill}", expanded=True):
                        for course in courses:
                            name = course.get("name", "")
                            platform = course.get("platform", "")
                            url = course.get("url", "")
                            duration = course.get("duration", "")
                            price = course.get("price", "")
                            price_label = "FREE" if "Free" in price else "PAID"
                            if url:
                                st.markdown(
                                    f"**[{name}]({url})**  \n"
                                    f"&nbsp;&nbsp;&nbsp;{platform} &nbsp;|&nbsp; {duration} &nbsp;|&nbsp; {price_label}"
                                )
                            else:
                                st.markdown(f"**{name}** — {platform} | {duration} | {price_label}")
                            st.write("")
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
                    col_num, col_content = st.columns([0.08, 0.92])
                    with col_num:
                        st.markdown(
                            f"<div style='background:#00BCD4;color:white;border-radius:50%;"
                            f"width:36px;height:36px;display:flex;align-items:center;"
                            f"justify-content:center;font-weight:bold;'>{idx}</div>",
                            unsafe_allow_html=True
                        )
                    with col_content:
                        st.markdown(f"**{phase}**")
                        if focus:
                            st.markdown(f"_{focus}_")
                        if skills_to_learn:
                            st.markdown("Skills to focus on: " + " ".join([f"`{s}`" for s in skills_to_learn]))
                    st.write("")
        else:
            st.info("No roadmap available")

    st.divider()
    st.subheader("Export Results")
    col1, col2 = st.columns(2)

    # Generate custom PDF filename
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
                    label="Click to download PDF",
                    data=pdf_response.content,
                    file_name=pdf_filename,
                    mime="application/pdf"
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
                    label="Click to download CSV",
                    data=csv_response.content,
                    file_name=csv_filename,
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error generating CSV: {str(e)}")

else:
    st.info("Please upload a resume and click 'Analyze Resume' to get started.")