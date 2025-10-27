"use client";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import axios from "axios";

export default function GenerateEmail() {
  const params = useSearchParams();
  const resumeText = params.get("resumeText");
  const jdText = params.get("jdText");
  const [generatedEmail,setGeneratedEmail]=useState("")
  const [tone, setTone] = useState("formal");
  const [maxChars, setMaxChars] = useState(300);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  
const handleEmailGen = async () => {
  const formData = new FormData();
  console.log("Generating email")
formData.append("resume_data", localStorage.getItem("resume_data") || "");
formData.append("jd_data", localStorage.getItem("jd_data") || "");
formData.append("tone", tone);
formData.append("max_chars", maxChars.toString());

const res = await axios.post("http://127.0.0.1:8000/generate_email/", formData, {
  headers: { "Content-Type": "multipart/form-data" },
});
console.log(res.data.email)
  setGeneratedEmail(res.data.email);
};

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex flex-col items-center py-12">
      <h1 className="text-3xl font-bold mb-6">AI Cover Letter / Cold Email Generator</h1>

      <div className="w-full max-w-2xl space-y-4">
        <div>
          <label className="block mb-2 text-sm">Tone</label>
          <select
            className="w-full p-2 bg-white/10 border border-white/20 rounded-lg"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
          >
            <option value="formal">Formal</option>
            <option value="friendly">Friendly</option>
            <option value="cold">Cold / Direct</option>
            <option value="warm">Warm / Personal</option>
          </select>
        </div>

        <div>
          <label className="block mb-2 text-sm">Max Characters</label>
          <input
            type="number"
            className="w-full p-2 bg-white/10 border border-white/20 rounded-lg"
            value={maxChars}
            onChange={(e) => setMaxChars(Number(e.target.value))}
            min="100"
            max="600"
          />
        </div>

        <button
          onClick={handleEmailGen}
          className="bg-pink-600 hover:bg-pink-700 px-5 py-3 rounded-lg w-full mt-4"
        >
          {loading ? "Generating..." : "Generate Email ✨"}
        </button>

        {email && (
          <div className="mt-6 bg-white/10 border border-white/20 rounded-lg p-4">
            <h2 className="text-lg font-semibold mb-2">Generated Email:</h2>
            <p className="whitespace-pre-wrap">{email}</p>
          </div>
        )}
      </div>
    </main>
  );
}
