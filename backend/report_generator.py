import io
import re
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_pdf_report(profile, questions, target_role):
    """
    Generate a formatted PDF report containing:
    - Candidate profile summary
    - Skill gap analysis
    - Learning recommendations
    - Preparation roadmap
    - Personalized interview questions
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1f77b4'),
        alignment=1,
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=30
    )

    section_heading_style = ParagraphStyle(
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

    # Title
    story.append(Paragraph("SkillWave Career Report", title_style))
    story.append(Paragraph(
        f"AI-Powered Resume Analysis & Interview Preparation for {target_role}",
        subtitle_style
    ))
    story.append(Spacer(1, 10))

    # Section 1: Candidate Profile
    story.append(Paragraph("1. Candidate Profile Summary", section_heading_style))

    profile_data = [
        [Paragraph("Candidate Name:", bold_body_style), Paragraph(profile.get("name", "N/A"), body_style)],
        [Paragraph("Education:", bold_body_style), Paragraph(profile.get("education", "N/A"), body_style)],
        [Paragraph("Target Role:", bold_body_style), Paragraph(target_role, body_style)],
        [Paragraph("Readiness Score:", bold_body_style), Paragraph(f"{profile.get('readiness', 0)}%", bold_body_style)],
    ]

    certs = ", ".join(profile.get("certifications", [])) if profile.get("certifications") else "None listed"
    exp = ", ".join(profile.get("experience", [])) if profile.get("experience") else "None listed"
    profile_data.append([Paragraph("Certifications:", bold_body_style), Paragraph(certs, body_style)])
    profile_data.append([Paragraph("Experience:", bold_body_style), Paragraph(exp, body_style)])

    profile_table = Table(profile_data, colWidths=[150, 380])
    profile_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 15))

    # Section 2: Skill Gap Analysis
    story.append(Paragraph("2. Skill Gap Analysis", section_heading_style))

    matched_skills = ", ".join(profile.get("matched_skills", [])) if profile.get("matched_skills") else "None"
    missing_skills = ", ".join(profile.get("missing_skills", [])) if profile.get("missing_skills") else "None"

    skills_data = [
        [Paragraph("Category", table_header_style), Paragraph("Details", table_header_style)],
        [Paragraph("Matched Skills", bold_body_style), Paragraph(matched_skills, body_style)],
        [Paragraph("Skills to Develop", bold_body_style), Paragraph(missing_skills, body_style)],
    ]

    skills_table = Table(skills_data, colWidths=[180, 350])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 15))

    # Section 3: Learning Recommendations
    story.append(Paragraph("3. Learning Recommendations", section_heading_style))

    recommendations = profile.get("learning_recommendations", [])
    if recommendations:
        for rec in recommendations:
            skill = rec.get("skill", "N/A")
            courses = rec.get("courses", [])
            story.append(Paragraph(f"Skill: {skill}", bold_body_style))
            if courses:
                for course in courses:
                    course_info = (
                        f"• {course.get('name', 'N/A')} "
                        f"({course.get('platform', 'N/A')}) | "
                        f"Duration: {course.get('duration', 'N/A')} | "
                        f"Price: {course.get('price', 'N/A')}"
                    )
                    story.append(Paragraph(course_info, body_style))
            else:
                story.append(Paragraph(
                    "Recommended: Search Coursera, Udemy, or YouTube for related courses",
                    body_style
                ))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No missing skills identified.", body_style))

    story.append(Spacer(1, 10))

    # Section 4: Preparation Roadmap
    story.append(Paragraph("4. Preparation Roadmap", section_heading_style))

    roadmap = profile.get("preparation_roadmap", [])
    if roadmap:
        for step in roadmap:
            phase = step.get("phase", "Phase")
            skills = ", ".join(step.get("skills", []))
            story.append(Paragraph(f"{phase}: Focus on {skills}", body_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("Preparation roadmap not available.", body_style))

    story.append(PageBreak())

    # Section 5: Interview Questions
    story.append(Paragraph("5. Personalized Interview Questions", section_heading_style))
    story.append(Paragraph(
        f"The following {len(questions)} questions were generated based on your profile, experience, and skill gaps.",
        body_style
    ))
    story.append(Spacer(1, 12))

    for idx, question in enumerate(questions, 1):
        clean_question = re.sub(r"^\d+[\.\s\-]+", "", question).strip()
        clean_question = re.sub(r"^[\-\*\s•]+", "", clean_question).strip()
        story.append(Paragraph(f"{idx}. {clean_question}", body_style))
        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_report(profile, questions, target_role):
    """
    Generate a CSV report with profile details and interview questions.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["SECTION", "FIELD", "VALUE"])

    # Profile
    writer.writerow(["Profile", "Candidate Name", profile.get("name", "N/A")])
    writer.writerow(["Profile", "Education", profile.get("education", "N/A")])
    writer.writerow(["Profile", "Target Role", target_role])
    writer.writerow(["Profile", "Readiness Score", f"{profile.get('readiness', 0)}%"])

    certs = ", ".join(profile.get("certifications", [])) if profile.get("certifications") else "None"
    exp = ", ".join(profile.get("experience", [])) if profile.get("experience") else "None"
    writer.writerow(["Profile", "Certifications", certs])
    writer.writerow(["Profile", "Experience", exp])

    # Skill gap
    matched = ", ".join(profile.get("matched_skills", [])) if profile.get("matched_skills") else "None"
    missing = ", ".join(profile.get("missing_skills", [])) if profile.get("missing_skills") else "None"
    all_skills = ", ".join(profile.get("skills", [])) if profile.get("skills") else "None"

    writer.writerow(["Skill Gap", "Matched Skills", matched])
    writer.writerow(["Skill Gap", "Missing Skills", missing])
    writer.writerow(["Skill Gap", "All Skills", all_skills])

    writer.writerow([])

    # Questions
    writer.writerow(["QUESTION #", "INTERVIEW QUESTION"])
    for idx, question in enumerate(questions, 1):
        clean_question = re.sub(r"^\d+[\.\s\-]+", "", question).strip()
        clean_question = re.sub(r"^[\-\*\s•]+", "", clean_question).strip()
        writer.writerow([idx, clean_question])

    return output.getvalue().encode("utf-8")