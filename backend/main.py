import os
import shutil
import logging
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import services & agents
from backend import database
from backend.services.pdf_service import extract_text_from_pdf, generate_tailored_pdf
from backend.agents.job_researcher import search_jobs_and_research
from backend.agents.resume_tailor import tailor_resume
from backend.agents.recruiter_critic import review_resume
from backend.agents.debate_system import run_candidate_debate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Initialize Directories
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="AI Career Copilot API",
    description="Multi-agent Career Copilot using FastAPI and LangGraph",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas for Requests

class TailorRequest(BaseModel):
    resume_id: int
    job_id: int

class ScoreRequest(BaseModel):
    resume_id: int
    job_id: int

class DebateRequest(BaseModel):
    resume_id: int
    job_id: int

class StatusUpdateRequest(BaseModel):
    status: str

# Endpoints

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "sqlite"}

# 1. Job Finder + Company Research Endpoints
@app.get("/api/jobs/search")
def search_jobs(query: str = Query(..., min_length=2), location: str = Query("Bangalore")):
    try:
        jobs = search_jobs_and_research(query, location)
        
        # Save found jobs into our tracker
        saved_jobs = []
        for job in jobs:
            job_id = database.save_job(
                job_title=job["job_title"],
                company_name=job["company_name"],
                location=job["location"],
                description=job["description"],
                url=job["url"],
                company_profile=job["company_profile"]
            )
            job_copy = job.copy()
            job_copy["id"] = job_id
            saved_jobs.append(job_copy)
            
        return {"count": len(saved_jobs), "jobs": saved_jobs}
    except Exception as e:
        logger.error(f"Search jobs endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
def get_jobs_tracker():
    try:
        return {"jobs": database.get_all_jobs()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/jobs/{job_id}/status")
def update_job_status(job_id: int, request: StatusUpdateRequest):
    try:
        database.update_job_status(job_id, request.status)
        return {"status": "success", "job_id": job_id, "new_status": request.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Resume Upload & Tailoring Endpoints
@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Save temp file
        temp_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse PDF text
        text = extract_text_from_pdf(temp_path)
        
        # Remove temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. Make sure it is not scanned or empty.")
            
        # Store in DB
        resume_id = database.save_resume(file.filename, text)
        
        return {
            "resume_id": resume_id,
            "filename": file.filename,
            "text_length": len(text),
            "sample_text": text[:200] + "..."
        }
    except Exception as e:
        logger.error(f"Upload resume endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resume/tailor")
def trigger_tailor(request: TailorRequest):
    # Fetch original resume
    resume = database.get_resume_by_id(request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
        
    # Fetch target job description
    jobs = database.get_all_jobs()
    target_job = next((j for j in jobs if j["id"] == request.job_id), None)
    if not target_job:
        raise HTTPException(status_code=404, detail="Job description not found in database tracker.")
        
    try:
        # 1. Run LLM Resume Tailoring (Agent 2)
        tailoring_result = tailor_resume(
            original_resume=resume["original_text"],
            job_description=target_job["description"]
        )
        
        sections = tailoring_result.get("sections", [])
        suggested_changes = tailoring_result.get("suggested_changes", [])
        
        # Format tailored text for DB storage
        tailored_text_dump = ""
        for sec in sections:
            tailored_text_dump += f"--- {sec.get('title')} ---\n{str(sec.get('content'))}\n\n"
            
        # 2. Generate PDF output
        pdf_filename = f"tailored_{request.resume_id}_{request.job_id}.pdf"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
        
        generate_tailored_pdf(sections, pdf_path)
        
        # 3. Update Resume entry in DB
        database.update_tailored_resume(
            resume_id=request.resume_id,
            tailored_text=tailored_text_dump,
            tailored_pdf_path=pdf_filename # Save relative path filename
        )
        
        # Mark job status as "Tailored"
        database.update_job_status(request.job_id, "Tailored")
        
        return {
            "resume_id": request.resume_id,
            "job_id": request.job_id,
            "suggested_changes": suggested_changes,
            "sections": sections,
            "pdf_download_url": f"/api/resume/download/{request.resume_id}"
        }
    except Exception as e:
        logger.error(f"Tailoring endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. Recruiter Review Endpoint (Agent 3)
@app.post("/api/resume/score")
def get_recruiter_score(request: ScoreRequest):
    resume = database.get_resume_by_id(request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
        
    jobs = database.get_all_jobs()
    target_job = next((j for j in jobs if j["id"] == request.job_id), None)
    if not target_job:
        raise HTTPException(status_code=404, detail="Job description not found.")
        
    try:
        # Check if we already compiled tailored resume sections.
        # If not, generate them on the fly.
        import ast
        sections = []
        if resume["tailored_text"]:
            # Recruiter evaluates tailored resume.
            # Parse sections from structured text or re-run tailor. We will re-run tailoring internally or reconstruct.
            # In our main workflow, Agent 2 has already run, so we parse sections from tailored resume JSON.
            # In mock or missing, we can pass original text.
            # To be absolutely sure, we can just re-request resume tailor or parse. Let's make an LLM-friendly review.
            # Let's rebuild sections structure from SQLite tailored_text or just pass the text.
            # Actually, recruiter_critic review_resume takes sections. If we have tailored_text, we can treat it as one text block.
            sections = [{"title": "Tailored Resume", "content": resume["tailored_text"]}]
        else:
            sections = [{"title": "Original Resume", "content": resume["original_text"]}]
            
        review_result = review_resume(
            sections=sections,
            job_description=target_job["description"]
        )
        
        return review_result
    except Exception as e:
        logger.error(f"Score endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 4. Multi-Agent Debate Endpoint (Agent 4)
@app.post("/api/resume/debate")
def run_debate(request: DebateRequest):
    resume = database.get_resume_by_id(request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
        
    jobs = database.get_all_jobs()
    target_job = next((j for j in jobs if j["id"] == request.job_id), None)
    if not target_job:
        raise HTTPException(status_code=404, detail="Job description not found.")
        
    try:
        # Check if debate already exists to prevent repetitive API costs
        existing_debate = database.get_debate_by_job_resume(request.job_id, request.resume_id)
        if existing_debate:
            logger.info("Found existing debate in database. Returning cached result.")
            return existing_debate
            
        # Reconstruct sections for the debate state
        sections = [{"title": "Resume Details", "content": resume["tailored_text"] or resume["original_text"]}]
        
        # Run LangGraph Debate
        debate_result = run_candidate_debate(
            original_resume=resume["original_text"],
            tailored_sections=sections,
            job_title=target_job["job_title"],
            job_description=target_job["description"],
            company_name=target_job["company_name"],
            company_profile=target_job["company_profile"] or {}
        )
        
        # Save debate to database
        database.save_debate(
            job_id=request.job_id,
            resume_id=request.resume_id,
            transcript=debate_result["debate_transcript"],
            score=debate_result["final_composite_score"],
            verdict="", # Handled by recommendations
            strengths=[], # Handled by recommendations
            weaknesses=[],
            ats_keywords_missing=[]
        )
        
        return {
            "score": debate_result["final_composite_score"],
            "recommendations": debate_result["final_recommendations"],
            "transcript": debate_result["debate_transcript"]
        }
    except Exception as e:
        logger.error(f"Debate endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PDF Download Endpoint
@app.get("/api/resume/download/{resume_id}")
def download_resume(resume_id: int):
    resume = database.get_resume_by_id(resume_id)
    if not resume or not resume["tailored_pdf_path"]:
        raise HTTPException(status_code=404, detail="Tailored PDF not generated yet.")
        
    pdf_path = os.path.join(UPLOAD_DIR, resume["tailored_pdf_path"])
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk.")
        
    return FileResponse(
        pdf_path, 
        media_type="application/pdf", 
        filename=resume["filename"]
    )

if __name__ == "__main__":
    import uvicorn
    # Use environment PORT or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
