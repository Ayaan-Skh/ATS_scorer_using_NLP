from fastapi import FastAPI, UploadFile, File, Form
from .jd_scraper import DescriptionScraper
from .resume_parser import PdfParser
import shutil
import os
from .scorer import Resume_scorer

app = FastAPI()

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
    resume_text = parser.resume_parse(file_path)

    return {"filename": file.filename, "extracted_text": resume_text[:1000]}

# ------------------ JD Scraper Endpoint ------------------
@app.post("/scrape_jd/")
async def scrape_jd(desc_link: str = Form(...)):
    """Scrapes job description from a given URL"""
    jd_text = scraper.jd_scraper(desc_link)
    if jd_text:
        return {"status": "success", "job_description": jd_text[:1500]}
    else:
        return {"status": "error", "message": "Failed to extract job description"}
from pydantic import BaseModel

class ScoreRequest(BaseModel):
    resume_data:str
    jd_data:str
    

@app.post('/score_resume/')
def score_resume(data:ScoreRequest):
    ResumeScoreClass=Resume_scorer()    
    result=ResumeScoreClass.scorer(data.resume_data,data.jd_data)
    
    return {
        "Resume ATS Score": result['ats_score'],
        "Matched Keywords": result['Matched Keywords'],
        "Missing Keywords": result['Missing Keywords']
    }

    
# if __name__ == "__main__":
#     scorer = Resume_scorer()
#     resume = "Developed ML models using Python, TensorFlow, and Scikit-learn for fraud detection."
#     jd = "Looking for a Python developer with experience in Machine Learning, TensorFlow, and fraud detection."
#     print(scorer.scorer(resume, jd))
    
