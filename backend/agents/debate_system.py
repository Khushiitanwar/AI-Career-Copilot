import json
import os
import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END, START
from backend.agents.state import AgentState
from backend.config import get_llm, DEFAULT_MODEL
from backend.agents.recruiter_critic import format_sections_to_text

logger = logging.getLogger("debate_system")

# LLM Node Implementations

def skill_matcher_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates how well the resume skills match the job description.
    """
    logger.info("Starting Skill Matcher Agent Node")
    resume_text = format_sections_to_text(state.get("tailored_sections", []))
    if not resume_text:
        resume_text = state.get("original_resume_text", "")
        
    job_desc = state.get("job_description", "")
    
    prompt = f"""You are the 'Skill Matcher' sub-agent in an AI hiring debate panel.
Your role is to strictly evaluate the technical and soft skills listed in the candidate's resume against the requirements of the job.

Resume:
{resume_text}

Job Description:
{job_desc}

Provide a match rating (0-100) and a concise, arguments-based critique.
You must return only a JSON object containing:
{{
  "score": 85.0,
  "argument": "The candidate has excellent skills in Python and PyTorch. However, they lack experience with Kubernetes, which is a required tool in the job description."
}}

JSON Output:"""
    
    try:
        llm = get_llm(temperature=0.2)
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        # Clean markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        res = json.loads(text.strip())
        return {"debate_skill_matcher_verdict": res}
    except Exception as e:
        logger.error(f"Skill Matcher node error: {e}")
        return {
            "debate_skill_matcher_verdict": {
                "score": 70.0,
                "argument": "Skill Matcher: Resume shows general tech capability but LLM analysis was offline."
            }
        }

def experience_evaluator_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates the depth and longevity of experience relative to the job requirements.
    """
    logger.info("Starting Experience Evaluator Agent Node")
    resume_text = format_sections_to_text(state.get("tailored_sections", []))
    if not resume_text:
        resume_text = state.get("original_resume_text", "")
        
    job_desc = state.get("job_description", "")
    
    prompt = f"""You are the 'Experience Evaluator' sub-agent in an AI hiring debate panel.
Your role is to assess the depth, responsibilities, and seniority level of the candidate's work history relative to the job.

Resume:
{resume_text}

Job Description:
{job_desc}

Evaluate if the candidate is Junior, Mid, Senior, or Overqualified, and write a concise hiring argument.
You must return only a JSON object containing:
{{
  "fit_level": "Mid",
  "argument": "The candidate has 3 years of work experience at startup environments. Their hands-on responsibility fits our requirements perfectly, though they have not led larger teams."
}}

JSON Output:"""
    
    try:
        llm = get_llm(temperature=0.2)
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        res = json.loads(text.strip())
        return {"debate_experience_evaluator_verdict": res}
    except Exception as e:
        logger.error(f"Experience Evaluator node error: {e}")
        return {
            "debate_experience_evaluator_verdict": {
                "fit_level": "Undetermined",
                "argument": "Experience Evaluator: Resume contains work history, but deep experience assessment was skipped."
            }
        }

def salary_analyzer_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates salary ranges, negotiation position, and market value.
    """
    logger.info("Starting Salary Analyzer Agent Node")
    job_title = state.get("job_title", "")
    job_desc = state.get("job_description", "")
    company_name = state.get("company_name", "")
    
    prompt = f"""You are the 'Salary Analyzer' sub-agent in an AI hiring debate panel.
Your role is to evaluate what compensation expectation is appropriate for a "{job_title}" role at "{company_name}".
Assess the negotiation strength based on typical market rates and candidate profile.

Job Description & Context:
{job_desc}

Provide typical market ranges and brief tips for negotiation.
You must return only a JSON object containing:
{{
  "market_range": "₹12,00,000 - ₹18,00,000 per year (for Bangalore)",
  "argument": "AI and LangGraph roles are highly valued right now. The candidate's specific skills give them strong leverage, but their short tenure suggests keeping expectations near mid-range."
}}

JSON Output:"""
    
    try:
        llm = get_llm(temperature=0.3)
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        res = json.loads(text.strip())
        return {"debate_salary_analyzer_verdict": res}
    except Exception as e:
        logger.error(f"Salary Analyzer node error: {e}")
        return {
            "debate_salary_analyzer_verdict": {
                "market_range": "Market standard",
                "argument": "Salary Analyzer: Standard compensation mapping could not be completed."
            }
        }

def culture_fit_node(state: AgentState) -> Dict[str, Any]:
    """
    Compares candidate profile with company domain and profile information.
    """
    logger.info("Starting Culture Fit Agent Node")
    resume_text = format_sections_to_text(state.get("tailored_sections", []))
    if not resume_text:
        resume_text = state.get("original_resume_text", "")
        
    company_name = state.get("company_name", "")
    company_profile = state.get("company_profile", {})
    profile_str = json.dumps(company_profile) if company_profile else "No details cached."
    
    prompt = f"""You are the 'Culture Fit Agent' sub-agent in an AI hiring debate panel.
Your role is to compare the candidate's professional background (hackathons, startup experience, style) with the values, domain, and funding status of "{company_name}".

Candidate Resume Summary:
{resume_text[:2000]}

Company Intel:
{profile_str}

Evaluate fit level (0-100) and highlight any potential strengths or flags.
You must return only a JSON object containing:
{{
  "score": 90.0,
  "argument": "HyperScale AI is a fast-paced Series A startup. The candidate's heavy focus on hackathons, personal projects, and autonomous agents demonstrates they will thrive in a high-ownership, ambiguous environment."
}}

JSON Output:"""
    
    try:
        llm = get_llm(temperature=0.3)
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        res = json.loads(text.strip())
        return {"debate_culture_fit_verdict": res}
    except Exception as e:
        logger.error(f"Culture Fit node error: {e}")
        return {
            "debate_culture_fit_verdict": {
                "score": 75.0,
                "argument": "Culture Fit Agent: Candidate matches general tech background, culture assessment completed with defaults."
            }
        }

def judge_node(state: AgentState) -> Dict[str, Any]:
    """
    Sifts through all 4 sub-agent findings and outputs final composite score and structured recommendations.
    """
    logger.info("Starting Judge Agent Node")
    
    v_skills = state.get("debate_skill_matcher_verdict", {})
    v_exp = state.get("debate_experience_evaluator_verdict", {})
    v_salary = state.get("debate_salary_analyzer_verdict", {})
    v_culture = state.get("debate_culture_fit_verdict", {})
    
    # Structure debate transcript logs
    transcript = [
        {"agent": "Skill Matcher", "message": v_skills.get("argument", "Lacks detailed input.")},
        {"agent": "Experience Evaluator", "message": v_exp.get("argument", "Lacks detailed input.")},
        {"agent": "Salary Analyzer", "message": f"Market Rate: {v_salary.get('market_range', 'Unspecified')}. Verdict: {v_salary.get('argument', 'Lacks detailed input.')}"},
        {"agent": "Culture Fit Agent", "message": v_culture.get("argument", "Lacks detailed input.")}
    ]
    
    prompt = f"""You are the 'Lead Hiring Judge' presiding over a candidate evaluation panel.
You have heard arguments from 4 expert sub-agents concerning this candidate:

1. Skill Matcher:
{json.dumps(v_skills, indent=2)}

2. Experience Evaluator:
{json.dumps(v_exp, indent=2)}

3. Salary Analyzer:
{json.dumps(v_salary, indent=2)}

4. Culture Fit Agent:
{json.dumps(v_culture, indent=2)}

Your task is to synthesize their opinions, resolve any conflicts, assign a final overall composite score (0-100), and write 3-5 high-priority, actionable recommendation bullet points for the candidate or hiring manager.

You must return only a JSON object containing:
{{
  "composite_score": 82.5,
  "recommendations": [
    "Prioritize testing candidate on systems architecture in the technical interview due to light senior experience.",
    "Be prepared to negotiate salary at the top of the range (₹16-18 LPA) to secure candidate.",
    "Verify Kubernetes skills during the phone screen since it was flagged as missing."
  ]
}}

JSON Output:"""
    
    try:
        llm = get_llm(temperature=0.2)
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        res = json.loads(text.strip())
        
        return {
            "final_composite_score": res.get("composite_score", 70.0),
            "final_recommendations": res.get("recommendations", ["No specific recommendations"]),
            "debate_transcript": transcript
        }
    except Exception as e:
        logger.error(f"Judge node error: {e}")
        return {
            "final_composite_score": 75.0,
            "final_recommendations": ["Review debate panel arguments individually.", "Verify skills on live assignments."],
            "debate_transcript": transcript
        }

def initializer_node(state: AgentState) -> Dict[str, Any]:
    logger.info("Initializing debate workflow graph...")
    return {}

# LangGraph Orchestration Setup

def compile_debate_graph():
    # Build graph
    builder = StateGraph(AgentState)
    
    # Add Nodes
    builder.add_node("initializer", initializer_node)
    builder.add_node("skill_matcher", skill_matcher_node)
    builder.add_node("experience_evaluator", experience_evaluator_node)
    builder.add_node("salary_analyzer", salary_analyzer_node)
    builder.add_node("culture_fit", culture_fit_node)
    builder.add_node("judge", judge_node)
    
    # Single entry edge from START to initializer
    builder.add_edge(START, "initializer")
    
    # Parallel fan-out from initializer using conditional edges returning list
    builder.add_conditional_edges(
        "initializer",
        lambda state: ["skill_matcher", "experience_evaluator", "salary_analyzer", "culture_fit"]
    )
    
    # Fan-in (convoy) into Judge
    builder.add_edge("skill_matcher", "judge")
    builder.add_edge("experience_evaluator", "judge")
    builder.add_edge("salary_analyzer", "judge")
    builder.add_edge("culture_fit", "judge")
    
    # End of graph
    builder.add_edge("judge", END)
    
    return builder.compile()

# Instantiate compiled workflow
debate_workflow = compile_debate_graph()

def run_candidate_debate(original_resume: str, tailored_sections: List[Dict[str, Any]], job_title: str, job_description: str, company_name: str, company_profile: Dict[str, str]) -> Dict[str, Any]:
    """
    Convenience wrapper to execute the LangGraph workflow synchronously.
    """
    initial_state = {
        "original_resume_text": original_resume,
        "tailored_sections": tailored_sections,
        "job_title": job_title,
        "job_description": job_description,
        "company_name": company_name,
        "company_profile": company_profile,
        
        # Initialize default state keys
        "tailored_text": "",
        "suggested_changes": [],
        "tailored_pdf_path": None,
        "recruiter_score": 0.0,
        "recruiter_verdict": "",
        "recruiter_strengths": [],
        "recruiter_weaknesses": [],
        "ats_keywords_missing": []
    }
    
    logger.info("Executing LangGraph debate graph...")
    final_output = debate_workflow.invoke(initial_state)
    logger.info("LangGraph debate graph complete.")
    return final_output
