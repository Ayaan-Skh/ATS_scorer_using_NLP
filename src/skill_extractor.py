from keybert import KeyBERT

SKILL_LIST = [
    # Programming languages
    "python", "java", "c++", "javascript", "typescript", "go", "ruby", "rust",
    # ML/AI
    "machine learning", "deep learning", "tensorflow", "keras", "pytorch",
    "scikit-learn", "numpy", "pandas", "matplotlib", "seaborn", "opencv",
    "xgboost", "lightgbm", "nlp", "transformers", "hugging face",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite",
    # Tools/Frameworks
    "flask", "django", "fastapi", "react", "next.js", "node.js", "express.js",
    "docker", "kubernetes", "git", "github", "linux",
    # Cloud
    "aws", "azure", "gcp", "cloud computing", "api", "rest", "graphql",
    # Misc
    "data visualization", "data preprocessing", "feature engineering",
    "deployment", "model evaluation", "version control", "ci/cd"
]


from keybert import KeyBERT
from rapidfuzz import fuzz


class KeyBertSkillExtractor:
    def __init__(self):
        self.model = KeyBERT(model='all-MiniLM-L6-v2')
        self.skill_list = [s.lower() for s in SKILL_LIST]


    def extract_skills(self, text: str):
        if not text.strip():
            return []

        keywords = self.model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words='english',
            top_n=50
        )
        extracted = [kw[0].lower() for kw in keywords]

        # fuzzy match to known skills (handles small typos / word gaps)
        matched = []
        for kw in extracted:
            for skill in self.skill_list:
                if fuzz.partial_ratio(kw, skill) > 85:
                    matched.append(skill)
                    break

        return list(set(matched))
