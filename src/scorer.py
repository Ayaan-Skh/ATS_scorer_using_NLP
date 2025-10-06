import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('stopwords')
nltk.download('wordnet')

class Resume_scorer():
    def __init__(self):
        self.stop_words=set(stopwords.words('english'))
        self.lemmatizer=WordNetLemmatizer()
        
    def clean_text(self,text:str)->str:
        """Clean text remove punctuation, stopwords, lowercase it and lemmatize"""
        
        text=text.lower()
        text = re.sub(r'<[^>]+>', ' ', text)  # remove HTML
        text=text.translate(str.maketrans('','',string.punctuation)) ##Remove punctuations
        words=text.split() ## Split the sentence into list of words
        words=[self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words and word.isalpha()] ## Lemmatize each word
        return " ".join(words)
    
    def scorer(self,resume_text:str, jd_text:str):
        
        resume_clean=self.clean_text(resume_text) #Clean the resume text
        jd_clean=self.clean_text(jd_text) #Clean the description text
        
        vectorizer=TfidfVectorizer()
        vectors=vectorizer.fit_transform([resume_clean,jd_clean])
        
        score=cosine_similarity(vectors[0:1],vectors[1:2])[0][0] #Calculate cosine similarity
        ats_score=round(score*100,2) #Convert cosine similarity to percentage
        
        resume_words = set(resume_clean.split())
        jd_words = set(jd_clean.split())
        
        matched_keywords = sorted(list(resume_words & jd_words))
        missing_keywords = sorted(list(jd_words - resume_words))
        
        return{
            "ats_score":ats_score,
            "Matched Keywords":matched_keywords,
            "Missing Keywords":missing_keywords
        }