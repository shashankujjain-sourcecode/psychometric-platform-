import io
import html
import streamlit as st
import pandas as pd

# Optional ReportLab import with fallback
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

st.set_page_config(page_title="Psychometric Assessment", layout="wide")

# -------------------------------------------------------------
# 1. QUESTION DATA
# -------------------------------------------------------------
QUESTIONS = [
    {"id": "RIA_R", "scale": "Realistic", "text": "I enjoy working with tools, mechanics, or building physical objects."},
    {"id": "RIA_I", "scale": "Investigative", "text": "I enjoy solving science experiments, math logic, or writing code."},
    {"id": "RIA_A", "scale": "Artistic", "text": "I enjoy creative writing, visual design, sketch art, or music."},
    {"id": "RIA_S", "scale": "Social", "text": "I enjoy teaching, counseling, mentoring, and helping other people."},
    {"id": "RIA_E", "scale": "Enterprising", "text": "I enjoy leading projects, public speaking, debating, and business."},
    {"id": "RIA_C", "scale": "Conventional", "text": "I like clear rules, organizing files, tracking data, and schedules."},
    {"id": "APT_NUM", "scale": "Numerical Aptitude", "text": "I solve math equations and numerical logic puzzles with ease."},
    {"id": "APT_VER", "scale": "Verbal Aptitude", "text": "I express ideas fluently in English and grasp long articles easily."},
]

def score_test(responses):
    scores = {q["scale"]: round((responses.get(q["id"], 3) / 5.0) * 100, 1) for q in QUESTIONS}
    
    num = scores.get("Numerical Aptitude", 0)
    verb = scores.get("Verbal Aptitude", 0)
    r = scores.get("Realistic", 0)
    i = scores.get("Investigative", 0)
    a = scores.get("Artistic", 0)
    s = scores.get("Social", 0)
    e = scores.get("Enterprising", 0)
    c = scores.get("Conventional", 0)

    pcm_score = int((i * 0.4) + (num * 0.4) + (r * 0.2))
    pcb_score = int((i * 0.4) + (s * 0.3) + (verb * 0.3))
    comm_score = int((e * 0.35) + (c * 0.35) + (num * 0.3))
    hum_score = int((a * 0.4) + (s * 0.3) + (verb * 0.3))

    stream_list = [
        {"stream": "Science (PCM)", "fit": pcm_score, "careers": "Engineering, AI & Computing, Architecture, Physics"},
        {"stream": "Science (PCB)", "fit": pcb_score, "careers": "Medicine, Biotechnology, Psychology, Genetics"},
        {"stream": "Commerce (with Math)", "fit": comm_score, "careers": "Chartered Accountancy, Finance, Business Analytics"},
        {"stream": "Humanities / Arts", "fit": hum_score, "careers": "Law, Journalism, Civil Services (UPSC), Design"}
    ]
    stream_list.sort(key=lambda x: x["fit"], reverse=True)
    return scores, stream_list

def create_pdf(name, grade, scores, streams):
    if not REPORTLAB_AVAILABLE:
        return None
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#2563EB"))
    body_style = styles['Normal']

    story.append(Paragraph("Student Career Assessment Report", title_style))
    story.append(Paragraph(f"<b>Student Name:</b> {html.escape(name)} | <b>Grade:</b> Class {grade}", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Stream Match Rankings", h2_style))
    rows = [["Academic Stream", "Match Score", "Career Pathways"]]
    for item in streams:
        rows.append([item["stream"], f"{item['fit']}%", item["careers"]])
    
    t = Table(rows, colWidths=[150, 80, 310])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EFF6FF")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------------------
# 2. UI LAYOUT
# -------------------------------------------------------------
st.title("Student Psychometric & Stream Selection Portal")
st.write("Complete the ratings below and click **Generate Report**.")

col_name, col_grade = st.columns([3, 1])
student_name = col_name.text_input("Student Name", value="Aarav Sharma")
student_grade = col_grade.selectbox("Class/Grade", [8, 9, 10, 11, 12], index=2)

st.divider()

user_answers = {}
col_left, col_right = st.columns(2)

for index, item in enumerate(QUESTIONS):
    target_col = col_left if index % 2 == 0 else col_right
    with target_col:
        user_answers[item["id"]] = st.slider(
            f"**{item['scale']}**: {item['text']}",
            min_value=1,
            max_value=5,
            value=3,
            key=item["id"]
        )

st.divider()

if st.button("Generate Assessment Results", type="primary", use_container_width=True):
    try:
        calculated_scores, ranked_streams = score_test(user_answers)
        
        st.success("Assessment Calculated Successfully!")
        
        # Display Stream Cards
        st.subheader("Recommended Stream Rankings")
        cols = st.columns(len(ranked_streams))
        for idx, stream in enumerate(ranked_streams):
            with cols[idx]:
                st.metric(label=stream["stream"], value=f"{stream['fit']}%")
                st.caption(f"**Careers:** {stream['careers']}")

        # Display Trait Scores
        st.subheader("Detailed Trait Scores")
        chart_df = pd.DataFrame(list(calculated_scores.items()), columns=["Trait", "Score (%)"])
        st.dataframe(chart_df, use_container_width=True)

        # PDF Download Section
        pdf_data = create_pdf(student_name, student_grade, calculated_scores, ranked_streams)
        if pdf_data:
            st.download_button(
                label="📥 Download Official PDF Report",
                data=pdf_data,
                file_name=f"{student_name}_Assessment.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Install `reportlab` to enable PDF downloads: `pip install reportlab`")

    except Exception as e:
        st.error(f"Error while processing results: {e}")
