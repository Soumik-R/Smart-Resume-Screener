"""Smart Resume Screener API"""

from fastapi import FastAPI, UploadFile, File, Form
from parse_resume import extract_resume_data
from parse_job_desc import extract_jd_data
from match_resume import compute_surface_fit
from database import store_resume, Resume, Session

app = FastAPI(title="Smart Resume Screener", version="1.0.0")

@app.get("/")
async def root():
    """API health check"""
    return {"message": "Smart Resume Screener API", "status": "running"}

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), job_desc: str = Form(...)):
    """Upload resume and get surface fit score"""
    # Save uploaded file
    with open("temp.pdf", "wb") as f:
        f.write(await file.read())
    
    # Parse resume and job description
    resume_data = extract_resume_data("temp.pdf")
    resume_data['name'] = "Candidate"
    jd_data = extract_jd_data(job_desc)
    
    # Store resume and compute score
    store_resume(resume_data)
    score = compute_surface_fit(resume_data, jd_data)
    
    return {"surface_fit": score}

@app.get("/shortlisted")
async def get_shortlisted(job_desc: str, threshold: float = 70.0):
    """Get shortlisted candidates based on surface fit threshold"""
    session = Session()
    try:
        resumes = session.query(Resume).all()
        jd_data = extract_jd_data(job_desc)
        shortlisted = []
        
        for resume in resumes:
            resume_data = {
                "skills": eval(resume.skills) if resume.skills else [],
                "education": eval(resume.education) if resume.education else []
            }
            score = compute_surface_fit(resume_data, jd_data)
            
            if score >= threshold:
                shortlisted.append({
                    "name": resume.name,
                    "surface_fit": score
                })
        
        return {"shortlisted": shortlisted, "threshold": threshold}
    finally:
        session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)