const API_BASE_URL = "http://localhost:8000/api";

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === "healthy";
  } catch (e) {
    return false;
  }
}

export async function searchJobs(query, location) {
  const url = `${API_BASE_URL}/jobs/search?query=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to search jobs");
  return res.json();
}

export async function getJobsTracker() {
  const res = await fetch(`${API_BASE_URL}/jobs`);
  if (!res.ok) throw new Error("Failed to fetch jobs tracker");
  return res.json();
}

export async function updateJobStatus(jobId, status) {
  const res = await fetch(`${API_BASE_URL}/jobs/${jobId}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error("Failed to update status");
  return res.json();
}

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);
  
  const res = await fetch(`${API_BASE_URL}/resume/upload`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to upload resume");
  }
  return res.json();
}

export async function tailorResume(resumeId, jobId) {
  const res = await fetch(`${API_BASE_URL}/resume/tailor`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, job_id: jobId })
  });
  if (!res.ok) throw new Error("Failed to tailor resume");
  return res.json();
}

export async function getRecruiterScore(resumeId, jobId) {
  const res = await fetch(`${API_BASE_URL}/resume/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, job_id: jobId })
  });
  if (!res.ok) throw new Error("Failed to fetch recruiter score");
  return res.json();
}

export async function runDebate(resumeId, jobId) {
  const res = await fetch(`${API_BASE_URL}/resume/debate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, job_id: jobId })
  });
  if (!res.ok) throw new Error("Failed to run debate panel");
  return res.json();
}

export function getDownloadUrl(resumeId) {
  return `http://localhost:8000/api/resume/download/${resumeId}`;
}
