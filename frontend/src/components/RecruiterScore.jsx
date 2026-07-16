import React, { useState } from "react";
import { getRecruiterScore } from "../utils/api";
import { Award, CheckCircle2, AlertTriangle, AlertCircle, RefreshCw, Star, Play } from "lucide-react";

export default function RecruiterScore({ resumeData, selectedJob }) {
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const triggerReview = async () => {
    if (!resumeData?.id || !selectedJob?.id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getRecruiterScore(resumeData.id, selectedJob.id);
      setScoreData(data);
    } catch (err) {
      setError(err.message || "Failed to compile recruiter review.");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8.5) return "text-emerald-400 stroke-emerald-500";
    if (score >= 7.0) return "text-cyan-400 stroke-cyan-500";
    if (score >= 5.0) return "text-yellow-400 stroke-yellow-500";
    return "text-red-400 stroke-red-500";
  };

  return (
    <div className="space-y-6">
      {/* Run Review Action Panel */}
      {!scoreData && !loading ? (
        <div className="glass rounded-2xl p-12 border border-white/5 text-center flex flex-col items-center justify-center min-h-[400px] space-y-6">
          <Award className="w-16 h-16 text-slate-700 animate-pulse" />
          <div className="max-w-md space-y-2">
            <h3 className="font-bold text-lg text-slate-200">Recruiter Perspective Reviewer</h3>
            <p className="text-sm text-slate-400">
              Submit your tailored resume to an automated review simulating a senior technical recruiter with 10+ years experience at a top AI firm.
            </p>
          </div>
          <button
            onClick={triggerReview}
            disabled={!resumeData?.id || !selectedJob?.id}
            className="px-8 py-3.5 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-semibold rounded-xl text-xs transition-all shadow-md shadow-cyan-600/10 flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4 fill-current" />
            Initiate Recruiter Scan
          </button>
        </div>
      ) : loading ? (
        <div className="glass rounded-2xl p-12 border border-white/5 text-center flex flex-col items-center justify-center min-h-[400px] space-y-4">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div>
            <h4 className="font-bold text-slate-200">Evaluating Tailored Resume...</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
              Scanning keyword density, checking employment history alignment, and mapping ATS compatibility markers.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-6 animate-fadeIn">
          {/* Header Score Overview */}
          <div className="glass rounded-2xl p-6 border border-white/5 grid grid-cols-1 md:grid-cols-4 gap-6 items-center bg-gradient-to-r from-dark-800 via-dark-800 to-cyan-950/15">
            {/* Circular Gauge */}
            <div className="flex flex-col items-center justify-center space-y-1.5 md:border-r border-slate-800/80 pr-6">
              <div className="relative w-28 h-28">
                {/* SVG Radial Progress */}
                <svg className="w-full h-full -rotate-95" viewBox="0 0 36 36">
                  <path
                    className="stroke-slate-800"
                    strokeWidth="3"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className={`stroke-current ${getScoreColor(scoreData.score).split(" ")[1]}`}
                    strokeDasharray={`${scoreData.score * 10}, 100`}
                    strokeWidth="3"
                    strokeLinecap="round"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className={`text-3xl font-extrabold ${getScoreColor(scoreData.score).split(" ")[0]}`}>
                    {scoreData.score}
                  </span>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Score / 10</span>
                </div>
              </div>
            </div>

            {/* Recruiter Verdict block */}
            <div className="md:col-span-3 space-y-3">
              <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
                <Star className="w-4 h-4 fill-cyan-500/20" />
                Senior Recruiter Verdict
              </div>
              <p className="text-lg font-bold text-slate-100 italic leading-relaxed">
                "{scoreData.verdict}"
              </p>
              <div className="flex items-center gap-4 mt-2">
                <button
                  onClick={triggerReview}
                  className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[10px] font-semibold rounded-lg flex items-center gap-1.5 transition-all"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Re-evaluate
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Strengths Card */}
            <div className="glass rounded-2xl p-6 border border-white/5 space-y-4">
              <h4 className="font-bold text-sm text-emerald-400 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                Key Hiring Advantages
              </h4>
              <div className="space-y-3">
                {scoreData.strengths.map((str, idx) => (
                  <div key={idx} className="p-4 bg-emerald-950/15 border border-emerald-500/10 rounded-xl text-xs text-slate-300 leading-relaxed flex gap-2">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{str}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Weaknesses Card */}
            <div className="glass rounded-2xl p-6 border border-white/5 space-y-4">
              <h4 className="font-bold text-sm text-yellow-400 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                Gaps & Vague Areas
              </h4>
              <div className="space-y-3">
                {scoreData.weaknesses.map((weak, idx) => (
                  <div key={idx} className="p-4 bg-yellow-950/15 border border-yellow-500/10 rounded-xl text-xs text-slate-300 leading-relaxed flex gap-2">
                    <span className="text-yellow-400 font-bold">•</span>
                    <span>{weak}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* ATS Missing Keywords */}
            <div className="glass rounded-2xl p-6 border border-white/5 space-y-4">
              <h4 className="font-bold text-sm text-cyan-400 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-cyan-500" />
                Missing ATS Keywords
              </h4>
              
              {scoreData.ats_keywords_missing.length === 0 ? (
                <div className="p-4 bg-emerald-950/15 border border-emerald-500/10 rounded-xl text-xs text-emerald-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  All critical keywords mapped in resume. Excellent match!
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-[11px] text-slate-400">
                    The recruiter noticed that these standard terms and technologies from the job description are missing in your resume. Integrate them where appropriate:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {scoreData.ats_keywords_missing.map((keyword, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 bg-cyan-950/30 text-cyan-400 border border-cyan-500/20 text-[10px] font-semibold rounded-lg"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
