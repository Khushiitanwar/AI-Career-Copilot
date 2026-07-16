import React, { useState, useEffect } from "react";
import JobSearch from "./components/JobSearch";
import ResumeTailor from "./components/ResumeTailor";
import RecruiterScore from "./components/RecruiterScore";
import DebateArena from "./components/DebateArena";
import Settings from "./components/Settings";
import { checkBackendHealth } from "./utils/api";
import { Briefcase, FileText, Award, Users, Settings as SettingsIcon, Link, ShieldAlert, Cpu } from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("jobs");
  const [selectedJob, setSelectedJob] = useState(null);
  const [resumeData, setResumeData] = useState(null);
  const [tailoredData, setTailoredData] = useState(null);
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  useEffect(() => {
    verifyHealth();
  }, []);

  const verifyHealth = async () => {
    const health = await checkBackendHealth();
    setIsBackendHealthy(health);
  };

  const handleSelectJob = (job) => {
    setSelectedJob(job);
    setActiveTab("tailor"); // Automatically transition user to resume upload/tailoring
  };

  const handleTailorComplete = (result) => {
    setTailoredData(result);
  };

  // Logic to determine if tabs should be locked
  const isTailorLocked = !selectedJob;
  const isScoreLocked = !selectedJob || !resumeData || !tailoredData;
  const isDebateLocked = !selectedJob || !resumeData || !tailoredData;

  return (
    <div className="min-h-screen bg-dark-900 bg-gradient-to-tr from-dark-900 via-[#0e172a] to-[#0b162c] pb-12">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 glass border-b border-white/5 shadow-md">
        <div className="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-cyan-950 border border-cyan-500/30 text-cyan-400 rounded-xl shadow-lg shadow-cyan-500/5 pulse-glow-cyan">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5 uppercase">
                AI Career Copilot
                <span className="text-[9px] px-1.5 py-0.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded">
                  LangGraph Inside
                </span>
              </h1>
              <p className="text-[10px] text-slate-400">Autonomous Multi-Agent Job Search & Evaluation Panel</p>
            </div>
          </div>

          {/* Connection Status Badge */}
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${isBackendHealthy ? "bg-emerald-500 animate-pulse" : "bg-red-500"}`}></span>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider hidden sm:inline">
              Backend Server: {isBackendHealthy ? "Online" : "Offline / Retry"}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 mt-8 space-y-6">
        {/* Navigation Tabs Bar */}
        <div className="glass rounded-2xl p-2 border border-white/5 flex flex-wrap gap-1 shadow-lg">
          <button
            onClick={() => setActiveTab("jobs")}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-semibold transition-all ${
              activeTab === "jobs"
                ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
            }`}
          >
            <Briefcase className="w-4 h-4" />
            1. Job Finder & Research
          </button>

          <button
            onClick={() => !isTailorLocked && setActiveTab("tailor")}
            disabled={isTailorLocked}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-semibold transition-all relative ${
              isTailorLocked
                ? "opacity-40 cursor-not-allowed text-slate-500"
                : activeTab === "tailor"
                ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
            }`}
          >
            <FileText className="w-4 h-4" />
            2. Resume Tailoring
            {isTailorLocked && <ShieldAlert className="w-3.5 h-3.5 text-slate-500" />}
          </button>

          <button
            onClick={() => !isScoreLocked && setActiveTab("score")}
            disabled={isScoreLocked}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-semibold transition-all relative ${
              isScoreLocked
                ? "opacity-40 cursor-not-allowed text-slate-500"
                : activeTab === "score"
                ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
            }`}
          >
            <Award className="w-4 h-4" />
            3. Recruiter Scan
            {isScoreLocked && <ShieldAlert className="w-3.5 h-3.5 text-slate-500" />}
          </button>

          <button
            onClick={() => !isDebateLocked && setActiveTab("debate")}
            disabled={isDebateLocked}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-semibold transition-all relative ${
              isDebateLocked
                ? "opacity-40 cursor-not-allowed text-slate-500"
                : activeTab === "debate"
                ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/10"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
            }`}
          >
            <Users className="w-4 h-4" />
            4. Debate Arena
            {isDebateLocked && <ShieldAlert className="w-3.5 h-3.5 text-slate-500" />}
          </button>

          <button
            onClick={() => setActiveTab("settings")}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-semibold transition-all ml-auto ${
              activeTab === "settings"
                ? "bg-cyan-600 text-white"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
            }`}
          >
            <SettingsIcon className="w-4 h-4" />
            System Intel
          </button>
        </div>

        {/* Informational Stage Banner */}
        {activeTab === "jobs" && !selectedJob && (
          <div className="glass border-l-4 border-cyan-500 rounded-r-2xl p-4 text-xs text-cyan-200 flex items-center gap-2 shadow bg-cyan-950/5">
            <Cpu className="w-4.5 h-4.5 text-cyan-400 shrink-0" />
            <p><b>Getting Started:</b> Search for a role (e.g. <b>"AI Intern"</b>) and click <b>"Select Job"</b> on any posting card to lock in your targeting configuration and proceed.</p>
          </div>
        )}

        {activeTab === "tailor" && !resumeData && (
          <div className="glass border-l-4 border-yellow-500 rounded-r-2xl p-4 text-xs text-yellow-200 flex items-center gap-2 shadow bg-yellow-950/5 animate-pulse">
            <FileText className="w-4.5 h-4.5 text-yellow-400 shrink-0" />
            <p><b>Prerequisite:</b> Drag your original PDF resume file into the upload zone and press <b>"Parse & Save"</b> to begin alignment.</p>
          </div>
        )}

        {/* Tab Panels */}
        <div className="mt-6">
          {activeTab === "jobs" && (
            <JobSearch onSelectJob={handleSelectJob} selectedJobId={selectedJob?.id} />
          )}

          {activeTab === "tailor" && (
            <ResumeTailor
              selectedJob={selectedJob}
              onTailorComplete={handleTailorComplete}
              resumeData={resumeData}
              setResumeData={setResumeData}
            />
          )}

          {activeTab === "score" && (
            <RecruiterScore resumeData={resumeData} selectedJob={selectedJob} />
          )}

          {activeTab === "debate" && (
            <DebateArena resumeData={resumeData} selectedJob={selectedJob} />
          )}

          {activeTab === "settings" && <Settings />}
        </div>
      </main>

      {/* Floating Status Bar */}
      {selectedJob && (
        <div className="fixed bottom-4 right-4 z-50 glass border border-slate-700/80 rounded-xl px-4 py-2.5 flex items-center gap-3 text-xs shadow-2xl animate-slideUp">
          <div className="flex flex-col">
            <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Target Job Locked</span>
            <span className="font-semibold text-slate-200 line-clamp-1">{selectedJob.job_title} at <b className="text-cyan-400 font-semibold">{selectedJob.company_name}</b></span>
          </div>
        </div>
      )}
    </div>
  );
}
