import json
import os
import re
import time
import traceback
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Real course links per skill
COURSE_LINKS = {
    "figma": [
        {"name": "Figma UI UX Design Essentials", "platform": "Udemy", "url": "https://www.udemy.com/course/figma-ux-ui-design-user-experience-tutorial-course/", "duration": "12 hrs", "price": "Paid"},
        {"name": "Figma for Beginners (4 courses)", "platform": "Coursera", "url": "https://www.coursera.org/learn/figma-ui-ux-design", "duration": "8 hrs", "price": "Free Audit"},
    ],
    "wireframing": [
        {"name": "Wireframing with Figma", "platform": "YouTube - DesignCourse", "url": "https://www.youtube.com/watch?v=D4NyQ5ZsLs8", "duration": "1 hr", "price": "Free"},
        {"name": "UX Design: Wireframing", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/ux-design-wireframing", "duration": "3 hrs", "price": "Free Trial"},
    ],
    "user research": [
        {"name": "User Research – Methods and Best Practices", "platform": "Interaction Design Foundation", "url": "https://www.interaction-design.org/courses/user-research-methods-and-best-practices", "duration": "10 hrs", "price": "Free Trial"},
        {"name": "UX Research & Strategy", "platform": "Udemy", "url": "https://www.udemy.com/course/ux-research/", "duration": "6 hrs", "price": "Paid"},
    ],
    "prototyping": [
        {"name": "Prototyping & Design in Figma", "platform": "YouTube - Figma", "url": "https://www.youtube.com/watch?v=lTIeZ2ahEkQ", "duration": "2 hrs", "price": "Free"},
        {"name": "Advanced Prototyping in Figma", "platform": "Udemy", "url": "https://www.udemy.com/course/figma-advanced/", "duration": "8 hrs", "price": "Paid"},
    ],
    "css": [
        {"name": "CSS Full Course", "platform": "YouTube - freeCodeCamp", "url": "https://www.youtube.com/watch?v=1Rs2ND1ryYc", "duration": "11 hrs", "price": "Free"},
        {"name": "CSS Grid & Flexbox for Responsive Layouts", "platform": "Udemy", "url": "https://www.udemy.com/course/css-grid-flexbox/", "duration": "5 hrs", "price": "Paid"},
    ],
    "adobe xd": [
        {"name": "Adobe XD Tutorial for Beginners", "platform": "YouTube - DesignCourse", "url": "https://www.youtube.com/watch?v=3aOU9MbITlM", "duration": "2 hrs", "price": "Free"},
        {"name": "Adobe XD: UI/UX Design", "platform": "Udemy", "url": "https://www.udemy.com/course/adobe-xd-design/", "duration": "9 hrs", "price": "Paid"},
    ],
    "usability testing": [
        {"name": "Usability Testing – How to Do It Right", "platform": "Interaction Design Foundation", "url": "https://www.interaction-design.org/courses/conducting-usability-testing", "duration": "8 hrs", "price": "Free Trial"},
        {"name": "UX Usability Testing", "platform": "YouTube - NNGroup", "url": "https://www.youtube.com/watch?v=kX7Ef6Pq4cs", "duration": "1 hr", "price": "Free"},
    ],
    "design systems": [
        {"name": "Design Systems with Figma", "platform": "Udemy", "url": "https://www.udemy.com/course/design-systems-in-figma/", "duration": "6 hrs", "price": "Paid"},
        {"name": "Building Design Systems", "platform": "YouTube - Malewicz", "url": "https://www.youtube.com/watch?v=wc5krC28ynQ", "duration": "1 hr", "price": "Free"},
    ],
    "python": [
        {"name": "Python for Everybody", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python", "duration": "30 hrs", "price": "Free Audit"},
        {"name": "Complete Python Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/complete-python-bootcamp/", "duration": "22 hrs", "price": "Paid"},
    ],
    "machine learning": [
        {"name": "Machine Learning Specialization", "platform": "Coursera - Andrew Ng", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "duration": "30 hrs", "price": "Free Audit"},
        {"name": "ML with Python", "platform": "YouTube - freeCodeCamp", "url": "https://www.youtube.com/watch?v=i_LwzRVP7bg", "duration": "10 hrs", "price": "Free"},
    ],
    "react": [
        {"name": "React - The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "duration": "48 hrs", "price": "Paid"},
        {"name": "React Full Course", "platform": "YouTube - freeCodeCamp", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "duration": "12 hrs", "price": "Free"},
    ],
    "sql": [
        {"name": "SQL for Data Science", "platform": "Coursera", "url": "https://www.coursera.org/learn/sql-for-data-science", "duration": "12 hrs", "price": "Free Audit"},
        {"name": "Complete SQL Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "duration": "9 hrs", "price": "Paid"},
    ],
    "docker": [
        {"name": "Docker for Beginners", "platform": "YouTube - TechWorld", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "duration": "3 hrs", "price": "Free"},
        {"name": "Docker & Kubernetes: The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/", "duration": "21 hrs", "price": "Paid"},
    ],
    "aws": [
        {"name": "AWS Cloud Practitioner Essentials", "platform": "AWS Training", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "duration": "6 hrs", "price": "Free"},
        {"name": "Ultimate AWS Certified Solutions Architect", "platform": "Udemy", "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/", "duration": "27 hrs", "price": "Paid"},
    ],
}

ROADMAP_TEMPLATES = {
    "UI/UX Designer": [
        {"phase": "Week 1-2: Design Foundations", "focus": "Core UX principles, design thinking, user research basics", "skills_category": ["user research", "wireframing", "prototyping"]},
        {"phase": "Week 3-4: Tool Mastery", "focus": "Master Figma, Adobe XD workflows, component libraries", "skills_category": ["figma", "adobe xd", "design systems"]},
        {"phase": "Week 5-6: Visual & Interaction Design", "focus": "CSS for designers, micro-interactions, usability testing", "skills_category": ["css", "usability testing", "micro interactions"]},
        {"phase": "Week 7-8: Portfolio & Practice", "focus": "Build 2-3 case studies, conduct usability tests, prepare portfolio", "skills_category": []},
    ],
    "Data Analyst": [
        {"phase": "Week 1-2: Data Foundations", "focus": "SQL queries, Excel, data cleaning techniques", "skills_category": ["sql", "excel"]},
        {"phase": "Week 3-4: Python for Analysis", "focus": "Pandas, NumPy, data visualization with Matplotlib/Seaborn", "skills_category": ["python", "pandas"]},
        {"phase": "Week 5-6: BI Tools & Statistics", "focus": "Tableau or Power BI dashboards, statistical analysis", "skills_category": ["tableau", "statistics"]},
        {"phase": "Week 7-8: Projects & Portfolio", "focus": "Complete 2 end-to-end analysis projects, publish on GitHub", "skills_category": []},
    ],
    "ML Engineer": [
        {"phase": "Week 1-2: ML Foundations", "focus": "Supervised/unsupervised learning, scikit-learn, model evaluation", "skills_category": ["machine learning", "python"]},
        {"phase": "Week 3-4: Deep Learning", "focus": "Neural networks, TensorFlow/PyTorch, CNNs and RNNs", "skills_category": ["deep learning", "tensorflow"]},
        {"phase": "Week 5-6: MLOps & Deployment", "focus": "Model deployment with Flask/FastAPI, Docker, monitoring", "skills_category": ["docker", "deployment"]},
        {"phase": "Week 7-8: Projects", "focus": "Build and deploy 2 ML projects, contribute to Kaggle", "skills_category": []},
    ],
    "Python Developer": [
        {"phase": "Week 1-2: Python Core", "focus": "OOP, file handling, error handling, modules, virtual envs", "skills_category": ["python"]},
        {"phase": "Week 3-4: Web Frameworks", "focus": "Django or FastAPI, REST APIs, database integration", "skills_category": ["django", "fastapi", "sql"]},
        {"phase": "Week 5-6: Testing & DevOps", "focus": "Unit testing, CI/CD pipelines, Docker basics", "skills_category": ["docker", "testing"]},
        {"phase": "Week 7-8: Projects", "focus": "Build a full-stack Python web app, deploy on cloud", "skills_category": []},
    ],
    "DevOps Engineer": [
        {"phase": "Week 1-2: Linux & Scripting", "focus": "Linux commands, bash scripting, networking basics", "skills_category": ["linux", "bash"]},
        {"phase": "Week 3-4: Containers & Orchestration", "focus": "Docker, Kubernetes, container networking", "skills_category": ["docker", "kubernetes"]},
        {"phase": "Week 5-6: CI/CD & Cloud", "focus": "Jenkins/GitHub Actions pipelines, AWS/GCP fundamentals", "skills_category": ["aws", "ci/cd"]},
        {"phase": "Week 7-8: Monitoring & Projects", "focus": "Prometheus, Grafana, ELK stack, build a complete pipeline", "skills_category": []},
    ],
}


def get_course_links(skill: str):
    """Return course links for a skill, with fallback search links."""
    key = skill.lower().strip()
    if key in COURSE_LINKS:
        return COURSE_LINKS[key]
    # Partial match
    for k, v in COURSE_LINKS.items():
        if k in key or key in k:
            return v
    # Generic fallback with search URLs
    encoded = skill.replace(" ", "+")
    return [
        {"name": f"{skill} - Full Course", "platform": "YouTube", "url": f"https://www.youtube.com/results?search_query={encoded}+tutorial", "duration": "Varies", "price": "Free"},
        {"name": f"Learn {skill}", "platform": "Udemy", "url": f"https://www.udemy.com/courses/search/?q={encoded}", "duration": "Varies", "price": "Paid"},
    ]


def clean_name(name: str) -> str:
    if not name:
        return "Candidate"
    if re.match(r'^([A-Za-z] )+[A-Za-z]$', name.strip()):
        return name.replace(" ", "")
    return name.strip()


def analyze_skills(resume_text, target_role):
    print("=== skill_analyzer.py v8 loaded ===")

    with open("role_skills.json") as f:
        role_skills = json.load(f)
    required_skills = role_skills.get(target_role, [])

    part1 = resume_text[:2000]
    part2 = resume_text[2000:4500]
    part3 = resume_text[4500:7500]

    extraction_prompt = f"""You are a resume parser. Read the ENTIRE resume below carefully. All three parts are from the SAME resume.

=== RESUME PART 1 ===
{part1}

=== RESUME PART 2 ===
{part2}

=== RESUME PART 3 ===
{part3}

Extract these fields accurately:
- name: The candidate's full name exactly as it appears. Return as normal name like "Sahaya Varshini M J".
- education: Full degree and institution (e.g. "B.Tech Information Technology, University College of Engineering Nagercoil")
- skills: Every technical skill, tool, language, framework mentioned
- projects: ONLY distinct named software/app projects like "Practiq", "StudyMate AI", "FocusTrack", "foodi.", "Peblo Notes", "Voc - AI Voice Note Summarizer". Do NOT include: URLs, .vercel/.github links, portfolio addresses, UX artifacts (timelines, case studies), or alternate names of same project.
- internships: Company names where INTERNSHIPS specifically were completed (e.g. "Cognifyz Technologies", "Besant Technologies", "Alric Infotech", "Zoro Tech"). Internships are usually short-term, student-oriented, and explicitly labeled "Intern" or "Internship" in the resume.
- experience: Full-time, part-time, or freelance WORK roles — NOT internships. Format each entry as "Job Title at Company Name" (e.g. "Software Engineer at XYZ Corp", "Freelance Web Developer"). If the candidate has no such roles (common for students), return an empty list. Do NOT repeat internship companies here.
- certifications: Full certification names found anywhere in the resume (e.g. "IBM Python for Data Science", "Infosys Springboard CI/CD", "AWS Cloud Practitioner"). Look carefully through ALL parts.

Return ONLY valid JSON:
{{"name":"Sahaya Varshini M J","education":"B.Tech IT, University College of Engineering Nagercoil","skills":["Python","React"],"projects":["Practiq","StudyMate AI"],"internships":["Cognifyz Technologies"],"experience":[],"certifications":["IBM Python for Data Science","Infosys Springboard CI/CD"]}}"""

    resume_data = {
        "name": "Candidate",
        "education": "Not extracted",
        "skills": [],
        "projects": [],
        "internships": [],
        "experience": [],
        "certifications": []
    }

    models_to_try = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]

    for model in models_to_try:
        try:
            print(f"Trying model: {model}")
            resp = client.chat.completions.create(
                model=model,
                max_tokens=1200,
                temperature=0.1,
                messages=[{"role": "user", "content": extraction_prompt}]
            )
            response_text = resp.choices[0].message.content.strip()
            print(f"Raw ({model}): {response_text[:400]}")

            response_text = response_text.replace("```json", "").replace("```", "").strip()
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                response_text = response_text[start:end]

            parsed = json.loads(response_text)
            parsed["name"] = clean_name(parsed.get("name", "Candidate"))

            # Clean projects
            url_kw = ["http", "www", ".com", ".app", ".io", ".vercel", "github", "portfolio"]
            bad_phrases = ["restaurant discovery", "customer journey", "time line", "case study", "landing page"]
            projects = [p for p in parsed.get("projects", []) if not any(x in p.lower() for x in url_kw + bad_phrases)]
            seen, deduped = set(), []
            for p in projects:
                if p.lower().strip() not in seen:
                    seen.add(p.lower().strip())
                    deduped.append(p)
            parsed["projects"] = deduped

            # Make sure experience never silently collapses into internships
            if "experience" not in parsed or parsed.get("experience") is None:
                parsed["experience"] = []
            internship_names_lower = [i.lower().strip() for i in parsed.get("internships", [])]
            parsed["experience"] = [
                e for e in parsed["experience"]
                if not any(name in e.lower() for name in internship_names_lower)
            ]

            resume_data = parsed
            print(f"OK: name={resume_data['name']}, certs={resume_data.get('certifications')}, internships={resume_data.get('internships')}, experience={resume_data.get('experience')}")
            break

        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower():
                print(f"Rate limited on {model}, retrying...")
                time.sleep(3)
                continue
            elif isinstance(e, json.JSONDecodeError):
                print(f"JSON error on {model}: {e}")
                break
            else:
                print(f"Error on {model}: {type(e).__name__}: {e}")
                traceback.print_exc()
                break

    # Skill gap
    candidate_lower = [s.lower() for s in resume_data.get("skills", [])]
    missing_skills, matched_skills = [], []
    for req in required_skills:
        if req.lower() in candidate_lower:
            matched_skills.append(req)
        else:
            missing_skills.append(req)

    readiness = int((len(matched_skills) / len(required_skills)) * 100) if required_skills else 0

    # Learning recommendations with real links
    learning_recommendations = []
    for skill in missing_skills[:6]:
        courses = get_course_links(skill)
        learning_recommendations.append({"skill": skill, "courses": courses})

    # Role-specific roadmap with missing skills injected
    roadmap_template = ROADMAP_TEMPLATES.get(target_role, [])
    if roadmap_template:
        preparation_roadmap = []
        missing_lower = [s.lower() for s in missing_skills]
        for phase in roadmap_template:
            # Find missing skills that match this phase's category
            phase_missing = [
                s for s in missing_skills
                if any(cat in s.lower() or s.lower() in cat for cat in phase["skills_category"])
            ]
            preparation_roadmap.append({
                "phase": phase["phase"],
                "focus": phase["focus"],
                "skills_to_learn": phase_missing if phase_missing else [],
            })
    else:
        # Generic fallback roadmap
        chunk = max(1, len(missing_skills) // 3)
        preparation_roadmap = []
        phases = [
            ("Week 1-2: Foundation Skills", missing_skills[:chunk], "Build core fundamentals"),
            ("Week 3-4: Core Technical Skills", missing_skills[chunk:chunk*2], "Deepen technical knowledge"),
            ("Week 5-6: Advanced & Projects", missing_skills[chunk*2:], "Apply skills in real projects"),
        ]
        for phase_name, skills, focus in phases:
            if skills:
                preparation_roadmap.append({"phase": phase_name, "focus": focus, "skills_to_learn": skills})

    profile = {
        "name": resume_data.get("name", "Candidate"),
        "education": resume_data.get("education", "Not specified"),
        "skills": resume_data.get("skills", []),
        "projects": resume_data.get("projects", []),
        "internships": resume_data.get("internships", []),
        "experience": resume_data.get("experience", []),
        "certifications": resume_data.get("certifications", []),
        "required_skills": required_skills,
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
        "readiness": readiness,
        "learning_recommendations": learning_recommendations,
        "preparation_roadmap": preparation_roadmap
    }

    print(f"Final Profile keys: {list(profile.keys())}")
    return profile