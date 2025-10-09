import spacy
import re

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

def extract_jd_data(job_description):
    """Extract structured data from job description"""
    
    data = {
        "required_skills": [],
        "required_education": [],
        "tasks": [],
        "values": []
    }
    
    if nlp is None:
        return data
    
    doc = nlp(job_description)

    # Extract required skills: Similar to resume
    tech_patterns = r"(python|java|sql|ml|ai|javascript|react|node|docker|aws|git|agile)"
    entities_and_chunks = list(doc.ents) + [chunk for chunk in doc.noun_chunks]
    for ent in entities_and_chunks:
        skill = ent.text.strip().lower()
        if re.search(tech_patterns, skill):
            if skill not in data["required_skills"]:
                data["required_skills"].append(skill.capitalize())

    # Extract education: Patterns like "Bachelor's in CS"
    education_patterns = r"(b\.tech|m\.sc|b\.sc|phd|master|bachelor|degree)[\s\w]*"
    for sent in doc.sents:
        if re.search(education_patterns, sent.text.lower()):
            degree = re.search(r"(b\.tech|m\.sc|b\.sc|phd|master|bachelor|degree)", sent.text.lower()).group(0).capitalize()
            field = re.search(r"(cse|ai|computer science|data science)", sent.text.lower())
            data["required_education"].append({
                "degree": degree,
                "field": field.group(0).capitalize() if field else "Unknown"
            })

    # Extract tasks: Sentences with verbs like "develop", "manage"
    task_verbs = ["develop", "manage", "build", "analyze", "lead"]
    for sent in doc.sents:
        if any(verb in sent.text.lower() for verb in task_verbs):
            data["tasks"].append(sent.text.strip())

    # Extract values: Soft terms like "teamwork", "innovative"
    value_terms = ["collaboration", "ownership", "innovation", "teamwork", "leadership"]
    for token in doc:
        if token.lower_ in value_terms and token.lower_ not in data["values"]:
            data["values"].append(token.text.capitalize())

    return data