import streamlit as st
import requests
from resume_parser import extract_resume_text

st.set_page_config(page_title="SkillWave", layout="wide")
st.title("SkillWave")
st.markdown("#### AI Career Preparation and Skill Assessment")

roles = ["Data Analyst", "Python Developer", "ML Engineer", "UI/UX Designer", "DevOps Engineer"]

st.sidebar.header("Resume Analysis")
resume_file = st.sidebar.file_uploader("Upload resume (PDF)", type="pdf")
target_role = st.sidebar.selectbox("Target role", roles)

if resume_file and target_role:
    st.sidebar.info("Analyzing resume and generating recommendations...")

    resume_text = extract_resume_text(resume_file)

    evaluate_response = requests.post(
        "http://localhost:5000/analyze",
        json={"resume_text": resume_text, "target_role": target_role},
        timeout=30,
    )
    evaluate_response.raise_for_status()
    profile = evaluate_response.json()

    questions_response = requests.post(
        "http://localhost:5000/questions",
        json={"profile": profile, "target_role": target_role},
        timeout=30,
    )
    questions_response.raise_for_status()
    questions = questions_response.json().get("questions", [])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Candidate Profile")
        st.write(f"**Name:** {profile.get('name', 'N/A')}")
        st.write(f"**Skills:** {', '.join(profile.get('skills', []))}")

    with col2:
        st.subheader("Skill Assessment")
        st.metric("Readiness", f"{profile.get('readiness', 0)}%")
        st.write(f"**Missing skills:** {', '.join(profile.get('missing_skills', []))}")

    st.divider()
    st.subheader("Interview Questions")
    if questions:
        for index, question in enumerate(questions, start=1):
            st.write(f"{index}. {question}")
    else:
        st.write("No interview questions were generated for the selected role.")
else:
    st.info("Please upload a resume and select a target role to continue.")