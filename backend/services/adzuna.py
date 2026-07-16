import os
import requests
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")

logger = logging.getLogger("adzuna")

MOCK_JOBS = [
    {
        "id": "mock-1",
        "job_title": "AI Intern",
        "company_name": "HyperScale AI",
        "location": "Bangalore, India",
        "description": "We are seeking a passionate AI Research & Development Intern to join our core intelligence team in Bangalore. You will work on fine-tuning LLMs, building orchestration graphs using LangGraph/LlamaIndex, and deploying multi-agent systems. Requirements: Python, PyTorch, experience with transformer architectures, and building RAG pipelines.",
        "url": "https://hyperscale.ai/careers/ai-intern",
        "salary": "₹40,000 - ₹60,000 per month",
        "company_profile": {
            "tech_stack": "Python, PyTorch, LangGraph, FastAPI, Qdrant, React",
            "funding_status": "Series A ($12M raised)",
            "domain": "Enterprise generative AI tools for automate workflows",
            "recent_news": "Recently launched their autonomous agent developer platform at AI Bangalore Summit."
        }
    },
    {
        "id": "mock-2",
        "job_title": "Machine Learning Engineer",
        "company_name": "Kite Health",
        "location": "Bangalore, India",
        "description": "Kite Health is looking for an ML Engineer to build clinical NLP pipelines and agentic diagnostics copilots. You will develop medical-grade classification models and optimize local models (Llama 3, Mistral) for edge deployment. Requirements: 2+ years of ML experience, strong background in NLP, huggingface libraries, and vector databases.",
        "url": "https://kitehealth.co/jobs/ml-engineer",
        "salary": "₹18,00,000 - ₹24,00,000 per year",
        "company_profile": {
            "tech_stack": "Python, PyTorch, HuggingFace, Qdrant, PostgreSQL, AWS",
            "funding_status": "Seed Stage ($4.5M)",
            "domain": "AI-driven primary care diagnostics and transcription",
            "recent_news": "Partnered with 3 major hospital networks across South India for beta testing clinical agents."
        }
    },
    {
        "id": "mock-3",
        "job_title": "Generative AI Developer",
        "company_name": "DecentralLabs",
        "location": "Bangalore, India",
        "description": "DecentralLabs is building Web3 AI assistants. We need a Developer specializing in prompt engineering, LangChain workflows, vector search indexes, and custom embedding pipelines. Requirements: strong JS/Python skills, knowledge of vector search algorithms, and previous projects in GenAI.",
        "url": "https://decentrallabs.xyz/careers/genai-dev",
        "salary": "₹12,0,000 - ₹18,0,000 per year",
        "company_profile": {
            "tech_stack": "TypeScript, Python, LangChain, Pinecone, Next.js, Node.js",
            "funding_status": "Pre-seed ($1.5M)",
            "domain": "Decentralized AI agents and token-incentivized inference",
            "recent_news": "Featured in TechCrunch for their novel proof-of-compute network protocol."
        }
    },
    {
        "id": "mock-4",
        "job_title": "LLM Solutions Architect",
        "company_name": "Apex Enterprise Solutions",
        "location": "Remote",
        "description": "Help enterprise customers design, build, and deploy LLM systems at scale. You will advise clients on data compliance, vector DB setup, security practices, and agent-based automation architectures. Requirements: 5+ years of software architecture, expert in cloud providers (Azure/AWS), and GenAI frameworks.",
        "url": "https://apexsolutions.com/careers/llm-architect",
        "salary": "$140,000 - $180,000 per year",
        "company_profile": {
            "tech_stack": "Python, OpenAI API, LangGraph, Qdrant Cloud, Azure OpenAI, Terraform",
            "funding_status": "Publicly Traded",
            "domain": "Enterprise IT consulting and custom software integration",
            "recent_news": "Announced a $50M investment in their global generative AI consulting division."
        }
    },
    {
        "id": "mock-5",
        "job_title": "AI Product Manager",
        "company_name": "Synthetix AI",
        "location": "San Francisco, CA",
        "description": "Lead the product vision for our synthetic data generation engine. Work closely with AI researchers to design tools for training computer vision models. Requirements: 3+ years product management, technical degree, experience with AI/ML products.",
        "url": "https://synthetix.ai/jobs/pm",
        "salary": "$150,000 - $190,000 per year",
        "company_profile": {
            "tech_stack": "PyTorch, CUDA, React, Python, Go, GCP",
            "funding_status": "Series B ($35M raised)",
            "domain": "Synthetic data generation for autonomous vehicles and robotics",
            "recent_news": "Named one of the top 50 rising AI startups in the Bay Area by Y Combinator."
        }
    }
]

def search_adzuna_jobs(query: str, location: str) -> List[Dict[str, Any]]:
    """
    Queries Adzuna API for job listings in India (or global).
    Falls back to mock jobs if credentials are not configured or request fails.
    """
    if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
        logger.info("Adzuna API credentials missing. Falling back to mock jobs.")
        return filter_mock_jobs(query, location)

    # Adzuna API parameters
    # Country code 'in' for India, can fall back or expand
    country = "in"
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "what": query,
        "where": location,
        "results_per_page": 15,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            jobs = []
            for r in results:
                # Extract clean fields
                location_area = r.get("location", {}).get("area", [])
                loc_str = ", ".join(location_area) if location_area else location
                
                # Check for salary values
                min_sal = r.get("salary_min")
                max_sal = r.get("salary_max")
                salary_str = "Not Specified"
                if min_sal and max_sal:
                    salary_str = f"₹{int(min_sal):,} - ₹{int(max_sal):,} per year"
                elif min_sal:
                    salary_str = f"From ₹{int(min_sal):,} per year"
                
                jobs.append({
                    "id": r.get("id"),
                    "job_title": r.get("title", ""),
                    "company_name": r.get("company", {}).get("display_name", "Unknown Company"),
                    "location": loc_str,
                    "description": r.get("description", ""),
                    "url": r.get("redirect_url", ""),
                    "salary": salary_str,
                    "company_profile": None # Will be filled by Agent 1's RAG/LLM synthesis
                })
            
            if not jobs:
                logger.info("Adzuna search returned empty. Falling back to mock jobs.")
                return filter_mock_jobs(query, location)
                
            return jobs
        else:
            logger.warning(f"Adzuna API returned error {response.status_code}. Using mock data.")
            return filter_mock_jobs(query, location)
    except Exception as e:
        logger.error(f"Adzuna API connection failed: {e}. Using mock data.")
        return filter_mock_jobs(query, location)

def filter_mock_jobs(query: str, location: str) -> List[Dict[str, Any]]:
    """
    Filters our mock job database to return relevant results.
    """
    query = query.lower() if query else ""
    location = location.lower() if location else ""
    
    filtered = []
    for job in MOCK_JOBS:
        title_match = not query or query in job["job_title"].lower() or query in job["description"].lower()
        loc_match = not location or location in job["location"].lower()
        if title_match or loc_match:
            filtered.append(job.copy())
            
    # If query matches nothing, return a subset of our mock database anyway so the UI remains active
    if not filtered:
        return [job.copy() for job in MOCK_JOBS[:3]]
        
    return filtered
