"""
FastAPI Backend for Smart Resume Screener
Provides REST API endpoints for resume parsing, matching, and database operations
"""
import os
import uuid
import csv
import logging
from datetime import datetime
from typing import Optional, List
from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator, ValidationError
from dotenv import load_dotenv
import openai

# Import local modules
import db
from matcher import extract_jd_requirements, match_resume_to_jd, score_batch

# Load environment variables
load_dotenv()

# Configuration constants
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = ['pdf', 'txt', 'text']
API_KEY_HEADER = "X-API-Key"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Resume Screener API",
    description="Intelligent resume parsing and matching system using GPT-4o",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Alternative
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("🚀 Smart Resume Screener API initialized")


# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"❌ Validation error: {exc}")
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request validation failed. Please check your input.",
            "details": errors,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    
    # Check if it's a database connection error
    error_str = str(exc).lower()
    if "connection" in error_str or "timeout" in error_str or "mongo" in error_str:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "message": "Database connection failed. Please try again later.",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Check if it's an OpenAI API error
    if "openai" in error_str or "api" in error_str:
        return JSONResponse(
            status_code=502,
            content={
                "error": "AI Service Error",
                "message": "AI service temporarily unavailable. Please try again later.",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Generic server error
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please contact support if the issue persists.",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================================================

class ResumeUploadResponse(BaseModel):
    candidate_id: str
    parsed_data: dict
    message: str

class JDUploadResponse(BaseModel):
    jd_id: str
    requirements: dict
    message: str

class MatchRequest(BaseModel):
    candidate_ids: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=50,
        description="List of candidate IDs to match (1-50 candidates)"
    )
    
    @validator('candidate_ids')
    def validate_candidate_ids(cls, v):
        if not v:
            raise ValueError("At least one candidate ID is required")
        
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate candidate IDs found")
        
        # Check ID format (basic UUID validation)
        for cid in v:
            if not cid or len(cid) < 8:
                raise ValueError(f"Invalid candidate ID format: {cid}")
        
        return v

class MatchResult(BaseModel):
    id: str
    overall: float = Field(..., ge=0, le=10, description="Overall score (0-10)")
    justifications: dict
    feedback: str
    strengths: List[str]
    improvement_areas: List[str]

class MatchResponse(BaseModel):
    jd_id: str
    matched_candidates: List[MatchResult]
    total_candidates: int = Field(..., ge=0)
    message: str

class ShortlistCandidate(BaseModel):
    candidate_id: str
    name: str
    overall_score: float = Field(..., ge=0, le=10)
    skills_score: float = Field(..., ge=0, le=10)
    experience_score: float = Field(..., ge=0, le=10)
    education_projects_score: float = Field(..., ge=0, le=10)
    achievements_score: float = Field(..., ge=0, le=10)
    extracurricular_score: float = Field(..., ge=0, le=10)
    feedback: str
    strengths: List[str]
    improvement_areas: List[str]
    matched_at: str

class ShortlistResponse(BaseModel):
    jd_id: str
    candidates: List[ShortlistCandidate]
    total_count: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    filters_applied: dict
    message: str

class BiasCheckResponse(BaseModel):
    candidate_id: str
    bias_detected: bool
    bias_flags: List[str]
    analysis: str
    recommendations: List[str]
    timestamp: str
    message: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: str



# ============================================================================
# SECURITY AND VALIDATION HELPERS
# ============================================================================

def verify_api_key(api_key: Optional[str] = Header(None, alias=API_KEY_HEADER)) -> bool:
    """
    Verify API key (optional - for future use)
    Currently disabled but ready for production deployment
    """
    # For development, accept all requests
    # In production, uncomment and set REQUIRED_API_KEY in environment
    
    # required_key = os.getenv("API_KEY")
    # if required_key and api_key != required_key:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Invalid or missing API key"
    #     )
    
    return True


def validate_file_upload(file: UploadFile) -> None:
    """
    Validate uploaded file (size, extension, etc.)
    
    Args:
        file: Uploaded file from request
        
    Raises:
        HTTPException: If validation fails
    """
    # Check filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )
    
    # Check file extension
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: .{file_ext}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (if available from Content-Length header)
    if hasattr(file, 'size') and file.size:
        if file.size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB. Your file: {file.size / 1024 / 1024:.2f}MB"
            )
    
    logger.debug(f"✓ File validation passed: {file.filename}")


def validate_file_content(content: bytes, filename: str) -> None:
    """
    Validate file content after reading
    
    Args:
        content: File bytes
        filename: Original filename
        
    Raises:
        HTTPException: If validation fails
    """
    # Check content size
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB. Your file: {len(content) / 1024 / 1024:.2f}MB"
        )
    
    # Check content is not empty
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
    
    # For PDF files, check magic bytes
    if filename.lower().endswith('.pdf'):
        if not content.startswith(b'%PDF'):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. File does not contain valid PDF header."
            )
    
    logger.debug(f"✓ Content validation passed: {len(content)} bytes")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_resume_file(file_content: bytes, filename: str) -> dict:
    """
    Parse resume file (PDF or text) and extract structured data
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Returns:
        Parsed resume dictionary
    """
    # Detect file type
    file_ext = filename.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        # Parse PDF
        import pdfplumber
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        logger.info(f"📄 Extracted {len(text)} characters from PDF: {filename}")
    
    elif file_ext in ['txt', 'text']:
        # Parse text file
        text = file_content.decode('utf-8', errors='ignore')
        logger.info(f"📄 Extracted {len(text)} characters from text file: {filename}")
    
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Use PDF or TXT files.")
    
    # Basic extraction
    resume_data = {
        "name": "Extracted Name",
        "email": None,
        "phone": None,
        "skills": [],
        "experience": {
            "years": 0,
            "roles": []
        },
        "education": [],
        "projects": [],
        "achievements": [],
        "extracurricular": [],
        "raw_text": text[:5000]
    }
    
    # Extract name from first 20 lines
    lines = text.split('\n')
    for line in lines[:20]:
        line = line.strip()
        if len(line) > 3 and len(line) < 50 and not any(kw in line.lower() for kw in ['resume', 'cv', 'curriculum']):
            resume_data["name"] = line
            break
    
    # Extract email
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        resume_data["email"] = emails[0]
    
    # Extract phone
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phones = re.findall(phone_pattern, text)
    if phones:
        resume_data["phone"] = phones[0]
    
    # Extract common skills
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'MongoDB', 'React', 
        'Node.js', 'AWS', 'Docker', 'Kubernetes', 'Machine Learning', 'AI',
        'FastAPI', 'Django', 'Flask', 'PostgreSQL', 'Git', 'Linux'
    ]
    
    text_lower = text.lower()
    for skill in common_skills:
        if skill.lower() in text_lower:
            resume_data["skills"].append(skill)
    
    logger.info(f"✓ Parsed resume: {resume_data['name']}, {len(resume_data['skills'])} skills found")
    
    return resume_data


def anonymize_resume_data(resume_data: dict) -> dict:
    """Anonymize resume for bias-free processing"""
    import copy
    anonymized = copy.deepcopy(resume_data)
    
    anonymized["name"] = "[REDACTED]"
    anonymized["email"] = None
    anonymized["phone"] = None
    
    if "raw_text" in anonymized:
        del anonymized["raw_text"]
    
    logger.debug("✓ Resume anonymized")
    
    return anonymized


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Smart Resume Screener API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "upload_resume": "POST /upload_resume",
            "upload_jd": "POST /upload_jd",
            "health": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - verifies API and database connectivity"""
    try:
        stats = db.get_database_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "connected": True,
                "name": stats["database"],
                "collections": stats["collections"]
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.post("/upload_resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF or TXT, max 5MB)")
):
    """
    Upload and parse a resume file
    
    - Accepts PDF or TXT files (max 5MB)
    - Validates file type and size
    - Extracts structured data (name, skills, experience, etc.)
    - Anonymizes for bias-free processing
    - Saves to database
    - Returns candidate ID and parsed data summary
    """
    logger.info("="*80)
    logger.info(f"📤 Received resume upload: {file.filename}")
    
    try:
        # Validate file
        validate_file_upload(file)
        
        # Read and validate content
        file_content = await file.read()
        validate_file_content(file_content, file.filename)
        logger.info(f"✓ Read and validated {len(file_content)} bytes from file")
        
        logger.info("🔍 Parsing resume...")
        resume_data = parse_resume_file(file_content, file.filename)
        
        # Generate unique ID
        candidate_id = str(uuid.uuid4())
        logger.info(f"✓ Generated candidate ID: {candidate_id}")
        
        # Save to database
        logger.info("💾 Saving to database...")
        db_id = db.save_parsed_resume(resume_data, file_id=candidate_id)
        logger.info(f"✓ Saved to database with ID: {db_id}")
        
        # Create response summary
        parsed_summary = {
            "name": resume_data.get("name", "Unknown"),
            "email": resume_data.get("email"),
            "skills_count": len(resume_data.get("skills", [])),
            "skills": resume_data.get("skills", [])[:10],
            "experience_years": resume_data.get("experience", {}).get("years", 0),
            "has_education": len(resume_data.get("education", [])) > 0,
            "has_projects": len(resume_data.get("projects", [])) > 0
        }
        
        logger.info("="*80)
        logger.info(f"✅ Resume upload complete: {resume_data.get('name')} ({candidate_id})")
        logger.info("="*80)
        
        return ResumeUploadResponse(
            candidate_id=candidate_id,
            parsed_data=parsed_summary,
            message=f"Resume parsed and saved successfully. Extracted {len(resume_data.get('skills', []))} skills."
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"❌ Error uploading resume: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@app.post("/upload_jd", response_model=JDUploadResponse)
async def upload_jd(
    file: Optional[UploadFile] = File(None, description="Job description file (PDF/TXT, max 5MB)"),
    jd_text: Optional[str] = Form(None, description="Job description text (optional, max 50,000 chars)")
):
    """
    Upload and parse a job description
    
    - Accepts JD as file (PDF/TXT, max 5MB) or text form data (max 50,000 chars)
    - Validates file type, size, and text length
    - Extracts requirements (skills, experience, education)
    - Saves to database
    - Returns JD ID and parsed requirements
    """
    logger.info("="*80)
    logger.info("📤 Received job description upload")
    
    try:
        # Get JD text from file or form
        if file and file.filename:
            logger.info(f"📄 Processing JD file: {file.filename}")
            
            # Validate file
            validate_file_upload(file)
            
            file_content = await file.read()
            validate_file_content(file_content, file.filename)
            
            file_ext = file.filename.lower().split('.')[-1]
            if file_ext == 'pdf':
                import pdfplumber
                with pdfplumber.open(BytesIO(file_content)) as pdf:
                    jd_text = ""
                    for page in pdf.pages:
                        jd_text += page.extract_text() or ""
            else:
                jd_text = file_content.decode('utf-8', errors='ignore')
            
            logger.info(f"✓ Extracted {len(jd_text)} characters from file")
        
        elif jd_text:
            logger.info(f"📝 Processing JD text: {len(jd_text)} characters")
            
            # Validate text length
            if len(jd_text) > 50000:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job description text too long. Maximum: 50,000 characters. Your text: {len(jd_text)} characters"
                )
            
            if len(jd_text.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Job description too short. Please provide at least 50 characters."
                )
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Please provide either a file or jd_text"
            )
        
        # Extract requirements
        logger.info("🔍 Extracting JD requirements...")
        requirements = extract_jd_requirements(jd_text)
        
        logger.info(f"✓ Extracted requirements: {len(requirements['required_skills'])} skills, "
                   f"{requirements['experience_years']} years exp")
        
        # Generate unique JD ID
        jd_id = str(uuid.uuid4())
        logger.info(f"✓ Generated JD ID: {jd_id}")
        
        # Save to database
        logger.info("💾 Saving JD to database...")
        db_id = db.save_job_description(jd_text, requirements, jd_id=jd_id)
        logger.info(f"✓ Saved to database with ID: {db_id}")
        
        logger.info("="*80)
        logger.info(f"✅ Job description upload complete: {jd_id}")
        logger.info("="*80)
        
        return JDUploadResponse(
            jd_id=jd_id,
            requirements=requirements,
            message=f"Job description parsed and saved successfully. Extracted {len(requirements['required_skills'])} required skills."
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"❌ Error uploading JD: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process job description: {str(e)}")


@app.post("/match/{jd_id}", response_model=MatchResponse)
async def match_candidates(
    jd_id: str,
    request: MatchRequest
):
    """
    Match candidates to a job description using GPT-4o
    
    - Accepts list of candidate IDs
    - Fetches resumes and JD from database
    - Runs batch scoring via matcher.py
    - Stores results in each candidate's match_history
    - Returns ranked list with scores and feedback
    """
    logger.info("="*80)
    logger.info(f"🎯 Starting matching process for JD: {jd_id}")
    logger.info(f"📊 Candidates to match: {len(request.candidate_ids)}")
    
    try:
        # Fetch job description
        logger.info(f"🔍 Fetching job description: {jd_id}")
        jd_doc = db.get_job_by_id(jd_id)
        if not jd_doc:
            raise HTTPException(status_code=404, detail=f"Job description not found: {jd_id}")
        
        jd_text = jd_doc.get("jd_text", "")
        jd_requirements = jd_doc.get("requirements", {})
        logger.info(f"✓ Loaded JD: {len(jd_text)} chars, {len(jd_requirements.get('required_skills', []))} skills")
        
        # Fetch all candidate resumes
        logger.info(f"🔍 Fetching {len(request.candidate_ids)} candidate resumes...")
        candidates_data = []
        missing_ids = []
        
        for candidate_id in request.candidate_ids:
            resume = db.get_resume_by_id(candidate_id)
            if resume:
                candidates_data.append({
                    "resume_id": candidate_id,
                    "resume_data": resume
                })
                logger.info(f"  ✓ Loaded candidate: {candidate_id}")
            else:
                missing_ids.append(candidate_id)
                logger.warning(f"  ⚠️ Candidate not found: {candidate_id}")
        
        if missing_ids:
            logger.warning(f"⚠️ {len(missing_ids)} candidates not found in database")
        
        if not candidates_data:
            raise HTTPException(
                status_code=404, 
                detail="None of the provided candidate IDs were found in database"
            )
        
        logger.info(f"✓ Loaded {len(candidates_data)} valid candidates")
        
        # Run batch scoring
        logger.info("🚀 Starting batch scoring with GPT-4o...")
        scored_results = score_batch(candidates_data, jd_text, jd_requirements)
        
        logger.info(f"✓ Scoring complete: {len(scored_results)} results")
        
        # Store results in database
        logger.info("💾 Saving match results to database...")
        for result in scored_results:
            candidate_id = result["resume_id"]
            match_data = {
                "jd_id": jd_id,
                "timestamp": datetime.now().isoformat(),
                "scores": result["scores"],
                "shortlisted": result["shortlisted"],
                "feedback": result.get("feedback", ""),
                "strengths": result.get("strengths", []),
                "improvement_areas": result.get("improvement_areas", [])
            }
            
            # Update candidate's match_history
            db.update_match_results(candidate_id, jd_id, match_data)
            
            # Also save to match_results collection
            db.save_match_result(candidate_id, jd_id, match_data)
        
        logger.info(f"✓ Saved {len(scored_results)} match results")
        
        # Format response
        matched_candidates = []
        for result in scored_results:
            matched_candidates.append(MatchResult(
                id=result["resume_id"],
                overall=result["scores"]["overall"],
                justifications=result["scores"],
                feedback=result.get("feedback", ""),
                strengths=result.get("strengths", []),
                improvement_areas=result.get("improvement_areas", [])
            ))
        
        logger.info("="*80)
        logger.info(f"✅ Matching complete: {len(matched_candidates)} candidates ranked")
        logger.info(f"📊 Top score: {scored_results[0]['scores']['overall']:.2f}")
        logger.info("="*80)
        
        return MatchResponse(
            jd_id=jd_id,
            matched_candidates=matched_candidates,
            total_candidates=len(matched_candidates),
            message=f"Successfully matched {len(matched_candidates)} candidates. Results saved to database."
        )
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error during matching: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to match candidates: {str(e)}")


@app.get("/shortlist/{jd_id}", response_model=ShortlistResponse)
async def get_shortlist(
    jd_id: str,
    threshold: float = Query(7.0, description="Minimum overall score threshold", ge=0, le=10),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience", ge=0),
    min_skills_score: Optional[float] = Query(None, description="Minimum skills score", ge=0, le=10),
    limit: int = Query(10, description="Number of results per page", ge=1, le=100),
    offset: int = Query(0, description="Number of results to skip", ge=0)
):
    """
    Get shortlisted candidates for a job description
    
    - Query candidates with matches for the specified JD
    - Filter by overall score threshold (default: 7.0)
    - Optional filters: min_experience, min_skills_score
    - Returns paginated results sorted by overall score (descending)
    """
    logger.info("="*80)
    logger.info(f"🔍 Fetching shortlist for JD: {jd_id}")
    logger.info(f"📊 Filters: threshold={threshold}, min_exp={min_experience}, limit={limit}, offset={offset}")
    
    try:
        # Verify JD exists
        jd_doc = db.get_job_by_id(jd_id)
        if not jd_doc:
            raise HTTPException(status_code=404, detail=f"Job description not found: {jd_id}")
        
        # Get all match results for this JD
        logger.info("🔍 Querying match results...")
        all_matches = db.get_match_history(jd_id=jd_id)
        
        logger.info(f"✓ Found {len(all_matches)} total matches")
        
        # Apply filters
        filtered_candidates = []
        filters_applied = {
            "threshold": threshold,
            "min_experience": min_experience,
            "min_skills_score": min_skills_score
        }
        
        for match in all_matches:
            candidate_id = match.get("candidate_id")
            match_data = match.get("match_data", {})
            scores = match_data.get("scores", {})
            overall_score = scores.get("overall", 0)
            
            # Apply threshold filter
            if overall_score < threshold:
                continue
            
            # Fetch candidate details for additional filters
            if min_experience is not None or min_skills_score is not None:
                candidate = db.get_resume_by_id(candidate_id)
                if not candidate:
                    continue
                
                # Apply experience filter
                if min_experience is not None:
                    exp_years = candidate.get("experience", {}).get("years", 0)
                    if exp_years < min_experience:
                        continue
                
                # Apply skills score filter
                if min_skills_score is not None:
                    skills_score = scores.get("skills", 0)
                    if skills_score < min_skills_score:
                        continue
                
                candidate_name = candidate.get("name", "Unknown")
            else:
                # Just fetch name without full validation
                candidate = db.get_resume_by_id(candidate_id)
                candidate_name = candidate.get("name", "Unknown") if candidate else "Unknown"
            
            # Add to filtered list
            filtered_candidates.append({
                "candidate_id": candidate_id,
                "name": candidate_name,
                "overall_score": overall_score,
                "skills_score": scores.get("skills", 0),
                "experience_score": scores.get("experience", 0),
                "education_projects_score": scores.get("education_projects", 0),
                "achievements_score": scores.get("achievements", 0),
                "extracurricular_score": scores.get("extracurricular", 0),
                "feedback": match_data.get("feedback", ""),
                "strengths": match_data.get("strengths", []),
                "improvement_areas": match_data.get("improvement_areas", []),
                "matched_at": match_data.get("timestamp", "")
            })
        
        logger.info(f"✓ After filtering: {len(filtered_candidates)} candidates")
        
        # Sort by overall score (descending)
        filtered_candidates.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Apply pagination
        total_count = len(filtered_candidates)
        page = offset // limit + 1
        paginated_candidates = filtered_candidates[offset:offset + limit]
        
        logger.info(f"✓ Returning page {page}: {len(paginated_candidates)} candidates")
        
        # Format response
        shortlist = [
            ShortlistCandidate(**candidate)
            for candidate in paginated_candidates
        ]
        
        logger.info("="*80)
        logger.info(f"✅ Shortlist retrieved: {len(shortlist)} candidates (page {page})")
        logger.info("="*80)
        
        return ShortlistResponse(
            jd_id=jd_id,
            candidates=shortlist,
            total_count=total_count,
            page=page,
            page_size=limit,
            filters_applied=filters_applied,
            message=f"Found {total_count} candidates matching criteria. Showing page {page}."
        )
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error fetching shortlist: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch shortlist: {str(e)}")


@app.get("/export/{jd_id}/csv")
async def export_shortlist_csv(
    jd_id: str,
    threshold: float = Query(7.0, description="Minimum overall score threshold", ge=0, le=10),
    min_experience: Optional[int] = Query(None, description="Minimum years of experience", ge=0),
    min_skills_score: Optional[float] = Query(None, description="Minimum skills score", ge=0, le=10)
):
    """
    Export shortlisted candidates to CSV file
    
    - Uses same filters as /shortlist endpoint
    - Generates CSV with comprehensive candidate data
    - Returns as downloadable file
    """
    logger.info("="*80)
    logger.info(f"📊 Exporting shortlist to CSV for JD: {jd_id}")
    logger.info(f"📋 Filters: threshold={threshold}, min_exp={min_experience}, min_skills={min_skills_score}")
    
    try:
        # Verify JD exists
        jd_doc = db.get_job_by_id(jd_id)
        if not jd_doc:
            raise HTTPException(status_code=404, detail=f"Job description not found: {jd_id}")
        
        # Get all match results for this JD
        logger.info("🔍 Querying match results...")
        all_matches = db.get_match_history(jd_id=jd_id)
        
        logger.info(f"✓ Found {len(all_matches)} total matches")
        
        # Apply filters (same logic as shortlist endpoint)
        filtered_candidates = []
        
        for match in all_matches:
            candidate_id = match.get("candidate_id")
            match_data = match.get("match_data", {})
            scores = match_data.get("scores", {})
            overall_score = scores.get("overall", 0)
            
            # Apply threshold filter
            if overall_score < threshold:
                continue
            
            # Fetch candidate details for additional filters
            candidate = db.get_resume_by_id(candidate_id)
            if not candidate:
                continue
            
            # Apply experience filter
            if min_experience is not None:
                exp_years = candidate.get("experience", {}).get("years", 0)
                if exp_years < min_experience:
                    continue
            
            # Apply skills score filter
            if min_skills_score is not None:
                skills_score = scores.get("skills", 0)
                if skills_score < min_skills_score:
                    continue
            
            # Add to filtered list
            filtered_candidates.append({
                "candidate_id": candidate_id,
                "name": candidate.get("name", "Unknown"),
                "email": candidate.get("email", "N/A"),
                "phone": candidate.get("phone", "N/A"),
                "overall_score": overall_score,
                "skills_score": scores.get("skills", 0),
                "experience_score": scores.get("experience", 0),
                "education_projects_score": scores.get("education_projects", 0),
                "achievements_score": scores.get("achievements", 0),
                "extracurricular_score": scores.get("extracurricular", 0),
                "experience_years": candidate.get("experience", {}).get("years", 0),
                "skills": ", ".join(candidate.get("skills", [])[:10]),
                "feedback": match_data.get("feedback", ""),
                "strengths": " | ".join(match_data.get("strengths", [])[:5]),
                "improvement_areas": " | ".join(match_data.get("improvement_areas", [])[:5]),
                "matched_at": match_data.get("timestamp", "")
            })
        
        logger.info(f"✓ After filtering: {len(filtered_candidates)} candidates")
        
        if not filtered_candidates:
            raise HTTPException(
                status_code=404, 
                detail=f"No candidates found matching criteria (threshold={threshold})"
            )
        
        # Sort by overall score (descending)
        filtered_candidates.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Generate CSV
        logger.info("📝 Generating CSV file...")
        output = StringIO()
        
        # Define CSV headers
        csv_headers = [
            "Rank",
            "Candidate ID",
            "Name",
            "Email",
            "Phone",
            "Overall Score",
            "Skills Score",
            "Experience Score",
            "Education & Projects Score",
            "Achievements Score",
            "Extracurricular Score",
            "Years of Experience",
            "Top Skills",
            "Strengths",
            "Improvement Areas",
            "Feedback Summary",
            "Matched At"
        ]
        
        writer = csv.DictWriter(output, fieldnames=csv_headers)
        writer.writeheader()
        
        # Write candidate data
        for rank, candidate in enumerate(filtered_candidates, 1):
            writer.writerow({
                "Rank": rank,
                "Candidate ID": candidate["candidate_id"],
                "Name": candidate["name"],
                "Email": candidate["email"],
                "Phone": candidate["phone"],
                "Overall Score": f"{candidate['overall_score']:.2f}",
                "Skills Score": f"{candidate['skills_score']:.2f}",
                "Experience Score": f"{candidate['experience_score']:.2f}",
                "Education & Projects Score": f"{candidate['education_projects_score']:.2f}",
                "Achievements Score": f"{candidate['achievements_score']:.2f}",
                "Extracurricular Score": f"{candidate['extracurricular_score']:.2f}",
                "Years of Experience": candidate["experience_years"],
                "Top Skills": candidate["skills"],
                "Strengths": candidate["strengths"],
                "Improvement Areas": candidate["improvement_areas"],
                "Feedback Summary": candidate["feedback"][:200] + "..." if len(candidate["feedback"]) > 200 else candidate["feedback"],
                "Matched At": candidate["matched_at"]
            })
        
        logger.info(f"✓ CSV generated with {len(filtered_candidates)} rows")
        
        # Prepare response
        output.seek(0)
        csv_content = output.getvalue()
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shortlist_{jd_id[:8]}_{timestamp}.csv"
        
        logger.info("="*80)
        logger.info(f"✅ CSV export complete: {filename}")
        logger.info("="*80)
        
        # Return as downloadable file
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error exporting CSV: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")


@app.post("/bias_check/{candidate_id}", response_model=BiasCheckResponse)
async def check_bias(candidate_id: str):
    """
    Run bias detection on candidate resume (anonymized data)
    
    - Fetches candidate resume from database
    - Anonymizes personal information
    - Uses LLM to detect potential demographic inferences or biases
    - Stores bias check results in candidate document
    - Returns analysis and recommendations
    """
    logger.info("="*80)
    logger.info(f"🔍 Running bias check for candidate: {candidate_id}")
    
    try:
        # Fetch candidate
        logger.info("📄 Fetching candidate resume...")
        candidate = db.get_resume_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate not found: {candidate_id}")
        
        logger.info(f"✓ Loaded candidate: {candidate.get('name', 'Unknown')}")
        
        # Anonymize data
        logger.info("🔒 Anonymizing candidate data...")
        anonymized_data = anonymize_resume_data(candidate)
        
        # Prepare bias check prompt
        bias_check_prompt = f"""You are an AI bias detection expert. Analyze the following anonymized resume data for potential biases or unintended demographic inferences.

ANONYMIZED RESUME DATA:
{anonymized_data}

TASK:
1. Identify any language, phrases, or patterns that could inadvertently reveal or infer:
   - Gender, age, race, ethnicity, nationality
   - Socioeconomic status
   - Disability status
   - Religious affiliation
   - Any other protected characteristics

2. Detect potential biases in how the resume is written:
   - Unconscious biases in skill descriptions
   - Gendered language or stereotypes
   - Cultural assumptions
   - Educational elitism

3. Flag any concerns even if subtle

RESPOND IN JSON FORMAT:
{{
    "bias_detected": true/false,
    "bias_flags": ["flag1", "flag2", ...],
    "analysis": "Detailed analysis of potential biases found",
    "recommendations": ["recommendation1", "recommendation2", ...]
}}

BE THOROUGH: Look for both obvious and subtle indicators. If no biases detected, explain why the resume appears neutral."""
        
        logger.info("🤖 Calling GPT-4o for bias analysis...")
        
        # Initialize OpenAI client
        openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in detecting bias and ensuring fair, unbiased hiring practices."},
                {"role": "user", "content": bias_check_prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        import json
        bias_result = json.loads(response.choices[0].message.content)
        
        logger.info(f"✓ Bias check complete: {bias_result.get('bias_detected', False)}")
        logger.info(f"   Flags found: {len(bias_result.get('bias_flags', []))}")
        
        # Store bias check in candidate document
        timestamp = datetime.now().isoformat()
        bias_check_record = {
            "timestamp": timestamp,
            "bias_detected": bias_result.get("bias_detected", False),
            "bias_flags": bias_result.get("bias_flags", []),
            "analysis": bias_result.get("analysis", ""),
            "recommendations": bias_result.get("recommendations", [])
        }
        
        # Update candidate document
        logger.info("💾 Saving bias check results...")
        from pymongo import UpdateOne
        db_client = db.get_client()
        database = db.get_database()
        candidates_collection = database["candidates"]
        
        candidates_collection.update_one(
            {"_id": candidate_id},
            {
                "$push": {"bias_checks": bias_check_record},
                "$set": {"last_bias_check": timestamp}
            }
        )
        
        logger.info("✓ Bias check results saved to database")
        
        logger.info("="*80)
        logger.info(f"✅ Bias check complete for candidate: {candidate_id}")
        logger.info("="*80)
        
        return BiasCheckResponse(
            candidate_id=candidate_id,
            bias_detected=bias_result.get("bias_detected", False),
            bias_flags=bias_result.get("bias_flags", []),
            analysis=bias_result.get("analysis", ""),
            recommendations=bias_result.get("recommendations", []),
            timestamp=timestamp,
            message=f"Bias check completed. {'Potential biases detected.' if bias_result.get('bias_detected') else 'No significant biases detected.'}"
        )
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error during bias check: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to perform bias check: {str(e)}")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Smart Resume Screener API server...")
    logger.info("📍 Server will be available at http://localhost:8000")
    logger.info("📖 API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
