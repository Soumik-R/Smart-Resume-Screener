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
# PROMPT ENGINEERING
# ============================================================================

def build_scoring_prompt(
    resume_json: str,
    jd_text: str,
    weights: Optional[Dict[str, float]] = None,
    role_context: str = "general"
) -> str:
    """
    Build a comprehensive LLM prompt for resume-JD matching
    
    This prompt is designed to extract nuanced, recruiter-level analysis with:
    - Multi-category scoring (skills, experience, education, achievements, extracurricular)
    - Semantic skill matching (e.g., "data analysis" matches "SQL")
    - Context-aware evaluation (junior vs senior roles)
    - Bias avoidance (demographics ignored)
    - Structured JSON output
    
    Args:
        resume_json: Anonymized resume data in JSON format
        jd_text: Job description text
        weights: Scoring weights (defaults to DEFAULT_WEIGHTS)
        role_context: Context hint - "junior", "senior", "mid-level", or "general"
        
    Returns:
        Formatted prompt string for GPT-4o
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    else:
        validate_weights(weights)
    
    # Format weights for display
    weights_display = "\n".join([
        f"  - {category.replace('_', ' ').title()}: {weight*100:.0f}%"
        for category, weight in weights.items()
    ])
    
    # Context-specific instructions
    context_instructions = {
        "junior": """
CONTEXT: This is a JUNIOR-LEVEL role (0-2 years experience).
- Emphasize educational background and academic projects over work experience
- Internships are highly valuable - count each 3-6 month internship as 0.5 years equivalent
- Look for learning agility, foundational skills, and growth potential
- Projects and coursework demonstrate practical application of knowledge
- Extracurricular activities show soft skills, leadership potential, and cultural fit
""",
        "senior": """
CONTEXT: This is a SENIOR-LEVEL role (5+ years experience).
- Prioritize depth of experience, leadership, and strategic impact
- Look for progressive career growth and increasing responsibility
- Achievements should demonstrate measurable business impact
- Technical depth matters more than breadth for specialized roles
- Management/mentorship experience is highly valuable
""",
        "mid-level": """
CONTEXT: This is a MID-LEVEL role (2-5 years experience).
- Balance between foundational skills and proven track record
- Look for consistency in career progression
- Projects should show increasing complexity and ownership
- Both technical skills and soft skills are important
- Some leadership or mentorship experience is a plus
""",
        "general": """
CONTEXT: General role assessment.
- Evaluate the candidate holistically across all categories
- Consider both technical competencies and soft skills
- Look for alignment between career trajectory and role requirements
"""
    }
    
    prompt = f"""You are an EXPERT HR RECRUITER with 10+ years of experience in tech hiring and talent assessment. You have successfully placed hundreds of candidates and have a deep understanding of what makes a great fit for technical roles.

# YOUR MISSION
Analyze the provided anonymized resume data against the job description below. Your goal is to provide a comprehensive, fair, and insightful evaluation that helps hiring managers make informed decisions.

# CRITICAL INSTRUCTIONS - READ CAREFULLY

## 1. BIAS AVOIDANCE (MANDATORY)
- The resume data is ANONYMIZED - personal identifiers have been removed
- Do NOT make assumptions about demographics (age, gender, ethnicity, nationality, etc.)
- Focus ONLY on skills, experience, education, and demonstrated capabilities
- Ignore any potential indicators of protected characteristics
- Evaluate purely on job-relevant qualifications and merit

## 2. SEMANTIC UNDERSTANDING
Use your advanced language understanding to recognize:
- Equivalent skills: "data analysis" ≈ "SQL", "analytics", "statistical analysis"
- Related technologies: "React" ≈ "React.js", "ReactJS", "frontend development"
- Similar roles: "Software Engineer" ≈ "Developer", "Programmer", "SDE"
- Domain knowledge: "machine learning" includes "neural networks", "deep learning", "AI"
- Transferable skills: Project management, problem-solving, communication

## 3. EXPERIENCE CALCULATION RULES
- Count ALL relevant work experience (full-time, part-time, contract)
- INTERNSHIPS: Count each 3-6 month internship as 0.5 years equivalent
- Shorter internships (<3 months): Count as 0.25 years
- Longer internships (>6 months): Count full duration
- FRESHERS (0 years): This is NOT a negative - evaluate based on projects and potential
- Overlapping roles: Count only the total time span, not cumulative
- Career gaps: Do not penalize if candidate has maintained skills through projects

## 4. CONTEXT AWARENESS
{context_instructions.get(role_context, context_instructions["general"])}

## 5. CREATIVITY & INSIGHT
Go beyond surface-level matching:
- Identify TRANSFERABLE SKILLS from extracurricular activities
  Example: "Led university debate team" → Communication, leadership, critical thinking
  Example: "Organized coding bootcamp" → Project management, community building
- Recognize POTENTIAL from projects and self-learning
- Spot UNIQUE STRENGTHS that aren't explicitly in the JD but add value
- Suggest how candidate's background might bring FRESH PERSPECTIVES

# JOB DESCRIPTION
{jd_text}

# CANDIDATE RESUME DATA (Anonymized)
{resume_json}

# SCORING METHODOLOGY

You must score the candidate on a **1-10 scale** for FIVE categories:

## Category 1: SKILLS (Technical & Functional)
- Extract required skills from JD (programming languages, tools, frameworks, methodologies)
- Match candidate's skills semantically (exact matches AND equivalent skills)
- Score based on:
  - Coverage: What % of required skills are present? (40% weight)
  - Proficiency level: Evidence of depth vs surface knowledge (30% weight)
  - Bonus skills: Nice-to-have or adjacent skills (20% weight)
  - Skill recency: Recently used vs outdated (10% weight)
- 10 = Perfect match with all required + bonus skills
- 1 = Minimal skill overlap

## Category 2: EXPERIENCE (Work History)
- Calculate total relevant years using the rules above
- Evaluate:
  - Years of experience vs JD requirement (40% weight)
  - Relevance of past roles to target role (35% weight)
  - Career progression and growth (15% weight)
  - Industry alignment (10% weight)
- 10 = Exceeds experience requirement with highly relevant background
- 5 = Meets minimum threshold or fresher with strong projects
- 1 = Significantly under-qualified or irrelevant experience

## Category 3: EDUCATION & PROJECTS
- Education: Degree level, field of study, institution reputation, GPA if available
- Projects: Complexity, relevance, technologies used, impact/outcomes
- Evaluate:
  - Educational foundation for the role (40% weight)
  - Quality and relevance of projects (40% weight)
  - Continuous learning evidence (certifications, courses) (20% weight)
- 10 = Top-tier education + impressive projects
- 1 = Education/projects unrelated to role

## Category 4: ACHIEVEMENTS
- Awards, competitions, publications, certifications
- Open-source contributions, patents, recognitions
- Quantifiable accomplishments (revenue impact, user growth, performance metrics)
- Evaluate:
  - Relevance to target role (50% weight)
  - Prestige/impact level (30% weight)
  - Quantity and consistency (20% weight)
- 10 = Multiple prestigious achievements directly relevant
- 5 = Some achievements showing excellence
- 1 = No notable achievements listed

## Category 5: EXTRACURRICULAR & LEADERSHIP
- Clubs, volunteering, organizing events, mentorship
- Leadership roles, team building, community involvement
- Soft skills demonstrated (communication, teamwork, initiative)
- Evaluate:
  - Leadership and ownership demonstrated (40% weight)
  - Teamwork and collaboration skills (30% weight)
  - Initiative and passion (20% weight)
  - Cultural fit indicators (10% weight)
- 10 = Strong leadership with significant impact
- 5 = Moderate involvement showing soft skills
- 1 = No extracurricular activities listed

# WEIGHTS FOR OVERALL SCORE
The overall score (1-10) is calculated as a weighted average:
{weights_display}

# OUTPUT FORMAT (STRICT JSON)

You MUST respond with a valid JSON object in this EXACT format:

{{
  "sub_scores": {{
    "skills": <float 1-10>,
    "experience": <float 1-10>,
    "education_projects": <float 1-10>,
    "achievements": <float 1-10>,
    "extracurricular": <float 1-10>
  }},
  "overall": <float 1-10>,
  "justifications": {{
    "skills": "<1-2 sentences explaining the skills score, mention key matches and gaps>",
    "experience": "<1-2 sentences explaining experience score, mention years and relevance>",
    "education_projects": "<1-2 sentences explaining education/projects score>",
    "achievements": "<1-2 sentences explaining achievements score>",
    "extracurricular": "<1-2 sentences explaining extracurricular score>"
  }},
  "feedback": [
    "<Suggestion 1: Specific skill/certification to acquire>",
    "<Suggestion 2: Experience area to develop or highlight better>",
    "<Suggestion 3: Additional improvement or unique strength to leverage>"
  ],
  "strengths": [
    "<Key strength 1>",
    "<Key strength 2>",
    "<Key strength 3>"
  ],
  "gaps": [
    "<Critical gap 1>",
    "<Critical gap 2>"
  ],
  "transferable_skills": [
    "<Transferable skill 1 from extracurricular/projects>",
    "<Transferable skill 2>"
  ],
  "hiring_recommendation": "<STRONG_FIT | GOOD_FIT | MODERATE_FIT | WEAK_FIT> - <1 sentence rationale>"
}}

# IMPORTANT NOTES
1. Be HONEST but CONSTRUCTIVE - highlight both strengths and gaps
2. Provide ACTIONABLE feedback that helps candidates improve
3. Consider CONTEXT - a 7.0 fresher might be better than a 6.5 experienced candidate for a junior role
4. Ensure JSON is VALID - use double quotes, proper escaping
5. Be CONSISTENT - use the same evaluation criteria for all candidates
6. Calculate overall score using the weighted formula: overall = Σ(sub_score × weight)

Now, provide your comprehensive analysis:"""

    return prompt


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
