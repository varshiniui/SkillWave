import json
import os
import re
import time
import traceback
from difflib import SequenceMatcher
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Master list of valid tech skills (normalized lowercase)
VALID_SKILLS = {
    # Frontend
    "html", "css", "javascript", "react", "vue", "angular", "typescript", "tailwind",
    "bootstrap", "material ui", "figma", "adobe xd", "next.js", "nuxt", "svelte", "sass",
    # Backend
    "python", "java", "node.js", "express", "django", "fastapi", "flask", "spring boot",
    "ruby", "php", "laravel", "asp.net", "c#", "go", "rust", "kotlin", "scala",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "firebase", "dynamodb", "redis", "elasticsearch",
    "cassandra", "oracle", "nosql", "supabase",
    # DevOps & Cloud
    "docker", "kubernetes", "aws", "google cloud", "azure", "jenkins", "github", "gitlab",
    "ci/cd", "terraform", "ansible", "linux", "bash", "git", "github actions",
    # Data & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas",
    "numpy", "matplotlib", "seaborn", "jupyter", "kaggle", "data science", "nlp", "computer vision",
    "spark", "hadoop", "hive", "etl",
    # Tools
    "jira", "slack", "postman", "vercel", "netlify", "heroku", "railway", "notion",
    # Mobile
    "react native", "flutter", "dart", "swift", "kotlin",
    # Testing
    "jest", "pytest", "mocha", "jasmine", "cypress", "selenium", "testng",
    # Design
    "ui/ux design", "user research", "wireframing", "prototyping", "design systems",
    "usability testing",
    # Data Tools
    "power bi", "tableau", "excel", "r", "stata",
    # Other
    "rest api", "graphql", "websockets", "microservices", "agile", "scrum",
    "solid principles", "design patterns", "oop", "oauth", "jwt", "ssl", "encryption",
    "git", "grpc", "protobuf", "groovy", "gradle", "maven",
    "authentication", "deployment",
}

def normalize_skill(skill: str) -> str:
    """Normalize skill: lowercase, remove extra spaces, check aliases."""
    normalized = skill.lower().strip()
    # Remove common suffixes that don't add meaning
    normalized = re.sub(r'\s+(programming|development|development|engineer|engineer|developer)', '', normalized)
    # Replace common abbreviations
    abbreviations = {
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'dl': 'deep learning',
        'js': 'javascript',
        'ts': 'typescript',
        'css3': 'css',
        'html5': 'html',
        'ux': 'ui/ux design',
        'ui': 'ui/ux design',
        'ds': 'data science',
        'api': 'rest api',
        'cicd': 'ci/cd',
        'react.js': 'react',
        'reactjs': 'react',
        'node.js': 'node.js',
        'nodejs': 'node.js',
        'vue.js': 'vue',
        'vuejs': 'vue',
        'tf': 'tensorflow',
        'sklearn': 'scikit-learn',
    }
    if normalized in abbreviations:
        normalized = abbreviations[normalized]
    return normalized

def similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings (0-1)."""
    return SequenceMatcher(None, a, b).ratio()

def is_valid_skill(skill: str) -> bool:
    """Check if extracted skill is actually a valid tech skill."""
    normalized = normalize_skill(skill)
    
    # Direct match
    if normalized in VALID_SKILLS:
        return True
    
    # Fuzzy match (80%+ similarity)
    for valid_skill in VALID_SKILLS:
        if similarity(normalized, valid_skill) > 0.80:
            return True
    
    # Reject if it's too generic or looks like a word, not a skill
    reject_patterns = [
        r'^(and|or|the|is|are|was|were|been|be|have|has|had|do|does|did|can|could|would|should|may|might|must|will|shall|using|used|include|including|such|etc|e\.g|i\.e)$',
        r'^(with|for|from|to|in|on|at|by|up|down)$',
        r'^(a|an|all|any|some|no|my|your|his|her|its|our|their)$',
        r'^[a-z]$',  # single letters
        r'^\d+',  # starts with number
    ]
    normalized_clean = normalized.strip()
    for pattern in reject_patterns:
        if re.match(pattern, normalized_clean):
            return False
    
    return False

def filter_and_validate_skills(extracted_skills: list) -> list:
    """Filter extracted skills to keep only valid ones, remove duplicates."""
    validated = []
    seen = set()
    
    for skill in extracted_skills:
        if not skill or not isinstance(skill, str):
            continue
        
        normalized = normalize_skill(skill)
        
        # Skip if already seen
        if normalized in seen:
            continue
        
        # Check if valid
        if is_valid_skill(skill):
            seen.add(normalized)
            # Return the skill as it was in VALID_SKILLS (proper capitalization)
            for valid_skill in VALID_SKILLS:
                if normalize_skill(valid_skill) == normalized:
                    validated.append(valid_skill.title() if valid_skill not in ['api', 'ui/ux design', 'rest api', 'c#', 'asp.net'] else valid_skill)
                    break
            else:
                # If not in VALID_SKILLS but passed fuzzy match, add original
                validated.append(skill)
    
    return validated

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
        {"phase": "Week 5-6: Visual & Interaction Design", "focus": "CSS for designers, micro-interactions, usability testing", "skills_category": ["css", "usability testing"]},
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
    for k, v in COURSE_LINKS.items():
        if k in key or key in k:
            return v
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
    print("=== skill_analyzer.py v9 (FIXED) loaded ===")

    with open("role_skills.json") as f:
        role_skills = json.load(f)
    required_skills = role_skills.get(target_role, [])

    part1 = resume_text[:2000]
    part2 = resume_text[2000:4500]
    part3 = resume_text[4500:7500]

    extraction_prompt = f"""You are a resume parser. Extract ONLY actual technical skills, tools, frameworks, and languages.

Resume text (3 parts):
=== RESUME PART 1 ===
{part1}

=== RESUME PART 2 ===
{part2}

=== RESUME PART 3 ===
{part3}

Extract these fields:
- name: Full name exactly as written
- education: Full degree and institution
- skills: ONLY technical skills/tools/frameworks/languages. Include compound skills:
  * Languages: Python, JavaScript, Java, C#, PHP, Dart, Kotlin, etc.
  * Frontend: React, Next.js, Angular, Vue, Flutter, etc.
  * Backend: Node.js, Express, Django, Flask, FastAPI, Spring Boot, etc.
  * Databases: SQL, PostgreSQL, MongoDB, MySQL, Supabase, Firebase, etc.
  * APIs & Authentication: REST APIs, GraphQL, JWT, OAuth, Authentication, etc.
  * Deployment & DevOps: Docker, Kubernetes, CI/CD, Deployment, Vercel, AWS, Azure, GCP, Railway, etc.
  * Tools: Git, GitHub, Figma, Jira, etc.
  * AI/ML: TensorFlow, PyTorch, scikit-learn, Groq, Gemini, etc.
  * DO NOT include soft skills (communication, teamwork, leadership, problem-solving)
- projects: Distinct named software projects only (NOT URLs or portfolio links)
- internships: Company names where internships were completed
- experience: Full-time/freelance roles in format "Job Title at Company" (NOT internships)
- certifications: Full certification names

IMPORTANT: If resume mentions "REST API", "JWT", "OAuth", "deployed on Vercel/Railway/etc", "CI/CD", include those skills explicitly.

Return ONLY valid JSON:
{{"name":"John Doe","education":"B.Tech IT, University","skills":["Python","React","Node.js","REST APIs","JWT","Authentication","Deployment","Docker","PostgreSQL"],"projects":["App1","App2"],"internships":["Company1"],"experience":[],"certifications":["AWS Certified"]}}"""

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

            # FILTER & VALIDATE SKILLS: Only keep actual tech skills
            raw_skills = parsed.get("skills", [])
            parsed["skills"] = filter_and_validate_skills(raw_skills)
            print(f"Raw skills ({len(raw_skills)}): {raw_skills}")
            print(f"Validated skills ({len(parsed['skills'])}): {parsed['skills']}")

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

            # Ensure experience doesn't repeat internships
            if "experience" not in parsed or parsed.get("experience") is None:
                parsed["experience"] = []
            internship_names_lower = [i.lower().strip() for i in parsed.get("internships", [])]
            parsed["experience"] = [
                e for e in parsed["experience"]
                if not any(name in e.lower() for name in internship_names_lower)
            ]

            resume_data = parsed
            print(f"OK: name={resume_data['name']}, skills={len(resume_data['skills'])}, projects={len(resume_data['projects'])}")
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

    # IMPROVED SKILL MATCHING: Normalize both candidate and required skills
    candidate_skills_normalized = [normalize_skill(s) for s in resume_data.get("skills", [])]
    missing_skills, matched_skills = [], []

    DEPLOYMENT_INDICATORS = {
        "vercel", "railway", "netlify", "render", "heroku",
        "docker", "kubernetes", "aws", "azure", "google cloud", "ci/cd"
    }

    for req in required_skills:
        req_normalized = normalize_skill(req)
        matched = False
        
        # Check for direct normalized match
        if req_normalized in candidate_skills_normalized:
            matched = True
        else:
            # Check for fuzzy match
            for cand_norm in candidate_skills_normalized:
                if similarity(req_normalized, cand_norm) > 0.80:
                    matched = True
                    break

        # Special case: "Deployment" counts as matched if candidate lists any deployment platform
        if not matched and req_normalized == "deployment":
            if any(plat in candidate_skills_normalized for plat in DEPLOYMENT_INDICATORS):
                matched = True
        
        if matched:
            matched_skills.append(req)
        else:
            missing_skills.append(req)

    readiness = int((len(matched_skills) / len(required_skills)) * 100) if required_skills else 0

    # Learning recommendations
    learning_recommendations = []
    for skill in missing_skills[:6]:
        courses = get_course_links(skill)
        learning_recommendations.append({"skill": skill, "courses": courses})

    # Roadmap template
    roadmap_template = ROADMAP_TEMPLATES.get(target_role, [])
    if roadmap_template:
        preparation_roadmap = []
        for phase in roadmap_template:
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

    print(f"Final: {len(matched_skills)}/{len(required_skills)} matched | Readiness: {readiness}%")
    return profile

def similarity(a: str, b: str) -> float:
    """Calculate string similarity (0-1)."""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()