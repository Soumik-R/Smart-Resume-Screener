from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from parse_resume import extract_resume_data
from parse_job_desc import extract_jd_data
from database import store_resume, Resume, Session
from match_resume import compute_final_score
from visualize import create_radar_chart
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Mount static directory to serve radar charts
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), job_desc: str = Form(...)):
    with open("temp.pdf", "wb") as f:
        f.write(await file.read())
    data = extract_resume_data("temp.pdf")
    data['name'] = "Candidate"
    store_resume(data)
    jd_data = extract_jd_data(job_desc)
    result = compute_final_score(data, jd_data)
    create_radar_chart(data['name'], result)
    result['radar_chart'] = f"/static/{data['name'].replace(' ', '_')}_radar_chart.png"
    return result

@app.get("/shortlisted")
async def get_shortlisted(job_desc: str):
    session = Session()
    resumes = session.query(Resume).all()
    shortlisted = []
    jd_data = extract_jd_data(job_desc)
    for resume in resumes:
        data = {
            "name": resume.name,
            "hard_skills": eval(resume.hard_skills),
            "education": eval(resume.education),
            "projects": eval(resume.projects),
            "soft_skills": eval(resume.soft_skills),
            "growth_verbs": eval(resume.growth_verbs),
            "certifications": eval(resume.certifications),
            "raw_text": resume.raw_text
        }
        result = compute_final_score(data, jd_data)
        if result["status"] in ["Shortlist", "On-hold"]:
            create_radar_chart(data['name'], result)
            result['radar_chart'] = f"/static/{data['name'].replace(' ', '_')}_radar_chart.png"
            shortlisted.append({
                "name": resume.name,
                **result
            })
    session.close()
    return shortlisted

@app.get("/static/{filename}")
async def get_image(filename: str):
    return FileResponse(f"static/{filename}")