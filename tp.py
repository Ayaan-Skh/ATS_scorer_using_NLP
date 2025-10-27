import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor

# 1. Load the spaCy model
nlp = spacy.load("en_core_web_lg")

# 2. Initialize the SkillExtractor, which uses PhraseMatcher
skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

# 3. Sample job description
job_description = """You are a Python developer with a solid experience in web development 
and can manage projects. You have solid experience in data analysis and visualization."""

# 4. Extract skills from the job description
annotations = skill_extractor.annotate(job_description)

# 5. The output contains the extracted skills
# For instance, the result would identify 'Python', 'web development', 
# 'data analysis', and 'visualization' as skills.
print(annotations)
