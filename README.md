# ✨ SkillWave - AI-Powered Resume Analyzer & Interview Preparation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Groq API](https://img.shields.io/badge/groq-1.4.0-orange.svg)](https://groq.com/)

> **An intelligent platform that analyzes your resume and generates personalized interview questions using AI.**

Perfect for internship interviews, job applications, and career preparation!

---

## 🌟 Features

- 🤖 **AI Resume Parser** - Automatically extract skills, projects, and education
- 📊 **Skill Gap Analysis** - Identify missing skills for your target role
- 📈 **Readiness Score** - Get a percentage showing how ready you are (0-100%)
- ❓ **20 Interview Questions** - AI-generated questions tailored to your profile
- 🎯 **Multi-Role Support** - Analysis for Data Analyst, Python Developer, ML Engineer, and more
- 📥 **Export Results** - Download analysis as JSON for reference
- 🔒 **Secure** - Input validation and error handling
- 📱 **Responsive UI** - Works on desktop and mobile

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key ([Get it free here](https://console.groq.com))

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo GROQ_API_KEY=your_api_key_here > .env

# Run server
python app.py
```

Server will start on `http://localhost:5000`

### 2. Frontend Setup

```bash
cd frontend
# Option 1: Just open index.html in browser
# Option 2: Use Python HTTP server
python -m http.server 8000
# Visit http://localhost:8000
```

---

## 📖 Usage

1. **Paste Your Resume** - Copy and paste your resume text
2. **Select Target Role** - Choose your desired job role
3. **Click Analyze** - AI analyzes and generates results
4. **Review Results** - See skills, gaps, and interview questions
5. **Download (Optional)** - Save results as JSON

---

## 🏗️ Project Structure

```
SkillWave/
├── backend/
│   ├── app.py                 # Flask API with endpoints
│   ├── skill_analyzer.py      # Resume parsing & analysis
│   ├── question_generator.py  # Interview question generation
│   ├── role_skills.json       # Role requirements database
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (not in repo)
│   └── API_DOCS.md            # API documentation
│
├── frontend/
│   ├── index.html             # Main HTML page
│   ├── styles.css             # Styling
│   ├── script.js              # Client-side logic
│   └── README.md              # Frontend guide
│
└── README.md                  # This file
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health |
| GET | `/roles` | Get available roles |
| POST | `/analyze` | Analyze resume |
| POST | `/questions` | Generate interview questions |

**Full API Documentation:** See [backend/API_DOCS.md](backend/API_DOCS.md)

---

## 🔐 Environment Variables

Create a `.env` file in `backend/`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 📊 Output Example

```json
{
  "name": "John Doe",
  "skills": ["Python", "Excel"],
  "projects": ["Sales Dashboard"],
  "education": "BTech IT",
  "required_skills": ["SQL", "Power BI", "Python", "Statistics", "Excel"],
  "missing_skills": ["SQL", "Power BI", "Statistics"],
  "readiness": 40
}
```

---

## 🛠️ Tech Stack

- **Backend:** Flask 2.3.3, Python 3.8+
- **AI/LLM:** Groq (llama-3.3-70b-versatile)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **CORS:** Flask-CORS

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Network error" | Ensure backend is running on `http://localhost:5000` |
| "Groq Error" | Check `GROQ_API_KEY` is set in `.env` |
| Resume not parsed | Ensure resume text is at least 50 characters |
| CORS error | Verify frontend URL is in allowed origins |

See [frontend/README.md](frontend/README.md) for more help.

---

## 📚 Documentation

- **[Backend API Docs](backend/API_DOCS.md)** - Complete API reference
- **[Frontend Guide](frontend/README.md)** - User guide for the UI
- **[Architecture](#project-structure)** - Project organization

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 👨‍💻 About

**Created for:** AIML Internship Program  
**Version:** 1.0  
**Last Updated:** June 2026

---

**⭐ If you found this helpful, give it a star!**
