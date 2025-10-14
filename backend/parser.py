"""
Resume and Job Description parsing module
Extracts structured information from PDF documents using pdfplumber and spaCy
Enhanced with NLP for smarter entity extraction and semantic matching
Includes comprehensive error handling, validation, and debugging features
"""
import pdfplumber
import spacy
from typing import Dict, List, Any, Union, Tuple, Set, Optional
from pathlib import Path
import re
from difflib import SequenceMatcher
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model 'en_core_web_sm' loaded successfully")
except OSError:
    logger.error("spaCy model 'en_core_web_sm' not found")
    raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")


# ============================================================================
# Error Handling and Validation
# ============================================================================

class ParserError(Exception):
    """Base exception for parser errors"""
    pass


class FileReadError(ParserError):
    """Raised when file cannot be read"""
    pass


class ValidationError(ParserError):
    """Raised when parsed data fails validation"""
    pass


def save_debug_output(data: Dict[str, Any], file_path: str, suffix: str = "debug") -> str:
    """
    Save extracted data to JSON file for debugging
    
    Args:
        data: Dictionary to save
        file_path: Original file path (used to generate debug filename)
        suffix: Suffix for debug file (default: "debug")
        
    Returns:
        Path to saved debug file
    """
    try:
        # Create debug directory if it doesn't exist
        debug_dir = Path("debug_output")
        debug_dir.mkdir(exist_ok=True)
        
        # Generate debug filename
        original_name = Path(file_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = debug_dir / f"{original_name}_{suffix}_{timestamp}.json"
        
        # Save to JSON
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Debug output saved to: {debug_file}")
        return str(debug_file)
        
    except Exception as e:
        logger.error(f"Failed to save debug output: {e}")
        return ""


def validate_resume(resume: 'Resume') -> List[str]:
    """
    Validate parsed resume data and return list of warnings
    
    Args:
        resume: Resume object to validate
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    # Check required fields
    if not resume.name or resume.name == "Unknown":
        warnings.append("⚠️  Name not detected - consider checking first line of resume")
    
    if not resume.email:
        warnings.append("⚠️  Email not found - ensure contact info is clearly visible")
    
    if not resume.phone:
        warnings.append("⚠️  Phone number not found")
    
    # Check skills
    if not resume.skills or len(resume.skills) == 0:
        warnings.append("⚠️  No skills detected - check if resume has a Skills section")
    elif len(resume.skills) < 3:
        warnings.append(f"⚠️  Only {len(resume.skills)} skill(s) found - may need more comprehensive skills list")
    
    # Check experience
    if resume.experience.years == 0.0 and not resume.experience.roles:
        warnings.append("ℹ️  No experience detected - candidate appears to be a fresher")
    elif resume.experience.years == 0.0 and resume.experience.roles:
        warnings.append("ℹ️  Experience detected but years = 0 - check date parsing")
    
    # Check if only internships
    if resume.experience.roles:
        if all(role.is_internship for role in resume.experience.roles):
            warnings.append("ℹ️  All roles are internships - candidate is likely a fresher")
    
    # Check education
    if not resume.education or len(resume.education) == 0:
        warnings.append("⚠️  No education information found")
    
    # Check if all fields are empty (likely parsing failure)
    if (not resume.skills and not resume.experience.roles and 
        not resume.education and not resume.projects):
        warnings.append("❌ CRITICAL: No data extracted - file may be corrupted or format unsupported")
    
    return warnings


# ============================================================================
# NLP Enhancement - Semantic Skill Mapping and Fuzzy Matching
# ============================================================================

# Comprehensive skill taxonomy with synonyms and related terms
SKILL_TAXONOMY = {
    # Programming Languages
    "python": ["python", "py", "python3", "scripting", "python scripting"],
    "java": ["java", "j2ee", "java ee", "jdk", "jvm"],
    "javascript": ["javascript", "js", "es6", "ecmascript", "node"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c#": ["c#", "csharp", "c sharp", ".net"],
    "ruby": ["ruby", "rb", "ruby on rails", "rails"],
    "go": ["go", "golang"],
    "rust": ["rust"],
    "php": ["php", "php7", "php8"],
    "swift": ["swift", "ios development"],
    "kotlin": ["kotlin", "android development"],
    "scala": ["scala"],
    "r": ["r programming", "r language"],
    
    # Web Technologies
    "html": ["html", "html5", "markup"],
    "css": ["css", "css3", "styling", "sass", "less"],
    "react": ["react", "reactjs", "react.js"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs", "vue.js"],
    "node.js": ["node", "nodejs", "node.js"],
    "express": ["express", "expressjs", "express.js"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring boot": ["spring", "spring boot", "spring framework"],
    
    # Databases
    "sql": ["sql", "structured query language", "database queries"],
    "mongodb": ["mongodb", "mongo", "nosql"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "redis": ["redis", "caching"],
    "elasticsearch": ["elasticsearch", "elastic search", "elk"],
    "dynamodb": ["dynamodb", "dynamo"],
    "oracle": ["oracle", "oracle db"],
    
    # Cloud Platforms
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    
    # DevOps & Tools
    "docker": ["docker", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s", "container orchestration"],
    "jenkins": ["jenkins", "ci/cd", "continuous integration"],
    "git": ["git", "version control", "github", "gitlab"],
    "terraform": ["terraform", "infrastructure as code", "iac"],
    "ansible": ["ansible", "configuration management"],
    
    # AI/ML
    "machine learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
    "deep learning": ["deep learning", "neural networks", "dl"],
    "nlp": ["nlp", "natural language processing", "text processing"],
    "computer vision": ["computer vision", "cv", "image processing"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "scikit-learn": ["sklearn", "scikit-learn", "scikit learn"],
    
    # Methodologies
    "agile": ["agile", "agile methodology", "agile development"],
    "scrum": ["scrum", "scrum master"],
    "devops": ["devops", "dev ops"],
}


def fuzzy_match(text: str, target: str, threshold: float = 0.8) -> bool:
    """
    Fuzzy string matching using SequenceMatcher
    
    Args:
        text: Text to match
        target: Target string
        threshold: Similarity threshold (0-1)
        
    Returns:
        True if similarity >= threshold
    """
    return SequenceMatcher(None, text.lower(), target.lower()).ratio() >= threshold


def semantic_skill_matcher(text: str) -> Set[str]:
    """
    Match skills using semantic understanding and fuzzy matching
    Maps related terms to canonical skill names
    
    Args:
        text: Text containing potential skills
        
    Returns:
        Set of matched canonical skill names
    """
    matched_skills = set()
    text_lower = text.lower()
    
    # Direct matching with taxonomy
    for canonical_skill, variants in SKILL_TAXONOMY.items():
        for variant in variants:
            if variant in text_lower:
                matched_skills.add(canonical_skill.title())
                break
            # Fuzzy matching for close matches
            elif fuzzy_match(variant, text_lower, threshold=0.85):
                matched_skills.add(canonical_skill.title())
                break
    
    return matched_skills


def extract_entities_with_nlp(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities using spaCy NER
    Extracts ORG (organizations/companies), DATE (timelines), GPE (locations)
    
    Args:
        text: Text to process
        
    Returns:
        Dictionary with entity types as keys and lists of entities as values
    """
    doc = nlp(text)
    
    entities = {
        "ORG": [],      # Organizations (companies)
        "DATE": [],     # Dates and timelines
        "GPE": [],      # Locations (cities, countries)
        "PERSON": [],   # Person names
        "MONEY": [],    # Monetary values
        "PERCENT": [],  # Percentages
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    return entities


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
    Read and extract text from a PDF file with comprehensive error handling
    Handles multi-page PDFs by concatenating all pages
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted and cleaned text
        
    Raises:
        FileReadError: If the file cannot be read or processed
    """
    path = Path(file_path)
    
    # Validate file exists
    if not path.exists():
        error_msg = f"PDF file not found: {file_path}"
        logger.error(error_msg)
        raise FileReadError(error_msg)
    
    # Validate file extension
    if path.suffix.lower() != '.pdf':
        error_msg = f"File is not a PDF: {file_path} (extension: {path.suffix})"
        logger.error(error_msg)
        raise FileReadError(error_msg)
    
    # Check file size (warn if > 10MB)
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > 10:
        logger.warning(f"Large PDF file: {file_size_mb:.1f}MB - processing may be slow")
    
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            # Check if PDF has pages
            if len(pdf.pages) == 0:
                error_msg = "PDF file is empty (no pages)"
                logger.error(error_msg)
                raise FileReadError(error_msg)
            
            logger.info(f"Processing PDF with {len(pdf.pages)} page(s)")
            
            # Extract text from all pages
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        logger.warning(f"Page {page_num} is empty or couldn't be extracted")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    continue
        
        # Validate extracted text
        if not text.strip():
            error_msg = "No text could be extracted from PDF - file may be image-based or corrupted"
            logger.error(error_msg)
            raise FileReadError(error_msg)
        
        # Clean the extracted text
        cleaned_text = clean_text(text)
        
        logger.info(f"Successfully extracted {len(cleaned_text)} characters from PDF")
        return cleaned_text
        
    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError as e:
        error_msg = f"PDF file is corrupted or malformed: {file_path}"
        logger.error(f"{error_msg} - {str(e)}")
        raise FileReadError(error_msg)
    except FileReadError:
        raise  # Re-raise our custom errors
    except Exception as e:
        error_msg = f"Unexpected error reading PDF: {str(e)}"
        logger.error(error_msg)
        raise FileReadError(error_msg)


def read_text_file(file_path: str) -> str:
    """
    Read text from a plain text file with error handling
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Cleaned text content
        
    Raises:
        FileReadError: If the file cannot be read
    """
    path = Path(file_path)
    
    # Validate file exists
    if not path.exists():
        error_msg = f"Text file not found: {file_path}"
        logger.error(error_msg)
        raise FileReadError(error_msg)
    
    # Check if file is empty
    if path.stat().st_size == 0:
        error_msg = f"Text file is empty: {file_path}"
        logger.error(error_msg)
        raise FileReadError(error_msg)
    
    try:
        # Try reading with UTF-8 first, fallback to other encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                
                if text:  # File has content (even if just whitespace)
                    # Clean the text
                    cleaned_text = clean_text(text)
                    logger.info(f"Successfully read text file ({len(cleaned_text)} characters) using {encoding} encoding")
                    return cleaned_text
                    
            except UnicodeDecodeError:
                continue
        
        error_msg = f"Could not decode text file with any supported encoding: {file_path}"
        logger.error(error_msg)
        raise FileReadError(error_msg)
        
    except FileReadError:
        raise
    except Exception as e:
        error_msg = f"Error reading text file: {str(e)}"
        logger.error(error_msg)
        raise FileReadError(error_msg)
        raise FileReadError(error_msg)


def read_document(file_path: str) -> str:
    """
    Universal document reader with comprehensive error handling
    Automatically detects and reads PDF or text files
    
    Args:
        file_path: Path to the document (PDF or text)
        
    Returns:
        Extracted and cleaned text
        
    Raises:
        FileReadError: If the file cannot be read or type is unsupported
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise FileReadError(error_msg)
        
        # Determine file type and read accordingly
        suffix = path.suffix.lower()
        
        logger.info(f"Reading document: {file_path} (type: {suffix})")
        
        if suffix == '.pdf':
            return read_pdf(file_path)
        elif suffix in ['.txt', '.text']:
            return read_text_file(file_path)
        else:
            error_msg = f"Unsupported file type: {suffix}. Supported types: .pdf, .txt"
            logger.error(error_msg)
            raise FileReadError(error_msg)
            
    except FileReadError:
        raise
    except Exception as e:
        error_msg = f"Unexpected error reading document: {str(e)}"
        logger.error(error_msg)
        raise FileReadError(error_msg)


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



# ============================================================================
# Section Detection and Extraction Functions
# ============================================================================

def detect_sections(text: str) -> Dict[str, str]:
    """
    Detect and extract different sections from resume text
    Uses regex patterns to identify section headers
    
    Args:
        text: Cleaned resume text
        
    Returns:
        Dictionary with section names as keys and section content as values
    """
    sections = {}
    
    # Define section patterns (case-insensitive)
    section_patterns = {
        'skills': r'(?:^|\n)\s*(?:SKILLS?|TECHNICAL SKILLS?|CORE COMPETENCIES|EXPERTISE)[:\-]?\s*\n',
        'experience': r'(?:^|\n)\s*(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|PROFESSIONAL EXPERIENCE)[:\-]?\s*\n',
        'education': r'(?:^|\n)\s*(?:EDUCATION|ACADEMIC|QUALIFICATION)[:\-]?\s*\n',
        'projects': r'(?:^|\n)\s*(?:PROJECTS?|PERSONAL PROJECTS?|ACADEMIC PROJECTS?)[:\-]?\s*\n',
        'achievements': r'(?:^|\n)\s*(?:ACHIEVEMENTS?|ACCOMPLISHMENTS?|AWARDS?|HONORS?)[:\-]?\s*\n',
        'extracurricular': r'(?:^|\n)\s*(?:EXTRA[- ]?CURRICULAR|ACTIVITIES|LEADERSHIP|VOLUNTEERING?|COMMUNITY)[:\-]?\s*\n'
    }
    
    # Find all section headers and their positions
    section_positions = []
    for section_name, pattern in section_patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            section_positions.append((match.start(), section_name))
    
    # Sort by position
    section_positions.sort()
    
    # Extract content between sections
    for i, (start_pos, section_name) in enumerate(section_positions):
        # Find the end position (start of next section or end of text)
        if i < len(section_positions) - 1:
            end_pos = section_positions[i + 1][0]
        else:
            end_pos = len(text)
        
        # Extract section content
        section_content = text[start_pos:end_pos].strip()
        
        # Remove the header line
        lines = section_content.split('\n')
        if len(lines) > 1:
            section_content = '\n'.join(lines[1:]).strip()
        
        sections[section_name] = section_content
    
    return sections


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None


def extract_name(text: str) -> str:
    """
    Extract candidate name from resume text
    Usually the first line or first PERSON entity
    
    Args:
        text: Resume text
        
    Returns:
        Candidate name or empty string
    """
    # Try first line (often the name)
    lines = text.split('\n')
    first_line = lines[0].strip() if lines else ""
    
    # Check if first line looks like a name (not too long, no special chars)
    if first_line and len(first_line) < 50 and not re.search(r'[@:\d]', first_line):
        # Check if it's not a common header
        if not re.match(r'(?:resume|cv|curriculum)', first_line, re.IGNORECASE):
            return first_line
    
    # Fallback: Use spaCy NER to find PERSON entity
    doc = nlp(text[:500])  # Check first 500 chars
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    
    return ""


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from text using enhanced NLP and semantic matching
    Uses skill taxonomy and fuzzy matching for better accuracy
    
    Args:
        text: Input text (preferably from skills section)
        
    Returns:
        List of identified canonical skills
    """
    # Remove common prefixes
    text = re.sub(r'(?:proficient in|experienced with|familiar with|knowledge of|expertise in)[\s:]+', '', text, flags=re.IGNORECASE)
    
    found_skills = set()
    
    # Method 1: Semantic skill matcher (uses taxonomy and fuzzy matching)
    semantic_skills = semantic_skill_matcher(text)
    found_skills.update(semantic_skills)
    
    # Method 2: Split by delimiters and match individual items
    items = re.split(r'[,•|/\n]+', text)
    
    for item in items:
        item = item.strip()
        if not item or len(item) < 2 or len(item) > 50:
            continue
        
        # Remove leading symbols
        item = re.sub(r'^[-*•\s]+', '', item)
        
        # Check against taxonomy
        item_skills = semantic_skill_matcher(item)
        found_skills.update(item_skills)
        
        # Use NLP for additional extraction
        if len(item) < 30:
            doc = nlp(item)
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
                    # Check if this token matches any skill variant
                    token_skills = semantic_skill_matcher(token.text)
                    if token_skills:
                        found_skills.update(token_skills)
    
    # Method 3: Extract using spaCy entities
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ['PRODUCT', 'ORG']:  # Often tech products/frameworks
            ent_skills = semantic_skill_matcher(ent.text)
            found_skills.update(ent_skills)
    
    # Convert to sorted list
    return sorted(list(found_skills))


from datetime import datetime
from dateutil import parser as date_parser
from models import Resume, Experience, Role, Education, Project


def parse_dates_and_calculate_years(text: str) -> float:
    """
    Parse date ranges and calculate years of experience
    Handles formats like:
    - "Jan 2020 - Present"
    - "2020 - 2023"
    - "June 2021 - December 2022"
    
    Args:
        text: Text containing date ranges
        
    Returns:
        Total years of experience (float)
    """
    # Common date patterns
    date_patterns = [
        r'(\w+\s+\d{4})\s*[-–to]+\s*(\w+\s+\d{4}|present)',
        r'(\d{4})\s*[-–to]+\s*(\d{4}|present)',
        r'(\w+\s+\d{2})\s*[-–to]+\s*(\w+\s+\d{2}|present)',
    ]
    
    total_years = 0.0
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            start_date_str, end_date_str = match
            
            try:
                # Parse start date
                start_date = date_parser.parse(start_date_str, fuzzy=True)
                
                # Parse end date (handle "Present")
                if 'present' in end_date_str.lower():
                    end_date = datetime.now()
                else:
                    end_date = date_parser.parse(end_date_str, fuzzy=True)
                
                # Calculate years
                years = (end_date - start_date).days / 365.25
                total_years += max(0, years)
                
            except:
                continue
    
    return round(total_years, 1)


def extract_experience(text: str) -> Experience:
    """
    Extract work experience from resume section using NLP
    Uses spaCy NER to identify organizations and dates
    
    Args:
        text: Experience section text
        
    Returns:
        Experience object with years and roles
    """
    roles = []
    
    # Extract entities using spaCy
    entities = extract_entities_with_nlp(text)
    organizations = entities.get('ORG', [])
    dates = entities.get('DATE', [])
    
    # Split into individual role blocks (separated by blank lines)
    role_blocks = re.split(r'\n\s*\n', text)
    
    for block in role_blocks:
        if not block.strip():
            continue
        
        lines = block.strip().split('\n')
        
        # Try to extract role title, company, and dates
        role_title = ""
        company = ""
        duration = ""
        description = ""
        is_internship = False
        
        # Check for internship keywords
        if re.search(r'\bintern\b|\binternship\b', block, re.IGNORECASE):
            is_internship = True
        
        # Use NLP to extract organizations from this block
        block_doc = nlp(block)
        block_orgs = [ent.text for ent in block_doc.ents if ent.label_ == 'ORG']
        if block_orgs:
            company = block_orgs[0]  # Take first organization
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for date patterns (usually contains dates)
            if re.search(r'\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|present', line, re.IGNORECASE):
                duration = line
                # Previous lines might be company or title
                if i > 0 and not role_title:
                    role_title = lines[i-1].strip()
                if i > 1 and not company:
                    potential_company = lines[i-2].strip()
                    # Use NLP to verify it's an organization
                    potential_doc = nlp(potential_company)
                    if any(ent.label_ == 'ORG' for ent in potential_doc.ents):
                        company = potential_company
                continue
            
            # Extract company (often has keywords or is an NLP ORG entity)
            if re.search(r'\bat\b|Inc|Corp|Ltd|LLC|Company|Technologies', line, re.IGNORECASE):
                if not company:
                    company = re.sub(r'^at\s+', '', line, flags=re.IGNORECASE).strip()
                continue
            
            # Build description from remaining lines
            if line and not role_title:
                role_title = line
            elif line and line.startswith(('-', '•', '*')):
                description += line + " "
        
        # Clean up extracted data
        role_title = re.sub(r'^[-•*\s]+', '', role_title).strip()
        company = re.sub(r'^[-•*\s]+|^at\s+', '', company, flags=re.IGNORECASE).strip()
        description = description.strip()
        
        if role_title or company:
            roles.append(Role(
                title=role_title or "Position",
                company=company or "Company",
                duration=duration or "Duration not specified",
                description=description or "No description",
                is_internship=is_internship
            ))
    
    # Calculate total years
    total_years = parse_dates_and_calculate_years(text)
    
    # Adjust for internships (count as 0.5x)
    internship_years = sum([parse_dates_and_calculate_years(role.duration) * 0.5 
                           for role in roles if role.is_internship])
    professional_years = sum([parse_dates_and_calculate_years(role.duration) 
                             for role in roles if not role.is_internship])
    
    total_years = professional_years + internship_years
    
    return Experience(years=total_years, roles=roles)


def extract_education(text: str) -> List[Education]:
    """
    Extract education details from resume section
    
    Args:
        text: Education section text
        
    Returns:
        List of Education objects
    """
    education_list = []
    
    # Common degree patterns
    degree_patterns = [
        r"(Bachelor'?s?|B\.?Tech|B\.?E\.?|B\.?S\.?|B\.?A\.?|BSc|BA)\s*(?:of|in|degree in)?\s*([A-Za-z\s&]+)",
        r"(Master'?s?|M\.?Tech|M\.?E\.?|M\.?S\.?|M\.?A\.?|MBA|MSc|MA)\s*(?:of|in|degree in)?\s*([A-Za-z\s&]+)",
        r"(Ph\.?D\.?|Doctorate)\s*(?:of|in)?\s*([A-Za-z\s&]+)",
        r"(Associate'?s?|A\.?S\.?|A\.?A\.?)\s*(?:of|in)?\s*([A-Za-z\s&]+)",
    ]
    
    # Split into blocks
    blocks = re.split(r'\n\s*\n', text)
    
    for block in blocks:
        if not block.strip():
            continue
        
        degree = ""
        field = ""
        institution = ""
        year = None
        
        # Extract degree and field
        for pattern in degree_patterns:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                degree = match.group(1).strip()
                field = match.group(2).strip() if len(match.groups()) > 1 else ""
                break
        
        # Extract institution (often contains "University", "College", "Institute")
        inst_match = re.search(r'([A-Z][A-Za-z\s,&]+(?:University|College|Institute|School)[A-Za-z\s,]*)', block)
        if inst_match:
            institution = inst_match.group(1).strip()
        
        # Extract year (4-digit number)
        year_match = re.search(r'\b(19|20)\d{2}\b', block)
        if year_match:
            year = int(year_match.group(0))
        
        if degree or institution:
            education_list.append(Education(
                degree=degree or "Degree",
                field=field or "Field of study",
                institution=institution or "Institution",
                year=year
            ))
    
    return education_list


def extract_projects(text: str) -> List[Project]:
    """
    Extract project details from resume section
    
    Args:
        text: Projects section text
        
    Returns:
        List of Project objects
    """
    projects = []
    
    # Split by bullet points or blank lines
    project_blocks = re.split(r'\n\s*[-•*]\s*|\n\s*\n', text)
    
    for block in project_blocks:
        if not block.strip() or len(block.strip()) < 20:
            continue
        
        lines = block.strip().split('\n')
        project_name = lines[0].strip()
        
        # Remove leading bullets
        project_name = re.sub(r'^[-•*\s]+', '', project_name)
        
        # Extract tech stack (look for parentheses or keywords)
        technologies = []
        tech_match = re.search(r'\(([^)]+)\)', block)
        if tech_match:
            tech_str = tech_match.group(1)
            technologies = [t.strip() for t in re.split(r'[,/|]+', tech_str) if t.strip()]
        
        # Also extract from description
        tech_keywords = extract_skills(block)
        technologies.extend(tech_keywords)
        technologies = list(set(technologies))  # Remove duplicates
        
        # Description is the rest of the block
        description = ' '.join(lines[1:]).strip() if len(lines) > 1 else block
        description = re.sub(r'\([^)]+\)', '', description).strip()  # Remove tech in parentheses
        
        if project_name:
            projects.append(Project(
                name=project_name[:100],  # Limit name length
                technologies=technologies[:10],  # Limit tech list
                description=description[:500]  # Limit description
            ))
    
    return projects


def extract_achievements(text: str) -> List[str]:
    """
    Extract achievements from resume section
    Flags quantifiable achievements (with numbers/percentages)
    
    Args:
        text: Achievements section text
        
    Returns:
        List of achievement strings
    """
    achievements = []
    
    # Split by bullet points or newlines
    items = re.split(r'\n\s*[-•*]\s*|\n', text)
    
    for item in items:
        item = item.strip()
        if not item or len(item) < 10:
            continue
        
        # Remove leading bullets
        item = re.sub(r'^[-•*\s]+', '', item)
        
        # Prioritize quantifiable achievements (contain numbers or percentages)
        if re.search(r'\d+%|\d+\+|\d+x|improved|increased|reduced|achieved', item, re.IGNORECASE):
            achievements.insert(0, item)  # Add to front (higher priority)
        else:
            achievements.append(item)
    
    return achievements[:10]  # Limit to top 10


def extract_extracurricular(text: str) -> List[str]:
    """
    Extract extra-curricular activities and leadership roles
    
    Args:
        text: Extra-curricular section text
        
    Returns:
        List of activity strings
    """
    activities = []
    
    # Keywords that indicate leadership/activities
    leadership_keywords = [
        'president', 'vice president', 'treasurer', 'secretary',
        'captain', 'lead', 'head', 'founder', 'co-founder',
        'volunteer', 'mentor', 'organizer', 'coordinator'
    ]
    
    # Split by bullet points or newlines
    items = re.split(r'\n\s*[-•*]\s*|\n', text)
    
    for item in items:
        item = item.strip()
        if not item or len(item) < 5:
            continue
        
        # Remove leading bullets
        item = re.sub(r'^[-•*\s]+', '', item)
        
        # Prioritize items with leadership keywords
        if any(keyword in item.lower() for keyword in leadership_keywords):
            activities.insert(0, item)  # Add to front (higher priority)
        else:
            activities.append(item)
    
    return activities[:10]  # Limit to top 10


def parse_resume_to_model(file_path: str, debug: bool = False) -> Resume:
    """
    Parse a resume file (PDF or text) and extract comprehensive structured information
    Returns a Resume model object with all sections
    
    Args:
        file_path: Path to the resume file (PDF or text)
        debug: If True, save debug JSON output and enable detailed logging
        
    Returns:
        Resume model object with extracted data
        
    Raises:
        FileReadError: If file cannot be read
        ValidationError: If critical fields are missing or invalid
        ParserError: For other parsing errors
    """
    try:
        logging.info(f"Starting resume parsing for: {file_path}")
        
        # Read the document with error handling
        try:
            text = read_document(file_path)
        except FileReadError as e:
            logging.error(f"Failed to read resume file: {e}")
            raise
        
        if not text or len(text.strip()) < 50:
            raise ValidationError(f"Resume text too short ({len(text)} chars). Minimum 50 characters required.")
        
        # Detect sections
        try:
            sections = detect_sections(text)
            logging.info(f"Detected sections: {list(sections.keys())}")
        except Exception as e:
            logging.warning(f"Section detection failed, using full text: {e}")
            sections = {}
        
        # Extract basic information from full text with error handling
        try:
            name = extract_name(text)
            if not name:
                logging.warning("Name extraction returned empty, using 'Unknown'")
                name = "Unknown"
        except Exception as e:
            logging.error(f"Name extraction failed: {e}")
            name = "Unknown"
        
        try:
            email = extract_email(text)
            if not email:
                logging.warning("Email not found in resume")
        except Exception as e:
            logging.warning(f"Email extraction failed: {e}")
            email = None
        
        try:
            phone = extract_phone(text)
            if not phone:
                logging.warning("Phone number not found in resume")
        except Exception as e:
            logging.warning(f"Phone extraction failed: {e}")
            phone = None
        
        # Extract from detected sections (or use full text as fallback)
        try:
            skills = extract_skills(sections.get('skills', text))
            if not skills:
                logging.warning("No skills extracted from resume")
                skills = []
        except Exception as e:
            logging.error(f"Skills extraction failed: {e}")
            skills = []
        
        try:
            experience = extract_experience(sections.get('experience', ''))
            if not experience.roles:
                # Set to 0 years for freshers
                logging.info("No experience roles found, marking as fresher")
                experience = Experience(years=0.0, roles=[])
        except Exception as e:
            logging.error(f"Experience extraction failed: {e}")
            experience = Experience(years=0.0, roles=[])
        
        try:
            education = extract_education(sections.get('education', ''))
            if not education:
                logging.warning("No education information extracted")
        except Exception as e:
            logging.error(f"Education extraction failed: {e}")
            education = []
        
        try:
            projects = extract_projects(sections.get('projects', ''))
            if not projects:
                logging.info("No projects found in resume")
        except Exception as e:
            logging.error(f"Projects extraction failed: {e}")
            projects = []
        
        try:
            achievements = extract_achievements(sections.get('achievements', ''))
            if not achievements:
                logging.info("No achievements found in resume")
        except Exception as e:
            logging.error(f"Achievements extraction failed: {e}")
            achievements = []
        
        try:
            extracurricular = extract_extracurricular(sections.get('extracurricular', ''))
            if not extracurricular:
                logging.info("No extracurricular activities found in resume")
        except Exception as e:
            logging.error(f"Extracurricular extraction failed: {e}")
            extracurricular = []
        
        # Create Resume model
        try:
            resume = Resume(
                name=name,
                email=email,
                phone=phone,
                skills=skills,
                experience=experience,
                education=education,
                projects=projects,
                achievements=achievements,
                extracurricular=extracurricular,
                raw_text=text
            )
        except Exception as e:
            logging.error(f"Failed to create Resume model: {e}")
            raise ParserError(f"Resume model creation failed: {e}")
        
        # Validate the resume
        validate_resume(resume)
        
        # Save debug output if requested
        if debug:
            try:
                debug_file = save_debug_output(resume, file_path)
                logging.info(f"Debug output saved to: {debug_file}")
            except Exception as e:
                logging.warning(f"Failed to save debug output: {e}")
        
        logging.info(f"Successfully parsed resume for: {name}")
        return resume
        
    except (FileReadError, ValidationError, ParserError):
        # Re-raise known exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors
        logging.error(f"Unexpected error during resume parsing: {e}")
        raise ParserError(f"Unexpected parsing error: {e}")


# ============================================================================
# Legacy functions - kept for backward compatibility
# ============================================================================

def parse_resume(pdf_path: str) -> Dict[str, Any]:
    """
    Parse a resume PDF and extract structured information (legacy version)
    Use parse_resume_to_model() for comprehensive extraction
    
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


# ============================================================================
# Testing and Validation Functions
# ============================================================================

def test_parser_on_sample(file_path: str, verbose: bool = True) -> Resume:
    """
    Test the parser on a sample resume file and display results
    Manually verify accuracy against expected data
    
    Args:
        file_path: Path to sample resume (PDF or text file)
        verbose: If True, print detailed extraction results
        
    Returns:
        Parsed Resume object
        
    Example:
        >>> resume = test_parser_on_sample('samples/john_doe_resume.pdf')
        >>> print(f"Accuracy: {calculate_accuracy(resume, expected_data)}")
    """
    import json
    from pathlib import Path
    
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Sample file not found: {file_path}")
    
    print("=" * 80)
    print(f"TESTING PARSER ON: {file_path}")
    print("=" * 80)
    
    # Parse the resume
    resume = parse_resume_to_model(file_path)
    
    if verbose:
        print("\n[BASIC INFORMATION]")
        print(f"Name: {resume.name}")
        print(f"Email: {resume.email}")
        print(f"Phone: {resume.phone}")
        
        print("\n[SKILLS]")
        print(f"Total: {len(resume.skills)} skills")
        print(f"Skills: {', '.join(resume.skills)}")
        
        print("\n[EXPERIENCE]")
        print(f"Total Experience: {resume.experience.years} years")
        print(f"Number of Roles: {len(resume.experience.roles)}")
        print(f"Is Fresher: {resume.is_fresher()}")
        for i, role in enumerate(resume.experience.roles, 1):
            print(f"\nRole {i}:")
            print(f"  Title: {role.title}")
            print(f"  Company: {role.company}")
            print(f"  Duration: {role.duration}")
            print(f"  Internship: {role.is_internship}")
            if role.description:
                print(f"  Description: {role.description[:100]}...")
        
        print("\n[EDUCATION]")
        print(f"Total: {len(resume.education)} qualification(s)")
        for edu in resume.education:
            print(f"  - {edu.degree} in {edu.field}")
            print(f"    {edu.institution} ({edu.year or 'Year not found'})")
        
        print("\n[PROJECTS]")
        print(f"Total: {len(resume.projects)} project(s)")
        for proj in resume.projects:
            print(f"  - {proj.name}")
            print(f"    Technologies: {', '.join(proj.technologies[:5])}")
            print(f"    Description: {proj.description[:80]}...")
        
        print("\n[ACHIEVEMENTS]")
        print(f"Total: {len(resume.achievements)} achievement(s)")
        for ach in resume.achievements[:5]:
            print(f"  - {ach}")
        
        print("\n[EXTRA-CURRICULAR]")
        print(f"Total: {len(resume.extracurricular)} activit(ies)")
        for act in resume.extracurricular:
            print(f"  - {act}")
        
        print("\n[JSON OUTPUT]")
        # Convert to dict for JSON serialization
        resume_dict = {
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "skills": resume.skills,
            "experience": {
                "years": resume.experience.years,
                "roles": [
                    {
                        "title": role.title,
                        "company": role.company,
                        "duration": role.duration,
                        "description": role.description,
                        "is_internship": role.is_internship
                    }
                    for role in resume.experience.roles
                ]
            },
            "education": [
                {
                    "degree": edu.degree,
                    "field": edu.field,
                    "institution": edu.institution,
                    "year": edu.year
                }
                for edu in resume.education
            ],
            "projects": [
                {
                    "name": proj.name,
                    "technologies": proj.technologies,
                    "description": proj.description
                }
                for proj in resume.projects
            ],
            "achievements": resume.achievements,
            "extracurricular": resume.extracurricular,
            "is_fresher": resume.is_fresher()
        }
        
        print(json.dumps(resume_dict, indent=2))
        
        print("\n" + "=" * 80)
        print("MANUAL VERIFICATION CHECKLIST:")
        print("=" * 80)
        print("□ Name extracted correctly?")
        print("□ Contact info (email/phone) correct?")
        print(f"□ Skills comprehensive? (Found {len(resume.skills)}, aim for 80%+ accuracy)")
        print(f"□ Experience years calculated correctly? ({resume.experience.years} years)")
        print(f"□ All roles extracted? ({len(resume.experience.roles)} roles found)")
        print("□ Internships flagged correctly?")
        print(f"□ Education complete? ({len(resume.education)} entries)")
        print(f"□ Projects captured? ({len(resume.projects)} projects)")
        print(f"□ Achievements included? ({len(resume.achievements)} achievements)")
        print("□ Fresher classification correct?")
        print("=" * 80)
    
    return resume


def batch_test_parser(samples_dir: str = "samples") -> None:
    """
    Test parser on all sample files in a directory
    Useful for validation across multiple resumes
    
    Args:
        samples_dir: Directory containing sample resume files
    """
    from pathlib import Path
    
    samples_path = Path(samples_dir)
    if not samples_path.exists():
        print(f"Samples directory not found: {samples_dir}")
        return
    
    # Find all PDF and text files
    resume_files = list(samples_path.glob("*.pdf")) + list(samples_path.glob("*.txt"))
    
    if not resume_files:
        print(f"No resume files found in {samples_dir}")
        print("Add .pdf or .txt resume files to test the parser")
        return
    
    print(f"Found {len(resume_files)} resume file(s) to test")
    print("=" * 80)
    
    results = []
    for file_path in resume_files:
        try:
            print(f"\nTesting: {file_path.name}")
            resume = test_parser_on_sample(str(file_path), verbose=False)
            
            # Summary stats
            stats = {
                "file": file_path.name,
                "name": resume.name,
                "skills_count": len(resume.skills),
                "experience_years": resume.experience.years,
                "roles_count": len(resume.experience.roles),
                "education_count": len(resume.education),
                "projects_count": len(resume.projects),
                "is_fresher": resume.is_fresher()
            }
            results.append(stats)
            
            print(f"✅ Parsed successfully: {resume.name}")
            print(f"   Skills: {stats['skills_count']}, Experience: {stats['experience_years']}yr, "
                  f"Roles: {stats['roles_count']}, Projects: {stats['projects_count']}")
            
        except Exception as e:
            print(f"❌ Error parsing {file_path.name}: {str(e)}")
            results.append({"file": file_path.name, "error": str(e)})
    
    print("\n" + "=" * 80)
    print("BATCH TEST SUMMARY")
    print("=" * 80)
    successful = len([r for r in results if 'error' not in r])
    print(f"Successfully parsed: {successful}/{len(resume_files)} files")
    print("=" * 80)


if __name__ == "__main__":
    """
    Run parser tests when module is executed directly
    Usage: python backend/parser.py
    """
    import sys
    
    if len(sys.argv) > 1:
        # Test specific file
        file_path = sys.argv[1]
        test_parser_on_sample(file_path)
    else:
        # Batch test all samples
        print("Testing parser on all sample files...")
        batch_test_parser()
