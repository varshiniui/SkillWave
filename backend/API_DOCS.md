# SkillWave Backend - API Documentation

## Overview
SkillWave is an AI-powered resume analyzer that identifies skill gaps and generates personalized interview questions.

**Base URL:** `http://localhost:5000`

---

## Endpoints

### 1. Health Check
Get API status.

**Endpoint:** `GET /health`

**Response (200):**
```json
{
  "status": "healthy",
  "service": "SkillWave API",
  "version": "1.0"
}
```

---

### 2. Get Available Roles
Retrieve list of supported job roles.

**Endpoint:** `GET /roles`

**Response (200):**
```json
{
  "roles": [
    "Data Analyst",
    "Python Developer",
    "ML Engineer",
    "UI/UX Designer",
    "DevOps Engineer"
  ]
}
```

---

### 3. Analyze Resume
Analyze a candidate's resume and identify skill gaps for a target role.

**Endpoint:** `POST /analyze`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "resume_text": "I am John Doe. I have experience with Python, Excel, and built a Sales Dashboard project. I studied BTech IT.",
  "target_role": "Data Analyst"
}
```

**Request Validation:**
- `resume_text`: Required, minimum 10 characters
- `target_role`: Required, must be one of the available roles

**Response (200 - Success):**
```json
{
  "name": "John Doe",
  "skills": ["Python", "Excel"],
  "projects": ["Sales Dashboard"],
  "education": "BTech IT",
  "required_skills": ["SQL", "Power BI", "Python", "Statistics", "Excel", "Data Visualization", "Tableau", "Google Analytics"],
  "missing_skills": ["SQL", "Power BI", "Statistics", "Data Visualization", "Tableau", "Google Analytics"],
  "readiness": 25
}
```

**Response (400 - Bad Request):**
```json
{
  "error": "Invalid target_role. Valid roles are: Data Analyst, Python Developer, ML Engineer, UI/UX Designer, DevOps Engineer"
}
```

**Response (500 - Server Error):**
```json
{
  "error": "Server error: [error details]"
}
```

---

### 4. Generate Interview Questions
Generate 20 personalized interview questions based on candidate profile.

**Endpoint:** `POST /questions`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "profile": {
    "name": "John Doe",
    "skills": ["Python", "Excel"],
    "projects": ["Sales Dashboard"],
    "education": "BTech IT",
    "required_skills": ["SQL", "Power BI", "Python", "Statistics", "Excel", "Data Visualization", "Tableau", "Google Analytics"],
    "missing_skills": ["SQL", "Power BI", "Statistics", "Data Visualization", "Tableau", "Google Analytics"],
    "readiness": 25
  },
  "target_role": "Data Analyst"
}
```

**Note:** The profile object should come from the `/analyze` endpoint response.

**Request Validation:**
- `profile`: Required, must be a valid profile object
- `target_role`: Required, must be one of the available roles

**Response (200 - Success):**
```json
{
  "questions": [
    "1. How do you handle missing data in a dataset using Python?",
    "2. What is the difference between a LEFT JOIN and an INNER JOIN in SQL?",
    "3. Can you explain the concept of correlation versus causation in statistics?",
    "...",
    "20. Can you describe a situation where you had to explain complex data insights to a non-technical audience?"
  ]
}
```

**Response (400 - Bad Request):**
```json
{
  "error": "Missing required field: profile"
}
```

**Response (500 - Server Error):**
```json
{
  "error": "Server error: [error details]"
}
```

---

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Invalid endpoint |
| 500 | Server Error - Internal issue |

All error responses follow this format:
```json
{
  "error": "Description of the error"
}
```

---

## CORS Policy

The API is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

To add additional origins, update the CORS configuration in `app.py`.

---

## Authentication

Currently, no authentication is required. In production, consider adding:
- API Key authentication
- JWT tokens
- Rate limiting

---

## Rate Limiting

Not currently implemented. For production, consider adding:
- Per-IP rate limits
- Per-user rate limits
- Request queuing

---

## Testing with cURL

### Health Check
```bash
curl http://localhost:5000/health
```

### Get Roles
```bash
curl http://localhost:5000/roles
```

### Analyze Resume
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "I am John Doe. I have experience with Python, Excel, and built a Sales Dashboard project. I studied BTech IT.",
    "target_role": "Data Analyst"
  }'
```

### Generate Questions
```bash
curl -X POST http://localhost:5000/questions \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "name": "John Doe",
      "skills": ["Python", "Excel"],
      "projects": ["Sales Dashboard"],
      "education": "BTech IT",
      "required_skills": ["SQL", "Power BI", "Python", "Statistics", "Excel", "Data Visualization", "Tableau", "Google Analytics"],
      "missing_skills": ["SQL", "Power BI", "Statistics", "Data Visualization", "Tableau", "Google Analytics"],
      "readiness": 25
    },
    "target_role": "Data Analyst"
  }'
```

---

## Example Workflow

1. **Start the server:**
   ```bash
   cd backend
   python app.py
   ```

2. **Check health:**
   ```bash
   curl http://localhost:5000/health
   ```

3. **Get available roles:**
   ```bash
   curl http://localhost:5000/roles
   ```

4. **Analyze resume:**
   ```bash
   curl -X POST http://localhost:5000/analyze ...
   # Save the response as profile
   ```

5. **Generate questions:**
   ```bash
   curl -X POST http://localhost:5000/questions \
     -d '{
       "profile": <saved_profile>,
       "target_role": "Data Analyst"
     }'
   ```

---

## Development Notes

- **Framework:** Flask
- **AI Model:** Groq (llama-3.3-70b-versatile)
- **Python Version:** 3.8+
- **Dependencies:** See `requirements.txt`

---

## Troubleshooting

### "Server error" responses
- Check that the GROQ_API_KEY environment variable is set
- Ensure the Groq API is accessible
- Check the server logs for detailed error messages

### CORS errors
- Verify the frontend URL is in the CORS allowed origins
- For local development, use `http://localhost:3000` or `http://localhost:5173`

### Resume not being parsed correctly
- Ensure the resume text contains clear information about skills, projects, and education
- The AI may miss information if it's formatted unusually

---

## Future Improvements

- [ ] Add authentication and authorization
- [ ] Implement rate limiting
- [ ] Add request/response logging and monitoring
- [ ] Support file uploads (PDF, DOCX)
- [ ] Add caching for frequently analyzed roles
- [ ] Implement webhook support for async processing
- [ ] Add multi-language support
- [ ] Create SDK for popular languages (Python, JavaScript, etc.)
