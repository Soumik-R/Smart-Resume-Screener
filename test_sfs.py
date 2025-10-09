"""Simple test for Surface Fit Score functionality"""

from parse_resume import extract_resume_data
from parse_job_desc import extract_jd_data  
from match_resume import compute_surface_fit

def test_surface_fit():
    """Test surface fit between resume and job description"""
    
    # Parse sample resume
    resume_data = extract_resume_data("sample_resume.pdf")
    
    # Parse job description
    job_desc = "Seeking Python developer with 2+ years experience, B.Tech in CSE, SQL skills."
    jd_data = extract_jd_data(job_desc)
    
    # Compute surface fit score
    score = compute_surface_fit(resume_data, jd_data)
    
    print(f"Surface Fit Score: {score}")
    print(f"Valid score: {0 <= score <= 100}")
    
    return score

if __name__ == "__main__":
    test_surface_fit()