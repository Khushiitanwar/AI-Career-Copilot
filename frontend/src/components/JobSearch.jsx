import React, { useState, useEffect } from "react";
import { searchJobs, getJobsTracker, updateJobStatus } from "../utils/api";
import { Search, MapPin, DollarSign, ExternalLink, Briefcase, Cpu, Award, Globe, FileText, CheckCircle } from "lucide-react";

export default function JobSearch({ onSelectJob, selectedJobId }) {
  const [query, setQuery] = useState("AI Intern");
  const [location, setLocation] = useState("Bangalore");
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedJobId, setExpandedJobId] = useState(null);

  // Load previously searched jobs on mount
  useEffect(() => {
    fetchJobsTracker();
  }, []);

  const fetchJobsTracker = async () => {
    try {
      const data = await getJobsTracker();
      setJobs(data.jobs || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await searchJobs(query, location);
      setJobs(data.jobs || []);
    } catch (err) {
      setError(err.message || "Failed to search jobs. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Bar Panel */}
      <form onSubmit={handleSearch} className="glass rounded-2xl p-6 flex flex-col md:flex-row gap-4 items-center shadow-lg border border-white/5">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Job title, keywords, or company..."
            className="w-full pl-12 pr-4 py-3.5 bg-dark-900/60 border border-slate-700/50 rounded-xl focus:outline-none focus:border-cyan-500/80 text-white placeholder-slate-400 text-sm transition-all"
          />
        </div>
        <div className="relative flex-1 w-full">
          <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Location (e.g., Bangalore, Remote)..."
            className="w-full pl-12 pr-4 py-3.5 bg-dark-900/60 border border-slate-700/50 rounded-xl focus:outline-none focus:border-cyan-500/80 text-white placeholder-slate-400 text-sm transition-all"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full md:w-auto px-8 py-3.5 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 text-white font-medium rounded-xl text-sm transition-all shadow-md shadow-cyan-600/10 flex items-center justify-center gap-2"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Find Jobs
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="p-4 bg-red-950/40 border border-red-500/20 rounded-xl text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Jobs Grid */}
      <div className="grid grid-cols-1 gap-6">
        {jobs.length === 0 && !loading ? (
          <div className="glass rounded-2xl p-12 text-center text-slate-400 border border-white/5 flex flex-col items-center">
            <Briefcase className="w-12 h-12 text-slate-600 mb-4 animate-pulse" />
            <h3 className="font-semibold text-lg text-slate-200">No Job Postings Found</h3>
            <p className="text-sm mt-1 max-w-md">Search for "AI Intern Bangalore" or other tech keywords to trigger live searches and company profile research.</p>
          </div>
        ) : (
          jobs.map((job) => {
            const isSelected = selectedJobId === job.id;
            const isExpanded = expandedJobId === job.id;
            const profile = job.company_profile;
            
            return (
              <div
                key={job.id}
                className={`glass rounded-2xl border transition-all duration-300 ${
                  isSelected ? "border-cyan-500 shadow-[0_0_20px_-5px_rgba(6,182,212,0.2)]" : "border-white/5 hover:border-slate-700"
                }`}
              >
                <div className="p-6">
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <h3 className="font-bold text-lg text-slate-100 hover:text-cyan-400 cursor-pointer transition-colors">
                          {job.job_title}
                        </h3>
                        <span className="px-2.5 py-0.5 bg-slate-800 text-slate-400 text-xs rounded-full border border-slate-700/50">
                          {job.status || "Found"}
                        </span>
                      </div>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-slate-400">
                        <span className="font-semibold text-cyan-400">{job.company_name}</span>
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5" />
                          {job.location}
                        </span>
                        {job.salary && job.salary !== "Not Specified" && (
                          <span className="flex items-center gap-1 text-emerald-400">
                            <DollarSign className="w-3.5 h-3.5" />
                            {job.salary}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 self-end md:self-start">
                      <button
                        onClick={() => setExpandedJobId(isExpanded ? null : job.id)}
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs font-semibold text-slate-300 transition-all"
                      >
                        {isExpanded ? "Hide Intel" : "Company Intel"}
                      </button>
                      <button
                        onClick={() => onSelectJob(job)}
                        className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                          isSelected 
                            ? "bg-emerald-600/20 text-emerald-400 border border-emerald-500/30" 
                            : "bg-cyan-600 hover:bg-cyan-500 text-white"
                        }`}
                      >
                        {isSelected ? <CheckCircle className="w-3.5 h-3.5" /> : <FileText className="w-3.5 h-3.5" />}
                        {isSelected ? "Job Selected" : "Select Job"}
                      </button>
                    </div>
                  </div>
                  
                  <p className="mt-4 text-slate-300 text-sm line-clamp-3 leading-relaxed">
                    {job.description}
                  </p>
                  
                  {job.url && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 mt-3 text-xs text-cyan-500 hover:text-cyan-400 transition-colors"
                    >
                      View Original Job Post
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                {/* Expanded Company Profile Card (Agent 1 Output) */}
                {isExpanded && profile && (
                  <div className="border-t border-slate-800/80 bg-dark-800/40 rounded-b-2xl p-6 space-y-6">
                    <h4 className="font-bold text-sm text-cyan-400 flex items-center gap-2 glow-cyan">
                      <Cpu className="w-4 h-4" />
                      Company Research Dossier (Agent AI Synthesis)
                    </h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="md:col-span-2 space-y-4">
                        <div className="space-y-1">
                          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Business Domain</span>
                          <p className="text-sm text-slate-300 leading-relaxed">{profile.domain}</p>
                        </div>
                        
                        <div className="space-y-1">
                          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Recent Milestones & News</span>
                          <p className="text-sm text-slate-300 leading-relaxed">{profile.recent_news}</p>
                        </div>
                      </div>

                      <div className="space-y-4 bg-slate-900/40 border border-slate-800 p-4 rounded-xl">
                        <div className="space-y-1.5">
                          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider flex items-center gap-1">
                            <Award className="w-3.5 h-3.5 text-yellow-500" />
                            Funding Status
                          </span>
                          <p className="text-sm font-semibold text-slate-200">{profile.funding_status}</p>
                        </div>
                        
                        <div className="space-y-1.5">
                          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider flex items-center gap-1">
                            <Cpu className="w-3.5 h-3.5 text-cyan-500" />
                            Core Tech Stack
                          </span>
                          <div className="flex flex-wrap gap-1.5 mt-1">
                            {profile.tech_stack.split(",").map((tech, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-cyan-950/40 text-cyan-400 border border-cyan-500/20 text-[10px] font-medium rounded"
                              >
                                {tech.trim()}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
