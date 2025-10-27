"use client";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import axios from "axios";
import { Copy } from "lucide-react";

export default function GenerateEmail() {
  const params = useSearchParams();
  const resumeText = params.get("resumeText");
  const jdText = params.get("jdText");
  const [generatedEmail, setGeneratedEmail] = useState("");
  const [tone, setTone] = useState("formal");
  const [maxChars, setMaxChars] = useState(300);
  const [loading, setLoading] = useState(false);
  const [messageType, setMessageType] = useState<"email" | "linkedin" | "cover">("email");

  function copyContent() {
    const textElement = document.getElementById('textToCopy');
    // @ts-ignore
    const text = textElement.innerText;

    navigator.clipboard.writeText(text)
      .then(() => {
        alert('Text copied to clipboard!');
      })
      .catch(err => {
        console.error('Failed to copy text: ', err);
      });
  }
  const handleEmailGen = async () => {
    setLoading(true); // ✅ Set loading state
    try {
      const formData = new FormData();
      console.log("Generating email");
      formData.append("resume_data", localStorage.getItem("resume_data") || "");
      formData.append("jd_data", localStorage.getItem("jd_data") || "");
      formData.append("tone", tone);
      formData.append("max_chars", maxChars.toString());
      formData.append("message_type", messageType);

      const res = await axios.post("http://127.0.0.1:8000/generate_email/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      console.log(res.data);
      setGeneratedEmail(res.data.content || res.data.error || "Failed to generate email");
    } catch (error) {
      console.error("Error generating email:", error);
      setGeneratedEmail("Error: Could not generate email. Check console.");
    } finally {
      setLoading(false); // ✅ Always reset loading
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white flex flex-col items-center py-12">
      <h1 className="text-3xl font-bold mb-6">AI Cover Letter / Cold Email Generator</h1>

      <div className="w-full max-w-2xl space-y-4">
        <div>
          <label className="block mb-2 text-sm">Tone</label>
          <select
            className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white"
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
            className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white"
            value={maxChars}
            onChange={(e) => setMaxChars(Number(e.target.value))}
            min="100"
            max="600"
          />
        </div>
        <div>
          <label className="block mb-2 text-sm">Message Type</label>
          <select
            className="w-full p-2 bg-white/10 border border-white/20 rounded-lg text-white"
            value={messageType}
            onChange={(e) => setMessageType(e.target.value as any)}
          >
            <option value="email">Cold Email</option>
            <option value="linkedin">LinkedIn DM</option>
            <option value="cover">Cover Answer</option>
          </select>
        </div>
        <button
          onClick={handleEmailGen}
          disabled={loading}
          className="bg-pink-600 hover:bg-pink-700 px-5 py-3 rounded-lg w-full mt-4 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Email ✨"}
        </button>

        {/* ✅ Fixed: Use generatedEmail instead of email */}
        {generatedEmail && (
          <div className="mt-6 bg-white/10 border border-white/20 rounded-lg p-4">
            <div className="flex justify-between">

              <h2 className="text-lg font-semibold mb-2">Generated Message:</h2>
              <button className="relative" onClick={copyContent}>
                <Copy size={18} /></button>
            </div>
            <p id='textToCopy' className="whitespace-pre-wrap">{generatedEmail}</p>
          </div>
        )}
      </div>
    </main>
  );
}