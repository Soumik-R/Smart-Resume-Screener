import pdfplumber
import spacy
import re
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
nlp = spacy.load("en_core_web_sm")

SYNONYMS = {
    "js": "JavaScript",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
}

def normalize_skill(skill):
    return SYNONYMS.get(skill.lower(), skill)

def extract_resume_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    doc = nlp(text)  # Process with spaCy

    data = {
        "raw_text": text,
        "hard_skills": [],
        "education": [],  # e.g., [{"degree": "B.Tech", "field": "CSE", "institution": "XYZ Univ"}]
        "projects": [],   # e.g., [{"description": "...", "tech": [...], "problem": "...", "impact": "..."}]
        "soft_skills": [],
        "growth_verbs": [],
        "certifications": [],  # New field
        "years_experience": 0,  # New field for experience extraction
    }

    # Extract hard skills: Noun phrases likely to be skills (filter common tech terms)
    tech_patterns = r"(python|java|sql|ml|ai|javascript|react|node|docker|aws|git|agile)"  # Regex for common skills
    for ent in list(doc.ents) + list(doc.noun_chunks):
        skill = ent.text.strip().lower()
        if re.search(tech_patterns, skill):
            normalized = normalize_skill(skill)
            if normalized not in data["hard_skills"]:
                data["hard_skills"].append(normalized.capitalize())

    # Extract education: Look for degrees using patterns and entities
    education_patterns = r"(b\.tech|m\.sc|b\.sc|phd|master|bachelor|degree)[\s\w]*"
    for sent in doc.sents:
        if re.search(education_patterns, sent.text.lower()):
            degree = re.search(r"(b\.tech|m\.sc|b\.sc|phd|master|bachelor|degree)", sent.text.lower()).group(0).capitalize()
            field = re.search(r"(cse|ai|computer science|data science)", sent.text.lower())
            institution = next((ent.text for ent in sent.ents if ent.label_ == "ORG"), "Unknown")
            data["education"].append({
                "degree": degree,
                "field": field.group(0).capitalize() if field else "Unknown",
                "institution": institution
            })

    # Extract certifications - look for certification keywords AND provider/technology keywords
    cert_keywords = ["certified", "certificate", "certification", "cert"]
    provider_keywords = ["aws", "google", "microsoft", "oracle", "coursera", "udemy", "python", 
                         "machine learning", "data science", "azure", "cloud", "analytics"]
    
    for sent in doc.sents:
        sent_lower = sent.text.lower()
        # Check if sentence contains both certification terms and provider/technology terms
        has_cert_keyword = any(keyword in sent_lower for keyword in cert_keywords)
        has_provider_keyword = any(keyword in sent_lower for keyword in provider_keywords)
        
        if has_cert_keyword and has_provider_keyword:
            cert = sent.text.strip()
            if cert not in data["certifications"]:
                data["certifications"].append(cert)

    # Extract and summarize projects with LLM
    current_section = None
    project_desc = ""
    for line in text.split("\n"):
        line = line.strip()
        if re.search(r"\bexperience\b|\bprojects\b|\bwork\b", line.lower()):
            current_section = "projects"
        elif current_section == "projects" and line:
            project_desc += line + " "
        elif re.search(r"\beducation\b|\bskills\b", line.lower()):
            current_section = None

    if project_desc:
        try:
            prompt = f"""
            Summarize the following project descriptions into structured summaries.
            For each project, provide:
            - Technologies used (list)
            - Problem solved (short sentence)
            - Impact (short sentence)
            Input: {project_desc}
            Output format: List of dicts, each with 'technologies', 'problem', 'impact'
            """
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            data["projects"] = eval(response.choices[0].message.content)  # Convert LLM string to list of dicts
        except Exception as e:
            # Silently fallback to basic parsing when LLM is unavailable
            project_doc = nlp(project_desc)
            for sent in project_doc.sents:
                if len(sent.text.strip()) > 10:  # Only consider meaningful sentences
                    tech = [normalize_skill(token.text) for token in sent if token.lower_ in SYNONYMS or re.search(tech_patterns, token.lower_)]
                    data["projects"].append({
                        "description": sent.text.strip(),
                        "technologies": tech,
                        "problem": "Extracted from resume",
                        "impact": "Unknown"
                    })

    # Extract soft skills: Predefined list + NLP
    soft_skills_list = ["teamwork", "leadership", "communication", "creativity", "problem-solving", "initiative"]
    for token in doc:
        if token.lower_ in soft_skills_list and token.lower_ not in data["soft_skills"]:
            data["soft_skills"].append(token.text.capitalize())

    # Extract growth verbs: Verbs like learned, adapted
    growth_verbs_list = ["learned", "adapted", "built", "self-taught", "mastered", "improved"]
    for token in doc:
        if token.pos_ == "VERB" and token.lower_ in growth_verbs_list and token.lower_ not in data["growth_verbs"]:
            data["growth_verbs"].append(token.text)

    # Extract years of experience
    data["years_experience"] = extract_experience_from_resume(text)

    return data

def extract_experience_from_resume(text):
    """Extract years of experience from resume text"""
    if not text:
        return 0
    
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*[:]\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*year\s*(?:of\s*)?experience',
        r'(\d+)\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
        r'over\s*(\d+)\s*years?',
        r'more\s*than\s*(\d+)\s*years?'
    ]
    
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            try:
                years = int(match)
                max_years = max(max_years, years)
            except ValueError:
                continue
    
    return max_years