"""Smart Resume Screener - Main Application"""

from parse_resume import extract_resume_data
from parse_job_desc import extract_jd_data
from database import store_resume
from match_resume import compute_surface_fit

def main():
    # Extract resume data
    data = extract_resume_data("sample_resume.pdf")
    data['name'] = "Soumik Roy"
    
    # Store in database
    store_resume(data)
    
    # Parse job description
    job_desc = "Seeking Python developer with 2+ years experience, B.Tech in CSE, SQL skills."
    jd_data = extract_jd_data(job_desc)
    
    # Compute and display surface fit score
    score = compute_surface_fit(data, jd_data)
    print(f"Surface Fit Score: {score}")

if __name__ == "__main__":
    main()