"""
FastAPI Backend for Smart Resume Screener
Provides REST API endpoints for resume parsing, matching, and database operations
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, List
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Import local modules
import db
from matcher import extract_jd_requirements, match_resume_to_jd, score_batch

# Load environment variables
load_dotenv()

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
    candidate_ids: List[str]

class MatchResult(BaseModel):
    id: str
    overall: float
    justifications: dict
    feedback: str
    strengths: List[str]
    improvement_areas: List[str]

class MatchResponse(BaseModel):
    jd_id: str
    matched_candidates: List[MatchResult]
    total_candidates: int
    message: str

class ShortlistCandidate(BaseModel):
    candidate_id: str
    name: str
    overall_score: float
    skills_score: float
    experience_score: float
    education_projects_score: float
    achievements_score: float
    extracurricular_score: float
    feedback: str
    strengths: List[str]
    improvement_areas: List[str]
    matched_at: str

class ShortlistResponse(BaseModel):
    jd_id: str
    candidates: List[ShortlistCandidate]
    total_count: int
    page: int
    page_size: int
    filters_applied: dict
    message: str



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
    file: UploadFile = File(..., description="Resume file (PDF or TXT)")
):
    """
    Upload and parse a resume file
    
    - Accepts PDF or TXT files
    - Extracts structured data (name, skills, experience, etc.)
    - Anonymizes for bias-free processing
    - Saves to database
    - Returns candidate ID and parsed data summary
    """
    logger.info("="*80)
    logger.info(f"📤 Received resume upload: {file.filename}")
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = file.filename.lower().split('.')[-1]
        if file_ext not in ['pdf', 'txt', 'text']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_ext}. Use PDF or TXT files."
            )
        
        # Read and parse file
        file_content = await file.read()
        logger.info(f"✓ Read {len(file_content)} bytes from file")
        
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
    file: Optional[UploadFile] = File(None, description="Job description file (optional)"),
    jd_text: Optional[str] = Form(None, description="Job description text (optional)")
):
    """
    Upload and parse a job description
    
    - Accepts JD as file (PDF/TXT) or text form data
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
            file_content = await file.read()
            
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


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Smart Resume Screener API server...")
    logger.info("📍 Server will be available at http://localhost:8000")
    logger.info("📖 API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
