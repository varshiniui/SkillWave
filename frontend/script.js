// API Configuration
const API_URL = 'http://localhost:5000';

// DOM Elements
const resumeFile = document.getElementById('resumeFile');
const uploadCard = document.getElementById('uploadCard');
const uploadFilename = document.getElementById('uploadFilename');
const clearFileBtn = document.getElementById('clearFileBtn');
const targetRole = document.getElementById('targetRole');
const analyzeBtn = document.getElementById('analyzeBtn');
const inputSection = document.getElementById('inputSection');
const resultsSection = document.getElementById('resultsSection');
const loadingSpinner = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');


// State
let currentProfile = null;

/**
 * Validate form inputs
 */
function validateForm() {
    const fileSelected = resumeFile && resumeFile.files && resumeFile.files.length > 0;
    const role = targetRole.value;

    if (!fileSelected) {
        showError('Please upload your resume (PDF)');
        return false;
    }

    if (!role) {
        showError('Please select a target role');
        return false;
    }

    return true;
}


/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

/**
 * Show loading spinner
 */
function showLoading(show = true) {
    loadingSpinner.style.display = show ? 'block' : 'none';
    if (show) {
        loadingSpinner.classList.add('active');
    } else {
        loadingSpinner.classList.remove('active');
    }
}

/**
 * Analyze resume
 */
async function analyzeResume() {
    if (!validateForm()) return;
    showLoading(true);
    analyzeBtn.disabled = true;
    try {
        const formData = new FormData();
        formData.append('resume_file', resumeFile.files[0]);
        formData.append('target_role', targetRole.value);
        const response = await fetch(`${API_URL}/analyze-file`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (!response.ok) {
            showError(data.error || 'Failed to analyze uploaded PDF');
            showLoading(false);
            analyzeBtn.disabled = false;
            return;
        }
        currentProfile = data;
        await generateQuestions();
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check if the server is running on http://localhost:5000');
        showLoading(false);
        analyzeBtn.disabled = false;
    }
}


/**
 * Generate interview questions
 */
async function generateQuestions() {
    try {
        const response = await fetch(`${API_URL}/questions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                profile: currentProfile,
                target_role: targetRole.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Failed to generate questions');
            showLoading(false);
            analyzeBtn.disabled = false;
            return;
        }

        // Display results
        displayResults(currentProfile, data.questions);
        showLoading(false);
        analyzeBtn.disabled = false;

    } catch (error) {
        console.error('Error:', error);
        showError('Failed to generate questions');
        showLoading(false);
        analyzeBtn.disabled = false;
    }
}

/**
 * Display results
 */
function displayResults(profile, questions) {
    // Profile information
    document.getElementById('profileName').textContent = profile.name || 'Candidate';
    document.getElementById('profileEducation').textContent = profile.education || 'Not specified';

    // Skills
    const skillsList = document.getElementById('skillsList');
    if (profile.skills && profile.skills.length > 0) {
        skillsList.innerHTML = profile.skills
            .map(skill => `<span class="skill-tag matched">✓ ${skill}</span>`)
            .join('');
    } else {
        skillsList.innerHTML = '<span class="no-data">No skills detected</span>';
    }

    // Projects
    const projectsList = document.getElementById('projectsList');
    if (profile.projects && profile.projects.length > 0) {
        projectsList.innerHTML = profile.projects
            .map(project => `<span class="project-tag">📁 ${project}</span>`)
            .join('');
    } else {
        projectsList.innerHTML = '<span class="no-data">No projects detected</span>';
    }

    // Target role display
    document.getElementById('targetRoleDisplay').textContent = `Target Role: ${targetRole.value}`;

    // Readiness
    const readiness = profile.readiness || 0;
    const matchedSkills = profile.required_skills.length - profile.missing_skills.length;
    const totalSkills = profile.required_skills.length;

    document.getElementById('readinessPercent').textContent = `${readiness}%`;
    document.getElementById('readinessFill').style.width = `${readiness}%`;
    
    if (readiness >= 80) {
        document.getElementById('readinessLabel').textContent = '🚀 Excellent Fit!';
    } else if (readiness >= 60) {
        document.getElementById('readinessLabel').textContent = '✨ Good Fit';
    } else if (readiness >= 40) {
        document.getElementById('readinessLabel').textContent = '⚡ Moderate - Keep Learning';
    } else {
        document.getElementById('readinessLabel').textContent = '📚 Beginner - Lots to Learn';
    }

    document.getElementById('matchedSkills').textContent = matchedSkills;
    document.getElementById('totalSkills').textContent = totalSkills;

    // Missing skills
    const missingSkillsList = document.getElementById('missingSkillsList');
    if (profile.missing_skills && profile.missing_skills.length > 0) {
        missingSkillsList.innerHTML = profile.missing_skills
            .map(skill => `<span class="skill-tag missing">✗ ${skill}</span>`)
            .join('');
    } else {
        missingSkillsList.innerHTML = '<span class="no-data">No missing skills - You\'re ready!</span>';
    }

    // Learning recommendations
    const learningCard = document.getElementById('learningCard');
    const learningRecommendations = document.getElementById('learningRecommendations');
    if (profile.learning_recommendations && profile.learning_recommendations.length > 0) {
        learningCard.style.display = 'block';
        learningRecommendations.innerHTML = profile.learning_recommendations
            .map(rec => `
                <div class="recommendation-item">
                    <h4 class="recommendation-skill">${rec.skill}</h4>
                    <div class="courses-list">
                        ${rec.courses.map(course => `
                            <div class="course-card">
                                <p class="course-name">${course.name}</p>
                                <p class="course-platform">📌 ${course.platform}</p>
                                <p class="course-duration">⏱️ ${course.duration}</p>
                                ${course.price ? `<p class="course-price">💰 ${course.price}</p>` : ''}
                                <a href="${course.url}" target="_blank" class="course-link">View Course →</a>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('');
    } else {
        learningCard.style.display = 'none';
    }

    // Preparation roadmap
    const roadmapCard = document.getElementById('roadmapCard');
    const preparationRoadmap = document.getElementById('preparationRoadmap');
    if (profile.preparation_roadmap && profile.preparation_roadmap.length > 0) {
        roadmapCard.style.display = 'block';
        preparationRoadmap.innerHTML = profile.preparation_roadmap
            .map(phase => `
                <div class="roadmap-phase">
                    <h4 class="phase-title">${phase.phase}</h4>
                    <div class="phase-skills">
                        <strong>Skills to focus on:</strong>
                        <div class="skills-list-inline">
                            ${phase.skills.map(skill => `<span class="skill-badge">${skill}</span>`).join('')}
                        </div>
                    </div>
                    ${phase.recommended_resources && phase.recommended_resources.length > 0 ? `
                        <div class="phase-resources">
                            <strong>Resources:</strong>
                            <ul>
                                ${phase.recommended_resources.map(res => `
                                    <li>${res.name} (${res.platform})</li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `).join('');
    } else {
        roadmapCard.style.display = 'none';
    }

    // Questions
    const questionsList = document.getElementById('questionsList');
    if (questions && questions.length > 0) {
        questionsList.innerHTML = questions
            .map(q => `<div class="question-item">${q}</div>`)
            .join('');
    } else {
        questionsList.innerHTML = '<span class="no-data">No questions generated</span>';
    }

    // Show results section
    inputSection.style.display = 'none';
    resultsSection.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Reset form
 */
function resetForm() {
    resumeFile.value = '';
    uploadFilename.textContent = '';
    clearFileBtn.style.display = 'none';
    uploadCard.style.borderColor = '';
    uploadCard.style.backgroundColor = '';
    targetRole.value = '';
    currentProfile = null;
    inputSection.style.display = 'block';
    resultsSection.style.display = 'none';
    errorMessage.style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Download results as JSON
 */
function downloadResults() {
    if (!currentProfile) {
        showError('No results to download');
        return;
    }

    const results = {
        timestamp: new Date().toISOString(),
        targetRole: targetRole.value,
        profile: currentProfile,
        questions: Array.from(document.querySelectorAll('.question-item')).map(el => el.textContent)
    };

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `skillwave-analysis-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
}

/**
 * Drag and drop functionality
 */

// Open file picker when clicking upload card
uploadCard.addEventListener('click', () => {
    resumeFile.click();
});

// Handle file selection from input
resumeFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        updateFileDisplay(e.target.files[0]);
    }
    if (errorMessage.style.display !== 'none') {
        errorMessage.style.display = 'none';
    }
});

// Drag over event - add visual feedback
uploadCard.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadCard.classList.add('dragover');
});

// Drag leave event - remove visual feedback
uploadCard.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadCard.classList.remove('dragover');
});

// Drop event - handle dropped files
uploadCard.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadCard.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        
        // Validate file type
        if (file.type !== 'application/pdf') {
            showError('Please upload a PDF file');
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showError('File size must be less than 10MB');
            return;
        }
        
        // Set the file to the input element
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        resumeFile.files = dataTransfer.files;
        
        updateFileDisplay(file);
    }
});

/**
 * Update file display when file is selected
 */
function updateFileDisplay(file) {
    uploadFilename.textContent = file.name;
    clearFileBtn.style.display = 'inline-block';
    uploadCard.style.borderColor = '#06b6d4';
    uploadCard.style.backgroundColor = 'rgba(6, 182, 212, 0.05)';
}

/**
 * Clear file selection
 */
clearFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resumeFile.value = '';
    uploadFilename.textContent = '';
    clearFileBtn.style.display = 'none';
    uploadCard.style.borderColor = '';
    uploadCard.style.backgroundColor = '';
});

// Analyze button listener
analyzeBtn.addEventListener('click', analyzeResume);

// Clear error message on role change
targetRole.addEventListener('change', () => {
    if (errorMessage.style.display !== 'none') {
        errorMessage.style.display = 'none';
    }
});
