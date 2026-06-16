# SkillWave Frontend - User Guide

## Overview
SkillWave is an AI-powered tool that analyzes your resume and prepares you for interviews by identifying skill gaps and generating personalized questions.

## Features

### 1. Resume Analysis
- **Automatic Resume Parsing:** AI extracts your name, skills, projects, and education
- **Skill Gap Detection:** Identifies which required skills you're missing
- **Readiness Score:** Shows how ready you are for your target role (0-100%)

### 2. Interview Questions
- **20 Personalized Questions:** AI generates questions tailored to your profile and target role
- **Question Categories:**
  - 10 Technical questions
  - 5 Project-based questions
  - 5 Behavioral/Scenario-based questions

### 3. Export Results
- Download your analysis as a JSON file for future reference

## Getting Started

### Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Backend server running on `http://localhost:5000`

### Running the Frontend

1. **Simple Method (No Build Required):**
   ```bash
   # Navigate to frontend folder
   cd frontend
   
   # Open in browser
   # Option 1: Double-click index.html
   # Option 2: Use Python HTTP server
   python -m http.server 8000
   
   # Then visit http://localhost:8000
   ```

2. **With Live Server (VS Code):**
   - Install "Live Server" extension
   - Right-click `index.html`
   - Select "Open with Live Server"

---

## How to Use

### Step 1: Paste Your Resume
1. Copy your resume text (from Word, PDF, or text file)
2. Paste it into the "Your Resume" field
3. Include details about:
   - Skills and technologies you know
   - Projects you've worked on
   - Education and qualifications
   - Work experience

**Tips for better results:**
- Be specific with skill names (e.g., "Python" instead of "coding")
- Mention all relevant projects clearly
- Include your highest education level

### Step 2: Select Target Role
1. Choose your desired job role from the dropdown
2. Available roles:
   - Data Analyst
   - Python Developer
   - ML Engineer
   - UI/UX Designer
   - DevOps Engineer

### Step 3: Analyze Resume
1. Click "Analyze Resume" button
2. Wait for AI to process (usually 10-20 seconds)
3. Results will appear below

### Step 4: Review Results

#### Your Profile
- **Name:** Automatically extracted from your resume
- **Education:** Your highest qualification
- **Your Skills:** Skills detected in your resume (marked with ✓)
- **Your Projects:** Projects mentioned in your resume

#### Role Readiness
Shows your preparedness for the target role:
- **🚀 Excellent Fit (80%+):** You have most required skills
- **✨ Good Fit (60-79%):** You're well-prepared
- **⚡ Moderate (40-59%):** Keep learning
- **📚 Beginner (<40%):** Many skills to learn

#### Skills to Develop
Red skills you should focus on to improve your readiness.

#### Interview Questions
20 personalized questions to help you prepare.

### Step 5: Download Results (Optional)
Click "📥 Download Results" to save your analysis as a JSON file for future reference.

---

## Understanding the Results

### Readiness Score
The percentage indicates how many of the required skills you already have.

**Example:**
- Required skills for Data Analyst: 8
- Your skills: 2
- Readiness: 25% (2 out of 8)

### Missing Skills Priority
Skills listed in "Skills to Develop" are in order of importance for the role.

**Focus on:**
1. High-impact skills (SQL for Data Analyst)
2. Skills that appear in multiple job roles
3. Skills with abundant learning resources

---

## Tips for Success

### 1. Improving Your Readiness
- **Take Online Courses:** Coursera, Udemy, LinkedIn Learning
- **Practice Projects:** Build real projects using required skills
- **Read Documentation:** Official docs for tools like SQL, Power BI, etc.
- **Join Communities:** GitHub, Stack Overflow, Reddit communities

### 2. Interview Preparation
- **Study the Questions:** Review all 20 generated questions
- **Prepare Stories:** Use STAR method (Situation, Task, Action, Result)
- **Mock Interviews:** Practice with friends or mentors
- **Record Yourself:** Practice answering questions on video

### 3. Before the Interview
- Download your results for reference
- Review the missing skills section
- Prepare examples for each question
- Research the company and role

---

## Troubleshooting

### Backend Server Not Running
**Error:** "Network error. Please check if the server is running on http://localhost:5000"

**Solution:**
1. Open terminal in `backend` folder
2. Run: `python app.py`
3. Should see: `Running on http://127.0.0.1:5000`

### Analysis Not Working
**Problem:** Clicking "Analyze Resume" does nothing

**Solutions:**
1. Check that resume text is at least 50 characters
2. Ensure target role is selected
3. Check browser console for errors (F12)
4. Make sure backend is running

### Questions Not Generating
**Problem:** Questions section stays blank

**Solution:**
1. Wait longer (first request may take 20+ seconds)
2. Check that backend has internet access for Groq API
3. Verify GROQ_API_KEY is set in backend

### Downloaded File Is Empty
**Problem:** JSON file has no data

**Solution:**
1. Complete the analysis first
2. Results must be displayed on screen before downloading
3. Try downloading again

---

## Browser Support

| Browser | Support |
|---------|---------|
| Chrome 90+ | ✅ Full Support |
| Firefox 88+ | ✅ Full Support |
| Safari 14+ | ✅ Full Support |
| Edge 90+ | ✅ Full Support |
| IE 11 | ❌ Not Supported |

---

## Privacy

- Your resume data is only sent to the backend server
- Resume text is used only for analysis
- No data is stored or logged permanently
- Generated results are only saved if you download them

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + Enter | Analyze Resume (when focused on resume text) |
| F12 | Open Developer Console |
| Escape | Clear error messages |

---

## Performance Tips

- **For Large Resumes:** Resumes over 2000 characters may take longer
- **Browser Performance:** Use Chrome for best performance
- **Internet Speed:** Fast internet connection recommended for API calls

---

## Common Questions

**Q: Can I upload a PDF file?**
A: Currently, only text input is supported. Copy-paste text from your PDF.

**Q: How accurate is the resume parsing?**
A: AI accuracy depends on resume format and clarity. More structured resumes parse better.

**Q: Can I analyze multiple resumes?**
A: Yes! Click "← Analyze Another Resume" to start over.

**Q: How long does analysis take?**
A: Usually 10-20 seconds depending on internet speed and Groq API load.

**Q: Can I edit the generated questions?**
A: Questions can't be edited in the interface, but you can edit the downloaded JSON file.

---

## Feedback and Support

Have issues or suggestions? Check the project README or contact the development team.

---

## Version Info
- **Frontend Version:** 1.0
- **Last Updated:** 2026
- **Created for:** AIML Internship Project
