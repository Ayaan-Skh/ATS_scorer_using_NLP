from fastapi import FastAPI, UploadFile, File, Form
from src.jd_scraper import DescriptionScraper
from src.resume_parser import PdfParser
import shutil
import os
from src.scorer import Resume_scorer, ResumeScorerPro
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = PdfParser()
scraper = DescriptionScraper()

# Directory to store uploaded resumes
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------ Resume Upload Endpoint ------------------
@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Uploads a PDF resume and extracts text"""
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save temporarily
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse text
    resume_text = parser.Resume_parse(file_path)

    return {"filename": file.filename, "extracted_text": resume_text}

# ------------------ JD Scraper Endpoint ------------------
@app.post("/scrape_jd/")
async def scrape_jd(desc_link: str = Form(...)):
    """Scrapes job description from a given URL"""
    jd_text = scraper.jd_scraper(desc_link)
    if jd_text:
        return {"status": "success", "job_description": jd_text}
    else:
        return {"status": "error", "message": "Failed to extract job description"}
from pydantic import BaseModel

scorer = ResumeScorerPro()

class ScoreRequest(BaseModel):
    resume_data: str
    jd_data: str

@app.post("/score_resume/")
def score_resume(data: ScoreRequest):
    result = scorer.resume_skill_score(data.resume_data, data.jd_data)
    return result

# ------------------ Email generator Endpoint ------------------
class EmailRequest(BaseModel):
    resume_text:str
    jd_text:str
    tone:str
    max_char:int
    
    
from src.email_genarator import EmailGenerator

generator = EmailGenerator()

@app.post("/generate_email/")
def generate_email(resume_data: str = Form(...), jd_data: str = Form(...), tone: str = Form("formal"), max_chars: int = Form(500)):
    result = generator.generate_email(resume_data, jd_data, tone, max_chars)
    return result

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
