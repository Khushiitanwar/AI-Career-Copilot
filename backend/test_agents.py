import sys
import os

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import database
from backend.services.pdf_service import extract_text_from_pdf
from backend.services.adzuna import filter_mock_jobs
from backend.agents.debate_system import debate_workflow

def test_db_setup():
    print("Testing DB connection...")
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Tables in SQLite: {tables}")
    assert "resumes" in tables
    assert "jobs" in tables
    assert "debates" in tables
    print("DB check: SUCCESS")

def test_job_fallback():
    print("Testing Adzuna mock filter...")
    jobs = filter_mock_jobs("AI", "Bangalore")
    print(f"Mock search returned {len(jobs)} jobs.")
    assert len(jobs) > 0
    print("Adzuna filter check: SUCCESS")

def test_langgraph_compilation():
    print("Testing LangGraph debate graph compilation...")
    assert debate_workflow is not None
    print(f"LangGraph Nodes: {debate_workflow.nodes.keys()}")
    print("LangGraph compilation: SUCCESS")

if __name__ == "__main__":
    print("=== STARTING AGENT TESTS ===")
    test_db_setup()
    test_job_fallback()
    test_langgraph_compilation()
    print("=== ALL STATIC TESTS PASSED SUCCESSFULLY ===")
