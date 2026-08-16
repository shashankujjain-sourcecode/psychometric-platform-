import io
import os
import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -------------------------------------------------------------
# 1. PSYCHOMETRIC ITEM BANK & SCORING ENGINE
# -------------------------------------------------------------
ITEM_BANK = {
    # RIASEC Career Interests
    "RIA_R01": {"scale": "Realistic", "reverse": False},
    "RIA_I01": {"scale": "Investigative", "reverse": False},
    "RIA_A01": {"scale": "Artistic", "reverse": False},
    "RIA_S01": {"scale": "Social", "reverse": False},
    "RIA_E01": {"scale": "Enterprising", "reverse": False},
    "RIA_C01": {"scale": "Conventional", "reverse": False},
    # Aptitude Dimensions
    "APT_NUM01": {"scale": "Numerical Aptitude", "reverse": False},
    "APT_VER01": {"scale": "Verbal Aptitude", "reverse": False},
    "APT_SPA01": {"scale": "Spatial Reasoning", "reverse": False},
    # Big Five Traits
    "IPIP_O01": {"scale": "Openness", "reverse": False},
    "IPIP_C01": {"scale": "Conscientiousness", "reverse": False},
}

def calculate_profile(responses_dict):
    totals, counts = {}, {}
    for item_id, val in responses_dict.items():
        if item_id in ITEM_BANK:
            scale = ITEM_BANK[item_id]["scale"]
            score = (6 - val) if ITEM_BANK[item_id]["reverse"] else val
            totals[scale] = totals.get(scale, 0) + score
            counts[scale] = counts.get(scale, 0) + 1

    scores = {k: round((totals[k] / (counts[k] * 5.0)) * 100, 1) for k in totals}
    
    streams = []
    r_score = scores.get("Realistic", 0)
    i_score = scores.get("Investigative", 0)
    a_score = scores.get("Artistic", 0)
    s_score = scores.get("Social", 0)
    e_score = scores.get("Enterprising", 0)
    c_score = scores.get("Conventional", 0)
    num_score = scores.get("Numerical Aptitude", 0)
    verb_score = scores.get("Verbal Aptitude", 0)

    if (r_score >= 50 or i_score >= 50) and num_score >= 50:
        streams.append({"stream": "Science (PCM)", "fit": "High", "careers": "Engineering, Data Science, Physical Sciences"})
    if (i_score >= 50 or s_score >= 50) and verb_score >= 45:
        streams.append({"stream": "Science (PCB)", "fit": "High", "careers": "Medicine, Biotechnology, Psychology"})
    if e_score >= 50 or c_score >= 50:
        math_tag = "with Math" if num_score >= 50 else "General"
        streams.append({"stream": f"Commerce ({math_tag})", "fit": "High", "careers": "Finance, CA, Management, Economics"})
    if a_score >= 50 or s_score >= 50:
        streams.append({"stream": "Humanities / Arts", "fit": "High", "careers": "Law, Journalism, Design, Civil Services"})
    if not streams:
        streams.append({"stream": "General Interdisciplinary", "fit": "Moderate", "careers": "Liberal Arts, Business Administration"})

    return scores, streams

# -------------------------------------------------------------
# 2. AI COUNSELOR INTEGRATION (GEMINI / OPENAI / FALLBACK)
# -------------------------------------------------------------
def get_ai_counselor_summary(name, grade, scores, streams, provider="gemini"):
    gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

    prompt = f"""
    You are an expert school psychologist and career counselor in India.
    Provide a supportive, empowering 3-paragraph counseling narrative for a student.
    
    Student Name: {name}
    Current Grade: Class {grade}
    Psychometric Profile Scores: {scores}
    Recommended Streams: {[s['stream'] for s in streams]}
    
    Structure:
    1. Acknowledge top cognitive and interest strengths.
    2. Explain the fit for Class 11/12 Indian academic streams.
    3. Suggest two concrete skill development areas.
    Keep the tone objective, encouraging, and under 150 words.
    """

    if provider == "gemini" and gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
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
            return completion.choices[0].message.content
        except Exception:
            pass

    top_stream = streams[0]["stream"] if streams else "General Studies"
    return (
        f"{name} demonstrates a balanced cognitive and interest profile with strong alignment toward "
        f"the {top_stream} stream. Focusing on analytical concepts while engaging in project-based learning "
        f"will provide clear direction for higher secondary education."
    )

# -------------------------------------------------------------
# 3. DIRECT PDF GENERATION
# -------------------------------------------------------------
def create_pdf_report(name, grade, scores, streams, ai_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#1E3A8A"))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#1D4ED8"), spaceBefore=6, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, leading=12)
    italic_body = ParagraphStyle('ItalicBody', parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Oblique', textColor=colors.gray)

    story.append(Paragraph("Student Psychometric & Career Evaluation Report", title_style))
    story.append(Paragraph(f"<b>Student:</b> {name} &nbsp;|&nbsp; <b>Grade:</b> Class {grade} &nbsp;|&nbsp; <b>Framework:</b> IPIP & RIASEC", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("AI Counselor Analysis & Recommendations", h2_style))
    story.append(Paragraph(ai_text.replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Recommended Academic Streams (Class 11/12)", h2_style))
    stream_rows = [["Recommended Stream", "Fit Level", "Example Pathways"]]
    for s in streams:
        stream_rows.append([s['stream'], s['fit'], s['careers']])
    
    t_stream = Table(stream_rows, colWidths=[150, 75, 315])
    t_stream.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EFF6FF")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_stream)
    story.append(Spacer(1, 10))

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

    disclaimer = (
        "Disclaimer: This report is an educational guidance summary generated using open-domain psychological inventories. "
        "It does not constitute a clinical psychological assessment."
    )
    story.append(Paragraph(disclaimer, italic_body))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -------------------------------------------------------------
# 4. STREAMLIT APPLICATION INTERFACE
# -------------------------------------------------------------
st.set_page_config(page_title="Psychometric Testing Platform", layout="wide")
st.title("Student Psychometric & Stream Selection Portal")

tabs = st.tabs(["Individual Student Assessment", "Paper Test Batch Upload (Excel)"])

with tabs[0]:
    st.subheader("Take the Assessment")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Student Name", value="Aarav Sharma")
    with col2:
        grade = st.selectbox("Current Grade", options=[8, 9, 10, 11, 12], index=2)
    with col3:
        provider = st.selectbox("AI Model Engine", options=["gemini", "openai"])

    st.markdown("---")
    st.markdown("#### Rate each statement from 1 (*Strongly Disagree*) to 5 (*Strongly Agree*):")

    st.markdown("##### Part 1: Career Interests (RIASEC)")
    q1 = st.slider("1. I enjoy mechanical tools, repairing, or building things.", 1, 5, 3)
    q2 = st.slider("2. I like science experiments, logic puzzles, or coding.", 1, 5, 4)
    q3 = st.slider("3. I like creative arts, writing, and design.", 1, 5, 2)
    q4 = st.slider("4. I enjoy teaching, volunteering, and mentoring others.", 1, 5, 4)
    q5 = st.slider("5. I like leading projects, debate, and business strategy.", 1, 5, 5)
    q6 = st.slider("6. I prefer clear routines, organization, and data management.", 1, 5, 3)

    st.markdown("##### Part 2: Cognitive Aptitude")
    q7 = st.slider("7. I solve math equations and numerical logic quickly.", 1, 5, 4)
    q8 = st.slider("8. I express ideas clearly in English and comprehend long passages.", 1, 5, 4)
    q9 = st.slider("9. I can easily visualize 3D spaces and diagram patterns.", 1, 5, 3)

    st.markdown("##### Part 3: Work & Learning Personality")
    q10 = st.slider("10. I love exploring new concepts and big theoretical ideas.", 1, 5, 4)
    q11 = st.slider("11. I keep my study tasks organized and complete work on time.", 1, 5, 4)

    if st.button("Generate Assessment Report", type="primary"):
        test_inputs = {
            "RIA_R01": q1, "RIA_I01": q2, "RIA_A01": q3, "RIA_S01": q4, "RIA_E01": q5,
            "RIA_C01": q6, "APT_NUM01": q7, "APT_VER01": q8, "APT_SPA01": q9,
            "IPIP_O01": q10, "IPIP_C01": q11
        }
        with st.spinner("Calculating profile and generating AI insights..."):
            scores, streams = calculate_profile(test_inputs)
            ai_summary = get_ai_counselor_summary(name, grade, scores, streams, provider)

            st.success("Analysis Complete!")
            
            st.markdown("### AI Counselor Guidance")
            st.info(ai_summary)

            st.markdown("### Recommended Academic Streams")
            for s in streams:
                st.markdown(f"- **{s['stream']}** ({s['fit']} Fit) — *{s['careers']}*")

            pdf_bytes = create_pdf_report(name, grade, scores, streams, ai_summary)
            st.download_button(
                label="Download Official PDF Report",
                data=pdf_bytes,
                file_name=f"{name}_Psychometric_Report.pdf",
                mime="application/pdf"
            )

with tabs[1]:
    st.subheader("Process Paper Tests from Excel")
    st.markdown("Upload an `.xlsx` file containing student responses matched to question IDs.")
    
    batch_provider = st.selectbox("AI Engine for Batch Evaluation", options=["gemini", "openai"], key="batch_ai")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    
    if uploaded_file and st.button("Process Batch Upload"):
        with st.spinner("Processing batch records..."):
            df = pd.read_excel(uploaded_file)
            results = []
            for _, row in df.iterrows():
                resp = {col: int(row[col]) for col in df.columns if col in ITEM_BANK and pd.notna(row[col])}
                scores, streams = calculate_profile(resp)
                ai_sum = get_ai_counselor_summary(str(row.get("student_name", "Student")), int(row.get("grade", 10)), scores, streams, batch_provider)
                
                results.append({
                    "Student ID": row.get("student_id", "N/A"),
                    "Name": row.get("student_name", "N/A"),
                    "Grade": row.get("grade", "N/A"),
                    "Recommended Stream": streams[0]["stream"] if streams else "General",
                    "AI Summary": ai_sum[:120] + "..."
                })
            st.dataframe(pd.DataFrame(results), use_container_width=True)
