"""
Question Generator Module
Creates personalized interview questions based on candidate profile
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_questions(profile, target_role):
    """
    Generate 20 personalized interview questions based on candidate profile.
    
    Args:
        profile (dict): Candidate profile from analyze_skills
        target_role (str): Target job role
    
    Returns:
        list: List of 20 interview questions
              (10 technical, 5 project-based, 5 scenario-based)
    """
    
    # Build context from profile
    candidate_skills = ", ".join(profile.get("skills", []))
    candidate_projects = ", ".join(profile.get("projects", []))
    missing_skills = ", ".join(profile.get("missing_skills", []))
    required_skills = ", ".join(profile.get("required_skills", []))
    
    # Create the prompt
    question_prompt = f"""You are an expert interviewer. Generate EXACTLY 20 interview questions for a candidate.

TARGET ROLE: {target_role}

CANDIDATE PROFILE:
- Candidate Skills: {candidate_skills if candidate_skills else "None"}
- Candidate Projects: {candidate_projects if candidate_projects else "None"}
- Missing Skills: {missing_skills if missing_skills else "None"}
- Role Requirements: {required_skills}

GENERATE EXACTLY:
- 10 TECHNICAL QUESTIONS (about {target_role} concepts)
- 5 PROJECT-BASED QUESTIONS (about their projects or approach)
- 5 SCENARIO-BASED QUESTIONS (situational/behavioral)

FORMAT:
Return ONLY the numbered questions (1-20), no headers, no explanations.
Example:
1. What is your experience with Python?
2. Explain how you approached your last project...
etc.

IMPORTANT: Return ONLY the 20 questions, nothing else."""
    
    try:
        # Call Groq API
        question_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": question_prompt
                }
            ]
        )
        
        # Extract questions from response
        questions_text = question_response.choices[0].message.content
        
        # Parse questions (split by newlines and filter empty)
        questions = [
            q.strip() 
            for q in questions_text.split("\n") 
            if q.strip()
        ]
        
        return questions
    
    except Exception as e:
        print(f"Warning: Error generating questions: {e}")
        # Fallback questions if API fails
        return [
            "1. Tell me about your experience with the required skills.",
            "2. Describe a project you worked on.",
            "3. What challenges did you face?",
            "4. How do you approach learning new technologies?",
            "5. Why are you interested in this role?",
            "6. What are your strengths?",
            "7. What are your weaknesses and how are you working on them?",
            "8. How do you stay updated with industry trends?",
            "9. Tell me about a time you failed and what you learned.",
            "10. How do you handle pressure and tight deadlines?"
        ]