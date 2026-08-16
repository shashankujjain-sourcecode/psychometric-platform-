import io
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_student_pdf(
    name: str,
    grade: int,
    scores: Dict[str, float],
    streams: List[dict],
    ai_summary: str
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#1D4ED8"), spaceBefore=6, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=12)
    italic_body = ParagraphStyle('ItalicBody', parent=styles['Normal'], fontSize=8.5, leading=11, fontName='Helvetica-Oblique')

    # Header
    story.append(Paragraph("Comprehensive Student Psychometric & Career Report", title_style))
    story.append(Paragraph(f"<b>Student:</b> {name} &nbsp;|&nbsp; <b>Grade:</b> Class {grade} &nbsp;|&nbsp; <b>Framework:</b> IPIP & RIASEC Open Models", body_style))
    story.append(Spacer(1, 10))

    # AI Counselor Insight
    story.append(Paragraph("Psychological Evaluation & Counselor Insights", h2_style))
    story.append(Paragraph(ai_summary.replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 10))

    # Academic Stream Recommendations
    story.append(Paragraph("Recommended Academic Streams (Class 11/12)", h2_style))
    stream_rows = [["Recommended Stream", "Fit Level", "Matched Career Trajectories"]]
    for s in streams:
        stream_rows.append([s['stream'], s['fit'], s['careers']])
    
    t_stream = Table(stream_rows, colWidths=[150, 75, 315])
    t_stream.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EFF6FF")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_stream)
    story.append(Spacer(1, 10))

    # Dimension Scores
    story.append(Paragraph("Trait & Aptitude Scores (0 - 100%)", h2_style))
    score_rows = [["Dimension", "Score", "Dimension", "Score"]]
    items = list(scores.items())
    for i in range(0, len(items), 2):
        col1_name, col1_val = items[i]
        col2_name, col2_val = items[i+1] if i+1 < len(items) else ("", "")
        score_rows.append([col1_name, f"{col1_val}%" if col1_val != "" else "", col2_name, f"{col2_val}%" if col2_val != "" else ""])

    t_scores = Table(score_rows, colWidths=[190, 80, 190, 80])
    t_scores.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_scores)
    story.append(Spacer(1, 10))

    # Disclaimer
    disclaimer = (
        "Disclaimer: This report is generated algorithmically for educational guidance using open-domain psychological scales. "
        "It does not constitute a clinical psychological assessment. Indian DPDP Act minor data compliance applies."
    )
    story.append(Paragraph(disclaimer, italic_body))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
