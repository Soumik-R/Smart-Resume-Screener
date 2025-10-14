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
- **BE CRITICAL**: Only give 9-10 if candidate has ALL required skills + extras
- 10 = Perfect match with all required + bonus skills + demonstrated mastery
- 7-8 = Strong match with most required skills
- 5-6 = Adequate match with some gaps
- 1-4 = Minimal skill overlap or significant gaps

## Category 2: EXPERIENCE (Work History)
- Calculate total relevant years using the rules above
- Evaluate:
  - Years of experience vs JD requirement (40% weight)
  - Relevance of past roles to target role (35% weight)
  - Career progression and growth (15% weight)
  - Industry alignment (10% weight)
- **BE CRITICAL**: Don't give high scores for barely meeting minimums
- 10 = Significantly exceeds requirement (2x+) with highly relevant background
- 7-8 = Exceeds requirement with relevant roles
- 5-6 = Meets minimum or fresher with strong projects/internships
- 3-4 = Below minimum but shows potential
- 1-2 = Significantly under-qualified or irrelevant experience

## Category 3: EDUCATION & PROJECTS
- Education: Degree level, field of study, institution reputation, GPA if available
- Projects: Complexity, relevance, technologies used, impact/outcomes
- Evaluate:
  - Educational foundation for the role (40% weight)
  - Quality and relevance of projects (40% weight)
  - Continuous learning evidence (certifications, courses) (20% weight)
- **BE CRITICAL**: Generic projects without impact don't deserve high scores
- 10 = Top-tier education + highly impressive, impactful projects
- 7-8 = Relevant degree + solid projects with measurable outcomes
- 5-6 = Adequate education + basic projects
- 1-4 = Education/projects unrelated or minimal quality

## Category 4: ACHIEVEMENTS
- Awards, competitions, publications, certifications
- Open-source contributions, patents, recognitions
- Quantifiable accomplishments (revenue impact, user growth, performance metrics)
- Evaluate:
  - Relevance to target role (50% weight)
  - Prestige/impact level (30% weight)
  - Quantity and consistency (20% weight)
- **BE CRITICAL**: Common certifications alone don't warrant 8+
- 10 = Multiple prestigious, directly relevant achievements (e.g., patents, major awards)
- 7-8 = Several strong achievements with clear impact
- 5-6 = Some achievements showing competence
- 3-4 = Minimal achievements
- 1-2 = No notable achievements listed

## Category 5: EXTRACURRICULAR & LEADERSHIP
- Clubs, volunteering, organizing events, mentorship
- Leadership roles, team building, community involvement
- Soft skills demonstrated (communication, teamwork, initiative)
- Evaluate:
  - Leadership and ownership demonstrated (40% weight)
  - Teamwork and collaboration skills (30% weight)
  - Initiative and passion (20% weight)
  - Cultural fit indicators (10% weight)
- **BE CRITICAL**: Membership alone doesn't equal leadership
- 10 = Substantial leadership with documented impact (e.g., founded organization, led 50+ people)
- 7-8 = Clear leadership roles with team management
- 5-6 = Active involvement showing soft skills
- 3-4 = Basic participation
- 1-2 = No extracurricular activities listed

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
1. **BE CRITICAL AND FAIR**: Reserve 9-10 scores for truly exceptional matches. Most candidates will score 4-7.
2. **SCORING CONSISTENCY**: Use the full 1-10 range. Don't cluster all scores around 7-8.
   - 10 = Exceptional, rare (top 1%)
   - 9 = Excellent, exceeds expectations significantly
   - 7-8 = Good, meets requirements with strengths
   - 5-6 = Adequate, meets minimums with gaps
   - 3-4 = Below par, significant development needed
   - 1-2 = Poor fit, major gaps
3. **BE HONEST but CONSTRUCTIVE**: Highlight both strengths and gaps with specifics
4. **ACTIONABLE FEEDBACK**: Provide concrete suggestions (e.g., "Obtain AWS certification" not "Improve cloud skills")
5. **CONTEXT MATTERS**: A 7.0 fresher with strong projects might be better than a 6.5 mid-level candidate for a junior role
6. **VALID JSON**: Use double quotes, proper escaping, no trailing commas
7. **WEIGHTED CALCULATION**: Verify overall = (skills × {weights['skills']}) + (experience × {weights['experience']}) + (education_projects × {weights['education_projects']}) + (achievements × {weights['achievements']}) + (extracurricular × {weights['extracurricular']})

Now, provide your comprehensive, critical, and insightful analysis:"""

    return prompt


# ============================================================================
# HELPER FUNCTIONS FOR MATCHING
# ============================================================================

def anonymize_resume(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Anonymize resume data by removing personal identifiers
    
    Args:
        resume_data: Resume data dictionary (from Resume model or dict)
        
    Returns:
        Anonymized copy of resume data
    """
    import copy
    anonymized = copy.deepcopy(resume_data)
    
    # Remove personal identifiers
    if 'name' in anonymized:
        anonymized['name'] = 'Anonymized Candidate'
    if 'email' in anonymized:
        anonymized['email'] = None
    if 'phone' in anonymized:
        anonymized['phone'] = None
    
    # Also anonymize raw_text if present (remove potential PII)
    if 'raw_text' in anonymized:
        # Keep raw_text but mark as anonymized
        anonymized['raw_text'] = anonymized['raw_text'][:500] + "... [truncated for privacy]"
    
    return anonymized


def parse_llm_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON from LLM response, handling common formatting issues
    
    Args:
        response_text: Raw text response from LLM
        
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    import json
    import re
    
    try:
        # Try direct parsing first
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object in text
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    return None


def validate_llm_output(output: Dict[str, Any]) -> bool:
    """
    Validate that LLM output has all required fields
    
    Args:
        output: Parsed LLM output dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = {
        'sub_scores': dict,
        'overall': (int, float),
        'justifications': dict,
        'feedback': list,
        'strengths': list,
        'gaps': list,
        'transferable_skills': list,
        'hiring_recommendation': str
    }
    
    for field, expected_type in required_fields.items():
        if field not in output:
            logger.warning(f"Missing required field: {field}")
            return False
        
        if not isinstance(output[field], expected_type):
            logger.warning(f"Field {field} has wrong type: expected {expected_type}, got {type(output[field])}")
            return False
    
    # Validate sub_scores has all categories
    required_categories = ['skills', 'experience', 'education_projects', 'achievements', 'extracurricular']
    for category in required_categories:
        if category not in output['sub_scores']:
            logger.warning(f"Missing category in sub_scores: {category}")
            return False
        
        score = output['sub_scores'][category]
        if not isinstance(score, (int, float)) or not (1 <= score <= 10):
            logger.warning(f"Invalid score for {category}: {score}")
            return False
    
    return True


# ============================================================================
# MAIN SCORING FUNCTIONS
# ============================================================================

def match_resume_to_jd(
    resume_json: str,
    jd_text: str,
    weights: Optional[Dict[str, float]] = None,
    role_context: str = "general",
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Match a resume to a job description using LLM analysis
    
    This is the main scoring function that:
    1. Anonymizes the resume data
    2. Builds a comprehensive prompt
    3. Calls GPT-4o for analysis
    4. Parses and validates the response
    5. Computes final weighted score
    
    Args:
        resume_json: Resume data in JSON string format
        jd_text: Job description text
        weights: Optional custom scoring weights (defaults to DEFAULT_WEIGHTS)
        role_context: Role level context ("junior", "senior", "mid-level", "general")
        max_retries: Maximum retry attempts if parsing fails
        
    Returns:
        Dictionary containing:
            - sub_scores: Dict of category scores (1-10)
            - overall: Overall weighted score (1-10)
            - justifications: Dict of explanations per category
            - feedback: List of improvement suggestions
            - strengths: List of key strengths
            - gaps: List of critical gaps
            - transferable_skills: List of transferable skills identified
            - hiring_recommendation: STRONG_FIT | GOOD_FIT | MODERATE_FIT | WEAK_FIT
            - shortlisted: Boolean (True if overall > 7.0)
            
    Raises:
        RuntimeError: If LLM call fails or response cannot be parsed after retries
    """
    import json
    
    if weights is None:
        weights = DEFAULT_WEIGHTS
    else:
        validate_weights(weights)
    
    logger.info("="*80)
    logger.info(f"🎯 Starting resume-JD matching with role_context='{role_context}'")
    logger.info(f"📊 Using weights: {weights}")
    
    # Parse resume JSON to anonymize it
    try:
        resume_data = json.loads(resume_json)
        logger.debug(f"Resume data keys: {list(resume_data.keys())}")
        
        anonymized_resume = anonymize_resume(resume_data)
        anonymized_json = json.dumps(anonymized_resume, indent=2)
        
        logger.info("✓ Resume anonymized successfully")
        logger.debug(f"Anonymized resume length: {len(anonymized_json)} characters")
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid resume JSON: {e}")
        raise ValueError(f"Invalid resume JSON format: {e}")
    
    # Build the comprehensive prompt
    logger.info("📝 Building LLM scoring prompt...")
    prompt = build_scoring_prompt(anonymized_json, jd_text, weights, role_context)
    logger.info(f"✓ Prompt built: {len(prompt)} characters")
    logger.debug(f"Prompt preview (first 500 chars):\n{prompt[:500]}...")
    
    # Call LLM with retries
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Calling GPT-4o (attempt {attempt + 1}/{max_retries + 1})")
            
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR recruiter with 10+ years of experience. Provide detailed, fair, and insightful resume analysis in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=GPT_TEMPERATURE,  # 0.3 for consistent scoring
                max_tokens=2000,  # Increased for detailed response
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"✓ Received LLM response ({len(response_text)} chars)")
            logger.debug(f"Raw LLM response (first 500 chars):\n{response_text[:500]}...")
            logger.debug(f"Token usage - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}, Total: {response.usage.total_tokens}")
            
            # Parse JSON response
            logger.info("📋 Parsing JSON response...")
            output = parse_llm_json_response(response_text)
            
            if output is None:
                logger.warning(f"⚠️ Failed to parse JSON (attempt {attempt + 1})")
                logger.debug(f"Unparseable response text:\n{response_text[:1000]}...")
                if attempt < max_retries:
                    logger.info("🔄 Retrying with fix-up prompt...")
                    # Retry with fix-up prompt
                    prompt = f"""The previous response was not valid JSON. Please provide the resume analysis in STRICT JSON format with these fields:
{{
  "sub_scores": {{"skills": <float>, "experience": <float>, "education_projects": <float>, "achievements": <float>, "extracurricular": <float>}},
  "overall": <float>,
  "justifications": {{"skills": "<text>", "experience": "<text>", "education_projects": "<text>", "achievements": "<text>", "extracurricular": "<text>"}},
  "feedback": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>"],
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "gaps": ["<gap 1>", "<gap 2>"],
  "transferable_skills": ["<skill 1>", "<skill 2>"],
  "hiring_recommendation": "<STRONG_FIT|GOOD_FIT|MODERATE_FIT|WEAK_FIT> - <rationale>"
}}

Original analysis request:
{prompt[:1000]}...
"""
                    continue
                else:
                    raise RuntimeError("Failed to parse LLM response as JSON after all retries")
            
            logger.info("✓ JSON parsed successfully")
            
            # Validate output structure
            logger.info("🔍 Validating LLM output structure...")
            if not validate_llm_output(output):
                logger.warning(f"⚠️ LLM output validation failed (attempt {attempt + 1})")
                logger.debug(f"Invalid output keys: {list(output.keys())}")
                if attempt < max_retries:
                    continue
                else:
                    raise RuntimeError("LLM output validation failed after all retries")
            
            logger.info("✓ Validation passed")
            
            # Compute final weighted score (verify LLM calculation)
            logger.info("🧮 Computing weighted overall score...")
            sub_scores = output['sub_scores']
            logger.debug(f"Sub-scores: {sub_scores}")
            
            calculated_overall = aggregate_scores(sub_scores, weights)
            logger.debug(f"Calculated overall: {calculated_overall:.2f}")
            
            # Use calculated score (more reliable than LLM's calculation)
            llm_overall = output.get('overall', 0)
            if abs(llm_overall - calculated_overall) > 0.5:
                logger.warning(f"⚠️ LLM overall ({llm_overall:.2f}) differs from calculated ({calculated_overall:.2f}) - using calculated")
            
            output['overall'] = calculated_overall
            
            # Add shortlist flag (True if score > 7.0)
            output['shortlisted'] = calculated_overall > 7.0
            logger.info(f"Shortlist status: {'✓ SHORTLISTED' if output['shortlisted'] else '✗ Not shortlisted'} (threshold: 7.0)")
            
            # Add metadata
            output['weights_used'] = weights
            output['role_context'] = role_context
            
            # Log final results
            logger.info("="*80)
            logger.info(f"✅ MATCHING COMPLETE - Overall score: {calculated_overall:.1f}/10")
            logger.info(f"📊 Sub-scores: Skills={sub_scores['skills']:.1f}, Experience={sub_scores['experience']:.1f}, Edu/Projects={sub_scores['education_projects']:.1f}, Achievements={sub_scores['achievements']:.1f}, Extracurricular={sub_scores['extracurricular']:.1f}")
            logger.info(f"💡 Recommendation: {output.get('hiring_recommendation', 'N/A')}")
            logger.info("="*80)
            
            return output
            
        except Exception as e:
            logger.error(f"Error in LLM call (attempt {attempt + 1}): {e}")
            if attempt < max_retries:
                continue
            else:
                raise RuntimeError(f"Failed to get LLM response after {max_retries + 1} attempts: {e}")
    
    raise RuntimeError("Unexpected error in match_resume_to_jd")


def calculate_match_score(resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function - wraps match_resume_to_jd for backward compatibility
    
    Args:
        resume_data: Parsed resume data (dict or Resume model)
        jd_data: Job description data (dict with 'text' or 'raw_text' field)
        
    Returns:
        Dictionary containing match score and analysis
    """
    import json
    
    # Convert Resume model to dict if needed
    if hasattr(resume_data, 'model_dump'):
        resume_dict = resume_data.model_dump()
    elif hasattr(resume_data, 'dict'):
        resume_dict = resume_data.dict()
    else:
        resume_dict = resume_data
    
    # Convert to JSON string
    resume_json = json.dumps(resume_dict, default=str)
    
    # Extract JD text
    jd_text = jd_data.get('text') or jd_data.get('raw_text') or str(jd_data)
    
    # Call new matching function
    result = match_resume_to_jd(resume_json, jd_text)
    
    # Convert to legacy format for compatibility
    return {
        "match_score": result['overall'] * 10,  # Convert 1-10 to 0-100 scale
        "overall_score": result['overall'],
        "sub_scores": result['sub_scores'],
        "analysis": json.dumps(result, indent=2),
        "shortlisted": result['shortlisted'],
        "candidate_name": resume_dict.get('name', 'Unknown'),
        "candidate_email": resume_dict.get('email', ''),
        "candidate_skills": resume_dict.get('skills', []),
        "justifications": result['justifications'],
        "feedback": result['feedback'],
        "strengths": result['strengths'],
        "gaps": result['gaps']
    }


def extract_jd_requirements(jd_text: str) -> Dict[str, Any]:
    """
    Extract key requirements from job description using regex patterns
    Falls back to simple parsing if complex extraction fails
    
    Args:
        jd_text: Raw job description text
        
    Returns:
        Dictionary with extracted requirements:
            - required_skills: List of required skills
            - experience_years: Required years of experience
            - education: Required education level
            - responsibilities: List of key responsibilities
    """
    import re
    
    result = {
        'required_skills': [],
        'experience_years': None,
        'education': None,
        'responsibilities': []
    }
    
    # Extract required skills section
    skills_pattern = r'(?:required skills|skills required|requirements|qualifications|must have)[:\s]*([^\n]+(?:\n[-•*]\s*[^\n]+)*)'
    skills_match = re.search(skills_pattern, jd_text, re.IGNORECASE)
    
    if skills_match:
        skills_text = skills_match.group(1)
        # Split by common delimiters
        skills = re.split(r'[,;•\n-]', skills_text)
        result['required_skills'] = [s.strip() for s in skills if s.strip() and len(s.strip()) > 2][:15]
    
    # Extract experience years
    exp_pattern = r'(\d+)[\s\-+]*(?:years?|yrs?).*?(?:experience|exp)'
    exp_match = re.search(exp_pattern, jd_text, re.IGNORECASE)
    if exp_match:
        result['experience_years'] = int(exp_match.group(1))
    
    # Extract education
    edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma', 'certification']
    for keyword in edu_keywords:
        if keyword in jd_text.lower():
            result['education'] = keyword.title()
            break
    
    # Extract responsibilities section
    resp_pattern = r'(?:responsibilities|duties|what you[\'\'\\s]ll do)[:\s]*([^\n]+(?:\n[-•*]\s*[^\n]+)*)'
    resp_match = re.search(resp_pattern, jd_text, re.IGNORECASE)
    
    if resp_match:
        resp_text = resp_match.group(1)
        responsibilities = re.split(r'\n[-•*]\s*', resp_text)
        result['responsibilities'] = [r.strip() for r in responsibilities if r.strip() and len(r.strip()) > 5][:10]
    
    logger.info(f"Extracted JD requirements: {len(result['required_skills'])} skills, {result['experience_years']} years exp")
    
    return result


def score_batch(
    resumes_list: List[Dict[str, Any]],
    jd_text: str,
    weights: Optional[Dict[str, float]] = None,
    role_context: str = "general",
    include_metadata: bool = True
) -> List[Dict[str, Any]]:
    """
    Score multiple resumes against a job description in batch
    
    Args:
        resumes_list: List of resume dictionaries (from Resume model or dicts)
        jd_text: Job description text
        weights: Optional custom scoring weights
        role_context: Role level context ("junior", "senior", "mid-level", "general")
        include_metadata: Include original resume data in results
        
    Returns:
        List of scored candidates, sorted by overall score (highest first)
        Each result contains:
            - candidate_id: Index or name of candidate
            - overall_score: Overall match score (1-10)
            - sub_scores: Category scores
            - shortlisted: Boolean flag
            - justifications: Explanations per category
            - feedback: Improvement suggestions
            - strengths: Key strengths
            - gaps: Critical gaps
            - transferable_skills: Identified transferable skills
            - hiring_recommendation: Fit level
            - rank: Position in sorted list (1 = best)
            - original_resume: Original resume data (if include_metadata=True)
    """
    import json
    
    logger.info("="*80)
    logger.info(f"🚀 Starting batch scoring for {len(resumes_list)} candidates")
    logger.info(f"⚙️ Settings: role_context='{role_context}', include_metadata={include_metadata}")
    logger.info(f"📊 Weights: {weights if weights else 'DEFAULT'}")
    
    # Extract JD requirements for better context
    logger.info("📋 Extracting JD requirements...")
    jd_requirements = extract_jd_requirements(jd_text)
    logger.info(f"✓ JD Requirements extracted:")
    logger.info(f"  - Skills: {jd_requirements['required_skills'][:5]}..." if jd_requirements['required_skills'] else "  - Skills: None extracted")
    logger.info(f"  - Experience: {jd_requirements['experience_years']} years" if jd_requirements['experience_years'] else "  - Experience: Not specified")
    logger.info(f"  - Education: {jd_requirements['education']}" if jd_requirements['education'] else "  - Education: Not specified")
    
    # Enhance JD text with extracted requirements
    enhanced_jd = jd_text
    if jd_requirements['required_skills']:
        skills_list = ', '.join(jd_requirements['required_skills'][:10])
        enhanced_jd += f"\n\nKey Required Skills: {skills_list}"
        logger.info(f"✓ JD enhanced with {len(jd_requirements['required_skills'])} extracted skills")
    
    results = []
    
    for idx, resume_data in enumerate(resumes_list):
        try:
            # Get candidate identifier
            candidate_id = resume_data.get('name', f'Candidate_{idx+1}')
            logger.info("-"*80)
            logger.info(f"👤 Scoring candidate {idx+1}/{len(resumes_list)}: {candidate_id}")
            
            # Convert to JSON string
            resume_json = json.dumps(resume_data, default=str)
            logger.debug(f"Resume JSON size: {len(resume_json)} characters")
            
            # Call matching function
            logger.info(f"🔄 Calling match_resume_to_jd for {candidate_id}...")
            match_result = match_resume_to_jd(
                resume_json=resume_json,
                jd_text=enhanced_jd,
                weights=weights,
                role_context=role_context
            )
            
            # Build result dictionary
            result = {
                'candidate_id': candidate_id,
                'overall_score': match_result['overall'],
                'sub_scores': match_result['sub_scores'],
                'shortlisted': match_result['shortlisted'],
                'justifications': match_result['justifications'],
                'feedback': match_result['feedback'],
                'strengths': match_result['strengths'],
                'gaps': match_result['gaps'],
                'transferable_skills': match_result['transferable_skills'],
                'hiring_recommendation': match_result['hiring_recommendation']
            }
            
            # Add metadata if requested
            if include_metadata:
                result['original_resume'] = {
                    'name': resume_data.get('name', 'Unknown'),
                    'email': resume_data.get('email'),
                    'phone': resume_data.get('phone'),
                    'skills': resume_data.get('skills', []),
                    'experience_years': resume_data.get('experience', {}).get('years', 0)
                }
            
            results.append(result)
            logger.info(f"✅ Scored {candidate_id}: {match_result['overall']:.1f}/10 - {match_result['hiring_recommendation']}")
            
        except Exception as e:
            logger.error(f"❌ Error scoring candidate {idx+1}: {e}")
            logger.debug(f"Error details:", exc_info=True)
            # Add failed result with error info
            failed_result = {
                'candidate_id': resume_data.get('name', f'Candidate_{idx+1}'),
                'overall_score': 0.0,
                'error': str(e),
                'shortlisted': False
            }
            results.append(failed_result)
            logger.warning(f"⚠️ Added error entry for {failed_result['candidate_id']}")
            continue
    
    # Sort by overall score (descending)
    logger.info("="*80)
    logger.info("📊 Sorting and ranking candidates...")
    results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
    
    # Add ranking
    for rank, result in enumerate(results, 1):
        result['rank'] = rank
    
    # Log final rankings
    logger.info("="*80)
    logger.info("🏆 BATCH SCORING COMPLETE - Final Rankings:")
    for i, result in enumerate(results[:5], 1):  # Top 5
        status = "✓" if result.get('shortlisted', False) else "✗"
        score = result.get('overall_score', 0)
        candidate = result.get('candidate_id', 'Unknown')
        logger.info(f"  {status} #{i}. {candidate}: {score:.1f}/10")
    
    if len(results) > 5:
        logger.info(f"  ... and {len(results) - 5} more candidates")
    
    logger.info(f"✅ Top candidate: {results[0]['candidate_id']} ({results[0]['overall_score']:.1f}/10)")
    shortlisted_count = sum(1 for r in results if r.get('shortlisted', False))
    logger.info(f"📋 Total shortlisted: {shortlisted_count}/{len(results)} candidates")
    logger.info("="*80)
    
    return results


def get_shortlisted_candidates(
    batch_results: List[Dict[str, Any]],
    min_score: float = 7.0
) -> List[Dict[str, Any]]:
    """
    Filter batch results to get only shortlisted candidates
    
    Args:
        batch_results: Results from score_batch()
        min_score: Minimum score threshold (default 7.0)
        
    Returns:
        Filtered list of candidates with score >= min_score
    """
    shortlisted = [
        result for result in batch_results
        if result.get('overall_score', 0) >= min_score
    ]
    
    logger.info(f"Shortlisted {len(shortlisted)}/{len(batch_results)} candidates (score >= {min_score})")
    
    return shortlisted


def batch_score_candidates(resumes: List[Dict[str, Any]], jd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Legacy function - wraps score_batch for backward compatibility
    
    Args:
        resumes: List of parsed resume data
        jd_data: Parsed job description data (dict with 'text' or 'raw_text' field)
        
    Returns:
        List of scored candidates, sorted by match score (highest first)
    """
    import json
    
    # Extract JD text
    jd_text = jd_data.get('text') or jd_data.get('raw_text') or str(jd_data)
    
    # Call new batch function
    results = score_batch(resumes, jd_text)
    
    # Convert to legacy format
    legacy_results = []
    for result in results:
        if 'error' not in result:
            legacy_results.append({
                'candidate_name': result['candidate_id'],
                'match_score': result['overall_score'] * 10,  # Convert to 0-100 scale
                'overall_score': result['overall_score'],
                'sub_scores': result['sub_scores'],
                'shortlisted': result['shortlisted'],
                'rank': result['rank'],
                'analysis': json.dumps(result, indent=2)
            })
    
    return legacy_results
