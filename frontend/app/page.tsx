"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Upload, Loader2, Rocket, Mail } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [resume, setResume] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [scoreData, setScoreData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Upload Resume
  const handleUpload = async () => {
    if (!resume) return alert("Please select a PDF resume!");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", resume);
    try {
      const res = await axios.post("http://127.0.0.1:8000/upload_resume/", formData);
      setResumeText(res.data.extracted_text);
      console.log(res.data.extracted_text)
      setLoading(false)
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (!error.response) {
          alert("Network error - Please check if the server is running");
        } else {
          alert(`Server error: ${error.response.status} - ${error.response.data}`);
        }
      }
      console.error(error);
    }
  };

  // Get ATS Score (SkillNER-backed)
  const handleScore = async () => {
    if (!resumeText || !jdText) return alert("Please upload resume and paste job description!");
    // setLoading(false);
    try {
      console.log("Resume score part")
      const res = await axios.post("http://localhost:8000/score_resume/", {
        resume_data: resumeText,
        jd_data: jdText,
      });
      setScoreData(res.data);
      console.log(res.data)
    } catch (err) {
      console.error(err);
      console.log(err)
      alert("Error scoring resume!");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    localStorage.setItem("resume_data", resumeText);
    localStorage.setItem("jd_data", jdText);
    if (!resumeText || !jdText) return alert("Please upload resume and paste job description!");
    else{
      window.location.href = "/email_generator";
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-slate-900 to-black p-6 text-white">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl shadow-lg p-10 w-full max-w-3xl"
      >
        <h1 className="text-3xl font-bold text-center mb-6">🚀 ATS Resume Scorer (Skill-Based)</h1>

        {/* Upload Resume */}
        <div className="mb-6">
          <label className="block mb-2 text-sm text-white/80 font-semibold">Upload Resume (PDF)</label>
          <div className="flex items-center gap-2">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setResume(e.target.files?.[0] || null)}
              className="bg-white/10 border border-white/20 rounded-md p-2 w-full"
            />
            <button
              onClick={handleUpload}
              disabled={loading || !resume}
              className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded flex items-center gap-2"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
              Upload
            </button>
          </div>
        </div>

        {/* Job Description */}
        <div className="mb-6">
          <label className="block mb-2 text-sm text-white/80 font-semibold">Paste Job Description</label>
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the full job description here..."
            className="w-full h-48 bg-white/10 border border-white/20 rounded-md p-3 text-gray-200"
          />
        </div>

        {/* Analyze Button */}
        <div className="text-center">
          <button
            onClick={handleScore}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg text-white flex items-center gap-2 mx-auto"
          >
            {loading ? <Loader2 className="animate-spin" /> : <Rocket size={18} />}
            {loading ? "Analyzing..." : "Get ATS Score"}
          </button>
          
          <button
            onClick={handleNext}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg mt-4"
          >
            <Mail size={18} className="inline-block mr-2 mb-1"></Mail>
            Generate Email
          </button>


        </div>

        {/* Results Section */}
        {scoreData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mt-8 bg-white/10 border border-white/20 rounded-xl p-6"
          >
            <h2 className="text-2xl font-semibold text-center mb-3">
              ATS Score: <span className="text-purple-400">{scoreData["ATS Skill Score"]}</span>
            </h2>


            {/* Progress Bar */}
            <div className="w-full bg-gray-800 h-3 rounded-full mb-4">
              <div
                className="bg-gradient-to-r from-purple-400 to-blue-400 h-3 rounded-full"
                style={{ width: `${scoreData["ATS Score"]}%` }}
              ></div>
            </div>

            {/* Matched and Missing Skills */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-lg font-semibold text-green-400 mb-2">Matched Skills ✅</h3>
                <div className="flex flex-wrap gap-2">
                  {scoreData["Matched Skills"]?.length ? (
                    scoreData["Matched Skills"].map((skill: string, i: number) => (
                      <span
                        key={i}
                        className="bg-green-500/20 border border-green-400/30 px-2 py-1 rounded text-sm"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-400 text-sm">No matched skills.</p>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-red-400 mb-2">Missing Skills ⚠️</h3>
                <div className="flex flex-wrap gap-2">
                  {scoreData["Missing Skills"]?.length ? (
                    scoreData["Missing Skills"].map((skill: string, i: number) => (
                      <span
                        key={i}
                        className="bg-red-500/20 border border-red-400/30 px-2 py-1 rounded text-sm"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-400 text-sm">No missing skills 🎉</p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </main>
  );
}
