"""
SkillWave Backend API
Analyzes resumes for skill gaps and generates personalized interview questions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from skill_analyzer import analyze_skills
from question_generator import generate_questions
import tempfile
import PyPDF2

load_dotenv()

app = Flask(__name__)

# Configure CORS for development (restrict to frontend URL in production)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load valid role options
with open("role_skills.json") as f:
    VALID_ROLES = list(json.load(f).keys())


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SkillWave API",
        "version": "1.0"
    }), 200


@app.route("/roles", methods=["GET"])
def get_roles():
    """Get list of available target roles"""
    return jsonify({"roles": VALID_ROLES}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze resume and identify skill gaps
    
    Request body:
    {
        "resume_text": "string (candidate's resume content)",
        "target_role": "string (one of: Data Analyst, Python Developer, ML Engineer, etc.)"
    }
    
    Response:
    {
        "name": "string",
        "skills": ["list of detected skills"],
        "projects": ["list of detected projects"],
        "education": "string",
        "required_skills": ["skills needed for role"],
        "missing_skills": ["skills to develop"],
        "readiness": "number (0-100 percentage)"
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get("resume_text"):
            return jsonify({"error": "Missing required field: resume_text"}), 400
        
        if not data.get("target_role"):
            return jsonify({"error": "Missing required field: target_role"}), 400
        
        # Validate target role
        if data["target_role"] not in VALID_ROLES:
            return jsonify({
                "error": f"Invalid target_role. Valid roles are: {', '.join(VALID_ROLES)}"
            }), 400
        
        # Validate resume text length
        if len(data["resume_text"].strip()) < 10:
            return jsonify({"error": "Resume text is too short"}), 400
        
        profile = analyze_skills(data["resume_text"], data["target_role"])
        # Add learning recommendations and preparation roadmap
        try:
            from learning_recommender import recommend_for_skills, create_roadmap
            recommendations = recommend_for_skills(profile.get("missing_skills", []))
            roadmap = create_roadmap(profile.get("missing_skills", []))
            profile["learning_recommendations"] = recommendations
            profile["preparation_roadmap"] = roadmap
        except Exception as e:
            profile["learning_recommendations"] = []
            profile["preparation_roadmap"] = []
            app.logger.warning(f"Could not generate recommendations: {e}")
        return jsonify(profile), 200
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/questions", methods=["POST"])
def get_questions():
    """
    Generate personalized interview questions based on candidate profile
    
    Request body:
    {
        "profile": {object returned from /analyze endpoint},
        "target_role": "string (same as used in /analyze)"
    }
    
    Response:
    {
        "questions": ["list of 20 interview questions"]
    }
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        
        if not data.get("profile"):
            return jsonify({"error": "Missing required field: profile"}), 400
        
        if not data.get("target_role"):
            return jsonify({"error": "Missing required field: target_role"}), 400
        
        if data["target_role"] not in VALID_ROLES:
            return jsonify({
                "error": f"Invalid target_role. Valid roles are: {', '.join(VALID_ROLES)}"
            }), 400
        
        questions = generate_questions(data["profile"], data["target_role"])
        return jsonify({"questions": questions}), 200
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.route("/analyze-file", methods=["POST"])
def analyze_file():
    """
    Accept multipart/form-data with fields:
    - resume_file: PDF file
    - target_role: target role
    """
    try:
        if 'resume_file' not in request.files:
            return jsonify({'error': 'Missing resume_file'}), 400
        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        target_role = request.form.get('target_role')
        if not target_role:
            return jsonify({'error': 'Missing required field: target_role'}), 400
        if target_role not in VALID_ROLES:
            return jsonify({'error': f"Invalid target_role. Valid roles are: {', '.join(VALID_ROLES)}"}), 400

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        file.save(tmp.name)

        try:
            import pdfplumber
            text_pages = []
            with pdfplumber.open(tmp.name) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(page_text)
            resume_text = '\n'.join(text_pages).strip()
        except Exception as e:
            return jsonify({'error': f'Failed to read PDF: {e}'}), 500

        if len(resume_text) < 10:
            return jsonify({'error': 'Extracted resume text is too short'}), 400

        profile = analyze_skills(resume_text, target_role)
        # Add learning recommendations and preparation roadmap
        try:
            from learning_recommender import recommend_for_skills, create_roadmap
            recommendations = recommend_for_skills(profile.get("missing_skills", []))
            roadmap = create_roadmap(profile.get("missing_skills", []))
            profile["learning_recommendations"] = recommendations
            profile["preparation_roadmap"] = roadmap
        except Exception as e:
            profile["learning_recommendations"] = []
            profile["preparation_roadmap"] = []
            app.logger.warning(f"Could not generate recommendations: {e}")
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {e}'}), 500


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)