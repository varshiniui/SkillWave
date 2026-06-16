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
                    # Extract text from PDF
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(resume_file.read()))
                    resume_text = ""
                    for page in pdf_reader.pages:
                        resume_text += page.extract_text() + "\n"
                    
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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Name", profile.get("name", "N/A"))
        with col2:
            st.metric("Education", profile.get("education", "N/A"))
        with col3:
            st.metric("Readiness Score", f"{profile.get('readiness', 0)}%")
        
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your Skills")
            for skill in profile.get("skills", []):
                st.write(f"• {skill}")
        
        with col2:
            st.subheader("Skills You Need")
            for skill in profile.get("missing_skills", []):
                st.write(f"• {skill}")
    
    with tab3:
        st.subheader("Personalized Interview Questions")
        st.info(f"Total Questions: {len(questions)}")
        
        for idx, question in enumerate(questions, 1):
            st.write(f"**{idx}. {question}**")
            st.divider()
    
    with tab4:
        st.subheader("Learning Recommendations")
        recommendations = profile.get("learning_recommendations", [])
        roadmap = profile.get("preparation_roadmap", [])
        
        if recommendations:
            st.markdown("### Recommended Courses & Resources")
            for rec in recommendations:
                st.info(rec)
        else:
            st.info("No recommendations available")
        
        if roadmap:
            st.markdown("### Preparation Roadmap")
            for idx, step in enumerate(roadmap, 1):
                st.write(f"**Step {idx}:** {step}")
        else:
            st.info("No roadmap available")
    
    # Export section
    st.divider()
    st.subheader("Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        json_str = json.dumps(profile, indent=2)
        st.download_button(
            label="Download as JSON",
            data=json_str,
            file_name="skillwave_analysis.json",
            mime="application/json"
        )
    
    with col2:
        st.info("Save your analysis for future reference")

else:
    st.info("Please upload a resume and click 'Analyze Resume' to get started.")