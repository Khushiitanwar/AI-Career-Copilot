import json
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.config import get_llm, CRITIC_MODEL

logger = logging.getLogger("recruiter_critic")

class RecruiterReview(BaseModel):
    score: float = Field(description="A rating from 1.0 to 10.0 reflecting candidate's fit for the job based on the resume.")
    strengths: List[str] = Field(description="Exactly 3 key strengths or positive highlights noticed in the resume.")
    weaknesses: List[str] = Field(description="Exactly 3 critical gaps, weaknesses, or red flags (e.g. lack of experience, missing tech keywords).")
    verdict: str = Field(description="A direct, honest one-line recruitment decision (e.g., 'Strong hire for this level', 'Reject - lacks core system experience').")
    ats_keywords_missing: List[str] = Field(description="List of critical keywords, libraries, or frameworks from the job description missing in the resume.")

def format_sections_to_text(sections: List[Dict[str, Any]]) -> str:
    """
    Converts structured resume sections into a clean text block for the LLM.
    """
    text = ""
    for sec in sections:
        title = sec.get("title", "")
        content = sec.get("content")
        if not content:
            continue
        text += f"\n=== {title} ===\n"
        if isinstance(content, str):
            text += content + "\n"
        elif isinstance(content, dict):
            for k, v in content.items():
                text += f"{k}: {v}\n"
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str):
                    text += f"- {item}\n"
                elif isinstance(item, dict):
                    header = item.get("role") or item.get("degree") or item.get("title") or ""
                    company = item.get("company") or item.get("school") or ""
                    dates = item.get("dates") or ""
                    text += f"* {header} at {company} ({dates})\n"
                    desc = item.get("description")
                    if isinstance(desc, str):
                        text += f"  {desc}\n"
                    elif isinstance(desc, list):
                        for b in desc:
                            text += f"  - {b}\n"
    return text

def review_resume(sections: List[Dict[str, Any]], job_description: str) -> Dict[str, Any]:
    """
    Evaluates the resume against the job description from a recruiter's perspective.
    """
    resume_text = format_sections_to_text(sections)
    logger.info("Initiating recruiter review LLM request")
    
    prompt = f"""You are a brutally honest Senior Technical Recruiter at a top-tier AI company.
You have exactly 10 seconds to scan the following resume against a job description.
Assess the candidate's alignment, flag potential issues, and calculate a score out of 10.

Original Resume Text:
{resume_text}

Target Job Description:
{job_description}

You must return a JSON response matching the following schema. Make sure strengths and weaknesses lists contain exactly 3 items.

Expected JSON schema:
{{
  "score": 8.5,
  "strengths": [
    "Highlight 1",
    "Highlight 2",
    "Highlight 3"
  ],
  "weaknesses": [
    "Weakness 1",
    "Weakness 2",
    "Weakness 3"
  ],
  "verdict": "Clear hire recommendation or specific rejection rationale.",
  "ats_keywords_missing": ["Keyword1", "Keyword2"]
}}

Rules:
1. Be objective, strict, and direct.
2. The score should represent real hiring bar (e.g. 9.0+ is exceptional, 7.0-8.9 is passable, below 7.0 is reject).
3. Do not include markdown formatting or wrapper tags.

JSON Output:"""

    try:
        # Use critic model for rigorous scanning
        llm = get_llm(model=CRITIC_MODEL, temperature=0.1)
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        # Clean markdown wrappers
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        parsed = json.loads(text)
        
        # Validate schema using Pydantic
        review = RecruiterReview(**parsed)
        return review.model_dump()
    except Exception as e:
        logger.error(f"Error during recruiter critic LLM call: {e}")
        # Return fallback structured response
        return {
            "score": 5.0,
            "strengths": ["Parsed resume header successfully", "Demonstrates software familiarity", "Professional format"],
            "weaknesses": ["Analysis connection failed", "Unable to run ATS scan", "Review incomplete"],
            "verdict": "Evaluation incomplete due to connection error. Please retry.",
            "ats_keywords_missing": []
        }
