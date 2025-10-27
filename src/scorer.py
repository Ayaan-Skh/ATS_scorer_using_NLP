import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

from src.skill_extractor import KeyBertSkillExtractor

nltk.download('stopwords')
nltk.download('wordnet')

class Resume_scorer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
    def clean_text(self, text: str) -> str:
        """Clean text: remove punctuation, stopwords, lowercase it, and lemmatize"""
        text = text.lower()
        text = re.sub(r'<[^>]+>', ' ', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = text.split()
        words = [
            self.lemmatizer.lemmatize(word)
            for word in words if word not in self.stop_words and word.isalpha()
        ]
        return " ".join(words)
    
    def clean_resume_text(text):
        text = re.sub(r'[^A-Za-z0-9\s\+\#]', ' ', text)  # remove weird chars
        text = re.sub(r'\s+', ' ', text)
        return text.lower()
    
    
    def compute_score(self, resume_text: str, jd_text: str):
        resume_clean = self.clean_resume_text(resume_text)
        jd_clean = self.clean_resume_text(jd_text)
        
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_clean, jd_clean])
        
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        ats_score = round(score * 100, 2)
        
        resume_words = set(resume_clean.split())
        jd_words = set(jd_clean.split())
        
        matched_keywords = sorted(list(resume_words & jd_words))
        missing_keywords = sorted(list(jd_words - resume_words))
        
        return {
            "ATS Score": ats_score,
            "Matched Keywords": matched_keywords,
            "Missing Keywords": missing_keywords
        }


class ResumeScorerPro:
    def __init__(self):
        self.extractor = KeyBertSkillExtractor()
    
    def resume_skill_score(self, resume_text: str, jd_text: str):
        resume_skills = self.extractor.extract_skills(resume_text)
        jd_skills = self.extractor.extract_skills(jd_text)
        
        matched_skills = [s for s in jd_skills if s in resume_skills]
        missing_skills = [s for s in jd_skills if s not in resume_skills]
        
        score = round((len(matched_skills) / len(jd_skills)) * 100, 2) if jd_skills else 0.0
        
        return {
            "ATS Skill Score": score,
            "Matched Skills": matched_skills,
            "Missing Skills": missing_skills,
            "Resume Skills": resume_skills,
            "Job Description Skills": jd_skills
        }
