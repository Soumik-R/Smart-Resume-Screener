# Smart Resume Screener

A clean, simple resume screening system that computes surface fit scores between resumes and job descriptions.

## Features
- **Resume Parsing**: Extract skills, education, and experience from PDF resumes
- **Job Description Analysis**: Parse job requirements and skills
- **Surface Fit Scoring**: Compute match scores (0-100) between resumes and jobs
- **REST API**: Upload resumes and get scores via FastAPI
- **Database Storage**: SQLite database for resume management

## Files Structure
```
├── main.py              # Main application - test surface fit
├── api.py               # FastAPI REST API
├── parse_resume.py      # Resume PDF parsing
├── parse_job_desc.py    # Job description parsing  
├── match_resume.py      # Surface fit scoring algorithm
├── database.py          # SQLite database operations
├── test_sfs.py          # Simple test for surface fit
└── sample_resume.pdf    # Sample resume for testing
```

## Quick Start

### Test Surface Fit Score
```bash
python main.py
# Output: Surface Fit Score: 65.0
```

### Run API Server
```bash
python api.py
# Or: uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

### Run Tests
```bash
python test_sfs.py
# Output: Surface Fit Score: 65.0, Valid score: True
```

## API Endpoints

- `GET /` - Health check
- `POST /upload` - Upload resume and job description, get surface fit score
- `GET /shortlisted` - Get candidates above threshold score

## Surface Fit Algorithm
- **Skills Match**: 70% weight - keyword matching between resume and job requirements
- **Education Match**: 30% weight - degree/field matching  
- **Score Range**: 0-100 (higher = better match)

## Dependencies
- FastAPI - REST API framework
- SQLAlchemy - Database ORM
- spaCy - Natural language processing
- PyPDF2 - PDF text extraction