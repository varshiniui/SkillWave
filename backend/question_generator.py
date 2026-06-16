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
    Generate 30 personalized interview questions based on candidate profile.

    Args:
        profile (dict): Candidate profile from analyze_skills
        target_role (str): Target job role

    Returns:
        list: List of 30 interview questions split as:
              - 10 Technical (role concepts & matched skills)
              - 5  Project-based (about candidate's actual projects)
              - 5  Experience-based (about internships / work experience)
              - 5  Missing-skill-based (exploring gaps)
              - 5  Scenario / Behavioural
    """

    # Build rich context from profile
    candidate_skills   = ", ".join(profile.get("skills", [])) or "None"
    candidate_projects = ", ".join(profile.get("projects", [])) or "None"
    missing_skills     = ", ".join(profile.get("missing_skills", [])) or "None"
    required_skills    = ", ".join(profile.get("required_skills", [])) or "None"
    matched_skills     = ", ".join(profile.get("matched_skills", [])) or "None"
    experience         = ", ".join(profile.get("experience", [])) or "None"
    certifications     = ", ".join(profile.get("certifications", [])) or "None"
    candidate_name     = profile.get("name", "the candidate")

    question_prompt = f"""You are a senior technical interviewer conducting a real interview. Generate EXACTLY 30 highly personalised interview questions for {candidate_name} applying for the role of {target_role}.

CANDIDATE PROFILE:
- Matched / Known Skills  : {matched_skills}
- All Extracted Skills    : {candidate_skills}
- Projects                : {candidate_projects}
- Work Experience         : {experience}
- Certifications          : {certifications}
- Missing Skills          : {missing_skills}
- Role Requirements       : {required_skills}

GENERATE EXACTLY 30 QUESTIONS IN THIS ORDER (do NOT add category headers):

Questions 1-10  → TECHNICAL QUESTIONS
  - Test depth of knowledge in {target_role} concepts and the candidate's matched skills ({matched_skills}).
  - Be specific and progressively harder (mix beginner, intermediate, and advanced).

Questions 11-15 → PROJECT-BASED QUESTIONS
  - Reference the candidate's actual projects ({candidate_projects}) by name.
  - Ask about design decisions, challenges, tools used, and outcomes.

Questions 16-20 → EXPERIENCE-BASED QUESTIONS
  - Reference the candidate's internships/experience ({experience}) by company and role.
  - Ask about real tasks, learnings, and contributions at those companies.

Questions 21-25 → MISSING SKILL QUESTIONS
  - Gently probe the candidate's familiarity with their missing skills ({missing_skills}).
  - Ask if they have worked with these tools, how they plan to learn them, and their exposure level.

Questions 26-30 → SCENARIO / BEHAVIOURAL QUESTIONS
  - Present real-world situations a {target_role} would face.
  - Use STAR format triggers (Situation, Task, Action, Result).

FORMAT:
- Return ONLY numbered questions 1-30, one per line.
- No category headers, no explanations, no markdown, no extra text.
- Example format:
  1. Question here.
  2. Question here.
"""

    try:
        question_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=3000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": question_prompt
                }
            ]
        )

        questions_text = question_response.choices[0].message.content

        # Parse: split by newlines, keep only non-empty lines
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
            "3. What challenges did you face in your projects?",
            "4. How do you approach learning new technologies?",
            "5. Why are you interested in this role?",
            "6. What are your technical strengths?",
            "7. What are your weaknesses and how are you working on them?",
            "8. How do you stay updated with industry trends?",
            "9. Tell me about a time you failed and what you learned.",
            "10. How do you handle pressure and tight deadlines?",
            "11. Describe the most complex project you have built.",
            "12. What tools did you use in your internship?",
            "13. How do you ensure code/design quality in your work?",
            "14. Tell me about a time you had to learn something quickly.",
            "15. How do you collaborate with a team under deadlines?",
        ]