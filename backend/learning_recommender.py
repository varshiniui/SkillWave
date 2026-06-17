import json
import os

HERE = os.path.dirname(__file__)
RESOURCE_FILE = os.path.join(HERE, "learning_resources.json")

try:
    with open(RESOURCE_FILE) as f:
        RESOURCES = json.load(f)
except Exception as e:
    print(f"Error loading resources: {e}")
    RESOURCES = {}


def get_recommendations(missing_skills):
    """
    Get course recommendations for missing skills with links and details.
    
    Returns: list of {skill, courses: [{name, platform, url, duration, price, difficulty}]}
    """
    recommendations = []
    
    for skill in missing_skills:
        if skill in RESOURCES:
            courses = RESOURCES[skill][:3]  # Top 3 courses
        else:
            # Fallback if skill not in database
            courses = [
                {
                    "name": f"Learn {skill}",
                    "platform": "Udemy/Coursera",
                    "url": f"https://www.udemy.com/search/?q={skill.lower().replace(' ', '+')}",
                    "duration": "Varies",
                    "price": "$15-50",
                    "difficulty": "beginner"
                }
            ]
        
        recommendations.append({
            "skill": skill,
            "courses": courses
        })
    
    return recommendations


def create_detailed_roadmap(missing_skills, weeks=8):
    """
    Create a detailed week-by-week preparation roadmap.
    
    Returns: list of {week, title, skills, focus, resources, goals, time_commitment}
    """
    roadmap = []
    skills_list = list(missing_skills)
    week_num = 1
    
    while skills_list and week_num <= weeks:
        # Group 2-3 skills per week
        weekly_skills = skills_list[:2]
        skills_list = skills_list[2:]
        
        # Get resources for this week
        weekly_resources = []
        for skill in weekly_skills:
            if skill in RESOURCES:
                top_course = RESOURCES[skill][0]  # Best course for the skill
                weekly_resources.append({
                    "skill": skill,
                    "course": top_course["name"],
                    "platform": top_course["platform"],
                    "url": top_course["url"],
                    "duration": top_course["duration"]
                })
        
        # Create week structure
        phase = {
            "week": week_num,
            "title": f"Week {week_num}: {' & '.join(weekly_skills)}",
            "skills": weekly_skills,
            "focus": f"Master fundamentals of {', '.join(weekly_skills)}",
            "recommended_courses": weekly_resources,
            "goals": [
                f"Complete introductory course on {weekly_skills[0]}",
                f"Practice with hands-on projects" if len(weekly_skills) > 1 else "Build a simple project",
                "Take practice quizzes"
            ],
            "time_commitment": "5-8 hours per week",
            "difficulty": "beginner" if week_num <= 2 else "intermediate"
        }
        
        roadmap.append(phase)
        week_num += 1
    
    # Add advanced phase if there's time
    if week_num <= weeks:
        roadmap.append({
            "week": week_num,
            "title": "Final Weeks: Integration & Practice",
            "skills": ["All covered skills"],
            "focus": "Integrate all skills into real-world projects",
            "recommended_courses": [],
            "goals": [
                "Build a portfolio project using multiple skills",
                "Participate in mock interviews",
                "Review and reinforce weak areas"
            ],
            "time_commitment": "8-10 hours per week",
            "difficulty": "advanced"
        })
    
    return roadmap