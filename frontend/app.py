import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="Psychometric Testing Platform", layout="wide")
st.title("Student Psychometric & Stream Selection Portal")

tabs = st.tabs(["Individual Student Assessment", "Paper Test Batch Upload (Excel)"])

# -------------------------------------------------------------
# TAB 1: INDIVIDUAL TEST
# -------------------------------------------------------------
with tabs[0]:
    st.subheader("Take the Assessment")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Student Full Name", value="Rohan Mehta")
    with col2:
        grade = st.selectbox("Current Grade", options=[8, 9, 10, 11, 12], index=2)
    with col3:
        provider = st.selectbox("AI Counselor Engine", options=["gemini", "openai"])

    st.markdown("---")
    st.markdown("#### Rate each statement from 1 (*Strongly Disagree*) to 5 (*Strongly Agree*):")

    responses = []
    
    # Career Interest Items
    st.markdown("##### Part 1: Career Interests")
    q_ria_r = st.slider("1. I like building, repairing, or assembling mechanical items.", 1, 5, 3, key="RIA_R01")
    q_ria_i = st.slider("2. I enjoy solving science experiments, logic puzzles, or coding.", 1, 5, 4, key="RIA_I01")
    q_ria_a = st.slider("3. I like writing creative stories, designing graphics, or music.", 1, 5, 2, key="RIA_A01")
    q_ria_s = st.slider("4. I enjoy mentoring, teaching, and helping people resolve problems.", 1, 5, 4, key="RIA_S01")
    q_ria_e = st.slider("5. I like leading teams, debating ideas, and pitching business plans.", 1, 5, 5, key="RIA_E01")
    q_ria_c = st.slider("6. I prefer structured routines, organizing data, and following rules.", 1, 5, 3, key="RIA_C01")

    # Aptitude Items
    st.markdown("##### Part 2: Cognitive Aptitude")
    q_apt_num = st.slider("7. I solve math equations and numerical puzzles quickly.", 1, 5, 4, key="APT_NUM01")
    q_apt_ver = st.slider("8. I comprehend complex texts easily and express ideas fluently.", 1, 5, 4, key="APT_VER01")
    q_apt_spa = st.slider("9. I can visualize 3D shapes, diagrams, and patterns easily.", 1, 5, 3, key="APT_SPA01")

    # Personality Items
    st.markdown("##### Part 3: Work & Study Personality")
    q_ipip_o = st.slider("10. I have a vivid imagination and love exploring new theories.", 1, 5, 4, key="IPIP_O01")
    q_ipip_c = st.slider("11. I complete tasks right away and pay attention to details.", 1, 5, 4, key="IPIP_C01")

    payload_responses = [
        {"item_id": "RIA_R01", "value": q_ria_r},
        {"item_id": "RIA_I01", "value": q_ria_i},
        {"item_id": "RIA_A01", "value": q_ria_a},
        {"item_id": "RIA_S01", "value": q_ria_s},
        {"item_id": "RIA_E01", "value": q_ria_e},
        {"item_id": "RIA_C01", "value": q_ria_c},
        {"item_id": "APT_NUM01", "value": q_apt_num},
        {"item_id": "APT_VER01", "value": q_apt_ver},
        {"item_id": "APT_SPA01", "value": q_apt_spa},
        {"item_id": "IPIP_O01", "value": q_ipip_o},
        {"item_id": "IPIP_C01", "value": q_ipip_c},
    ]

    if st.button("Generate Assessment Report", type="primary"):
        payload = {
            "student_name": name,
            "student_grade": grade,
            "ai_provider": provider,
            "responses": payload_responses
        }
        with st.spinner("Processing results and generating AI counseling insights..."):
            try:
                res = requests.post(f"{API_URL}/submit", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.success("Analysis Complete!")
                    
                    st.markdown("### AI Counselor Evaluation")
                    st.info(data["ai_summary"])

                    st.markdown("### Top Recommended Streams")
                    for s in data["streams"]:
                        st.markdown(f"- **{s['stream']}** ({s['fit']} Fit) — *{s['careers']}*")

                    pdf_res = requests.post(f"{API_URL}/pdf", json=payload)
                    if pdf_res.status_code == 200:
                        st.download_button(
                            label="Download Official PDF Report",
                            data=pdf_res.content,
                            file_name=f"{name}_Report.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.error("Error from backend server.")
            except requests.exceptions.ConnectionError:
                st.error("Could not reach FastAPI backend. Start it with `uvicorn api.main:app`.")

# -------------------------------------------------------------
# TAB 2: BATCH EXCEL UPLOAD FOR PAPER TESTS
# -------------------------------------------------------------
with tabs[1]:
    st.subheader("Process Paper Tests from Excel")
    st.markdown(
        "Upload an `.xlsx` file where column headers match Item IDs (`RIA_R01`, `APT_NUM01`, etc.)."
    )

    batch_provider = st.selectbox("AI Engine for Batch Evaluation", options=["gemini", "openai"], key="batch_ai")
    uploaded_file = st.file_uploader("Upload Student Answers Sheet", type=["xlsx", "xls"])

    if uploaded_file is not None:
        if st.button("Process Batch Upload"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"ai_provider": batch_provider}
            
            with st.spinner("Processing batch records and scoring paper assessments..."):
                try:
                    res = requests.post(f"{API_URL}/upload-excel", files=files, data=data)
                    if res.status_code == 200:
                        batch_data = res.json()
                        st.success(f"Successfully processed {batch_data['processed_count']} students!")
                        
                        summary_rows = []
                        for s in batch_data["students"]:
                            summary_rows.append({
                                "ID": s["student_id"],
                                "Name": s["student_name"],
                                "Grade": s["grade"],
                                "Recommended Stream": s["top_stream"],
                                "Counselor Insight": s["ai_summary"][:100] + "..."
                            })
                        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)
                    else:
                        st.error(f"Upload failed: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to FastAPI server.")
