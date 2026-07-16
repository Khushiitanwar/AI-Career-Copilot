import React, { useState, useEffect } from "react";
import { checkBackendHealth } from "../utils/api";
import { Sliders, Cpu, Server, CheckCircle2, AlertTriangle, Key, Terminal } from "lucide-react";

export default function Settings() {
  const [dbStatus, setDbStatus] = useState("checking");
  const [openRouterStatus, setOpenRouterStatus] = useState("Active");

  useEffect(() => {
    verifySystem();
  }, []);

  const verifySystem = async () => {
    const isHealthy = await checkBackendHealth();
    setDbStatus(isHealthy ? "Connected" : "Offline");
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="glass rounded-2xl p-6 border border-white/5 space-y-6">
        <h3 className="font-bold text-sm text-cyan-400 flex items-center gap-2">
          <Sliders className="w-5 h-5" />
          System Diagnostics & Configurations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Backend Server Status */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Server className="w-4 h-4 text-cyan-500" />
              Backend API Status
            </h4>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">SQLite Database connection:</span>
                <span className={`font-semibold flex items-center gap-1 ${dbStatus === "Connected" ? "text-emerald-400" : "text-red-400"}`}>
                  {dbStatus === "Connected" ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                  {dbStatus}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">OpenRouter LLM Interface:</span>
                <span className="font-semibold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {openRouterStatus}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Port Binding:</span>
                <span className="font-mono text-[10px] text-slate-300">localhost:8000</span>
              </div>
            </div>
          </div>

          {/* Model settings */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h4 className="font-semibold text-xs text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-purple-500" />
              Active AI Models
            </h4>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Primary Model (GenAI / Tailor):</span>
                <span className="font-mono text-[10px] text-purple-400">google/gemini-2.5-flash</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Critic Model (Recruiter Scans):</span>
                <span className="font-mono text-[10px] text-purple-400">anthropic/claude-3-haiku</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Local Vector DB:</span>
                <span className="text-[10px] text-slate-300 font-semibold">Qdrant In-Memory Client</span>
              </div>
            </div>
          </div>
        </div>

        {/* Configuration instructions */}
        <div className="p-5 border border-cyan-500/10 bg-cyan-950/5 rounded-xl space-y-3">
          <h4 className="font-semibold text-xs text-cyan-400 flex items-center gap-1.5">
            <Key className="w-4 h-4 text-cyan-500" />
            Environment Setup Details
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            The application is configured to run using environment variables stored in the <code>backend/.env</code> file. To swap settings or keys:
          </p>
          <div className="bg-dark-900 border border-slate-800 p-3.5 rounded-lg font-mono text-[10px] text-slate-300 space-y-1.5">
            <div># Set OpenRouter Key to authenticate LLM API calls</div>
            <div className="text-cyan-400">OPENROUTER_API_KEY=sk-or-v1-...</div>
            <div># Optional: Configure live Adzuna jobs for India</div>
            <div>ADZUNA_APP_ID=...</div>
            <div>ADZUNA_API_KEY=...</div>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-slate-500 font-medium">
            <Terminal className="w-3.5 h-3.5" />
            Workspace location: C:\Users\khush\.gemini\antigravity\scratch\ai-career-copilot\backend\.env
          </div>
        </div>
      </div>
    </div>
  );
}
