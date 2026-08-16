import streamlit as st

st.set_page_config(page_title="Student Career Assessment", layout="centered")

st.title("Student Psychometric & Career Stream Selector")
st.write("Rate each statement from **1 (Strongly Disagree)** to **5 (Strongly Agree)**.")

# ---------------------------------------------------------
# QUESTION BANK
# ---------------------------------------------------------
QUESTIONS = [
    {"id": "r", "scale": "Realistic (Hands-on / Technical)", "text": "I enjoy working with tools, machines, or assembling physical objects."},
    {"id": "i", "scale": "Investigative (Analytical / Science)", "text": "I enjoy solving science experiments, math logic, or writing code."},
    {"id": "a", "scale": "Artistic (Creative / Design)", "text": "I like creative writing, visual design, sketching, or music."},
    {"id": "s", "scale": "Social (Teaching / Counseling)", "text": "I enjoy teaching, volunteering, mentoring, and helping other people."},
    {"id": "e", "scale": "Enterprising (Leadership / Business)", "text": "I like leading teams, public speaking, debating, and business ideas."},
    {"id": "c", "scale": "Conventional (Organization / Data)", "text": "I prefer structured routines, organizing files, and tracking data."},
    {"id": "num", "scale": "Numerical Aptitude", "text": "I solve math equations and numerical logic puzzles with ease."},
    {"id": "verb", "scale": "Verbal Aptitude", "text": "I comprehend long reading passages and express ideas clearly in English."},
]

# ---------------------------------------------------------
# INPUT FORM
# ---------------------------------------------------------
with st.form("quiz_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input("Student Name", value="Student")
    with col2:
        grade = st.selectbox("Current Grade", [8, 9, 10, 11, 12], index=2)

    st.divider()

    answers = {}
    for item in QUESTIONS:
        answers[item["id"]] = st.slider(
            f"**{item['scale']}**\n\n{item['text']}",
            min_value=1,
            max_value=5,
            value=3,
            key=item["id"]
        )

    submit_button = st.form_submit_button("Submit Assessment & View Results", type="primary")

# ---------------------------------------------------------
# SCORING & REPORT GENERATION
# ---------------------------------------------------------
if submit_button:
    # 1. Compute Percentages
    r = answers["r"] * 20
    i = answers["i"] * 20
    a = answers["a"] * 20
    s = answers["s"] * 20
    e = answers["e"] * 20
    c = answers["c"] * 20
    num = answers["num"] * 20
    verb = answers["verb"] * 20

    # 2. Compute Stream Fit
    pcm = int((i * 0.4) + (num * 0.4) + (r * 0.2))
    pcb = int((i * 0.4) + (s * 0.3) + (verb * 0.3))
    comm = int((e * 0.35) + (c * 0.35) + (num * 0.3))
    hum = int((a * 0.4) + (s * 0.3) + (verb * 0.3))

    stream_data = [
        {"stream": "Science (PCM)", "fit": pcm, "careers": "Engineering, Computer Science, AI, Architecture"},
        {"stream": "Science (PCB)", "fit": pcb, "careers": "Medicine (MBBS), Biotechnology, Clinical Psychology"},
        {"stream": "Commerce (with Applied Math)", "fit": comm, "careers": "Chartered Accountancy, Finance, Business Analytics"},
        {"stream": "Humanities / Liberal Arts", "fit": hum, "careers": "Corporate Law, Public Policy, Journalism, Civil Services"},
    ]
    stream_data.sort(key=lambda x: x["fit"], reverse=True)

    # 3. Render Results to Screen
    st.success("Assessment Complete!")

    st.subheader("Recommended Stream Rankings (Class 11 & 12)")
    for rank, item in enumerate(stream_data, 1):
        st.markdown(f"**{rank}. {item['stream']}** — `{item['fit']}% Match`")
        st.caption(f"Target Careers: {item['careers']}")
        st.progress(item["fit"] / 100.0)

    # 4. Printable HTML Report Generation
    report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{name} - Career Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; color: #1e293b; }}
            h1 {{ color: #1e40af; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
            .card {{ background: #f8fafc; border: 1px solid #cbd5e1; padding: 15px; border-radius: 8px; margin-bottom: 12px; }}
            .score {{ font-weight: bold; color: #2563eb; }}
        </style>
    </head>
    <body>
        <h1>Student Psychometric & Stream Selection Report</h1>
        <p><strong>Candidate:</strong> {name} | <strong>Class:</strong> Grade {grade}</p>
        <hr/>
        <h2>Stream Fitment Rankings</h2>
        {"".join([f"<div class='card'><h3>{idx+1}. {s['stream']} — <span class='score'>{s['fit']}% Match</span></h3><p><strong>Career Trajectories:</strong> {s['careers']}</p></div>" for idx, s in enumerate(stream_data)])}
        <br/>
        <p><em>Note: Save or print this document as a PDF using your browser's Print dialog (Ctrl+P / Cmd+P).</em></p>
    </body>
    </html>
    """

    st.divider()
    st.download_button(
        label="📥 Download Formatted Report (.html)",
        data=report_html,
        file_name=f"{name}_Assessment_Report.html",
        mime="text/html",
        use_container_width=True
    )
