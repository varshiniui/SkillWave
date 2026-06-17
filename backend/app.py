from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from skill_analyzer import analyze_skills
from question_generator import generate_questions
from report_generator import generate_pdf_report, generate_csv_report

load_dotenv()

app = Flask(__name__)
CORS(app)

with open("role_skills.json") as f:
    ROLE_SKILLS = json.load(f)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Backend is running"}), 200


@app.route("/roles", methods=["GET"])
def get_roles():
    roles = list(ROLE_SKILLS.keys())
    return jsonify({"roles": roles}), 200


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json
        resume_text = data.get("resume_text")
        target_role = data.get("target_role")

        if not resume_text or not target_role:
            return jsonify({"error": "Missing resume_text or target_role"}), 400

        print(f"Analyzing resume for role: {target_role} | text length: {len(resume_text)}")
        profile = analyze_skills(resume_text, target_role)
        return jsonify(profile), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/questions", methods=["POST"])
def get_questions():
    try:
        data = request.json
        profile = data.get("profile")
        target_role = data.get("target_role")

        if not profile or not target_role:
            return jsonify({"error": "Missing profile or target_role"}), 400

        print(f"Generating questions for {target_role}")

        # generate_questions now returns (flat_list, structured_dict)
        flat_questions, structured_questions = generate_questions(profile, target_role)

        return jsonify({
            "questions": flat_questions,           # for export (PDF/CSV)
            "structured": structured_questions     # for UI display by category
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/export/pdf", methods=["POST"])
def export_pdf():
    try:
        data = request.json
        profile   = data.get("profile")
        questions = data.get("questions")
        target_role = data.get("target_role")

        if not profile or not questions or not target_role:
            return jsonify({"error": "Missing profile, questions, or target_role"}), 400

        pdf_data = generate_pdf_report(profile, questions, target_role)
        return pdf_data, 200, {
            "Content-Type": "application/pdf",
            "Content-Disposition": "attachment; filename=SkillWave_Report.pdf"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/export/csv", methods=["POST"])
def export_csv():
    try:
        data = request.json
        profile   = data.get("profile")
        questions = data.get("questions")
        target_role = data.get("target_role")

        if not profile or not questions or not target_role:
            return jsonify({"error": "Missing profile, questions, or target_role"}), 400

        csv_data = generate_csv_report(profile, questions, target_role)
        return csv_data, 200, {
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=SkillWave_Report.csv"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting SkillWave Backend...")
    print(f"Available roles: {list(ROLE_SKILLS.keys())}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)