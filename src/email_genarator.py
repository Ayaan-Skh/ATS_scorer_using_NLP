import subprocess
import json

class EmailGenerator:
    def __init__(self, model_name="llama3.2"):
        self.model = model_name

    def generate_email(self, resume_text, jd_text, tone="formal", max_chars=500):
        prompt = f"""
        You are an AI email writer. Generate a professional {tone} cold email or cover letter
        for a job based on the following details:
        
        Job Description:
        {jd_text}

        Candidate Resume Info:
        {resume_text}

        Keep it concise, within {max_chars} characters, and structured like a real email.
        """

        try:
            # Run Ollama as a subprocess (locally)
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
            )

            output = result.stdout.decode("utf-8")
            print("Ollama Output:", output.strip())
            return {"email": output.strip()}

        except subprocess.TimeoutExpired:
            return {"error": "Model took too long to respond"}
        except Exception as e:
            return {"error": str(e)}
