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
    
    parse_prompt = f"""Extract information from this resume and return ONLY valid JSON (no extra text, no markdown):

Resume:
{resume_text}

Return this exact JSON structure with real values from the resume:
{{
    "name": "full name of the candidate",
    "skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "projects": ["project1", "project2", "project3"],
    "education": "highest qualification or degree",
    "certifications": ["certification1", "certification2"],
    "experience": ["experience1", "experience2"]
}}

RULES:
- Extract ALL technical skills (programming languages, tools, frameworks, databases, methodologies).
- For "name": Extract the candidate's exact name as listed at the top of the resume. Do NOT guess last names, middle names, or initials if they are not explicitly written. Do NOT use website URLs, social profiles, email addresses, or unrelated text.
- For "projects": Extract only personal, academic, or professional projects (e.g., "Restaurant Discovery Platform", "Sales Dashboard"). Do NOT extract company names, employer names, training institutes (e.g., "Zoro Tech", "Saiket Systems", "Besant Technologies", "Alric InfoTech"), personal portfolios, or links.
- For "education": Extract the candidate's highest educational degree/qualification in full (e.g., "Bachelor of Technology in Information Technology" or "B.Tech Information Technology"), including the field of study.
- For "certifications": Extract any certifications, courses completed, or training certificates listed in the resume (e.g. "UI/UX Design - Zoro Tech").
- For "experience": Extract work experience, internships, or job roles listed in the resume, including job title and company name (e.g. "UI/UX Design Intern at Zoro Tech").
- Return ONLY valid JSON, no markdown, no code blocks, no extra text."""
    
    resume_data = {
        "name": "Unknown",
        "skills": [],
        "projects": [],
        "education": "Not specified",
        "certifications": [],
        "experience": []
    }
    
    # Save raw resume text for debugging
    try:
        with open("debug_resume.txt", "w", encoding="utf-8") as f:
            f.write(resume_text)
    except Exception as e:
        print(f"Error writing debug_resume.txt: {e}")

    try:
        parse_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": parse_prompt
                }
            ]
        )
        
        # Extract JSON from response
        response_text = parse_response.choices[0].message.content.strip()
        
        # Save raw LLM response for debugging
        try:
            with open("debug_response.txt", "w", encoding="utf-8") as f:
                f.write(response_text)
        except Exception as e:
            print(f"Error writing debug_response.txt: {e}")
        
        # Clean response (remove markdown if present)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        response_text = response_text.strip()
        
        # Parse JSON
        resume_data = json.loads(response_text)
        
        # Normalize unicode replacement characters in JSON values
        def normalize_val(val):
            if isinstance(val, str):
                # Replace replacement characters or corrupted chars with standard dash
                return val.replace('\ufffd', '–')
            elif isinstance(val, list):
                return [normalize_val(x) for x in val]
            return val
            
        for k, v in list(resume_data.items()):
            resume_data[k] = normalize_val(v)
        
        # Basic validation
        if not isinstance(resume_data.get("skills"), list):
            resume_data["skills"] = []
        if not isinstance(resume_data.get("projects"), list):
            resume_data["projects"] = []
        if not resume_data.get("education"):
            resume_data["education"] = "Not specified"
        if not isinstance(resume_data.get("certifications"), list):
            resume_data["certifications"] = []
        if not isinstance(resume_data.get("experience"), list):
            resume_data["experience"] = []
        
        # Post-process and clean extracted fields
        import re
        
        def extract_name_from_text(text):
            # Heuristic: choose first non-empty line with 2-5 capitalized words (including initials)
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            for line in lines[:10]:
                # skip obvious headings
                if re.search(r"resume|curriculum vitae|contact|details|email|phone", line, re.I):
                    continue
                words = line.split()
                # allow single letter initials as capitalized words by using * instead of +
                if 1 < len(words) <= 5 and all(re.match(r"^[A-Z][a-zA-Z\-']*$", w) for w in words):
                    return line
            # fallback: look for 'Name: ' pattern
            m = re.search(r"Name[:\s]+([A-Z][\w\-\s]{2,50})", text)
            if m:
                return m.group(1).strip()
            return None
        
        # Clean name if AI returned generic value or name looks like URL/email
        ai_name = (resume_data.get("name") or "").strip()
        if not ai_name or ai_name.lower() in ("unknown", "candidate") or re.search(r"http|linkedin|github|@", ai_name, re.I):
            possible = extract_name_from_text(resume_text)
            if possible:
                resume_data["name"] = possible
            else:
                resume_data["name"] = ai_name or "Unknown"
        
        # Clean projects: remove links, profiles, and company-like names
        cleaned_projects = []
        company_keywords = (
            "ltd", "pvt", "inc", "systems", "technologies", "co.", "corporation", 
            "solutions", "services", "company", "institute", "academy", "university", 
            "college", "school"
        )
        url_keywords = (
            "http://", "https://", ".com", ".app", ".dev", ".net", ".org", ".io", 
            "vercel", "netlify", "github.io", "github", "linkedin", "behance", 
            "dribbble", "portfolio", "portfoilo"
        )
        for p in resume_data.get("projects", []):
            if not isinstance(p, str):
                continue
            item = p.strip()
            lower = item.lower()
            
            # Skip if it contains url/profile keywords
            if any(x in lower for x in url_keywords):
                continue
                
            # Skip if it matches company/organization patterns
            if any(r"\b" + re.escape(word) + r"\b" in lower for word in company_keywords):
                continue
                
            # remove 'project:' prefixes
            if ':' in item:
                part = item.split(':', 1)[-1].strip()
                part_lower = part.lower()
                if part and not any(x in part_lower for x in url_keywords) and not any(r"\b" + re.escape(word) + r"\b" in part_lower for word in company_keywords):
                    cleaned_projects.append(part)
            else:
                cleaned_projects.append(item)
        resume_data['projects'] = cleaned_projects
        
        # Normalize and deduplicate skills
        seen = set()
        normalized_skills = []
        for s in resume_data.get("skills", []):
            if not isinstance(s, str):
                continue
            key = s.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            normalized_skills.append(s.strip())
        resume_data["skills"] = normalized_skills
        
        print(f"Successfully parsed resume: {resume_data}")
        
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse AI response as JSON: {e}")
        print(f"Response was: {response_text[:200]}")
        
    except Exception as e:
        print(f"Error: Exception during resume parsing: {e}")
        import traceback
        traceback.print_exc()
    
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
    
    # Find matched and missing skills with substring / word boundary support
    matched_skills = []
    missing_skills = []
    for required_skill in required_skills:
        req_lower = required_skill.lower()
        is_matched = False
        for cand_skill in candidate_skills_lower:
            # Exact match
            if req_lower == cand_skill:
                is_matched = True
                break
            # Required skill is inside candidate skill (e.g. "css" in "tailwind css", "wireframing" in "figma wireframing")
            if req_lower in cand_skill:
                is_matched = True
                break
            # Candidate skill is inside required skill (e.g. "django" in "django/flask")
            if len(cand_skill) > 3 and cand_skill in req_lower:
                is_matched = True
                break
        if is_matched:
            matched_skills.append(required_skill)
        else:
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
        "certifications": resume_data.get("certifications", []),
        "experience": resume_data.get("experience", []),
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "readiness": readiness
    }
    
    return profile