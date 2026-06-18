import os
import re
import json
import traceback
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_questions(profile, target_role):
    """
    Generate exactly 20 personalized interview questions split as:
    - 10 Technical Questions  (based on matched skills + role requirements)
    - 5  Project-Based Questions (based on candidate's actual projects)
    - 5  Scenario-Based Questions (situational + missing skills)
    """

    candidate_skills   = ", ".join(profile.get("skills", []))         or "None mentioned"
    matched_skills     = ", ".join(profile.get("matched_skills", []))  or "None"
    missing_skills     = ", ".join(profile.get("missing_skills", []))  or "None"
    candidate_projects = ", ".join(profile.get("projects", []))        or "None mentioned"
    candidate_name     = profile.get("name", "Candidate")

    question_prompt = f"""You are a senior technical interviewer. Generate exactly 20 interview questions for a {target_role} role, divided into 3 sections as shown below.

Candidate Profile:
- Name: {candidate_name}
- Skills they have: {candidate_skills}
- Matched skills for this role: {matched_skills}
- Missing skills for this role: {missing_skills}
- Projects built: {candidate_projects}

Generate questions in EXACTLY this format with section headers:

[TECHNICAL - 10 Questions]
1. <technical question about a skill they have>
2. <technical question about a skill they have>
3. <technical question about a skill they have>
4. <technical question about a skill they have>
5. <technical question about a skill they have>
6. <technical question about a skill they have>
7. <technical question about a skill they have>
8. <technical question about a skill they have>
9. <technical question about a missing skill - how they plan to learn it>
10. <technical question about a missing skill - what they know so far>

[PROJECT - 5 Questions]
11. <question about a specific project they built - why they built it>
12. <question about a specific project - technical challenges faced>
13. <question about a specific project - design or architecture decisions>
14. <question about a specific project - how they tested or validated it>
15. <question about a specific project - what they would improve>

[SCENARIO - 5 Questions]
16. <situational question: how would you handle a real work situation>
17. <situational question: conflict resolution or team collaboration>
18. <situational question: tight deadline or priority management>
19. <situational question: learning a new skill quickly on the job>
20. <situational question: receiving critical feedback or failure>

Rules:
- Make ALL questions specific to this candidate's actual skills and projects above
- Do NOT use placeholder text like <question> — write real questions
- Number questions 1-20 continuously
- Return ONLY the numbered questions with section headers, nothing else"""

    models_to_try = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]

    raw_text = None
    last_error = None

    for model in models_to_try:
        try:
            print(f"Calling Groq API for question generation with model: {model}")
            response = client.chat.completions.create(
                model=model,
                max_tokens=2500,
                temperature=0.7,
                messages=[{"role": "user", "content": question_prompt}]
            )
            raw_text = response.choices[0].message.content.strip()
            print(f"Raw questions ({model}, first 400 chars): {raw_text[:400]}")
            break
        except Exception as e:
            last_error = e
            print(f"Question generation failed on {model}: {type(e).__name__}: {e}")
            continue

    if raw_text is None:
        print(f"All models failed for question generation, using static fallback. Last error: {last_error}")
        flat = _fallback_questions(target_role)
        structured = {
            "technical": flat[:10],
            "project":   flat[10:15],
            "scenario":  flat[15:20],
        }
        return flat, structured

    try:
        # Parse into categorized sections
        technical, project, scenario = [], [], []
        current_section = None

        for line in raw_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if "[TECHNICAL" in line.upper():
                current_section = "technical"
                continue
            elif "[PROJECT" in line.upper():
                current_section = "project"
                continue
            elif "[SCENARIO" in line.upper():
                current_section = "scenario"
                continue

            match = re.match(r"^\d+[\.\)]\s+(.+)", line)
            if match:
                question_text = match.group(1).strip()
                if not question_text:
                    continue
                if current_section == "technical":
                    technical.append(question_text)
                elif current_section == "project":
                    project.append(question_text)
                elif current_section == "scenario":
                    scenario.append(question_text)
                else:
                    total = len(technical) + len(project) + len(scenario)
                    if total < 10:
                        technical.append(question_text)
                    elif total < 15:
                        project.append(question_text)
                    else:
                        scenario.append(question_text)

        print(f"Parsed: {len(technical)} technical, {len(project)} project, {len(scenario)} scenario")

        technical = _pad_section(technical, 10, "technical", target_role, candidate_skills)
        project   = _pad_section(project,   5,  "project",   target_role, candidate_projects)
        scenario  = _pad_section(scenario,  5,  "scenario",  target_role, missing_skills)

        structured = {
            "technical": technical[:10],
            "project":   project[:5],
            "scenario":  scenario[:5],
        }

        flat = technical[:10] + project[:5] + scenario[:5]

        print(f"Final: {len(flat)} total questions")
        return flat, structured

    except Exception as e:
        print(f"Question Parsing Error: {type(e).__name__}: {e}")
        traceback.print_exc()
        flat = _fallback_questions(target_role)
        structured = {
            "technical": flat[:10],
            "project":   flat[10:15],
            "scenario":  flat[15:20],
        }
        return flat, structured
        


def _pad_section(questions, target_count, section_type, role, context):
    """Fill in generic questions if a section has fewer than expected."""
    fallbacks = {
        "technical": [
            f"What is your experience with the core technologies required for a {role}?",
            f"How do you approach debugging complex issues in {role} work?",
            "Explain a technical concept you recently learned and how you applied it.",
            "What development tools and workflows do you use daily?",
            "How do you ensure code/work quality and maintainability?",
            "Describe your experience with version control and collaboration tools.",
            "How do you stay updated with the latest trends in your field?",
            "What is the most complex technical problem you've solved?",
            "How do you approach learning a new framework or tool quickly?",
            f"What do you consider best practices for a {role}?",
        ],
        "project": [
            "Walk me through your most significant project from start to finish.",
            "What was the biggest technical challenge you faced in one of your projects?",
            "How did you decide on the tech stack for one of your projects?",
            "How did you test and validate your project before deployment?",
            "What would you do differently if you rebuilt one of your projects today?",
        ],
        "scenario": [
            "How would you handle a situation where you disagreed with your team lead's technical decision?",
            "Describe how you would manage multiple tasks with competing deadlines.",
            "You are asked to learn a completely new technology in one week. How do you approach it?",
            "How would you handle receiving critical feedback on your work from a client?",
            "Describe a situation where you had to collaborate across teams to solve a problem.",
        ],
    }

    while len(questions) < target_count:
        idx = len(questions)
        fb = fallbacks.get(section_type, [])
        if idx < len(fb):
            questions.append(fb[idx])
        else:
            questions.append(f"Tell me more about your experience relevant to {role}.")

    return questions


def _fallback_questions(target_role):
    """Full fallback when API fails entirely."""
    technical = [
        f"What core technologies do you use as a {target_role}?",
        "Explain a key technical concept in your domain.",
        "How do you approach debugging a problem you've never seen before?",
        "What development tools and workflows are you most comfortable with?",
        "How do you ensure quality and maintainability in your work?",
        "Describe your experience with version control (Git).",
        "How do you stay updated with the latest industry trends?",
        "What is the most complex technical problem you've solved?",
        "How do you learn a new framework or tool quickly?",
        f"What best practices do you follow as a {target_role}?",
    ]
    project = [
        "Walk me through your most significant project from start to finish.",
        "What was the biggest challenge you faced in one of your projects?",
        "How did you decide on the tech stack for a project?",
        "How did you test and validate your project?",
        "What would you improve if you rebuilt your best project today?",
    ]
    scenario = [
        "How would you handle disagreeing with your team lead on a technical decision?",
        "Describe how you manage multiple tasks with competing deadlines.",
        "You need to learn a new technology in one week. What's your approach?",
        "How do you handle receiving critical feedback on your work?",
        f"Why should we hire you for this {target_role} position?",
    ]
    return technical + project + scenario