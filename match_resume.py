import numpy as np
from scipy.spatial.distance import cosine
from openai import OpenAI
from dotenv import load_dotenv
import os
from parse_job_desc import extract_jd_data

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_experience_years(text):
    """Extract years of experience from resume text"""
    import re
    if not text:
        return 0
    
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*[:]\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*year\s*(?:of\s*)?experience'
    ]
    
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            try:
                years = int(match)
                max_years = max(max_years, years)
            except ValueError:
                continue
    
    return max_years

def extract_required_experience(text):
    """Extract required years of experience from job description"""
    import re
    if not text:
        return 0
    
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience\s*required',
        r'minimum\s*(?:of\s*)?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'require[sd]?\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*year\s*minimum'
    ]
    
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            try:
                years = int(match)
                max_years = max(max_years, years)
            except ValueError:
                continue
    
    return max_years

def get_embedding(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return np.array(response.data[0].embedding)
    except Exception:
        # Fallback: return zero vector if embeddings fail
        return np.zeros(1536)  # text-embedding-ada-002 dimension

def compute_surface_fit(resume_data, jd_data):
    try:
        # 1. Skills matching (50% of surface fit)
        resume_skills_str = " ".join(resume_data['hard_skills'])
        jd_skills_str = " ".join(jd_data['required_skills'])
        if not resume_skills_str or not jd_skills_str:
            skill_overlap = 0
        else:
            resume_emb = get_embedding(resume_skills_str)
            jd_emb = get_embedding(jd_skills_str)
            if np.sum(resume_emb) != 0 and np.sum(jd_emb) != 0:
                skill_overlap = 1 - cosine(resume_emb, jd_emb)
            else:
                raise Exception("Zero embeddings detected")

        # 2. Education matching (25% of surface fit)
        edu_match = 0
        if jd_data['required_education']:
            jd_edu_strs = [f"{edu['degree']} {edu['field']}" for edu in jd_data['required_education']]
            resume_edu_strs = [f"{edu['degree']} {edu['field']}" for edu in resume_data['education']]
            similarities = []
            for r_edu in resume_edu_strs:
                for j_edu in jd_edu_strs:
                    r_emb = get_embedding(r_edu)
                    j_emb = get_embedding(j_edu)
                    if np.sum(r_emb) != 0 and np.sum(j_emb) != 0:
                        similarities.append(1 - cosine(r_emb, j_emb))
                    else:
                        raise Exception("Zero embeddings detected")
            edu_match = np.mean(similarities) if similarities else 0

        # 3. Experience matching (25% of surface fit)
        resume_experience = extract_experience_years(resume_data.get('raw_text', ''))
        required_experience = extract_required_experience(jd_data.get('job_description', ''))
        
        exp_match = 0
        if required_experience > 0:
            if resume_experience >= required_experience:
                exp_match = 1.0  # Perfect match
            elif resume_experience >= (required_experience * 0.8):
                exp_match = 0.8  # Good match (80% of required)
            else:
                exp_match = resume_experience / required_experience  # Proportional
        else:
            exp_match = 0.5  # No requirement specified, give neutral score

        # Combined Surface Fit Score: Skills(50%) + Education(25%) + Experience(25%)
        sfs = (0.50 * skill_overlap + 0.25 * edu_match + 0.25 * exp_match) * 100
        
        justifications = [
            f"Skills overlap: {skill_overlap * 100:.1f}%",
            f"Education match: {edu_match * 100:.1f}%", 
            f"Experience match: {exp_match * 100:.1f}% ({resume_experience} vs {required_experience} years required)"
        ]
        
        return round(sfs, 2), justifications
        
    except Exception:
        # Fallback to basic matching
        resume_skills = resume_data.get('hard_skills', resume_data.get('skills', []))
        jd_skills = jd_data.get('required_skills', [])
        
        skill_matches = 0
        if jd_skills and resume_skills:
            resume_text = ' '.join(str(skill) for skill in resume_skills).lower()
            for jd_skill in jd_skills:
                if jd_skill.lower() in resume_text:
                    skill_matches += 1
            skill_score = skill_matches / len(jd_skills)
        else:
            skill_score = 0.0

        # Fallback experience matching
        resume_experience = extract_experience_years(resume_data.get('raw_text', ''))
        required_experience = extract_required_experience(jd_data.get('job_description', ''))
        exp_score = min(resume_experience / max(required_experience, 1), 1.0) if required_experience > 0 else 0.5
        
        # Fallback: Skills(70%) + Experience(30%)
        sfs = round((0.7 * skill_score + 0.3 * exp_score) * 100, 2)
        return sfs, [f"Fallback scoring: {skill_matches} skills matched, {resume_experience} years experience"]

def compute_depth_fit(resume_data, jd_data):
    try:
        project_summaries = [f"{p['description']} {p['problem']} {p['impact']}" for p in resume_data['projects']]
        task_summaries = jd_data['tasks']
        similarities = []
        for project in project_summaries:
            for task in task_summaries:
                if project and task:
                    p_emb = get_embedding(project)
                    t_emb = get_embedding(task)
                    if np.sum(p_emb) != 0 and np.sum(t_emb) != 0:
                        similarities.append(1 - cosine(p_emb, t_emb))
                    else:
                        raise Exception("Zero embeddings detected")
        dfs = np.mean(similarities) * 100 if similarities else 0
        return round(dfs, 2), ["Average project-task similarity: {:.2f}".format(dfs)]
    except Exception:
        # Fallback to simple text matching
        project_texts = []
        for p in resume_data.get('projects', []):
            if isinstance(p, dict):
                project_texts.append(p.get('description', ''))
            else:
                project_texts.append(str(p))
        
        task_texts = jd_data.get('tasks', [])
        
        if not project_texts or not task_texts:
            return 0.0, ["No projects or tasks available for comparison"]
            
        matches = 0
        total_comparisons = 0
        for project in project_texts:
            if project.strip():
                for task in task_texts:
                    if task.strip():
                        total_comparisons += 1
                        project_words = set(project.lower().split())
                        task_words = set(task.lower().split())
                        meaningful_matches = project_words & task_words
                        meaningful_matches = {word for word in meaningful_matches if len(word) > 2}
                        if meaningful_matches:
                            matches += 1
        
        dfs = round((matches / total_comparisons) * 100 if total_comparisons > 0 else 0, 2)
        return dfs, [f"Fallback scoring: {matches} meaningful matches out of {total_comparisons} comparisons"]

def compute_growth_potential(resume_data):
    try:
        growth_input = f"""
        Growth verbs: {resume_data['growth_verbs']}
        Certifications: {resume_data['certifications']}
        Skills diversity: {len(resume_data['hard_skills'])} unique skills
        """
        prompt = f"""
        Based on the following resume data, rate the candidate's learning adaptability from 1–10.
        Focus on signs of continuous learning, certifications, and skill diversity.
        Input: {growth_input}
        Output format: Score: X/10\nJustification: - point 1\n- point 2
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content
        score = float(response_text.split("Score: ")[1].split("/")[0])
        gps = (score / 10) * 100
        justification = response_text.split("Justification:")[1].strip().split("\n")
        return round(gps, 2), justification
    except Exception:
        # Fallback scoring based on available data
        growth_score = 0
        
        # Score growth verbs (0-30 points)
        growth_verbs_count = len(resume_data.get('growth_verbs', []))
        growth_score += min(growth_verbs_count * 10, 30)
        
        # Score certifications (0-40 points)
        cert_count = len(resume_data.get('certifications', []))
        growth_score += min(cert_count * 20, 40)
        
        # Score skill diversity (0-30 points)
        skill_diversity = len(resume_data.get('hard_skills', []))
        if skill_diversity > 20:
            growth_score += 30
        elif skill_diversity > 10:
            growth_score += 20
        elif skill_diversity > 5:
            growth_score += 10
        
        gps = min(growth_score, 100)
        return gps, [f"Fallback scoring: {growth_verbs_count} growth verbs, {cert_count} certifications, {skill_diversity} skills"]

def compute_cultural_fit(resume_data, jd_data):
    try:
        culture_input = f"""
        Candidate soft skills: {resume_data['soft_skills']}
        Resume text: {resume_data['raw_text'][:1000]}
        Company values: {jd_data['values']}
        """
        prompt = f"""
        Compare the candidate's soft skills and tone of resume writing with the company's values.
        Rate cultural alignment from 1–10 and justify briefly.
        Input: {culture_input}
        Output format: Score: X/10\nJustification: - point 1\n- point 2
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content
        score = float(response_text.split("Score: ")[1].split("/")[0])
        cfs = (score / 10) * 100
        justification = response_text.split("Justification:")[1].strip().split("\n")
        return round(cfs, 2), justification
    except Exception:
        # Fallback scoring based on available data
        culture_score = 0
        
        # Score based on soft skills alignment (0-60 points)
        candidate_soft_skills = [skill.lower() for skill in resume_data.get('soft_skills', [])]
        company_values = [value.lower() for value in jd_data.get('values', [])]
        
        matches = 0
        if company_values and candidate_soft_skills:
            for value in company_values:
                for skill in candidate_soft_skills:
                    if value in skill or skill in value:
                        matches += 1
            culture_score = min((matches / len(company_values)) * 60, 60)
        
        # Base score for having soft skills (0-40 points)
        if candidate_soft_skills:
            culture_score += min(len(candidate_soft_skills) * 10, 40)
        
        cfs = min(culture_score, 100)
        return cfs, [f"Fallback scoring: {matches} value matches found, {len(candidate_soft_skills)} soft skills present"]

def compute_final_score(resume_data, jd_data):
    sfs, sfs_just = compute_surface_fit(resume_data, jd_data)
    dfs, dfs_just = compute_depth_fit(resume_data, jd_data)
    gps, gps_just = compute_growth_potential(resume_data)
    cfs, cfs_just = compute_cultural_fit(resume_data, jd_data)

    final_score = 0.60 * sfs + 0.25 * dfs + 0.10 * gps + 0.05 * cfs
    final_score = round(final_score, 2)

    status = "Reject"
    if final_score >= 70:
        status = "Shortlist"
    elif 60 <= final_score < 70:
        status = "On-hold"

    justification = (
        ["Surface Fit:"] + [f"- {j}" for j in sfs_just] +
        ["Depth Fit:"] + [f"- {j}" for j in dfs_just] +
        ["Growth Potential:"] + [f"- {j}" for j in gps_just] +
        ["Cultural Fit:"] + [f"- {j}" for j in cfs_just]
    )

    return {
        "surface_fit": sfs,
        "depth_fit": dfs,
        "growth_potential": gps,
        "cultural_fit": cfs,
        "final_score": final_score,
        "status": status,
        "justification": justification,
        "weights": "Surface Fit: 60% (Skills + Education + Experience), Depth Fit: 25%, Growth Potential: 10%, Cultural Fit: 5%"
    }