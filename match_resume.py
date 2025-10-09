import re

def compute_match(resume_data, job_description):
    """
    Compute match score between resume and job description using local algorithm.
    Returns a score out of 10 with justification.
    """
    
    # Combine all resume text
    resume_text = " ".join([
        " ".join(resume_data.get('skills', [])),
        " ".join(resume_data.get('experience', [])),
        " ".join(resume_data.get('education', []))
    ]).lower()
    
    job_desc_lower = job_description.lower()
    
    # Extract key terms from job description
    # Common technical terms and skills
    technical_terms = re.findall(r'\b(?:python|java|javascript|sql|mysql|mongodb|git|aws|docker|machine learning|ai|html|css|react|node|api|rest|database|web|software|development|programming|coding|algorithm|data|analysis|visualization|cloud|backend|frontend|fullstack)\b', job_desc_lower)
    
    # Extract experience requirements
    experience_match = re.findall(r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', job_desc_lower)
    
    # Calculate matches
    skill_matches = 0
    total_skills = len(technical_terms)
    
    for term in technical_terms:
        if term in resume_text:
            skill_matches += 1
    
    # Calculate base score
    if total_skills > 0:
        skill_score = (skill_matches / total_skills) * 7  # Skills contribute up to 7 points
    else:
        skill_score = 5  # Default score if no specific skills mentioned
    
    # Experience bonus
    experience_bonus = 0
    if experience_match:
        required_years = int(experience_match[0])
        if required_years == 0:  # Entry level
            experience_bonus = 2
        elif any(word in resume_text for word in ['intern', 'project', 'experience', 'developer', 'engineer']):
            experience_bonus = 1.5
        else:
            experience_bonus = 1
    else:
        experience_bonus = 1
    
    # Education bonus
    education_bonus = 0
    if any(word in resume_text for word in ['b.tech', 'bachelor', 'master', 'degree', 'computer science', 'engineering']):
        education_bonus = 0.5
    
    # Calculate final score
    final_score = min(10, skill_score + experience_bonus + education_bonus)
    
    # Generate justification
    justification_points = []
    
    if skill_matches > 0:
        matched_skills = [term for term in technical_terms if term in resume_text]
        justification_points.append(f"Skills match: Found {skill_matches}/{total_skills} required skills ({', '.join(matched_skills[:5])})")
    else:
        justification_points.append("Limited technical skills match found in resume")
    
    if experience_bonus >= 1.5:
        justification_points.append("Good relevant experience indicated")
    elif experience_bonus >= 1:
        justification_points.append("Some relevant experience found")
    else:
        justification_points.append("Limited experience information available")
    
    if education_bonus > 0:
        justification_points.append("Relevant educational background")
    
    # Format output
    result = f"Score: {final_score:.1f}/10\n"
    result += "Justification:\n"
    for point in justification_points:
        result += f"- {point}\n"
    
    return result

def compute_surface_fit(resume_data, jd_data):
    """Compute surface fit score between resume and job description (0-100)"""
    
    # Get skills
    resume_skills = resume_data.get('skills', [])
    if isinstance(resume_skills, str):
        resume_skills = [resume_skills]
    
    jd_skills = jd_data.get('required_skills', [])
    
    # Calculate skill match percentage
    skill_matches = 0
    if jd_skills:
        resume_text = ' '.join(resume_skills).lower()
        for jd_skill in jd_skills:
            if jd_skill.lower() in resume_text:
                skill_matches += 1
        skill_score = skill_matches / len(jd_skills)
    else:
        skill_score = 0.5
    
    # Calculate education match percentage
    resume_edu = resume_data.get('education', [])
    jd_edu = jd_data.get('required_education', [])
    
    if jd_edu and resume_edu:
        edu_matches = 0
        resume_edu_text = ' '.join(str(edu).lower() for edu in resume_edu)
        
        for req_edu in jd_edu:
            degree = req_edu.get('degree', '').lower()
            field = req_edu.get('field', '').lower()
            if degree in resume_edu_text or field in resume_edu_text:
                edu_matches += 1
        
        edu_score = edu_matches / len(jd_edu) if jd_edu else 0.5
    else:
        edu_score = 0.5
    
    # Weighted final score (70% skills, 30% education)
    final_score = (0.7 * skill_score + 0.3 * edu_score) * 100
    return round(final_score, 2)