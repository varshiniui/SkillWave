import json
import os

HERE = os.path.dirname(__file__)
RESOURCE_FILE = os.path.join(HERE, "learning_resources.json")

try:
    with open(RESOURCE_FILE) as f:
        RESOURCES = json.load(f)
except Exception:
    RESOURCES = {}


def recommend_for_skills(skills):
    """
    Return learning recommendations for a list of missing skills.
    Output: list of {skill, courses: [...]}
    """
    recs = []
    for skill in skills:
        courses = RESOURCES.get(skill, [])
        # pick top 2
        recs.append({
            "skill": skill,
            "courses": courses[:2]
        })
    return recs


def create_roadmap(missing_skills):
    """
    Create a simple week-by-week roadmap grouping skills.
    """
    roadmap = []
    skills = list(missing_skills)
    week = 1
    while skills:
        chunk = skills[:2]
        skills = skills[2:]
        resources = []
        for s in chunk:
            resources.extend([c for c in RESOURCES.get(s, [])[:1]])
        roadmap.append({
            "phase": f"Week {week}",
            "skills": chunk,
            "recommended_resources": resources
        })
        week += 1
    return roadmap
