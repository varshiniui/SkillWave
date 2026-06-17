# SkillWave

AI-Powered Resume Analyzer and Personalized Interview Preparation Platform

## Project Overview

SkillWave is an intelligent career preparation assistant designed to help job seekers and students identify skill gaps, receive personalized learning recommendations, and practice for role-specific interviews. The system analyzes resumes, compares candidate qualifications against target job requirements, and generates 20 customized interview questions categorized by technical, project-based, and scenario-based topics.

### Problem Statement

Job seekers face several challenges during interview preparation:
- Lack of clarity on skill gaps for target roles
- Difficulty finding relevant learning resources
- Generic interview questions that do not reflect their actual profile
- No structured preparation roadmap

SkillWave solves these problems by providing a data-driven, personalized preparation platform.

## Architecture

SkillWave follows a client-server architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                        │
│  - Resume Upload & Parsing                                      │
│  - Interactive Dashboard with Tabs                              │
│  - Input Validation & Error Handling                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP Requests (JSON)
┌─────────────────▼───────────────────────────────────────────────┐
│                   Backend (Flask API)                           │
│  - Resume Analysis (/analyze)                                   │
│  - Question Generation (/questions)                             │
│  - Report Export (/export/pdf, /export/csv)                     │
│  - Role Skills Management                                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Groq API Calls
┌─────────────────▼───────────────────────────────────────────────┐
│                    External Services                            │
│  - Groq LLMs (Resume Extraction, Question Generation)           │
│  - Udemy, Coursera, YouTube, LinkedIn Learning (Course Links)  │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Streamlit** - Web framework for interactive UI
- **Plotly** - Readiness score visualization (circular gauge)
- **Requests** - HTTP client for backend communication
- **PyPDF2** / **pdfplumber** - PDF text extraction

### Backend
- **Flask** - REST API framework
- **Flask-CORS** - Cross-origin request handling
- **Groq API** - LLM inference for resume parsing and question generation
  - Models: LLaMA 3.3 70B, LLaMA 4 Scout 17B, LLaMA 3.1 8B
- **Python-dotenv** - Environment variable management

### Data & Storage
- **JSON** - Role skills database and configuration
- **CSV/PDF** - Report export formats

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
│   ├── .env                        # API keys (GROQ_API_KEY)
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

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Groq API key (free tier available at https://console.groq.com)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd SkillWave
```

### Step 2: Create Environment Variables
Create a `.env` file in the `backend/` directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- flask==2.3.3
- flask-cors==4.0.0
- groq>=1.4.0
- python-dotenv==1.0.0
- pdfplumber>=0.11.0

### Step 4: Install Frontend Dependencies
```bash
cd ../frontend
pip install -r requirements.txt
```

Required packages:
- streamlit
- pdfplumber
- requests
- plotly

## Running Locally

### Terminal 1: Start Flask Backend
```bash
cd backend
python app.py
```

Backend will run on `http://localhost:5000`

Expected output:
```
Starting SkillWave Backend...
Available roles: ['UI/UX Designer', 'Data Analyst', 'Python Developer', ...]
Running on http://127.0.0.1:5000
```

### Terminal 2: Start Streamlit Frontend
```bash
cd frontend
streamlit run main.py
```

Frontend will open automatically at `http://localhost:8501`

## Core Modules

### 1. Resume Parser (`resume_parser.py`)

Extracts text from PDF resumes using PyPDF2.

**Key Features:**
- Multi-page PDF support
- Text cleaning and normalization
- Validation for scanned/image-based PDFs
- Graceful error handling

**Validation Heuristics:**
- Minimum 30 words extracted
- Minimum 35% alphabetic characters (catches scanned PDFs which are typically <20%)
- Returns specific error messages for invalid PDFs

### 2. Skill Analyzer (`skill_analyzer.py`)

Analyzes resume content and identifies skill gaps.

**Workflow:**
1. Splits resume into 3 parts for LLM processing (handles token limits)
2. Sends to Groq with detailed extraction prompt
3. Parses JSON response for: name, education, skills, projects, internships, work experience, certifications
4. Compares candidate skills against required skills for target role
5. Calculates readiness percentage: `(matched_skills / required_skills) * 100`

**Data Structure Output:**
```python
{
    "name": "Candidate Name",
    "education": "B.Tech Information Technology, ...",
    "skills": ["Python", "React", "Figma", ...],
    "projects": ["ProjectA", "ProjectB", ...],
    "internships": ["Company1", "Company2", ...],
    "experience": ["Job Title at Company", ...],
    "certifications": ["Cert1", "Cert2", ...],
    "matched_skills": ["Python", "React"],
    "missing_skills": ["SQL", "Docker"],
    "readiness": 65,
    "learning_recommendations": [...],
    "preparation_roadmap": [...]
}
```

**LLM Model Fallback Strategy:**
Tries models in order until successful:
1. meta-llama/llama-4-scout-17b-16e-instruct (fastest)
2. llama-3.3-70b-versatile (accurate)
3. llama-3.1-8b-instant (fallback)

Includes rate-limit handling with automatic retry.

### 3. Question Generator (`question_generator.py`)

Generates 20 personalized interview questions split into three categories.

**Question Distribution:**
- 10 Technical Questions: Based on matched skills, missing skills, and role requirements
- 5 Project-Based Questions: Based on actual projects from resume
- 5 Scenario-Based Questions: Situational/behavioral questions

**Parsing Logic:**
1. LLM generates questions with `[TECHNICAL]`, `[PROJECT]`, `[SCENARIO]` section headers
2. Regex extracts numbered questions per section
3. If parsing incomplete, `_pad_section()` fills with fallback questions
4. Final validation ensures exactly 10/5/5 split

**Output Format:**
```python
{
    "questions": [q1, q2, ..., q20],  # Flat list for export
    "structured": {
        "technical": [10 questions],
        "project": [5 questions],
        "scenario": [5 questions]
    }
}
```

### 4. Report Generator (`report_generator.py`)

Exports profile and questions as PDF or CSV reports.

**Supported Formats:**
- PDF: Styled report with profile summary, skill analysis, questions, and recommendations
- CSV: Tabular format for spreadsheet analysis

### 5. Learning Recommendations (`learning_recommendations.py`)

Recommends courses for missing skills with real course links.

**Data Source:**
- 20+ predefined skill-to-course mappings
- Covers: Figma, Python, React, SQL, Docker, AWS, Machine Learning, etc.
- Platforms: Udemy, Coursera, YouTube, LinkedIn Learning, AWS Training, Interaction Design Foundation

**Fallback Strategy:**
If skill not in predefined list, generates search links to YouTube and Udemy

**Roadmap Templates:**
Role-specific preparation roadmaps (Weeks 1-8) for:
- UI/UX Designer
- Data Analyst
- Python Developer
- ML Engineer
- DevOps Engineer

## API Documentation

### Backend Endpoints

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
    "status": "Backend is running"
}
```

#### GET `/roles`
Retrieve list of available target job roles.

**Response:**
```json
{
    "roles": ["UI/UX Designer", "Data Analyst", "Python Developer", ...]
}
```

#### POST `/analyze`
Analyze resume and generate candidate profile.

**Request Body:**
```json
{
    "resume_text": "Extracted text from PDF...",
    "target_role": "UI/UX Designer"
}
```

**Response:**
```json
{
    "name": "...",
    "education": "...",
    "skills": [...],
    "readiness": 75,
    ...
}
```

**HTTP Status Codes:**
- 200: Success
- 400: Missing resume_text or target_role
- 500: Processing error

#### POST `/questions`
Generate personalized interview questions.

**Request Body:**
```json
{
    "profile": {...},  // Profile object from /analyze
    "target_role": "UI/UX Designer"
}
```

**Response:**
```json
{
    "questions": [20 questions in flat list],
    "structured": {
        "technical": [...],
        "project": [...],
        "scenario": [...]
    }
}
```

#### POST `/export/pdf`
Generate and download PDF report.

**Request Body:**
```json
{
    "profile": {...},
    "questions": [...],
    "target_role": "UI/UX Designer"
}
```

**Response:** PDF file (application/pdf)

#### POST `/export/csv`
Generate and download CSV report.

**Request Body:** Same as `/export/pdf`

**Response:** CSV file (text/csv)

## Frontend Features

### Dashboard Tabs

**Tab 1: Profile**
- Candidate name, education, readiness gauge
- Skills found (from resume)
- Projects (named software projects)
- Internships (short-term roles)
- Work Experience (full-time/freelance roles)
- Certifications

**Tab 2: Skill Analysis**
- Readiness score with color-coded progress bar
  - Red: 0-40% (needs improvement)
  - Orange: 40-70% (moderate readiness)
  - Cyan: 70-100% (highly ready)
- Metric cards: Your Skills, Required Skills, Missing Skills, Matched Skills
- Matched skills list (green checkmarks)
- Skills to Develop list (warning icons)

**Tab 3: Interview Questions**
- Question count metrics by category
- Tabbed interface showing:
  - Technical Questions (10)
  - Project-Based Questions (5)
  - Scenario-Based Questions (5)
- Each question numbered and formatted

**Tab 4: Recommendations**
- Learning recommendations organized by skill
- Expandable sections with course details: name, platform, duration, price
- Real course links to Udemy, Coursera, YouTube
- Preparation roadmap (8-week structured plan)
- Phase-based skill focus areas

### Input Validation

**Resume Quality Checks:**
1. Non-empty file
2. Minimum 30 words
3. Minimum 35% alphabetic characters
4. Returns specific error messages if validation fails

## Deployment Options

### Option 1: Streamlit Community Cloud (Recommended)

Free, automatic deployment directly from GitHub.

**Steps:**
1. Push code to GitHub repository
2. Visit https://share.streamlit.io
3. Sign in with GitHub
4. Select your repository and `frontend/main.py`
5. Add secrets in Streamlit dashboard:
   - GROQ_API_KEY
   - BACKEND_API_URL (if using cloud backend)
6. Streamlit handles deployment automatically

**Limitations:**
- Must deploy frontend and backend separately
- Backend should be deployed to Heroku, Railway, or similar

### Option 2: Heroku (Backend + Frontend)

Deploy both frontend and backend to Heroku.

**Backend (Heroku):**
```bash
heroku create your-app-backend
git push heroku main
```

**Frontend (Heroku):**
```bash
heroku create your-app-frontend
git push heroku main
```

**Note:** Requires Procfile and runtime.txt

### Option 3: Self-Hosted (VPS/Cloud Instance)

Deploy on personal server, AWS EC2, DigitalOcean, etc.

**Setup:**
```bash
# Install Python and dependencies
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# Run with process manager (systemd, supervisor)
systemctl start skillwave-backend
systemctl start skillwave-frontend
```

**Reverse Proxy:** Use Nginx to handle traffic

## Key Technical Decisions

### 1. Three-Part Resume Splitting
Groq models have token limits. Splitting resume into 3 parts (first 2K, next 2.5K, rest) allows processing longer resumes while staying within limits.

### 2. LLM Model Fallback
Uses three models in sequence to handle rate limits and ensure reliability. Scout model is faster but less accurate; if needed, falls back to 70B model.

### 3. Validation Heuristics
35% alphabetic character threshold balances:
- Accepting formatted resumes with tables/symbols
- Rejecting scanned PDFs (typically <20% alphabetic)

### 4. Structured vs Flat Questions
Returns both formats:
- Flat list for exports (PDF/CSV)
- Structured dict for UI tabs
This allows flexible use in frontend and reports

## Testing & Debugging

### Test Resume Extraction
```python
from resume_parser import extract_resume_text
text = extract_resume_text(pdf_file)
print(len(text), "characters extracted")
```

### Test Backend Endpoint
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"Your resume text...","target_role":"UI/UX Designer"}'
```

### Common Issues

**Issue: "No module named plotly"**
Solution: `pip install plotly`

**Issue: "Cannot connect to backend"**
Solution: Ensure Flask server is running on port 5000

**Issue: Validation error "mostly non-alphabetic"**
Solution: Export resume as text-based PDF (not image/scanned)

**Issue: "429 Rate Limit" from Groq**
Solution: Wait 30 seconds, app will auto-retry with fallback model

## Future Enhancements

1. **Audio/Video Mock Interviews**: Add real-time interview simulation with speech recognition
2. **Interview Recording**: Record and playback interviews for self-review
3. **Analytics Dashboard**: Track readiness progress over time
4. **Resume Templates**: Provide ATS-friendly resume templates per role
5. **Peer Comparison**: Benchmark skills against other candidates
6. **Email Notifications**: Send weekly progress updates and learning milestones
7. **Multi-language Support**: Support resumes in multiple languages
8. **LinkedIn Integration**: Auto-import skills and experience from LinkedIn profile
9. **Interview History**: Store past interview sessions and track improvement
10. **Marketplace**: Connect with mentors for personalized coaching

## Contributing

Contributions are welcome. To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -am 'Add your feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support & Contact

For issues, questions, or feedback, please open an issue in the GitHub repository.

## Acknowledgments

- Groq for providing fast LLM inference
- Streamlit for the interactive web framework
- Flask for the REST API backend
- PyPDF2 and pdfplumber for PDF processing