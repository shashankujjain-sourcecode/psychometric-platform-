import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

def generate_counselor_narrative(
    student_name: str, 
    grade: int, 
    scores: Dict[str, float], 
    top_streams: List[dict],
    provider: Optional[str] = "gemini"
) -> str:
    """
    Generates a personalized, encouraging counselor summary using Gemini or OpenAI.
    Falls back to a deterministic rule-based response if no API keys are provided.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    prompt = f"""
    You are an expert school psychologist and career guidance counselor in India.
    Provide a supportive, empowering 3-paragraph counseling narrative for a student.
    
    Student Name: {student_name}
    Current Grade: Class {grade}
    Psychometric Profile Scores: {scores}
    Recommended Streams: {[s['stream'] for s in top_streams]}
    
    Structure your advice:
    1. Acknowledge and praise their top cognitive/interest strengths.
    2. Explain how these strengths match their recommended Class 11/12 stream choices in India.
    3. Provide 2 actionable study or skill-development tips.
    Keep the tone encouraging, empathetic, and objective. Keep under 180 words.
    """

    # 1. Attempt Gemini via google-genai SDK
    if provider == "gemini" and gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception:
            pass

    # 2. Attempt OpenAI via official SDK
    if provider == "openai" and openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional educational counselor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception:
            pass

    # 3. Deterministic Fallback if no LLM API is available
    primary_stream = top_streams[0]['stream'] if top_streams else "Interdisciplinary Studies"
    return (
        f"{student_name} demonstrates a balanced cognitive and interest profile aligned with "
        f"{primary_stream}. Based on these results, focusing on core analytical concepts while exploring "
        f"hands-on projects will provide strong clarity for upcoming secondary board exams."
    )
