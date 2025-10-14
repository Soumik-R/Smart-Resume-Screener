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
    Extract skills from text using NLP and keyword matching
    Filters out common prefixes like "proficient in"
    
    Args:
        text: Input text (preferably from skills section)
        
    Returns:
        List of identified skills
    """
    # Comprehensive technical skills database
    skill_keywords = [
        # Programming Languages
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
        "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "shell", "bash",
        
        # Web Frameworks
        "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi",
        "spring boot", "asp.net", "laravel", "rails", "nextjs", "gatsby",
        
        # Databases
        "mongodb", "postgresql", "mysql", "redis", "elasticsearch", "dynamodb",
        "oracle", "sql server", "cassandra", "neo4j", "sqlite",
        
        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "gitlab", "github actions", "ci/cd", "circleci",
        
        # AI/ML
        "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
        "pytorch", "keras", "scikit-learn", "opencv", "hugging face",
        
        # Tools
        "git", "jira", "confluence", "slack", "postman", "swagger",
        
        # Methodologies
        "agile", "scrum", "kanban", "test-driven development", "tdd"
    ]
    
    # Remove common prefixes
    text = re.sub(r'(?:proficient in|experienced with|familiar with|knowledge of)[\s:]+', '', text, flags=re.IGNORECASE)
    
    # Split by common delimiters
    items = re.split(r'[,•|/\n]+', text)
    
    found_skills = []
    text_lower = text.lower()
    
    # Keyword matching
    for skill in skill_keywords:
        if skill in text_lower:
            # Capitalize properly
            found_skills.append(skill.title())
    
    # Also extract from split items (for skills not in keyword list)
    for item in items:
        item = item.strip()
        if item and len(item) > 2 and len(item) < 30:
            # Remove leading symbols like - or *
            item = re.sub(r'^[-*•\s]+', '', item)
            if item and not any(prefix in item.lower() for prefix in ['proficient', 'experienced', 'familiar']):
                # Use spaCy for better extraction
                doc = nlp(item)
                for token in doc:
                    if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
                        found_skills.append(token.text.title())
    
    # Remove duplicates and return
    return list(set(found_skills))


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
    Extract work experience from resume section
    
    Args:
        text: Experience section text
        
    Returns:
        Experience object with years and roles
    """
    roles = []
    
    # Split into individual role blocks (separated by blank lines or bullet points)
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
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for internship keywords
            if re.search(r'\bintern\b', line, re.IGNORECASE):
                is_internship = True
            
            # Check for date patterns (usually contains dates)
            if re.search(r'\d{4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec', line, re.IGNORECASE):
                duration = line
                # Previous line might be company or title
                if i > 0:
                    if not role_title:
                        role_title = lines[i-1].strip()
                    if i > 1 and not company:
                        company = lines[i-2].strip()
                continue
            
            # Extract company (often has keywords like "at", "Inc", "Corp", "Ltd")
            if re.search(r'\bat\b|Inc|Corp|Ltd|LLC|Company|Technologies', line, re.IGNORECASE):
                if not company:
                    company = line
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


def parse_resume_to_model(file_path: str) -> Resume:
    """
    Parse a resume file (PDF or text) and extract comprehensive structured information
    Returns a Resume model object with all sections
    
    Args:
        file_path: Path to the resume file (PDF or text)
        
    Returns:
        Resume model object with extracted data
    """
    # Read the document
    text = read_document(file_path)
    
    # Detect sections
    sections = detect_sections(text)
    
    # Extract basic information from full text
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    
    # Extract from detected sections (or use full text as fallback)
    skills = extract_skills(sections.get('skills', text))
    
    experience = extract_experience(sections.get('experience', ''))
    if not experience.roles:
        # Set to 0 years for freshers
        experience = Experience(years=0.0, roles=[])
    
    education = extract_education(sections.get('education', ''))
    projects = extract_projects(sections.get('projects', ''))
    achievements = extract_achievements(sections.get('achievements', ''))
    extracurricular = extract_extracurricular(sections.get('extracurricular', ''))
    
    # Create and return Resume model
    resume = Resume(
        name=name or "Unknown",
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
    
    return resume


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
