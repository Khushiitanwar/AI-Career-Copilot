import React, { useState } from "react";
import { uploadResume, tailorResume, getDownloadUrl } from "../utils/api";
import { Upload, FileText, CheckCircle, ArrowRight, Download, Edit2, Info, Sparkles, RefreshCw } from "lucide-react";

export default function ResumeTailor({ selectedJob, onTailorComplete, resumeData, setResumeData }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [tailoring, setTailoring] = useState(false);
  const [tailoringResult, setTailoringResult] = useState(null);
  const [error, setError] = useState(null);
  const [customJobDesc, setCustomJobDesc] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setError(null);
    } else {
      setError("Please select a valid PDF file.");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const data = await uploadResume(file);
      setResumeData({
        id: data.resume_id,
        filename: data.filename,
        originalText: data.sample_text
      });
    } catch (err) {
      setError(err.message || "Failed to upload resume. Ensure backend is active.");
    } finally {
      setUploading(false);
    }
  };

  const handleTailor = async () => {
    if (!resumeData?.id) return;
    setTailoring(true);
    setError(null);
    try {
      // Use selected job id from job finder.
      const data = await tailorResume(resumeData.id, selectedJob.id);
      setTailoringResult(data);
      onTailorComplete(data); // Pass results back to parent to unlock scoring and debate
    } catch (err) {
      setError(err.message || "Resume tailoring failed. Please try again.");
    } finally {
      setTailoring(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Uploader & Job Context */}
        <div className="lg:col-span-1 space-y-6">
          {/* Step 1: Upload Resume */}
          <div className="glass rounded-2xl p-6 border border-white/5 space-y-4">
            <h3 className="font-bold text-sm text-cyan-400 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 flex items-center justify-center text-xs font-bold border border-cyan-500/20">1</span>
              Upload Original Resume (PDF)
            </h3>
            
            {!resumeData ? (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-slate-700/50 hover:border-cyan-500/50 rounded-xl p-6 transition-colors flex flex-col items-center justify-center text-center cursor-pointer relative bg-dark-900/40">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <Upload className="w-8 h-8 text-slate-500 mb-2" />
                  <p className="text-xs text-slate-300 font-medium">
                    {file ? file.name : "Click or drag PDF resume here"}
                  </p>
                  <p className="text-[10px] text-slate-500 mt-1">PDF format only (Max 5MB)</p>
                </div>
                
                {file && (
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 text-white font-medium rounded-xl text-xs transition-all shadow-md shadow-cyan-600/10 flex items-center justify-center gap-1.5"
                  >
                    {uploading ? (
                      <>
                        <RefreshCw className="w-4.5 h-4.5 animate-spin" />
                        Extracting Text...
                      </>
                    ) : (
                      <>
                        <Upload className="w-3.5 h-3.5" />
                        Parse & Save Resume
                      </>
                    )}
                  </button>
                )}
              </div>
            ) : (
              <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-cyan-950 border border-cyan-500/20 text-cyan-400 rounded-lg">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-200 line-clamp-1">{resumeData.filename}</p>
                    <p className="text-[10px] text-emerald-400 flex items-center gap-0.5 mt-0.5">
                      <CheckCircle className="w-3 h-3" /> Ready
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setResumeData(null);
                    setFile(null);
                    setTailoringResult(null);
                  }}
                  className="text-[10px] font-semibold text-red-400 hover:underline"
                >
                  Replace
                </button>
              </div>
            )}
          </div>

          {/* Step 2: Job Context Target */}
          <div className="glass rounded-2xl p-6 border border-white/5 space-y-4">
            <h3 className="font-bold text-sm text-cyan-400 flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 flex items-center justify-center text-xs font-bold border border-cyan-500/20">2</span>
              Target Job Profile
            </h3>
            
            {selectedJob ? (
              <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-xl space-y-2">
                <p className="text-xs font-bold text-slate-200">{selectedJob.job_title}</p>
                <p className="text-[11px] font-semibold text-cyan-400">{selectedJob.company_name}</p>
                <p className="text-[10px] text-slate-400 flex items-center gap-1">
                  <ArrowRight className="w-3 h-3 text-slate-600" />
                  Using profile card research cache
                </p>
              </div>
            ) : (
              <div className="p-4 bg-yellow-950/20 border border-yellow-500/20 rounded-xl text-yellow-400 text-xs flex gap-2">
                <Info className="w-4 h-4 shrink-0 mt-0.5" />
                <p>Go to the <b>Job Finder</b> tab and search/select a job listing to enable tailoring, or paste a description below.</p>
              </div>
            )}

            {resumeData && selectedJob && (
              <button
                onClick={handleTailor}
                disabled={tailoring}
                className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 text-white font-semibold rounded-xl text-xs transition-all shadow-md shadow-cyan-600/10 flex items-center justify-center gap-2"
              >
                {tailoring ? (
                  <>
                    <RefreshCw className="w-4.5 h-4.5 animate-spin" />
                    Analyzing & Tailoring Resume...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Tailor Resume
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Right Column: Tailoring Output & Previews */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="p-4 bg-red-950/40 border border-red-500/20 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          {!tailoringResult && !tailoring ? (
            <div className="glass rounded-2xl p-12 border border-white/5 text-center text-slate-500 flex flex-col items-center justify-center min-h-[400px]">
              <Sparkles className="w-12 h-12 text-slate-700 mb-4" />
              <h3 className="font-semibold text-base text-slate-300">Resume Tailoring Workbench</h3>
              <p className="text-xs mt-1 max-w-sm">Upload a PDF resume, select a job, and click Tailor. The AI writer will rewrite experience bullets and align keywords.</p>
            </div>
          ) : tailoring ? (
            <div className="glass rounded-2xl p-12 border border-white/5 text-center flex flex-col items-center justify-center min-h-[400px] space-y-4">
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
              <div>
                <h4 className="font-bold text-slate-200">Rephrasing Experience Bullet Points...</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">Calling OpenRouter LLM to conduct a skills gap diff and write impact-oriented sentences. Rules: Never fabricate.</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Action Banner */}
              <div className="glass rounded-2xl p-6 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-dark-800 via-dark-800 to-cyan-950/20">
                <div className="space-y-1">
                  <h3 className="font-bold text-base text-emerald-400 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Resume Tailored Successfully!
                  </h3>
                  <p className="text-xs text-slate-400">Generated a custom, single-page professional resume PDF matching {selectedJob?.company_name}.</p>
                </div>
                <a
                  href={getDownloadUrl(resumeData.id)}
                  download
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 shadow-md shadow-emerald-600/10 transition-all self-start sm:self-center"
                >
                  <Download className="w-4 h-4" />
                  Download PDF Resume
                </a>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* AI Change Log */}
                <div className="glass rounded-2xl p-6 border border-white/5 space-y-4 h-[450px] flex flex-col">
                  <h4 className="font-bold text-sm text-cyan-400 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    AI Optimization Changelog
                  </h4>
                  <div className="flex-1 overflow-y-auto pr-2 space-y-3">
                    {tailoringResult.suggested_changes.map((change, idx) => (
                      <div key={idx} className="p-3 bg-slate-900/60 border border-slate-800 rounded-xl text-xs text-slate-300 leading-relaxed flex gap-2">
                        <span className="text-cyan-500 font-bold mt-0.5">•</span>
                        <span>{change}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Structured Sections Preview */}
                <div className="glass rounded-2xl p-6 border border-white/5 space-y-4 h-[450px] flex flex-col">
                  <h4 className="font-bold text-sm text-cyan-400 flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Tailored Content Preview
                  </h4>
                  <div className="flex-1 overflow-y-auto pr-2 space-y-4 text-xs">
                    {tailoringResult.sections.map((sec, idx) => {
                      if (sec.title === "Header") return null;
                      return (
                        <div key={idx} className="space-y-1.5">
                          <h5 className="font-bold text-slate-200 border-b border-slate-800 pb-1 uppercase text-[10px] tracking-wider text-cyan-400">
                            {sec.title}
                          </h5>
                          {typeof sec.content === "string" ? (
                            <p className="text-slate-300 leading-relaxed">{sec.content}</p>
                          ) : Array.isArray(sec.content) ? (
                            <div className="space-y-2">
                              {sec.content.map((item, itemIdx) => (
                                <div key={itemIdx} className="space-y-1">
                                  <p className="font-semibold text-slate-200">
                                    {item.role || item.title || item.degree} 
                                    {item.company || item.school ? ` at ${item.company || item.school}` : ""}
                                  </p>
                                  <ul className="list-disc pl-4 space-y-1 text-slate-400">
                                    {Array.isArray(item.description) ? (
                                      item.description.map((bullet, bulletIdx) => (
                                        <li key={bulletIdx}>{bullet}</li>
                                      ))
                                    ) : (
                                      <li>{item.description}</li>
                                    )}
                                  </ul>
                                </div>
                              ))}
                            </div>
                          ) : null}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
