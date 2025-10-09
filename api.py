from fastapi import FastAPI, UploadFile, File, Form
from parse_resume import extract_resume_data
from database import store_resume, Resume, Session
from match_resume import compute_match

app = FastAPI()

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), job_desc: str = Form(...)):
    with open("temp.pdf", "wb") as f:
        f.write(await file.read())
    data = extract_resume_data("temp.pdf")
    data['name'] = "Candidate"  # Placeholder name
    store_resume(data)
    match = compute_match(data, job_desc)
    return {"match": match}

@app.get("/shortlisted")
async def get_shortlisted(job_desc: str):
    session = Session()
    resumes = session.query(Resume).all()
    shortlisted = []
    for resume in resumes:
        data = {
            "skills": eval(resume.skills),
            "experience": eval(resume.experience),
            "education": eval(resume.education)
        }
        match = compute_match(data, job_desc)
        score = float(match.split("Score: ")[1].split("/")[0])
        if score > 7:
            shortlisted.append({"name": resume.name, "match": match})
    session.close()
    return shortlisted

@app.get("/")
async def root():
    return {"message": "Smart Resume Screener API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)