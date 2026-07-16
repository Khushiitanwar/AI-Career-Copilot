import json
import logging
from typing import List, Dict, Any
from backend.services.adzuna import search_adzuna_jobs
from backend.services.qdrant_service import rag_service
from backend.config import get_llm

logger = logging.getLogger("job_researcher")

def search_jobs_and_research(query: str, location: str) -> List[Dict[str, Any]]:
    """
    Finds jobs and automatically researches company info for each.
    """
    logger.info(f"Searching jobs for query: '{query}' in location: '{location}'")
    
    # 1. Fetch job listings
    jobs = search_adzuna_jobs(query, location)
    
    # 2. Iterate and research companies
    for job in jobs:
        company_name = job.get("company_name")
        if not company_name or company_name == "Unknown Company":
            # Default blank company card
            job["company_profile"] = {
                "tech_stack": "Not specified",
                "funding_status": "N/A",
                "domain": "Not specified",
                "recent_news": "No recent updates available"
            }
            continue
            
        # 3. Check Qdrant Vector DB / Fallback DB
        profile = rag_service.query_company_profile(company_name)
        
        if profile:
            logger.info(f"Cache hit in Qdrant for company: {company_name}")
            job["company_profile"] = profile
        else:
            # Cache miss - Use LLM to synthesize company profile card
            logger.info(f"Cache miss for company: {company_name}. Synthesizing profile via LLM.")
            synthesized_profile = synthesize_company_profile(company_name, job.get("job_title", ""))
            
            # Save back to RAG DB for future queries
            rag_service.add_company_profile(company_name, synthesized_profile)
            job["company_profile"] = synthesized_profile
            
    return jobs

def synthesize_company_profile(company_name: str, job_title: str) -> Dict[str, str]:
    """
    Calls OpenRouter LLM to synthesize a standard profile card for a company.
    """
    default_profile = {
        "tech_stack": "Python, React, AWS",
        "funding_status": "Estimated Venture Backed / Private",
        "domain": f"Software solutions relating to {job_title}",
        "recent_news": f"Actively hiring for {job_title} positions to support growth."
    }
    
    try:
        llm = get_llm(temperature=0.2)
        prompt = f"""You are a professional company research analyst.
Analyze and synthesize details for the company: "{company_name}".
The candidate is looking at a "{job_title}" role at this company.

Please compile a company card detailing:
1. Tech Stack (Common technologies, languages, frameworks they use)
2. Funding Status (e.g. Seed, Series A/B/C, Public, Bootstrap, or Bootstrapped)
3. Domain (What the company does, its core products, market focus)
4. Recent News (Any notable product launches, partnerships, fundraises, or scaling milestones)

If you have no exact historical knowledge of this company, construct realistic, professional estimates based on its name and industry, and append "(est.)" to those fields.

You MUST return ONLY a raw JSON object with keys: "tech_stack", "funding_status", "domain", "recent_news". Do not wrap in markdown ```json blocks.

JSON Output:"""
        
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        # Clean potential markdown wrapping
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        profile = json.loads(text)
        # Ensure all required keys are present
        required_keys = ["tech_stack", "funding_status", "domain", "recent_news"]
        for key in required_keys:
            if key not in profile:
                profile[key] = default_profile[key]
        return profile
        
    except Exception as e:
        logger.error(f"Failed to synthesize company profile for {company_name}: {e}")
        # Return fallback profile
        return default_profile
