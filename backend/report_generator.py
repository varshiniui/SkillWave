"""
Report Generator Module
Generates PDF and CSV reports for candidates based on analysis results.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import re
import csv

def generate_pdf_report(profile, questions, target_role):
    """
    Generate a formatted PDF report of the candidate profile summary,
    skill gap analysis, learning recommendations, and interview questions.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles (safely building ParagraphStyles)
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1f77b4'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#555555'),
        alignment=1, # Center
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1f77b4'),
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )
    
    story = []
    
    # Title & Subtitle
    story.append(Paragraph("SkillWave Career Report", title_style))
    story.append(Paragraph(f"AI-Powered Resume Analysis & Interview Preparation for {target_role}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 1. Candidate Profile Summary
    story.append(Paragraph("1. Candidate Profile Summary", h1_style))
    
    profile_data = [
        [Paragraph("Candidate Name:", bold_body_style), Paragraph(profile.get("name", "N/A"), body_style)],
        [Paragraph("Highest Education:", bold_body_style), Paragraph(profile.get("education", "N/A"), body_style)],
        [Paragraph("Target Job Role:", bold_body_style), Paragraph(target_role, body_style)],
        [Paragraph("Readiness Score:", bold_body_style), Paragraph(f"{profile.get('readiness', 0)}%", bold_body_style)]
    ]
    
    # Add Certifications & Experience
    certs = ", ".join(profile.get("certifications", [])) if profile.get("certifications") else "None listed"
    exp = ", ".join(profile.get("experience", [])) if profile.get("experience") else "None listed"
    profile_data.append([Paragraph("Certifications:", bold_body_style), Paragraph(certs, body_style)])
    profile_data.append([Paragraph("Experience / Internships:", bold_body_style), Paragraph(exp, body_style)])
    
    t1 = Table(profile_data, colWidths=[150, 380])
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # 2. Skill Gap Analysis
    story.append(Paragraph("2. Skill Gap Analysis", h1_style))
    
    # Matched & Missing skills table
    matched_skills = ", ".join(profile.get("matched_skills", [])) if profile.get("matched_skills") else "None"
    missing_skills = ", ".join(profile.get("missing_skills", [])) if profile.get("missing_skills") else "None"
    
    skills_data = [
        [Paragraph("Category", table_header_style), Paragraph("Skills Details", table_header_style)],
        [Paragraph("Matched Required Skills", bold_body_style), Paragraph(matched_skills, body_style)],
        [Paragraph("Skills to Develop", bold_body_style), Paragraph(missing_skills, body_style)]
    ]
    
    t2 = Table(skills_data, colWidths=[180, 350])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f77b4')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))
    
    # 3. Learning Recommendations
    story.append(Paragraph("3. Learning Recommendations", h1_style))
    
    recs = profile.get("learning_recommendations", [])
    if recs:
        for rec in recs:
            skill = rec.get("skill", "N/A")
            courses = rec.get("courses", [])
            story.append(Paragraph(f"<b>Skill: {skill}</b>", bold_body_style))
            if courses:
                for c in courses:
                    story.append(Paragraph(f"• {c.get('name')} ({c.get('platform')}) | Duration: {c.get('duration')} | Price: {c.get('price')}", body_style))
            else:
                story.append(Paragraph("• Predefined courses not found in database. Search Coursera, Udemy, or YouTube.", body_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No missing skills to recommend courses for.", body_style))
        
    story.append(Spacer(1, 10))
    
    # 4. Week-by-Week Preparation Roadmap
    story.append(Paragraph("4. Preparation Roadmap", h1_style))
    roadmap = profile.get("preparation_roadmap", [])
    if roadmap:
        for step in roadmap:
            phase = step.get("phase", "Phase")
            skills = ", ".join(step.get("skills", []))
            story.append(Paragraph(f"<b>{phase}</b>: Focus on {skills}", body_style))
    else:
        story.append(Paragraph("No roadmap needed.", body_style))
        
    story.append(PageBreak()) # Put questions on the next page
    
    # 5. Personalized Interview Questions
    story.append(Paragraph("5. Personalized Interview Questions (20 Questions)", h1_style))
    story.append(Paragraph("The following questions were generated by AI based on your profile, experience, projects, and missing skills to help you prepare effectively.", body_style))
    story.append(Spacer(1, 10))
    
    for idx, q in enumerate(questions, 1):
        clean_q = re.sub(r"^\d+[\.\s\-]+", "", q).strip()
        clean_q = re.sub(r"^[\-\*\s•]+", "", clean_q).strip()
        story.append(Paragraph(f"<b>{idx}.</b> {clean_q}", body_style))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_report(profile, questions, target_role):
    """
    Generate a CSV report compiling profile details and interview questions.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Candidate Profile Summary
    writer.writerow(["SECTION", "FIELD", "VALUE"])
    writer.writerow(["Profile", "Candidate Name", profile.get("name", "N/A")])
    writer.writerow(["Profile", "Highest Education", profile.get("education", "N/A")])
    writer.writerow(["Profile", "Target Job Role", target_role])
    writer.writerow(["Profile", "Readiness Score", f"{profile.get('readiness', 0)}%"])
    
    certs = ", ".join(profile.get("certifications", [])) if profile.get("certifications") else "None"
    exp = ", ".join(profile.get("experience", [])) if profile.get("experience") else "None"
    writer.writerow(["Profile", "Certifications", certs])
    writer.writerow(["Profile", "Work Experience", exp])
    
    # Skill Gap
    matched_skills = ", ".join(profile.get("matched_skills", [])) if profile.get("matched_skills") else "None"
    missing_skills = ", ".join(profile.get("missing_skills", [])) if profile.get("missing_skills") else "None"
    all_skills = ", ".join(profile.get("skills", [])) if profile.get("skills") else "None"
    
    writer.writerow(["Skill Gap", "Matched Skills", matched_skills])
    writer.writerow(["Skill Gap", "Missing Skills", missing_skills])
    writer.writerow(["Skill Gap", "All Extracted Skills", all_skills])
    
    # Blank row
    writer.writerow([])
    
    # Interview Questions
    writer.writerow(["QUESTION NUMBER", "INTERVIEW QUESTION"])
    for idx, q in enumerate(questions, 1):
        clean_q = re.sub(r"^\d+[\.\s\-]+", "", q).strip()
        clean_q = re.sub(r"^[\-\*\s•]+", "", clean_q).strip()
        writer.writerow([idx, clean_q])
        
    return output.getvalue().encode('utf-8')
