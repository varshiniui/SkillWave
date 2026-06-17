import io
import re
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def safe(text):
    """
    Escape special XML characters so ReportLab's Paragraph() doesn't crash.
    This is the #1 cause of 500 errors when resume data contains &, <, >, etc.
    """
    if not text:
        return ""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


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

    # ── Title ──────────────────────────────────────────────────────────────
    story.append(Paragraph("SkillWave Career Report", title_style))
    story.append(Paragraph(
        f"AI-Powered Resume Analysis &amp; Interview Preparation for {safe(target_role)}",
        subtitle_style
    ))
    story.append(Spacer(1, 10))

    # ── Section 1: Candidate Profile ───────────────────────────────────────
    story.append(Paragraph("1. Candidate Profile Summary", section_heading_style))

    certs_list = profile.get("certifications", [])
    exp_list   = profile.get("experience", [])
    certs = safe(", ".join(certs_list)) if certs_list else "None listed"
    exp   = safe(", ".join(exp_list))   if exp_list   else "None listed"

    profile_data = [
        [Paragraph("Candidate Name:", bold_body_style), Paragraph(safe(profile.get("name", "N/A")), body_style)],
        [Paragraph("Education:",      bold_body_style), Paragraph(safe(profile.get("education", "N/A")), body_style)],
        [Paragraph("Target Role:",    bold_body_style), Paragraph(safe(target_role), body_style)],
        [Paragraph("Readiness Score:", bold_body_style), Paragraph(f"{profile.get('readiness', 0)}%", bold_body_style)],
        [Paragraph("Certifications:", bold_body_style), Paragraph(certs, body_style)],
        [Paragraph("Experience:",     bold_body_style), Paragraph(exp,   body_style)],
    ]

    profile_table = Table(profile_data, colWidths=[150, 380])
    profile_table.setStyle(TableStyle([
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ('BACKGROUND', (0, 0), (0,  -1), colors.HexColor('#f8f9fa')),
        ('PADDING',    (0, 0), (-1, -1), 8),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 15))

    # ── Section 2: Skill Gap Analysis ──────────────────────────────────────
    story.append(Paragraph("2. Skill Gap Analysis", section_heading_style))

    matched_list = profile.get("matched_skills", [])
    missing_list = profile.get("missing_skills", [])
    matched_skills = safe(", ".join(matched_list)) if matched_list else "None"
    missing_skills = safe(", ".join(missing_list)) if missing_list else "None"

    skills_data = [
        [Paragraph("Category",          table_header_style), Paragraph("Details", table_header_style)],
        [Paragraph("Matched Skills",    bold_body_style),    Paragraph(matched_skills, body_style)],
        [Paragraph("Skills to Develop", bold_body_style),    Paragraph(missing_skills, body_style)],
    ]

    skills_table = Table(skills_data, colWidths=[180, 350])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ('PADDING',    (0, 0), (-1, -1), 8),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 15))

    # ── Section 3: Learning Recommendations ────────────────────────────────
    story.append(Paragraph("3. Learning Recommendations", section_heading_style))

    recommendations = profile.get("learning_recommendations", [])
    if recommendations:
        for rec in recommendations:
            skill   = safe(rec.get("skill", "N/A"))
            courses = rec.get("courses", [])
            story.append(Paragraph(f"Skill: {skill}", bold_body_style))
            if courses:
                for course in courses:
                    name     = safe(course.get("name", "N/A"))
                    platform = safe(course.get("platform", "N/A"))
                    duration = safe(course.get("duration", "N/A"))
                    price    = safe(course.get("price", "N/A"))
                    course_info = (
                        f"• {name} ({platform}) | "
                        f"Duration: {duration} | "
                        f"Price: {price}"
                    )
                    story.append(Paragraph(course_info, body_style))
            else:
                story.append(Paragraph(
                    "Recommended: Search Coursera, Udemy, or YouTube for related courses.",
                    body_style
                ))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No missing skills identified — great job!", body_style))

    story.append(Spacer(1, 10))

    # ── Section 4: Preparation Roadmap ─────────────────────────────────────
    story.append(Paragraph("4. Preparation Roadmap", section_heading_style))

    roadmap = profile.get("preparation_roadmap", [])
    if roadmap:
        for step in roadmap:
            phase = safe(step.get("phase", "Phase"))
            # support both "skills" and "skills_to_learn" keys
            skills_list = step.get("skills_to_learn", step.get("skills", []))
            skills_str  = safe(", ".join(skills_list)) if skills_list else "—"
            focus       = safe(step.get("focus", ""))
            line = f"<b>{phase}</b>"
            if focus:
                line += f": {focus}"
            if skills_str and skills_str != "—":
                line += f" — Skills: {skills_str}"
            story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("Preparation roadmap not available.", body_style))

    story.append(PageBreak())

    # ── Section 5: Interview Questions ─────────────────────────────────────
    story.append(Paragraph("5. Personalized Interview Questions", section_heading_style))
    story.append(Paragraph(
        f"The following {len(questions)} questions were generated based on your profile, "
        f"experience, and skill gaps.",
        body_style
    ))
    story.append(Spacer(1, 12))

    for idx, question in enumerate(questions, 1):
        clean_q = re.sub(r"^\d+[\.\s\-]+", "", question).strip()
        clean_q = re.sub(r"^[\-\*\s•]+",   "", clean_q).strip()
        story.append(Paragraph(f"{idx}. {safe(clean_q)}", body_style))
        story.append(Spacer(1, 8))

    # ── Build ───────────────────────────────────────────────────────────────
    try:
        doc.build(story)
    except Exception as e:
        # Re-raise with a clearer message so Render logs show the real cause
        raise RuntimeError(f"ReportLab build failed: {e}") from e

    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_report(profile, questions, target_role):
    """
    Generate a CSV report with profile details and interview questions.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["SECTION", "FIELD", "VALUE"])

    writer.writerow(["Profile", "Candidate Name", profile.get("name", "N/A")])
    writer.writerow(["Profile", "Education",      profile.get("education", "N/A")])
    writer.writerow(["Profile", "Target Role",    target_role])
    writer.writerow(["Profile", "Readiness Score", f"{profile.get('readiness', 0)}%"])

    certs_list = profile.get("certifications", [])
    exp_list   = profile.get("experience", [])
    writer.writerow(["Profile", "Certifications", ", ".join(certs_list) if certs_list else "None"])
    writer.writerow(["Profile", "Experience",     ", ".join(exp_list)   if exp_list   else "None"])

    matched_list = profile.get("matched_skills", [])
    missing_list = profile.get("missing_skills", [])
    all_skills   = profile.get("skills", [])
    writer.writerow(["Skill Gap", "Matched Skills", ", ".join(matched_list) if matched_list else "None"])
    writer.writerow(["Skill Gap", "Missing Skills", ", ".join(missing_list) if missing_list else "None"])
    writer.writerow(["Skill Gap", "All Skills",     ", ".join(all_skills)   if all_skills   else "None"])

    writer.writerow([])

    writer.writerow(["QUESTION #", "INTERVIEW QUESTION"])
    for idx, question in enumerate(questions, 1):
        clean_q = re.sub(r"^\d+[\.\s\-]+", "", question).strip()
        clean_q = re.sub(r"^[\-\*\s•]+",   "", clean_q).strip()
        writer.writerow([idx, clean_q])

    return output.getvalue().encode("utf-8")