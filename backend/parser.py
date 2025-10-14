"""
Resume and Job Description parsing module
Extracts structured information from PDF documents using pdfplumber and spaCy
"""
import pdfplumber
import spacy
from typing import Dict, List, Any
import re

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract raw text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")
    
    return text.strip()


def extract_email(text: str) -> str:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else ""


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from text using NLP and keyword matching
    
    Args:
        text: Input text
        
    Returns:
        List of identified skills
    """
    # Common technical skills to look for
    skill_keywords = [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
        "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
        "machine learning", "deep learning", "nlp", "computer vision",
        "git", "agile", "scrum", "jira"
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates


def parse_resume(pdf_path: str) -> Dict[str, Any]:
    """
    Parse a resume PDF and extract structured information
    
    Args:
        pdf_path: Path to the resume PDF
        
    Returns:
        Dictionary containing parsed resume data
    """
    text = extract_text_from_pdf(pdf_path)
    doc = nlp(text)
    
    # Extract entities
    name = ""
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not name:
            name = ent.text
            break
    
    resume_data = {
        "name": name,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "raw_text": text
    }
    
    return resume_data


def parse_job_description(pdf_path: str) -> Dict[str, Any]:
    """
    Parse a job description PDF and extract key requirements
    
    Args:
        pdf_path: Path to the job description PDF
        
    Returns:
        Dictionary containing parsed job description data
    """
    text = extract_text_from_pdf(pdf_path)
    
    jd_data = {
        "required_skills": extract_skills(text),
        "raw_text": text
    }
    
    return jd_data
