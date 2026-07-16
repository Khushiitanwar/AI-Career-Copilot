from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Inputs
    original_resume_text: str
    job_title: str
    job_description: str
    company_name: str
    company_profile: Optional[Dict[str, str]]
    
    # Agent 2: Tailoring Outputs
    tailored_text: str
    tailored_sections: List[Dict[str, Any]]
    suggested_changes: List[str]
    tailored_pdf_path: Optional[str]
    
    # Agent 3: Recruiter Review
    recruiter_score: float # 1 to 10
    recruiter_verdict: str
    recruiter_strengths: List[str]
    recruiter_weaknesses: List[str]
    ats_keywords_missing: List[str]
    
    # Agent 4: Parallel Debate Verdicts
    debate_skill_matcher_verdict: Dict[str, Any]
    debate_experience_evaluator_verdict: Dict[str, Any]
    debate_salary_analyzer_verdict: Dict[str, Any]
    debate_culture_fit_verdict: Dict[str, Any]
    
    # Final synthesized recommendation
    final_composite_score: float # 0 to 100
    final_recommendations: List[str]
    debate_transcript: List[Dict[str, str]] # List of arguments: {"agent": str, "message": str}
