import streamlit as st
import requests
import PyPDF2
import io
import json

st.set_page_config(page_title="SkillWave", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">SkillWave</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Resume Analyzer & Interview Preparation</div>', unsafe_allow_html=True)

API_URL = "http://localhost:5000"

# Initialize session state
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None

# Sidebar
with st.sidebar:
    st.header("Resume Analysis")
    
    # Get available roles
    try:
        roles_response = requests.get(f"{API_URL}/roles", timeout=5)
        roles_response.raise_for_status()
        available_roles = roles_response.json().get("roles", [])
    except Exception as e:
        st.error(f"Cannot connect to backend. Make sure Flask server is running on {API_URL}")
        st.stop()
    
    # File upload
    resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    # Target role selection
    target_role = st.selectbox("Select Target Role", available_roles)
    
    st.divider()
    
    # Analyze button
    if st.button("Analyze Resume", use_container_width=True, type="primary"):
        if not resume_file:
            st.error("Please upload a resume PDF")
        elif not target_role:
            st.error("Please select a target role")
        else:
            with st.spinner("Analyzing resume..."):
                try:
                    # Extract text from PDF using pdfplumber
                    import pdfplumber
                    resume_text = ""
                    with pdfplumber.open(io.BytesIO(resume_file.read())) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                resume_text += page_text + "\n"
                    
                    st.session_state.resume_text = resume_text.strip()
                    
                    if len(st.session_state.resume_text) < 10:
                        st.error("Resume text is too short. Please ensure the PDF contains readable text.")
                        st.stop()
                    
                    # Analyze resume
                    response = requests.post(
                        f"{API_URL}/analyze",
                        json={
                            "resume_text": st.session_state.resume_text,
                            "target_role": target_role
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    st.session_state.profile = response.json()
                    
                    # Generate questions
                    questions_response = requests.post(
                        f"{API_URL}/questions",
                        json={
                            "profile": st.session_state.profile,
                            "target_role": target_role
                        },
                        timeout=30
                    )
                    questions_response.raise_for_status()
                    st.session_state.questions = questions_response.json().get("questions", [])
                    
                    st.success("Analysis complete!")
                    st.rerun()
                    
                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to backend at {API_URL}")
                except requests.exceptions.Timeout:
                    st.error("Request timeout. Backend took too long to respond.")
                except requests.exceptions.HTTPError as e:
                    error_msg = e.response.json().get("error", str(e))
                    st.error(f"Error: {error_msg}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")

# Main content area
if st.session_state.profile:
    profile = st.session_state.profile
    questions = st.session_state.questions
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Skill Analysis", "Interview Questions", "Recommendations"])
    
    with tab1:
        st.subheader("Candidate Profile Summary")
        
        # Display profile summary in premium custom-styled cards to prevent text truncation
        st.markdown(f"""
            <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; width: 100%;">
                <div style="flex: 1 1 250px; background-color: #f8f9fa; border: 1px solid #e9ecef; border-left: 5px solid #1f77b4; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 0.85em; color: #6c757d; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">Candidate Name</div>
                    <div style="font-size: 1.4em; font-weight: 700; color: #212529; margin-top: 6px; word-break: break-word;">{profile.get('name', 'N/A')}</div>
                </div>
                <div style="flex: 1.5 1 350px; background-color: #f8f9fa; border: 1px solid #e9ecef; border-left: 5px solid #2ca02c; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 0.85em; color: #6c757d; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">Education</div>
                    <div style="font-size: 1.3em; font-weight: 600; color: #212529; margin-top: 6px; word-break: break-word; line-height: 1.4;">{profile.get('education', 'N/A')}</div>
                </div>
                <div style="flex: 1 1 200px; background-color: #f8f9fa; border: 1px solid #e9ecef; border-left: 5px solid #ff7f0e; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div style="font-size: 0.85em; color: #6c757d; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">Readiness Score</div>
                    <div style="font-size: 2.2em; font-weight: 800; color: #ff7f0e; line-height: 1.1; margin-top: 2px;">{profile.get('readiness', 0)}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
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
            
            st.divider()
            st.subheader("Certifications")
            certs = profile.get("certifications", [])
            if certs:
                for cert in certs:
                    st.write(f"📜 {cert}")
            else:
                st.info("No certifications found")
        
        with col2:
            st.subheader("Projects")
            projects = profile.get("projects", [])
            if projects:
                for project in projects:
                    st.write(f"• {project}")
            else:
                st.info("No projects found")
                
            st.divider()
            st.subheader("Experience / Internships")
            experience = profile.get("experience", [])
            if experience:
                for exp in experience:
                    st.write(f"💼 {exp}")
            else:
                st.info("No work experience listed")
    
    with tab2:
        st.subheader("Skill Gap Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Your Skills", len(profile.get("skills", [])))
            st.metric("Required Skills", len(profile.get("required_skills", [])))
        
        with col2:
            st.metric("Missing Skills", len(profile.get("missing_skills", [])))
            st.metric("Readiness", f"{profile.get('readiness', 0)}%")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Extracted Skills")
            for skill in profile.get("skills", []):
                st.write(f"• {skill}")
        
        with col2:
            st.subheader("Matched Skills")
            matched_skills = profile.get("matched_skills", [])
            if matched_skills:
                for skill in matched_skills:
                    st.write(f"🟢 {skill}")
            else:
                st.info("No matching skills found")
        
        with col3:
            st.subheader("Skills You Need")
            for skill in profile.get("missing_skills", []):
                st.write(f"🔴 {skill}")
    
    with tab3:
        st.subheader("Personalized Interview Questions")

        import re

        # Helper: strip leading number/bullet from a question string
        def clean_question(q):
            q = re.sub(r"^\d+[\.\s\-]+", "", q).strip()
            q = re.sub(r"^[\-\*\s•]+", "", q).strip()
            return q

        cleaned = [clean_question(q) for q in questions if q.strip()]
        total = len(cleaned)

        st.info(f"Total Questions Generated: **{total}** — grouped into 5 categories below.")

        # Define 5 categories mapped to index slices (based on 30-question structure)
        categories = [
            ("🔧 Technical Questions",         "Tests depth of knowledge in role concepts and your matched skills.",      cleaned[0:10]),
            ("📁 Project-Based Questions",      "Questions about your actual projects by name.",                           cleaned[10:15]),
            ("💼 Experience-Based Questions",   "Questions about your internships and work experience.",                   cleaned[15:20]),
            ("📚 Missing Skill Questions",      "Explores your familiarity with skills you have yet to develop.",          cleaned[20:25]),
            ("🎯 Scenario / Behavioural",       "Real-world situational questions using STAR format.",                    cleaned[25:30]),
        ]

        global_idx = 1
        for cat_title, cat_desc, cat_questions in categories:
            if not cat_questions:
                continue
            with st.expander(f"{cat_title}  ({len(cat_questions)} questions)", expanded=False):
                st.caption(cat_desc)
                st.write("")
                for q in cat_questions:
                    st.markdown(
                        f"""<div style="padding: 10px 14px; margin-bottom: 8px; border-left: 4px solid #1f77b4;
                        background:#f8f9fa; border-radius: 4px; font-size: 0.97em; color: #212529;">
                        <b>{global_idx}.</b> {q}</div>""",
                        unsafe_allow_html=True
                    )
                    global_idx += 1
    
    with tab4:
        st.subheader("Learning Recommendations")
        recommendations = profile.get("learning_recommendations", [])
        roadmap = profile.get("preparation_roadmap", [])
        
        if recommendations:
            st.markdown("### Recommended Courses & Resources")
            for rec in recommendations:
                skill_name = rec.get("skill", "N/A")
                courses = rec.get("courses", [])
                
                st.markdown(f"#### 📚 {skill_name}")
                if courses:
                    for course in courses:
                        name = course.get("name", "N/A")
                        platform = course.get("platform", "N/A")
                        url = course.get("url", "#")
                        duration = course.get("duration", "N/A")
                        price = course.get("price", "N/A")
                        st.markdown(f"- **[{name}]({url})** on *{platform}* | ⏳ Duration: {duration} | 💰 Price: {price}")
                else:
                    # Provide a fallback search url if no predefined courses are found
                    search_query = f"{skill_name} course".replace(" ", "+")
                    coursera_url = f"https://www.coursera.org/search?query={search_query}"
                    udemy_url = f"https://www.udemy.com/courses/search/?q={search_query}"
                    youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
                    st.write("No specific courses in database. Try searching:")
                    st.markdown(f"- [Search on Coursera]({coursera_url}) | [Search on Udemy]({udemy_url}) | [Search on YouTube]({youtube_url})")
        else:
            st.info("No recommendations available")
        
        st.divider()
        
        if roadmap:
            st.markdown("### Preparation Roadmap")
            for idx, step in enumerate(roadmap, 1):
                phase = step.get("phase", f"Phase {idx}")
                skills_list = step.get("skills", [])
                skills = ", ".join(skills_list)
                resources = step.get("recommended_resources", [])
                
                with st.expander(f"📅 **{phase}**: Focus on {skills}", expanded=(idx == 1)):
                    st.markdown(f"**Skills to study:** {skills}")
                    if resources:
                        st.markdown("**Suggested Quick Resources:**")
                        for res in resources:
                            name = res.get("name", "N/A")
                            url = res.get("url", "#")
                            platform = res.get("platform", "N/A")
                            st.markdown(f"- **[{name}]({url})** on *{platform}*")
                    else:
                        st.write("Use the recommended search links under Courses for these skills.")
        else:
            st.info("No roadmap available")
    
    # Export section
    st.divider()
    st.subheader("Export Results")
    col1, col2, col3 = st.columns(3)
    
    # Generate PDF and CSV bytes
    try:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
        from report_generator import generate_pdf_report, generate_csv_report
        
        pdf_bytes = generate_pdf_report(profile, questions, target_role)
        csv_bytes = generate_csv_report(profile, questions, target_role)
    except Exception as e:
        st.error(f"Error loading report generators: {e}")
        pdf_bytes = None
        csv_bytes = None
        
    with col1:
        if pdf_bytes:
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"skillwave_report_{profile.get('name', 'candidate').replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
    with col2:
        if csv_bytes:
            st.download_button(
                label="📊 Download CSV Report",
                data=csv_bytes,
                file_name=f"skillwave_report_{profile.get('name', 'candidate').replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    with col3:
        json_str = json.dumps(profile, indent=2)
        st.download_button(
            label="⚙️ Download JSON Data",
            data=json_str,
            file_name="skillwave_analysis.json",
            mime="application/json",
            use_container_width=True
        )

else:
    st.info("Please upload a resume and click 'Analyze Resume' to get started.")