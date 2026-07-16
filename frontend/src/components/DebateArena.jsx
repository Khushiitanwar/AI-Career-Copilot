import React, { useState, useEffect } from "react";
import { runDebate } from "../utils/api";
import { Users, Shield, Cpu, MessageSquare, Award, Play, CheckCircle2, ChevronRight, CornerDownRight } from "lucide-react";

export default function DebateArena({ resumeData, selectedJob }) {
  const [debateData, setDebateData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Animation state to render debate messages sequentially
  const [visibleMessages, setVisibleMessages] = useState([]);
  const [animating, setAnimating] = useState(false);
  const [showVerdict, setShowVerdict] = useState(false);

  const startDebateSimulation = async () => {
    if (!resumeData?.id || !selectedJob?.id) return;
    
    setLoading(true);
    setError(null);
    setVisibleMessages([]);
    setShowVerdict(false);
    
    try {
      const data = await runDebate(resumeData.id, selectedJob.id);
      setDebateData(data);
      animateMessages(data.transcript);
    } catch (err) {
      setError(err.message || "Failed to run debate workflow.");
      setLoading(false);
    }
  };

  const animateMessages = (transcript) => {
    setLoading(false);
    setAnimating(true);
    let index = 0;
    
    const interval = setInterval(() => {
      if (index < transcript.length) {
        setVisibleMessages((prev) => [...prev, transcript[index]]);
        index++;
      } else {
        clearInterval(interval);
        setAnimating(false);
        setShowVerdict(true);
      }
    }, 1500); // 1.5 second delay per agent statement
  };

  const getAgentStyles = (agentName) => {
    switch (agentName) {
      case "Skill Matcher":
        return {
          bg: "bg-cyan-950/40 border-cyan-500/20",
          text: "text-cyan-400",
          tagBg: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
        };
      case "Experience Evaluator":
        return {
          bg: "bg-orange-950/30 border-orange-500/20",
          text: "text-orange-400",
          tagBg: "bg-orange-500/10 text-orange-400 border-orange-500/20"
        };
      case "Salary Analyzer":
        return {
          bg: "bg-emerald-950/30 border-emerald-500/20",
          text: "text-emerald-400",
          tagBg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
        };
      case "Culture Fit Agent":
        return {
          bg: "bg-purple-950/30 border-purple-500/20",
          text: "text-purple-400",
          tagBg: "bg-purple-500/10 text-purple-400 border-purple-500/20"
        };
      default:
        return {
          bg: "bg-slate-900/60 border-slate-800",
          text: "text-slate-300",
          tagBg: "bg-slate-800 text-slate-400"
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* Launch Panel */}
      {!debateData && !loading ? (
        <div className="glass rounded-2xl p-12 border border-white/5 text-center flex flex-col items-center justify-center min-h-[400px] space-y-6">
          <Users className="w-16 h-16 text-slate-700 animate-pulse" />
          <div className="max-w-md space-y-2">
            <h3 className="font-bold text-lg text-slate-200">Multi-Agent Debate Arena</h3>
            <p className="text-sm text-slate-400">
              Trigger a simultaneous review process. Four specialized AI sub-agents will evaluate your candidacy from distinct perspectives (Skills, Experience, Salary, Culture), debate their perspectives, and submit their arguments to a Judge Agent who renders the final decision.
            </p>
          </div>
          <button
            onClick={startDebateSimulation}
            disabled={!resumeData?.id || !selectedJob?.id}
            className="px-8 py-3.5 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-semibold rounded-xl text-xs transition-all shadow-md shadow-cyan-600/10 flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4 fill-current" />
            Convene Debate Panel
          </button>
        </div>
      ) : loading ? (
        <div className="glass rounded-2xl p-12 border border-white/5 text-center flex flex-col items-center justify-center min-h-[400px] space-y-4">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div>
            <h4 className="font-bold text-slate-200">Spawning Parallel LangGraph Nodes...</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
              LangGraph is orchestrating four parallel model executions concurrently. Initializing Skill Matcher, Experience Evaluator, Salary Analyzer, and Culture Fit.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          {/* Debate Stream */}
          <div className="lg:col-span-2 space-y-4">
            <div className="glass rounded-2xl p-5 border border-white/5 flex items-center justify-between">
              <h4 className="font-bold text-sm text-cyan-400 flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Live Agent Arguments
              </h4>
              {animating && (
                <span className="text-[10px] text-cyan-400 font-bold animate-pulse flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full animate-ping"></div>
                  Agent speaking...
                </span>
              )}
            </div>

            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
              {visibleMessages.map((msg, idx) => {
                const styles = getAgentStyles(msg.agent);
                return (
                  <div
                    key={idx}
                    className={`glass rounded-xl p-5 border ${styles.bg} transition-all duration-500 animate-slideUp`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2.5 py-0.5 border text-[10px] font-bold rounded-md ${styles.tagBg}`}>
                        {msg.agent}
                      </span>
                      <span className="text-[10px] text-slate-500">Super-step 2</span>
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed italic">
                      "{msg.message}"
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Judge Final Decision */}
          <div className="lg:col-span-1 space-y-6">
            {!showVerdict && animating ? (
              <div className="glass rounded-2xl p-8 border border-white/5 text-center flex flex-col items-center justify-center min-h-[300px] space-y-2">
                <Shield className="w-10 h-10 text-slate-700 animate-bounce" />
                <h4 className="font-bold text-sm text-slate-300">Awaiting Panel Debate</h4>
                <p className="text-[11px] text-slate-500 max-w-[200px] mx-auto">
                  The lead hiring judge node will render the final decision after all parallel nodes complete.
                </p>
              </div>
            ) : showVerdict && (
              <div className="space-y-6 animate-fadeIn">
                {/* Composite Score Card */}
                <div className="glass rounded-2xl p-6 border border-yellow-500/20 bg-gradient-to-br from-dark-800 to-yellow-950/10 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                    <h4 className="font-bold text-sm text-yellow-500 flex items-center gap-2">
                      <Shield className="w-4 h-4" />
                      Lead Judge Synthesis
                    </h4>
                    <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 text-[9px] font-bold uppercase rounded">
                      Consensus
                    </span>
                  </div>

                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-extrabold text-slate-100 glow-purple">
                      {debateData.score}
                    </span>
                    <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">/ 100 Match Score</span>
                  </div>

                  <div className="space-y-3">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                      Consolidated Action Items
                    </span>
                    <div className="space-y-2.5">
                      {debateData.recommendations.map((rec, idx) => (
                        <div key={idx} className="flex gap-2 text-xs text-slate-300 leading-relaxed">
                          <CornerDownRight className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <button
                  onClick={startDebateSimulation}
                  className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-semibold rounded-xl text-xs flex items-center justify-center gap-1.5 transition-all"
                >
                  Re-run Debate Session
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
