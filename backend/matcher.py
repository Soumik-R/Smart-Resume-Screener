"""
LLM-based resume matching and scoring module
Uses OpenAI GPT-4o API for intelligent, semantic resume-JD matching
with multi-category scoring, personalized feedback, and batch processing.
"""
import os
import logging
from openai import OpenAI
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Initialize OpenAI client with GPT-4o
client = OpenAI(api_key=api_key)

# Model configuration
GPT_MODEL = "gpt-4o"  # GPT-4o for superior semantic analysis and nuanced reasoning
GPT_TEMPERATURE = 0.3  # Lower temperature for more consistent, recruiter-like scoring
GPT_MAX_TOKENS = 2000  # Sufficient for detailed analysis

# ============================================================================
# SCORING WEIGHTS CONFIGURATION
# ============================================================================
# These weights determine how much each category contributes to the final score
# Total should sum to 1.0 (100%)
# 
# Rationale:
# - Skills (40%): Most critical - direct match to job requirements
# - Experience (25%): Second most important - years and relevance
# - Education & Projects (15%): Shows foundation and practical application
# - Achievements (10%): Demonstrates excellence and impact
# - Extracurricular (10%): Shows soft skills and leadership

DEFAULT_WEIGHTS = {
    'skills': 0.40,           # 40% - Technical/functional skills match
    'experience': 0.25,       # 25% - Work experience (years + relevance)
    'education_projects': 0.15,  # 15% - Education level + project quality
    'achievements': 0.10,     # 10% - Awards, publications, certifications
    'extracurricular': 0.10   # 10% - Leadership, volunteering, clubs
}

# Validate weights sum to 1.0
assert abs(sum(DEFAULT_WEIGHTS.values()) - 1.0) < 0.01, "Weights must sum to 1.0"

logger.info(f"Matcher initialized with GPT model: {GPT_MODEL}")
logger.info(f"Scoring weights: {DEFAULT_WEIGHTS}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_weights(weights: Dict[str, float]) -> bool:
    """
    Validate that custom weights are properly formatted
    
    Args:
        weights: Dictionary of category weights
        
    Returns:
        True if valid, raises ValueError if invalid
        
    Raises:
        ValueError: If weights are invalid
    """
    required_keys = set(DEFAULT_WEIGHTS.keys())
    provided_keys = set(weights.keys())
    
    # Check all required keys are present
    if required_keys != provided_keys:
        missing = required_keys - provided_keys
        extra = provided_keys - required_keys
        error_msg = []
        if missing:
            error_msg.append(f"Missing keys: {missing}")
        if extra:
            error_msg.append(f"Extra keys: {extra}")
        raise ValueError(f"Invalid weight keys. {' '.join(error_msg)}")
    
    # Check all values are numbers between 0 and 1
    for key, value in weights.items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"Weight for '{key}' must be a number, got {type(value)}")
        if not (0 <= value <= 1):
            raise ValueError(f"Weight for '{key}' must be between 0 and 1, got {value}")
    
    # Check weights sum to approximately 1.0 (allow small floating point errors)
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, got {total:.4f}")
    
    return True


def aggregate_scores(
    category_scores: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Aggregate category scores into an overall score using weighted average
    
    Formula: overall_score = sum(category_score * weight) for each category
    Result is on a 1-10 scale
    
    Args:
        category_scores: Dictionary mapping category names to scores (1-10 scale)
        weights: Optional custom weights (defaults to DEFAULT_WEIGHTS)
        
    Returns:
        Overall weighted score (1-10 scale)
        
    Example:
        category_scores = {
            'skills': 8.5,
            'experience': 7.0,
            'education_projects': 9.0,
            'achievements': 6.5,
            'extracurricular': 7.5
        }
        weights = DEFAULT_WEIGHTS
        # Result: 8.5*0.40 + 7.0*0.25 + 9.0*0.15 + 6.5*0.10 + 7.5*0.10 = 7.95
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    else:
        validate_weights(weights)
    
    # Calculate weighted sum
    overall_score = 0.0
    for category, weight in weights.items():
        score = category_scores.get(category, 0.0)
        # Ensure score is in valid range (1-10)
        score = max(1.0, min(10.0, score))
        overall_score += score * weight
    
    # Round to 1 decimal place
    overall_score = round(overall_score, 1)
    
    # Ensure final score is in range [1.0, 10.0]
    return max(1.0, min(10.0, overall_score))


def get_weights(custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Get scoring weights, using custom weights if provided, otherwise defaults
    
    Args:
        custom_weights: Optional custom weight configuration
        
    Returns:
        Validated weight dictionary
    """
    if custom_weights is None:
        return DEFAULT_WEIGHTS.copy()
    
    validate_weights(custom_weights)
    return custom_weights.copy()


# ============================================================================
# MAIN SCORING FUNCTIONS
# ============================================================================

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
