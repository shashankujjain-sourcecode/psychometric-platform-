from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import pandas as pd
import io

from api.item_bank import ITEM_BANK
from api.ai_service import generate_counselor_narrative
from api.pdf_generator import generate_student_pdf

app = FastAPI(title="Open Psychometric Assessment API")

class SingleResponse(BaseModel):
    item_id: str
    value: int = Field(..., ge=1, le=5)

class WebSubmission(BaseModel):
    student_name: str
    student_grade: int = Field(..., ge=8, le=12)
    ai_provider: Optional[str] = "gemini"
    responses: List[SingleResponse]

def calculate_results(responses_dict: Dict[str, int]):
    scale_totals = {}
    scale_counts = {}

    for item_id, val in responses_dict.items():
        if item_id in ITEM_BANK:
            meta = ITEM_BANK[item_id]
            scale = meta["scale"]
            score = (6 - val) if meta["reverse"] else val
            scale_totals[scale] = scale_totals.get(scale, 0) + score
            scale_counts[scale] = scale_counts.get(scale, 0) + 1

    scores = {
        k: round((scale_totals[k] / (scale_counts[k] * 5.0)) * 100, 1)
        for k in scale_totals
    }

    # Determine Streams
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
        math_status = "with Math" if num_score >= 50 else "General"
        streams.append({"stream": f"Commerce ({math_status})", "fit": "High", "careers": "Finance, CA, Management, Economics"})
    if a_score >= 50 or s_score >= 50:
        streams.append({"stream": "Humanities / Arts", "fit": "High", "careers": "Law, Journalism, Design, Civil Services"})
    
    if not streams:
        streams.append({"stream": "General Interdisciplinary", "fit": "Moderate", "careers": "Liberal Arts, Business Administration"})

    return scores, streams

@app.post("/api/submit")
async def evaluate_web_test(data: WebSubmission):
    resp_dict = {r.item_id: r.value for r in data.responses}
    scores, streams = calculate_results(resp_dict)
    ai_summary = generate_counselor_narrative(data.student_name, data.student_grade, scores, streams, data.ai_provider)
    return {"scores": scores, "streams": streams, "ai_summary": ai_summary}

@app.post("/api/pdf")
async def download_pdf(data: WebSubmission):
    resp_dict = {r.item_id: r.value for r in data.responses}
    scores, streams = calculate_results(resp_dict)
    ai_summary = generate_counselor_narrative(data.student_name, data.student_grade, scores, streams, data.ai_provider)
    pdf_bytes = generate_student_pdf(data.student_name, data.student_grade, scores, streams, ai_summary)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={data.student_name}_report.pdf"}
    )

@app.post("/api/upload-excel")
async def process_excel(file: UploadFile = File(...), ai_provider: str = Form("gemini")):
    contents = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Excel file: {str(e)}")

    required_cols = {"student_id", "student_name", "grade"}
    if not required_cols.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"Excel must contain columns: {required_cols}")

    results = []
    for _, row in df.iterrows():
        resp_dict = {}
        for col in df.columns:
            if col in ITEM_BANK and pd.notna(row[col]):
                resp_dict[col] = int(row[col])

        scores, streams = calculate_results(resp_dict)
        ai_summary = generate_counselor_narrative(str(row["student_name"]), int(row["grade"]), scores, streams, ai_provider)
        
        results.append({
            "student_id": row["student_id"],
            "student_name": row["student_name"],
            "grade": int(row["grade"]),
            "scores": scores,
            "top_stream": streams[0]["stream"] if streams else "N/A",
            "ai_summary": ai_summary
        })

    return {"processed_count": len(results), "students": results}
