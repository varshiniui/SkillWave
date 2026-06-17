# SkillWave 

> **AI-Powered Resume Analyzer & Personalized Interview Preparation Platform**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://varshiniui-skillwave-frontendmain-c8u2ih.streamlit.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq%20LLM-F55036?style=for-the-badge)](https://console.groq.com)

---

## Live Demo

**Try it now:** [https://varshiniui-skillwave-frontendmain-c8u2ih.streamlit.app/](https://varshiniui-skillwave-frontendmain-c8u2ih.streamlit.app/)

> Upload your resume, select a target role, and get your personalized skill gap analysis and interview questions in seconds.

---

## Overview

SkillWave is an intelligent career preparation assistant designed to help job seekers and students:

- **Identify skill gaps** against target job roles
- **Get personalized course recommendations** for missing skills
- **Practice with 20 custom interview questions** tailored to their actual resume
- **Follow a structured 8-week preparation roadmap**

---

## Features at a Glance

| Feature | Description |
|---|---|
| Resume Parsing | Upload PDF → auto-extract name, skills, projects, experience |
| Skill Gap Analysis | Compare your skills vs. role requirements with readiness score |
| AI Interview Questions | 20 personalized questions: Technical, Project-Based, Scenario |
| Learning Recommendations | Real course links from Udemy, Coursera, YouTube, LinkedIn Learning |
| Preparation Roadmap | 8-week structured plan per role |
| Export Reports | Download results as PDF or CSV |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Frontend (Streamlit Cloud)                         │
│   varshiniui-skillwave-frontendmain-c8u2ih.streamlit.app        │
│  - Resume Upload & Parsing                                      │
│  - Interactive Dashboard with Tabs                              │
│  - Input Validation & Error Handling                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP Requests (JSON)
┌─────────────────▼───────────────────────────────────────────────┐
│              Backend (Flask API on Render)                      │
│  - Resume Analysis (/analyze)                                   │
│  - Question Generation (/questions)                             │
│  - Report Export (/export/pdf, /export/csv)                     │
│  - Role Skills Management                                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Groq API Calls
┌─────────────────▼───────────────────────────────────────────────┐
│                    External Services                            │
│  - Groq LLMs (LLaMA 3.3 70B, LLaMA 4 Scout, LLaMA 3.1 8B)     │
│  - Udemy, Coursera, YouTube, LinkedIn Learning (Course Links)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Frontend
| Tool | Purpose |
|---|---|
| Streamlit | Web framework & interactive UI |
| Plotly | Readiness score circular gauge |
| Requests | HTTP client for backend communication |
| PyPDF2 + pdfplumber | PDF text extraction (dual fallback) |

### Backend
| Tool | Purpose |
|---|---|
| Flask | REST API framework |
| Flask-CORS | Cross-origin request handling |
| Groq API | LLM inference (resume parsing + question generation) |
| ReportLab | PDF report generation |
| Python-dotenv | Environment variable management |

---

## Project Structure

```
SkillWave/
├── backend/
│   ├── app.py                      # Flask application & API endpoints
│   ├── skill_analyzer.py           # Resume analysis & skill gap detection
│   ├── question_generator.py       # Personalized interview question generation
│   ├── report_generator.py         # PDF & CSV export functionality
│   ├── learning_recommendations.py # Course recommendation logic
│   ├── role_skills.json            # Mapping of job roles to required skills
│   ├── .env                        # API keys (GROQ_API_KEY) — not committed
│   └── requirements.txt            # Backend dependencies
│
├── frontend/
│   ├── main.py                     # Streamlit application
│   ├── resume_parser.py            # PDF text extraction & validation
│   └── requirements.txt            # Frontend dependencies
│
├── .gitignore
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.8+
- pip
- Groq API key — free at [console.groq.com](https://console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/varshiniui/SkillWave.git
cd SkillWave
```

### 2. Configure Environment Variables
Create a `.env` file inside `backend/`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd ../frontend
pip install -r requirements.txt
```

### 5. Run Locally

**Terminal 1 — Flask Backend:**
```bash
cd backend
python app.py
```
Backend runs at `http://localhost:5000`

**Terminal 2 — Streamlit Frontend:**
```bash
cd frontend
streamlit run main.py
```
Frontend opens at `http://localhost:8501`

---

## Deployment

### Current Deployment

| Layer | Platform | URL |
|---|---|---|
| Frontend | Streamlit Community Cloud | [Live App](https://varshiniui-skillwave-frontendmain-c8u2ih.streamlit.app/) |
| Backend | Render (Web Service) | Auto-deployed from GitHub |

### Deploy Your Own

#### Backend → Render
1. Push your `backend/` folder to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add environment variable: `GROQ_API_KEY = your_key`
6. Copy the generated Render URL

#### Frontend → Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub → select `frontend/main.py`
3. Add secret: `GROQ_API_KEY`
4. Update `API_URL` in `main.py` to your Render backend URL

> **Note:** Render's free tier sleeps after 15 minutes of inactivity. The first request after idle may take 30–50 seconds to wake up.

---

## 📡 API Reference

### `GET /health`
Health check.
```json
{ "status": "Backend is running" }
```

### `GET /roles`
Get available target job roles.
```json
{ "roles": ["UI/UX Designer", "Data Analyst", "Python Developer", ...] }
```

### `POST /analyze`
Analyze a resume against a target role.

**Request:**
```json
{
  "resume_text": "Extracted text from PDF...",
  "target_role": "UI/UX Designer"
}
```
**Response:**
```json
{
  "name": "Jane Doe",
  "education": "B.Tech Computer Science",
  "skills": ["Figma", "React", "CSS"],
  "matched_skills": ["Figma", "React"],
  "missing_skills": ["SQL", "Docker"],
  "readiness": 72,
  "learning_recommendations": [...],
  "preparation_roadmap": [...]
}
```

### `POST /questions`
Generate 20 personalized interview questions.

**Request:**
```json
{ "profile": { ...analyze response... }, "target_role": "UI/UX Designer" }
```
**Response:**
```json
{
  "questions": ["Q1", "Q2", ..., "Q20"],
  "structured": {
    "technical": [10 questions],
    "project": [5 questions],
    "scenario": [5 questions]
  }
}
```

### `POST /export/pdf`
Returns a styled PDF report (`application/pdf`).

### `POST /export/csv`
Returns a tabular CSV report (`text/csv`).

---

## Core Module Details

### Resume Parser
- **Dual extraction:** tries `pdfplumber` first, falls back to `PyPDF2`
- **Validation heuristics:** minimum 30 words, ≥35% alphabetic characters
- Catches scanned/image-based PDFs and returns clear error messages

### Skill Analyzer
- Splits resume into 3 chunks to respect LLM token limits
- **Model fallback chain:**
  1. `meta-llama/llama-4-scout-17b` (fastest)
  2. `llama-3.3-70b-versatile` (most accurate)
  3. `llama-3.1-8b-instant` (emergency fallback)
- Readiness formula: `(matched_skills / required_skills) × 100`

### Question Generator
- Generates exactly **10 Technical + 5 Project + 5 Scenario** questions
- Parses LLM output using `[TECHNICAL]`, `[PROJECT]`, `[SCENARIO]` section headers
- Auto-pads with fallback questions if LLM returns fewer than expected

### Learning Recommendations
- 20+ predefined skill-to-course mappings
- Real links to Udemy, Coursera, YouTube, LinkedIn Learning, AWS Training
- Falls back to search links for unmapped skills

---

## UI Tabs

| Tab | Contents |
|---|---|
| **Profile** | Name, education, readiness gauge, skills, projects, internships, certifications |
| **Skill Analysis** | Color-coded readiness bar, matched vs. missing skills |
| **Interview Questions** | 3 sub-tabs: Technical / Project-Based / Scenario-Based |
| **Recommendations** | Course links + 8-week preparation roadmap |

**Readiness Color Coding:**
- 0–40%: Needs significant preparation
- 40–70%: Moderate readiness
- 70–100%: Highly ready

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: reportlab` | Add `reportlab` to `requirements.txt` |
| `ModuleNotFoundError: PyPDF2` | Add `PyPDF2` to `requirements.txt` |
| `Cannot connect to backend` | Ensure Flask is running on port 5000; update `API_URL` in `main.py` |
| `No text extracted from PDF` | Export resume as text-based PDF from Word/Google Docs, not scanned |
| `429 Rate Limit from Groq` | App auto-retries with fallback model after 30 seconds |
| Render app slow on first load | Free tier sleeps after inactivity — first request takes ~30–50s to wake |

---

## Future Enhancements

- **Audio/Video Mock Interviews** — real-time speech recognition simulation
- **Progress Analytics** — track readiness improvement over time
- **Resume Templates** — ATS-friendly templates per role
- **LinkedIn Integration** — auto-import skills and experience
- **Peer Benchmarking** — compare skills against other candidates
- **Mentor Marketplace** — connect with industry coaches
- **Multi-language Support** — resumes in multiple languages
- **Email Notifications** — weekly learning milestone updates

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License**.

---

## Acknowledgments

- [Groq](https://groq.com) — blazing-fast LLM inference
- [Streamlit](https://streamlit.io) — interactive web framework
- [Flask](https://flask.palletsprojects.com) — lightweight REST API
- [pdfplumber](https://github.com/jsvine/pdfplumber) & [PyPDF2](https://pypdf2.readthedocs.io) — PDF processing
- [ReportLab](https://www.reportlab.com) — PDF generation

---

<div align="center">
  Built by Varshini &nbsp;|&nbsp;
  <a href="https://varshiniui-skillwave-frontendmain-c8u2ih.streamlit.app/"> Try SkillWave Live</a>
</div>