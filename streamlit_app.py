import io
import os
import html
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -------------------------------------------------------------
# 1. FIXED QUESTION BANK & SCORING TAXONOMY
# -------------------------------------------------------------
QUESTIONS = [
    # RIASEC Career Interests
    {"id": "RIA_R", "scale": "Realistic", "category": "Career Interest", "text": "Building, repairing, or assembling physical equipment and tools"},
    {"id": "RIA_I", "scale": "Investigative", "category": "Career Interest", "text": "Solving scientific puzzles, data problems, or coding algorithms"},
    {"id": "RIA_A", "scale": "Artistic", "category": "Career Interest", "text": "Designing visual media, creative writing, or artistic concepts"},
    {"id": "RIA_S", "scale": "Social", "category": "Career Interest", "text": "Teaching, counseling, mentoring, and helping other people"},
    {"id": "RIA_E", "scale": "Enterprising", "category": "Career Interest", "text": "Leading teams, public speaking, business management, and debating"},
    {"id": "RIA_C", "scale": "Conventional", "category": "Career Interest", "text": "Organizing data, following strict routines, and managing records"},
    
    # Cognitive Aptitudes
    {"id": "APT_NUM", "scale": "Numerical Aptitude", "category": "Aptitude", "text": "Solving mathematical equations and quantitative problems accurately"},
    {"id": "APT_VER", "scale": "Verbal Aptitude", "category": "Aptitude", "text": "Comprehending long passages and expressing ideas fluently in English"},
    {"id": "APT_SPA", "scale": "Spatial Reasoning", "category": "Aptitude", "text": "Visualizing 3D transformations, architectural spaces, and patterns"},
    
    # Personality & Study Style
    {"id": "IPIP_OPN", "scale": "Curiosity & Openness", "category": "Personality", "text": "Exploring complex theories, philosophical ideas, and innovations"},
    {"id": "IPIP_CON", "scale": "Conscientiousness & Focus", "category": "Personality", "text": "Maintaining a disciplined study schedule and completing work on time"}
]

def score_assessment(answers: dict):
    scores = {}
    for q in QUESTIONS:
        val = answers.get(q["id"], 3)
        scores[q["scale"]] = round((val / 5.0) * 100, 1)

    num = scores.get("Numerical Aptitude", 0)
    verb = scores.get("Verbal Aptitude", 0)
    r = scores.get("Realistic", 0)
    i = scores.get("Investigative", 0)
    a = scores.get("Artistic", 0)
    s = scores.get("Social", 0)
    e = scores.get("Enterprising", 0)
    c = scores.get("Conventional", 0)

    pcm_fit = int((i * 0.4) + (num * 0.4) + (r * 0.2))
    pcb_fit = int((i * 0.4) + (s * 0.3) + (verb * 0.3))
    comm_math_fit = int((e * 0.35) + (c * 0.35) + (num * 0.3))
    hum_fit = int((a * 0.4) + (s * 0.3) + (verb * 0.3))

    streams = [
        {
            "stream": "Science (PCM)",
            "fit_score": pcm_fit,
            "rating": "High Fit" if pcm_fit >= 70 else ("Moderate Fit" if pcm_fit >= 50 else "Exploratory"),
            "curriculum": "Physics, Chemistry, Mathematics, CS / Informatics",
            "careers": "Engineering, Data Science, AI, Architecture, Physics"
        },
        {
            "stream": "Science (PCB)",
            "fit_score": pcb_fit,
            "rating": "High Fit" if pcb_fit >= 70 else ("Moderate Fit" if pcb_fit >= 50 else "Exploratory"),
            "curriculum": "Physics, Chemistry, Biology, Psychology",
            "careers": "Medicine (MBBS), Biotechnology, Clinical Psychology, Genetics"
        },
        {
            "stream": "Commerce (with Applied Math)",
            "fit_score": comm_math_fit,
            "rating": "High Fit" if comm_math_fit >= 70 else ("Moderate Fit" if comm_math_fit >= 50 else "Exploratory"),
            "curriculum": "Accountancy, Economics, Business Studies, Applied Math",
            "careers": "Chartered Accountancy (CA), Investment Banking, Corporate Finance"
        },
        {
            "stream": "Humanities / Liberal Arts",
            "fit_score": hum_fit,
            "rating": "High Fit" if hum_fit >= 70 else ("Moderate Fit" if hum_fit >= 50 else "Exploratory"),
            "curriculum": "History, Political Science, Sociology, English, Psychology",
            "careers": "Corporate Law, Public Policy, Journalism, Civil Services (UPSC)"
        }
    ]
    streams.sort(key=lambda x: x["fit_score"], reverse=True)
    return scores, streams

# -------------------------------------------------------------
# 2. AI COUNSELOR NARRATIVE GENERATOR
# -------------------------------------------------------------
def get_ai_counselor_narrative(name, grade, scores, streams, provider="gemini"):
    gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

    prompt = f"""
    You are an expert school psychologist and career counselor in India.
    Provide a supportive, empowering 3-paragraph counseling narrative for:
    Student: {name} (Class {grade})
    Top Stream Match: {streams[0]['stream']} (Fit Score: {streams[0]['fit_score']}%)
    Secondary Stream: {streams[1]['stream']} (Fit Score: {streams[1]['fit_score']}%)
    Scores: {scores}

    Provide:
    1. Core Strengths: Highlight top cognitive and interest drivers.
    2. Academic Path Recommendation: Explain why their primary stream fits Class 11/12 goals.
    3. Action Plan: 2 specific skill development areas.
    Keep the tone encouraging, structured, and under 150 words. Do not use special markdown formatting.
    """

    if provider == "gemini" and gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            if response and response.text:
                return response.text
        except Exception:
            pass

    if provider == "openai" and openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250
            )
            if completion.choices:
                return completion.choices[0].message.content
        except Exception:
            pass

    return (
        f"{name} demonstrates strong alignment with {streams[0]['stream']} based on balanced scores in "
        f"analytical and domain-specific interest areas. The student exhibits the cognitive aptitudes "
        f"and work consistency required for rigorous higher secondary coursework. Engaging with advanced "
        f"problem-solving exercises and participating in applied project workshops will reinforce these core strengths."
    )

# -------------------------------------------------------------
# 3. REPORTLAB SECTIONAL PDF GENERATION
# -------------------------------------------------------------
def make_progress_bar_table(score: float, width: float = 120):
    score = max(0.0, min(100.0, score))
    fill_w = (score / 100.0) * width
    empty_w = width - fill_w

    col_widths = [fill_w, empty_w] if fill_w > 0 and empty_w > 0 else ([width] if fill_w == 100 else [width])
    t = Table([["", ""]], colWidths=col_widths, rowHeights=[8])
    fill_color = colors.HexColor("#2563EB") if score >= 60 else (colors.HexColor("#059669") if score >= 40 else colors.HexColor("#D97706"))
    
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), fill_color if fill_w > 0 else colors.HexColor("#E5E7EB")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#E5E7EB")) if len(col_widths) > 1 else ('BACKGROUND', (0,0), (-1,-1), fill_color),
        ('PADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t

def generate_detailed_pdf(name: str, grade: int, scores: dict, streams: list, ai_text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=32, bottomMargin=32)
    styles = getSampleStyleSheet()
    story = []

    safe_name = html.escape(name)
    safe_ai_text = html.escape(ai_text).replace("\n", "<br/>")

    PRIMARY = colors.HexColor("#0F172A")
    ACCENT = colors.HexColor("#1D4ED8")
    BORDER_COLOR = colors.HexColor("#CBD5E1")

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=PRIMARY, fontName='Helvetica-Bold')
    h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, leading=14, textColor=ACCENT, fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor("#334155"))
    meta_style = ParagraphStyle('MetaText', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor("#475569"))

    # Header
    banner_data = [
        [Paragraph(f"<b>STUDENT PSYCHOMETRIC ASSESSMENT REPORT</b>", title_style), ""],
        [Paragraph(f"<b>Candidate:</b> {safe_name} &nbsp;|&nbsp; <b>Academic Level:</b> Class {grade} &nbsp;|&nbsp; <b>Standard:</b> CBSE/ICSE Stream Profiler", meta_style), ""]
    ]
    banner_table = Table(banner_data, colWidths=[400, 140])
    banner_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 1), (-1, 1), 1.5, ACCENT),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    # Section 1: Counselor Evaluation Box
    story.append(Paragraph("1. EXECUTIVE COUNSELOR EVALUATION", h2_style))
    ai_box_data = [[Paragraph(safe_ai_text, body_style)]]
    ai_box_table = Table(ai_box_data, colWidths=[540])
    ai_box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(ai_box_table)
    story.append(Spacer(1, 10))

    # Section 2: Stream Suitability
    story.append(Paragraph("2. ACADEMIC STREAM FITMENT MATRIX (CLASS 11 & 12)", h2_style))
    stream_rows = [["Academic Stream", "Fit Score", "Suitability", "Recommended Subject Tracks"]]
    for s in streams:
        stream_rows.append([
            Paragraph(f"<b>{html.escape(s['stream'])}</b>", body_style),
            f"{s['fit_score']}%",
            s['rating'],
            Paragraph(html.escape(s['curriculum']), body_style)
        ])
    
    stream_table = Table(stream_rows, colWidths=[150, 60, 80, 250])
    stream_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(stream_table)
    story.append(Spacer(1, 10))

    # Section 3: Dimension Scorecards
    story.append(Paragraph("3. PSYCHOMETRIC & COGNITIVE PROFILE SCORECARDS", h2_style))
    score_rows = [["Dimension Scale", "Score", "Visualization", "Domain Category"]]
    for q in QUESTIONS:
        scale_name = q["scale"]
        score_val = scores.get(scale_name, 0.0)
        score_rows.append([
            Paragraph(html.escape(scale_name), body_style),
            f"{score_val}%",
            make_progress_bar_table(score_val, width=110),
            Paragraph(html.escape(q["category"]), meta_style)
        ])

    score_table = Table(score_rows, colWidths=[160, 50, 120, 210])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    # Section 4: Target Careers
    story.append(Paragraph("4. RECOMMENDED DEGREE & CAREER TRAJECTORIES", h2_style))
    career_rows = [["Academic Stream", "Primary Career Trajectories"]]
    for s in streams[:3]:
        career_rows.append([
            Paragraph(f"<b>{html.escape(s['stream'])}</b>", body_style),
            Paragraph(html.escape(s['careers']), body_style)
        ])
    
    career_table = Table(career_rows, colWidths=[150, 390])
    career_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(career_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------------------
# 4. STREAMLIT UI & PERSISTENT SESSION STATE
# -------------------------------------------------------------
st.set_page_config(page_title="Psychometric Portal", layout="wide")
st.title("Student Psychometric & Stream Selection Assessment")
st.caption("Standardized evaluation for Indian secondary school students (Classes 8–12)")

if "report_data" not in st.session_state:
    st.session_state.report_data = None

with st.form("psychometric_assessment_form"):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        student_name = st.text_input("Candidate Full Name", value="Ananya Sharma")
    with col_b:
        student_grade = st.selectbox("Current Academic Grade", [8, 9, 10, 11, 12], index=2)
    with col_c:
        ai_engine = st.selectbox("AI Counselor Engine", ["gemini", "openai"])

    st.markdown("---")
    st.subheader("Questionnaire (Rate 1: Strongly Disagree to 5: Strongly Agree)")

    temp_answers = {}

    # Section A
    st.markdown("#### Part 1: Career Interests (RIASEC)")
    c1, c2 = st.columns(2)
    interests = [q for q in QUESTIONS if q["category"] == "Career Interest"]
    for idx, q in enumerate(interests):
        col = c1 if idx % 2 == 0 else c2
        with col:
            temp_answers[q["id"]] = st.slider(f"**{q['scale']}**: {q['text']}", 1, 5, 3, key=f"q_{q['id']}")

    # Section B
    st.markdown("#### Part 2: Cognitive Aptitude")
    c3, c4 = st.columns(2)
    aptitudes = [q for q in QUESTIONS if q["category"] == "Aptitude"]
    for idx, q in enumerate(aptitudes):
        col = c3 if idx % 2 == 0 else c4
        with col:
            temp_answers[q["id"]] = st.slider(f"**{q['scale']}**: {q['text']}", 1, 5, 4, key=f"q_{q['id']}")

    # Section C
    st.markdown("#### Part 3: Learning Habits & Personality")
    c5, c6 = st.columns(2)
    personality = [q for q in QUESTIONS if q["category"] == "Personality"]
    for idx, q in enumerate(personality):
        col = c5 if idx % 2 == 0 else c6
        with col:
            temp_answers[q["id"]] = st.slider(f"**{q['scale']}**: {q['text']}", 1, 5, 4, key=f"q_{q['id']}")

    st.markdown("---")
    submitted = st.form_submit_button("Generate Full Assessment Report", type="primary")

    if submitted:
        scores, streams = score_assessment(temp_answers)
        ai_narrative = get_ai_counselor_narrative(student_name, student_grade, scores, streams, ai_engine)
        pdf_bytes = generate_detailed_pdf(student_name, student_grade, scores, streams, ai_narrative)
        
        st.session_state.report_data = {
            "name": student_name,
            "grade": student_grade,
            "scores": scores,
            "streams": streams,
            "ai_narrative": ai_narrative,
            "pdf_bytes": pdf_bytes
        }

# Render persistent results outside the form
if st.session_state.report_data is not None:
    data = st.session_state.report_data
    st.success("Assessment Evaluation Complete!")

    st.markdown("### 1. Counselor Evaluation")
    st.info(data["ai_narrative"])

    st.markdown("### 2. Stream Match Scores")
    s_cols = st.columns(len(data["streams"]))
    for i, s in enumerate(data["streams"]):
        with s_cols[i]:
            st.metric(label=s["stream"], value=f"{s['fit_score']}%", delta=s["rating"])
            st.caption(f"**Curriculum:** {s['curriculum']}")

    st.markdown("---")
    st.download_button(
        label="Download Official PDF Report",
        data=data["pdf_bytes"],
        file_name=f"{data['name']}_Career_Report.pdf",
        mime="application/pdf"
    )
