import pdfplumber

def extract_resume_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""  # Handle cases with no text
    
    data = {
        "skills": [],
        "experience": [],
        "education": []
    }
    lines = text.split("\n")
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "skills" in line.lower():
            current_section = "skills"
        elif "experience" in line.lower() or "work" in line.lower():
            current_section = "experience"
        elif "education" in line.lower():
            current_section = "education"
        elif current_section:
            data[current_section].append(line)
    
    return data
