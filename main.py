from parse_resume import extract_resume_data
from database import store_resume
from match_resume import compute_match

data = extract_resume_data("sample_resume.pdf")
data['name'] = "Soumik Roy"
store_resume(data)
job_desc = "Seeking Python developer with 0+ years experience and SQL skills."
match = compute_match(data, job_desc)
print(match)