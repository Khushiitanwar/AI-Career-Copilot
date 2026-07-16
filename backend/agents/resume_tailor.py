import json
import logging
from typing import Dict, Any, List
from backend.config import get_llm

logger = logging.getLogger("resume_tailor")

def tailor_resume(original_resume: str, job_description: str) -> Dict[str, Any]:
    """
    Tailors the original resume text to fit the job description.
    Returns a JSON dict with:
    - sections: List of formatted resume sections.
    - suggested_changes: List of strings detailing what changes were made.
    """
    logger.info("Initiating resume tailoring LLM request")
    
    prompt = f"""You are an expert resume writer and career coach specializing in the technology sector.
Your goal is to optimize the following candidate's resume for a specific job description by rewriting bullet points, structuring sections, and highlighting skill gaps.

STRICT RULES:
1. NEVER FABRICATE experience, projects, education, names, companies, or dates.
2. Only REFRAME and REORGANIZE existing details to show maximum relevance to the job.
3. Keep the output professional, crisp, and concise (ideal for a 1-page resume).
4. The contact details, links, name, etc. must be preserved exactly as they are in the original resume.

Original Resume Text:
{original_resume}

Target Job Description:
{job_description}

You must return a JSON response with two keys:
1. "suggested_changes": A list of strings describing the modifications you made and why (e.g. "Emphasized LangGraph experience in TechCorp role to match orchestrator requirement").
2. "sections": A list of sections conforming to this exact structure:
[
  {{
    "title": "Header",
    "content": {{
      "name": "Candidate Name",
      "email": "candidate@email.com",
      "phone": "+1 234 567 890",
      "location": "City, Country",
      "links": "github.com/profile | linkedin.com/in/profile"
    }}
  }},
  {{
    "title": "Professional Summary",
    "content": "A short, high-impact paragraph tailored to the role."
  }},
  {{
    "title": "Skills",
    "content": "Comma-separated list of technical and soft skills matching the job description requirements."
  }},
  {{
    "title": "Work Experience",
    "content": [
      {{
        "role": "Job Title",
        "company": "Company Name",
        "dates": "Start Date - End Date",
        "description": [
          "Action-oriented bullet point emphasizing achievements, metrics, and relevant technologies.",
          "Second action-oriented bullet point matching keywords from the job description."
        ]
      }}
    ]
  }},
  {{
    "title": "Projects",
    "content": [
      {{
        "title": "Project Name",
        "dates": "Date / Timeline",
        "description": [
          "Detail about what was built, tech stack used, and outcomes.",
          "Highlighting elements that match the job requirements."
        ]
      }}
    ]
  }},
  {{
    "title": "Education",
    "content": [
      {{
        "degree": "Degree and Major",
        "school": "University Name",
        "dates": "Graduation Date",
        "description": "GPA, honors, or relevant coursework (if applicable)."
      }}
    ]
  }}
]

Make sure all work experience and project bullet points start with strong action verbs (e.g., Developed, Engineered, Optimized, Spearheaded).
If a section (like Projects) is not present in the original resume, do not create a fake one—simply omit it or replace it with valid content from the original text.

You MUST return ONLY a raw JSON object. Do not include any markdown wrappers like ```json or explain the JSON.

JSON Output:"""

    try:
        llm = get_llm(temperature=0.3)
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        # Clean markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        parsed = json.loads(text)
        return parsed
    except Exception as e:
        logger.error(f"Error during resume tailoring LLM call: {e}")
        # Return fallback structure
        return {
            "suggested_changes": ["Error connecting to LLM. Using raw resume text."],
            "sections": [
                {
                    "title": "Header",
                    "content": {
                        "name": "Applicant Name",
                        "email": "email@example.com",
                        "phone": "",
                        "location": "",
                        "links": ""
                    }
                },
                {
                    "title": "Professional Summary",
                    "content": "Resume tailoring experienced a service interruption. Please try again."
                },
                {
                    "title": "Work Experience",
                    "content": [
                        {
                            "role": "Candidate",
                            "company": "Original Data",
                            "dates": "",
                            "description": [original_resume[:500] + "..."]
                        }
                    ]
                }
            ]
        }
