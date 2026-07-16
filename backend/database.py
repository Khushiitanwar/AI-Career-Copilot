import sqlite3
import os
import json
from datetime import datetime

DATABASE_FILE = "copilot.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Resumes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        original_text TEXT,
        tailored_text TEXT,
        tailored_pdf_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        company_name TEXT,
        location TEXT,
        description TEXT,
        url TEXT,
        company_profile TEXT, -- JSON string
        status TEXT DEFAULT 'Found', -- Found, Tailored, Applied, Interviewing, Rejected
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Debates and Evaluations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS debates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        resume_id INTEGER,
        transcript TEXT, -- JSON string
        score REAL,
        verdict TEXT,
        strengths TEXT, -- JSON string
        weaknesses TEXT, -- JSON string
        ats_keywords_missing TEXT, -- JSON string
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(job_id) REFERENCES jobs(id),
        FOREIGN KEY(resume_id) REFERENCES resumes(id)
    )
    """)
    
    conn.commit()
    conn.close()

# Helper DB Functions

# Resume Helpers
def save_resume(filename, original_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resumes (filename, original_text) VALUES (?, ?)",
        (filename, original_text)
    )
    conn.commit()
    resume_id = cursor.lastrowid
    conn.close()
    return resume_id

def update_tailored_resume(resume_id, tailored_text, tailored_pdf_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE resumes SET tailored_text = ?, tailored_pdf_path = ? WHERE id = ?",
        (tailored_text, tailored_pdf_path, resume_id)
    )
    conn.commit()
    conn.close()

def get_latest_resume():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_resume_by_id(resume_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

# Job Helpers
def save_job(job_title, company_name, location, description, url=None, company_profile=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    profile_str = json.dumps(company_profile) if company_profile else None
    cursor.execute(
        "INSERT INTO jobs (job_title, company_name, location, description, url, company_profile) VALUES (?, ?, ?, ?, ?, ?)",
        (job_title, company_name, location, description, url, profile_str)
    )
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id

def get_all_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    jobs = []
    for r in rows:
        job = dict(r)
        if job["company_profile"]:
            job["company_profile"] = json.loads(job["company_profile"])
        jobs.append(job)
    return jobs

def update_job_status(job_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()

# Debate Helpers
def save_debate(job_id, resume_id, transcript, score, verdict, strengths, weaknesses, ats_keywords_missing):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO debates 
           (job_id, resume_id, transcript, score, verdict, strengths, weaknesses, ats_keywords_missing) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            job_id, 
            resume_id, 
            json.dumps(transcript), 
            score, 
            verdict, 
            json.dumps(strengths), 
            json.dumps(weaknesses),
            json.dumps(ats_keywords_missing)
        )
    )
    conn.commit()
    debate_id = cursor.lastrowid
    conn.close()
    return debate_id

def get_debate_by_job_resume(job_id, resume_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM debates WHERE job_id = ? AND resume_id = ? ORDER BY id DESC LIMIT 1",
        (job_id, resume_id)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        debate = dict(row)
        debate["transcript"] = json.loads(debate["transcript"])
        debate["strengths"] = json.loads(debate["strengths"])
        debate["weaknesses"] = json.loads(debate["weaknesses"])
        debate["ats_keywords_missing"] = json.loads(debate["ats_keywords_missing"])
        return debate
    return None

# Run initialization on import
init_db()
