"""
Skill Analyzer Module
Parses resume and identifies skill gaps for target roles
"""

import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_skills(resume_text, target_role):
    """
    Analyze candidate's resume and identify skill gaps.
    
    Args:
        resume_text (str): Candidate's resume content
        target_role (str): Target job role
    
    Returns:
        dict: Profile containing name, skills, projects, education, 
              required_skills, missing_skills, and readiness percentage
    """
    
    # ============================================
    # STEP 1: Parse Resume with Groq AI
    # ============================================
    
    parse_prompt = f"""Extract information from this resume and return ONLY valid JSON (no extra text):

Resume:
{resume_text}

Return this exact JSON structure:
{{
    "name": "candidate name",
    "skills": ["skill1", "skill2"],
    "projects": ["project1", "project2"],
    "education": "highest qualification"
}}

IMPORTANT: Return ONLY JSON, no markdown, no explanations."""
    
    resume_data = {
        "name": "Candidate",
        "skills": [],
        "projects": [],
        "education": "Not extracted"
    }
    
    try:
        parse_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": parse_prompt
                }
            ]
        )
        
        # Extract JSON from response
        response_text = parse_response.choices[0].message.content
        
        # Clean response (remove markdown if present)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        resume_data = json.loads(response_text)
        
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse AI response as JSON: {e}")
        # Use fallback data (already initialized above)
        
    except Exception as e:
        print(f"Warning: Error parsing resume with AI: {e}")
        # Use fallback data
    
    # ============================================
    # STEP 2: Load Role Requirements
    # ============================================
    
    try:
        with open("role_skills.json") as f:
            role_skills = json.load(f)
        
        required_skills = role_skills.get(target_role, [])
    except Exception as e:
        print(f"Warning: Could not load role_skills.json: {e}")
        required_skills = []
    
    # ============================================
    # STEP 3: Calculate Skill Gaps
    # ============================================
    
    # Normalize to lowercase for comparison
    candidate_skills_lower = [s.lower() for s in resume_data.get("skills", [])]
    
    # Find missing skills
    missing_skills = []
    for required_skill in required_skills:
        if required_skill.lower() not in candidate_skills_lower:
            missing_skills.append(required_skill)
    
    # Calculate readiness percentage
    if len(required_skills) > 0:
        readiness = int(((len(required_skills) - len(missing_skills)) / len(required_skills)) * 100)
    else:
        readiness = 0
    
    # ============================================
    # STEP 4: Return Complete Profile
    # ============================================
    
    profile = {
        "name": resume_data.get("name", "Candidate"),
        "skills": resume_data.get("skills", []),
        "projects": resume_data.get("projects", []),
        "education": resume_data.get("education", ""),
        "required_skills": required_skills,
        "missing_skills": missing_skills,
        "readiness": readiness
    }
    
    return profile