import requests
import re
from typing import Dict, Literal

class EmailGenerator:
    def __init__(self, model_name="llama3.2", ollama_url="http://localhost:11434"):
        self.model = model_name
        self.ollama_url = ollama_url
        
        # Define tone characteristics
        self.tone_modifiers = {
            "formal": {
                "style": "professional and respectful",
                "avoid": "slang, emojis, casual phrases",
                "example_phrases": ["I am writing to express", "I would appreciate the opportunity", "Thank you for your consideration"]
            },
            "friendly": {
                "style": "warm and approachable while maintaining professionalism",
                "avoid": "overly stiff language",
                "example_phrases": ["I'd love to", "Really excited about", "Looking forward to connecting"]
            },
            "cold": {
                "style": "direct and concise with clear value proposition",
                "avoid": "unnecessary pleasantries, long introductions",
                "example_phrases": ["I noticed", "I can help with", "Let's discuss"]
            },
            "warm": {
                "style": "personable and enthusiastic",
                "avoid": "being too formal or distant",
                "example_phrases": ["I'm genuinely excited", "I'd really appreciate", "Would love to chat"]
            }
        }
        
        # Message type templates
        self.message_templates = {
            "email": {
                "format": "Cold email for job application",
                "structure": "Brief intro → Key skills match → Call to action",
                "max_paragraphs": 3
            },
            "linkedin": {
                "format": "LinkedIn direct message",
                "structure": "Hook → Relevant credential → Ask to connect",
                "max_paragraphs": 2
            },
            "cover": {
                "format": "Cover letter answer to 'Why this role?'",
                "structure": "Personal motivation → Skills alignment → Company interest",
                "max_paragraphs": 2
            }
        }

    def _extract_key_skills(self, text: str, max_skills: int = 5) -> list:
        """Extract most relevant technical skills from text (case-insensitive, word boundary matching)"""
        # Expanded tech keywords with proper variations
        tech_keywords = [
            'python', 'javascript', 'typescript', 'java', 'c\\+\\+', 'c#', 'ruby', 'go', 'rust',
            'react', 'next\\.?js', 'node\\.?js', 'vue', 'angular', 'svelte',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'machine learning', 'deep learning', 'ml', 'ai', 'nlp', 'computer vision',
            'data science', 'data analysis', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'flask', 'django', 'fastapi', 'express', 'spring boot',
            'rest api', 'graphql', 'microservices', 'serverless',
            'ci/cd', 'jenkins', 'github actions', 'gitlab',
            'git', 'agile', 'scrum', 'devops'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in tech_keywords:
            # Use word boundary regex to avoid partial matches
            pattern = r'\b' + skill + r'\b'
            if re.search(pattern, text_lower):
                # Store the original casing if possible
                found_skills.append(skill.replace('\\', ''))
        
        return found_skills[:max_skills]

    def _extract_relevant_context(self, resume_text: str, jd_text: str) -> Dict[str, str]:
        """Extract most relevant info from resume matching JD requirements"""
        resume_skills = self._extract_key_skills(resume_text, max_skills=8)
        jd_skills = self._extract_key_skills(jd_text, max_skills=8)
        
        # Find matching skills
        matching_skills = [skill for skill in jd_skills if skill in resume_skills]
        
        # Extract company name from JD if possible
        company_match = re.search(r'(?:at|for|join)\s+([A-Z][a-zA-Z\s&]+?)(?:\s+is|\.|\,)', jd_text[:500])
        company = company_match.group(1).strip() if company_match else "your company"
        
        # Extract role title
        role_match = re.search(r'(?:hiring|seeking|looking for)\s+(?:a|an)?\s*([A-Z][a-zA-Z\s]+?)(?:\s+to|\s+who|\.)', jd_text[:300])
        role = role_match.group(1).strip() if role_match else "this position"
        
        return {
            "resume_snippet": resume_text[:800],
            "jd_snippet": jd_text[:800],
            "matching_skills": matching_skills[:4],  # Top 4 matches
            "company": company,
            "role": role
        }

    def _build_prompt(
        self, 
        context: Dict[str, str], 
        tone: str, 
        message_type: str, 
        max_chars: int
    ) -> str:
        """Build optimized prompt based on constraints"""
        
        tone_info = self.tone_modifiers.get(tone, self.tone_modifiers["formal"])
        template_info = self.message_templates.get(message_type, self.message_templates["email"])
        
        # Build skill mention string
        skills_str = ", ".join(context["matching_skills"]) if context["matching_skills"] else "relevant technical skills"
        
        # Custom instructions per message type
        if message_type == "linkedin":
            specific_instructions = f"""
Write a LinkedIn DM to a recruiter/hiring manager about the {context['role']} position at {context['company']}.

CRITICAL RULES:
- Maximum {max_chars} characters (HARD LIMIT - count every character including spaces)
- No subject line, no signature, no "Dear X"
- Start directly with a hook
- ONLY mention skills from this verified list: {skills_str}
- DO NOT make up or hallucinate any skills
- End with a simple connection request
- Tone: {tone_info['style']}
- Avoid: {tone_info['avoid']}

Candidate's actual verified skills: {skills_str}

Example opening: "Hi! Saw your {context['role']} post — I've worked with [ONLY USE: {skills_str.split(',')[0] if context['matching_skills'] else 'relevant tools'}] and would love to connect."

Job context:
{context['jd_snippet'][:400]}

Candidate background (use ONLY what's mentioned here):
{context['resume_snippet'][:400]}

Write ONLY the message using real skills. Count characters carefully."""

        elif message_type == "cover":
            specific_instructions = f"""
Answer the interview question: "Why are you interested in this role at {context['company']}?"

CRITICAL RULES:
- Maximum {max_chars} characters (HARD LIMIT - count every character)
- {template_info['max_paragraphs']} paragraphs maximum
- Be authentic and specific
- ONLY reference skills the candidate actually has: {skills_str}
- DO NOT fabricate or hallucinate skills
- Show genuine interest in {context['company']}
- Tone: {tone_info['style']}
- Avoid: {tone_info['avoid']}, generic statements, making up experience

Candidate's verified skills: {skills_str}

Example: "I'm drawn to this {context['role']} position because it aligns with my experience in [USE ONLY: {skills_str.split(',')[0] if context['matching_skills'] else 'relevant areas'}]. Having worked on [mention actual project from resume], I'm excited to contribute to your team's goals."

Role requirements:
{context['jd_snippet'][:500]}

Candidate's actual experience (stick to what's written here):
{context['resume_snippet'][:500]}

Write ONLY the answer using verified skills. Stay under {max_chars} characters."""

        else:  # email
            specific_instructions = f"""
Write a cold email applying for {context['role']} at {context['company']}.

CRITICAL RULES:
- Maximum {max_chars} characters total (HARD LIMIT - every character counts)
- No "Dear Hiring Manager", no formal headers, no greetings
- Structure: {template_info['structure']}
- You MUST ONLY mention skills that appear in BOTH the resume AND job description
- Matching skills available: {skills_str}
- DO NOT invent or hallucinate skills not in the resume
- End with clear CTA (e.g., "Would love to discuss further")
- Tone: {tone_info['style']}
- Avoid: {tone_info['avoid']}, buzzwords like "passionate", "leverage", making up experience

IMPORTANT: Only reference actual experience from the candidate's background below. Do not fabricate skills.

What they need:
{context['jd_snippet'][:450]}

What the candidate actually has:
{context['resume_snippet'][:450]}

Candidate's proven skills: {skills_str}

Example format: "Hi, I noticed your {context['role']} opening. I've worked extensively with [ONLY USE SKILLS FROM: {skills_str}] which directly addresses your requirements. [One specific accomplishment]. Happy to discuss my experience further."

Write ONLY the email body using REAL skills from the resume. Stay strictly under {max_chars} characters."""

        return specific_instructions

    def generate_email(
        self, 
        resume_text: str, 
        jd_text: str, 
        tone: Literal["formal", "friendly", "cold", "warm"] = "formal",
        max_chars: int = 500,
        message_type: Literal["email", "linkedin", "cover"] = "email"
    ) -> Dict[str, str]:
        """
        Generate professional messages with strict constraint enforcement.
        
        Args:
            resume_text: Candidate's resume content
            jd_text: Job description text
            tone: Writing style (formal/friendly/cold/warm)
            max_chars: Maximum character count (strictly enforced)
            message_type: Type of message (email/linkedin/cover)
            
        Returns:
            Dict with 'content', 'type', 'actual_length', or 'error'
        """
        
        # Validate inputs
        if not resume_text or not jd_text:
            return {"error": "Resume and job description are required"}
        
        if max_chars < 100 or max_chars > 1000:
            return {"error": "max_chars must be between 100 and 1000"}
        
        try:
            # Extract relevant context
            context = self._extract_relevant_context(resume_text, jd_text)
            
            # Build optimized prompt
            prompt = self._build_prompt(context, tone, message_type, max_chars)
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.6 if tone in ["formal", "cold"] else 0.75,
                        "top_p": 0.9,
                        "num_predict": max_chars + 50,  # Small buffer
                        "stop": ["---", "Note:", "Example:", "\n\n\n"]  # Stop tokens
                    }
                },
                timeout=90
            )
            
            if response.status_code != 200:
                return {"error": f"Ollama API error: {response.status_code}"}
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            if not generated_text:
                return {"error": "Model returned empty response"}
            
            # Clean up common LLM artifacts
            generated_text = self._clean_output(generated_text, message_type)
            
            # Enforce strict character limit with smart truncation
            if len(generated_text) > max_chars:
                generated_text = self._smart_truncate(generated_text, max_chars, message_type)
            
            actual_length = len(generated_text)
            
            # Validate output meets minimum quality
            if actual_length < 50:
                return {"error": "Generated text too short - try increasing max_chars"}
            
            print(f"✅ Generated {message_type} | Tone: {tone} | Length: {actual_length}/{max_chars} chars")
            
            return {
                "type": message_type,
                "content": generated_text,
                "actual_length": actual_length,
                "max_allowed": max_chars,
                "tone": tone
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "error": "Cannot connect to Ollama. Please run 'ollama serve' in terminal first."
            }
        except requests.exceptions.Timeout:
            return {
                "error": "Request timeout. Try: 1) Reducing max_chars, 2) Restarting Ollama, 3) Using a smaller model"
            }
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return {"error": f"Generation failed: {str(e)}"}

    def _clean_output(self, text: str, message_type: str) -> str:
        """Remove common LLM artifacts and formatting issues"""
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
        
        # Remove email artifacts for non-email types
        if message_type == "linkedin":
            text = re.sub(r'^(Subject:|To:|From:).*?\n', '', text, flags=re.MULTILINE)
            text = re.sub(r'^(Dear|Hi there|Hello),?\s*', '', text)
        
        # Remove meta-commentary
        meta_phrases = [
            r'Here is the.*?:',
            r'Here\'s a.*?:',
            r'Below is.*?:',
            r'\[Note:.*?\]',
            r'\(Note:.*?\)',
            r'I hope this.*?helpful'
        ]
        for pattern in meta_phrases:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 newlines
        text = re.sub(r'[ \t]+', ' ', text)            # Single spaces
        text = text.strip()
        
        return text

    def _smart_truncate(self, text: str, max_chars: int, message_type: str) -> str:
        """Truncate text intelligently at sentence/phrase boundaries"""
        
        if len(text) <= max_chars:
            return text
        
        # Try to cut at sentence boundary
        truncated = text[:max_chars]
        
        # Find last complete sentence
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        sentence_end = max(last_period, last_exclamation, last_question)
        
        if sentence_end > max_chars * 0.7:  # If we can keep 70%+ of content
            return text[:sentence_end + 1].strip()
        
        # Otherwise, cut at last space and add ellipsis
        last_space = truncated.rfind(' ')
        if last_space > max_chars * 0.8:
            return text[:last_space].strip() + "..."
        
        # Last resort: hard cut with ellipsis
        return text[:max_chars - 3].strip() + "..."