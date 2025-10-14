"""
LLM-based resume matching and scoring module
Uses OpenAI API to intelligently match resumes to job descriptions
"""
import os
from openai import OpenAI
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def calculate_match_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use LLM to calculate a match score between resume and job description
    
    Args:
        resume_data: Parsed resume data
        jd_data: Parsed job description data
        
    Returns:
        Dictionary containing match score and analysis
    """
    prompt = f"""
You are an expert HR recruiter. Analyze the following resume against the job description and provide:
1. A match score from 0-100 (where 100 is a perfect match)
2. Key strengths of the candidate
3. Missing skills or gaps
4. A brief recommendation

Resume:
Name: {resume_data.get('name', 'N/A')}
Skills: {', '.join(resume_data.get('skills', []))}
Experience Summary: {resume_data.get('raw_text', '')[:500]}...

Job Description Requirements:
Required Skills: {', '.join(jd_data.get('required_skills', []))}
Full JD: {jd_data.get('raw_text', '')[:500]}...

Provide your analysis in the following format:
SCORE: [number]
STRENGTHS: [bullet points]
GAPS: [bullet points]
RECOMMENDATION: [brief recommendation]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert HR recruiter and talent assessor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        analysis = response.choices[0].message.content
        
        # Parse the response
        score = 0
        if "SCORE:" in analysis:
            score_line = analysis.split("SCORE:")[1].split("\n")[0].strip()
            try:
                score = int(''.join(filter(str.isdigit, score_line)))
            except ValueError:
                score = 0
        
        return {
            "match_score": score,
            "analysis": analysis,
            "candidate_name": resume_data.get('name', 'Unknown'),
            "candidate_email": resume_data.get('email', ''),
            "candidate_skills": resume_data.get('skills', [])
        }
        
    except Exception as e:
        raise RuntimeError(f"Error calling OpenAI API: {str(e)}")


def batch_score_candidates(resumes: List[Dict[str, Any]], jd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Score multiple candidates against a job description
    
    Args:
        resumes: List of parsed resume data
        jd_data: Parsed job description data
        
    Returns:
        List of scored candidates, sorted by match score (highest first)
    """
    scored_candidates = []
    
    for resume in resumes:
        try:
            result = calculate_match_score(resume, jd_data)
            scored_candidates.append(result)
        except Exception as e:
            print(f"Error scoring candidate {resume.get('name', 'Unknown')}: {str(e)}")
            continue
    
    # Sort by match score (descending)
    scored_candidates.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    return scored_candidates
