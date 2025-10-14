"""
Resume and Job Description parsing module
Extracts structured information from PDF documents using pdfplumber and spaCy
"""
import pdfplumber
import spacy
from typing import Dict, List, Any, Union
from pathlib import Path
import re

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")


# ============================================================================
# Text Reading and Cleaning Functions
# ============================================================================

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing noise and normalizing formatting
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove page numbers (e.g., "Page 1", "Page 2 of 5", "1/5", etc.)
    text = re.sub(r'Page\s+\d+(\s+of\s+\d+)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\s*/\s*\d+', '', text)  # Remove "1/5" style page numbers
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)  # Remove standalone page numbers
    
    # Remove common header/footer patterns
    text = re.sub(r'Confidential|Resume|CV|Curriculum Vitae', '', text, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Replace 3+ newlines with 2
    text = re.sub(r' +', ' ', text)  # Replace multiple spaces with single space
    text = re.sub(r'\t+', ' ', text)  # Replace tabs with spaces
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove empty lines at start and end
    text = text.strip()
    
    return text


def read_pdf(file_path: str) -> str:
    """
    Read and extract text from a PDF file
    Handles multi-page PDFs by concatenating all pages
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted and cleaned text
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file cannot be read or is corrupted
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    if path.suffix.lower() != '.pdf':
        raise ValueError(f"File is not a PDF: {file_path}")
    
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            # Check if PDF has pages
            if len(pdf.pages) == 0:
                raise ValueError("PDF file is empty (no pages)")
            
            # Extract text from all pages
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    # Warn about empty pages but continue
                    print(f"Warning: Page {page_num} is empty or couldn't be extracted")
        
        if not text.strip():
            raise ValueError("No text could be extracted from PDF")
        
        # Clean the extracted text
        cleaned_text = clean_text(text)
        
        return cleaned_text
        
    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError:
        raise ValueError(f"PDF file is corrupted or malformed: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")


def read_text_file(file_path: str) -> str:
    """
    Read text from a plain text file
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Cleaned text content
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file cannot be read
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    try:
        # Try reading with UTF-8 first, fallback to other encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                
                if text.strip():
                    # Clean the text
                    cleaned_text = clean_text(text)
                    return cleaned_text
                    
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not decode text file with any supported encoding")
        
    except Exception as e:
        raise ValueError(f"Error reading text file: {str(e)}")


def read_document(file_path: str) -> str:
    """
    Universal document reader - automatically detects and reads PDF or text files
    
    Args:
        file_path: Path to the document (PDF or text)
        
    Returns:
        Extracted and cleaned text
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file type is unsupported or cannot be read
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine file type and read accordingly
    suffix = path.suffix.lower()
    
    if suffix == '.pdf':
        return read_pdf(file_path)
    elif suffix in ['.txt', '.text']:
        return read_text_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported types: .pdf, .txt")


# ============================================================================
# Legacy function - kept for backward compatibility
# ============================================================================

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract raw text from a PDF file (legacy function)
    Use read_pdf() for better error handling and cleaning
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    return read_pdf(pdf_path)


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
