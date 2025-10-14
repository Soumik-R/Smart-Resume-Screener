# Phase 4 - Step 2: LLM Prompt Engineering ✅

## Overview
Successfully crafted a sophisticated, production-ready LLM prompt that mimics an expert HR recruiter with 10+ years of experience. The prompt includes comprehensive instructions for semantic matching, bias avoidance, context awareness, and creative insights.

---

## Prompt Architecture

### Design Principles

1. **Expert Persona** - "EXPERT HR RECRUITER with 10+ years in tech hiring"
2. **Structured Analysis** - Clear sections and categories
3. **Bias-Free Evaluation** - Explicit anonymization and fairness instructions
4. **Semantic Intelligence** - Advanced skill matching beyond exact keywords
5. **Context Awareness** - Role-specific evaluation (junior/senior/mid-level)
6. **Creative Insights** - Transferable skills and unique strengths
7. **Actionable Output** - Structured JSON with scores, justifications, and feedback

---

## Prompt Components

### 1. Expert Recruiter Persona

```
You are an EXPERT HR RECRUITER with 10+ years of experience in tech hiring 
and talent assessment. You have successfully placed hundreds of candidates 
and have a deep understanding of what makes a great fit for technical roles.
```

**Purpose:** Establishes authority and context for high-quality evaluation

---

### 2. Mission Statement

Clear goal: Provide comprehensive, fair, and insightful evaluation to help hiring managers make informed decisions.

---

### 3. Critical Instructions

#### A. Bias Avoidance (Mandatory) 🛡️

**Key Points:**
- Resume data is ANONYMIZED
- Do NOT make demographic assumptions (age, gender, ethnicity, nationality)
- Ignore protected characteristics
- Focus ONLY on skills, experience, education, capabilities
- Evaluate purely on job-relevant qualifications and merit

**Example Instructions:**
```
The resume data is ANONYMIZED - personal identifiers have been removed
Do NOT make assumptions about demographics (age, gender, ethnicity, nationality, etc.)
Focus ONLY on skills, experience, education, and demonstrated capabilities
Evaluate purely on job-relevant qualifications and merit
```

**Impact:** Ensures fair, unbiased evaluation compliant with hiring regulations

---

#### B. Semantic Understanding 🧠

**Capabilities:**
- Equivalent skills recognition: "data analysis" ≈ "SQL", "analytics"
- Related technologies: "React" ≈ "React.js", "ReactJS", "frontend development"
- Similar roles: "Software Engineer" ≈ "Developer", "Programmer"
- Domain knowledge: "machine learning" includes "neural networks", "AI"
- Transferable skills: Project management, problem-solving

**Example:**
```
Recognize equivalent skills:
- "data analysis" ≈ "SQL", "analytics", "statistical analysis"
- "React" ≈ "React.js", "ReactJS", "frontend development"
- "machine learning" includes "neural networks", "deep learning", "AI"
```

**Impact:** Matches candidates with relevant skills even without exact keyword matches

---

#### C. Experience Calculation Rules 📊

**Rules:**

1. **Internships:**
   - 3-6 month internship = 0.5 years equivalent
   - <3 months = 0.25 years
   - >6 months = full duration

2. **Freshers (0 years):**
   - NOT a negative factor
   - Evaluate based on projects and potential

3. **Overlapping Roles:**
   - Count only total time span, not cumulative

4. **Career Gaps:**
   - Do not penalize if skills maintained through projects

**Example:**
```
INTERNSHIPS: Count each 3-6 month internship as 0.5 years equivalent
FRESHERS (0 years): This is NOT a negative - evaluate based on projects and potential
Overlapping roles: Count only the total time span, not cumulative
```

**Impact:** Fair experience evaluation for all career stages

---

#### D. Context Awareness 🎯

**Four Context Types:**

##### 1. Junior-Level Roles (0-2 years)
```
CONTEXT: This is a JUNIOR-LEVEL role (0-2 years experience).
- Emphasize educational background and academic projects over work experience
- Internships are highly valuable - count each 3-6 month internship as 0.5 years
- Look for learning agility, foundational skills, and growth potential
- Projects and coursework demonstrate practical application
- Extracurricular activities show soft skills and leadership potential
```

##### 2. Senior-Level Roles (5+ years)
```
CONTEXT: This is a SENIOR-LEVEL role (5+ years experience).
- Prioritize depth of experience, leadership, and strategic impact
- Look for progressive career growth and increasing responsibility
- Achievements should demonstrate measurable business impact
- Technical depth matters more than breadth for specialized roles
- Management/mentorship experience is highly valuable
```

##### 3. Mid-Level Roles (2-5 years)
```
CONTEXT: This is a MID-LEVEL role (2-5 years experience).
- Balance between foundational skills and proven track record
- Look for consistency in career progression
- Projects should show increasing complexity and ownership
- Both technical skills and soft skills are important
- Some leadership or mentorship experience is a plus
```

##### 4. General Roles
```
CONTEXT: General role assessment.
- Evaluate the candidate holistically across all categories
- Consider both technical competencies and soft skills
- Look for alignment between career trajectory and role requirements
```

**Impact:** Tailored evaluation criteria based on role level

---

#### E. Creativity & Insight 💡

**Instructions:**

1. **Transferable Skills Identification**
   - Example: "Led university debate team" → Communication, leadership, critical thinking
   - Example: "Organized coding bootcamp" → Project management, community building

2. **Potential Recognition**
   - Look beyond current skills to learning capacity
   - Value self-learning and continuous improvement

3. **Unique Strengths**
   - Identify strengths not explicitly in JD but add value
   - Recognize diverse backgrounds and fresh perspectives

**Example:**
```
Identify TRANSFERABLE SKILLS from extracurricular activities:
  Example: "Led university debate team" → Communication, leadership, critical thinking
  Example: "Organized coding bootcamp" → Project management, community building
Recognize POTENTIAL from projects and self-learning
Spot UNIQUE STRENGTHS that aren't explicitly in the JD but add value
Suggest how candidate's background might bring FRESH PERSPECTIVES
```

**Impact:** Discovers hidden value and non-obvious strengths

---

### 4. Scoring Methodology

#### Five Categories (1-10 Scale)

##### Category 1: SKILLS (Technical & Functional)

**Evaluation Factors:**
- Coverage: % of required skills present (40% weight)
- Proficiency level: Depth vs surface knowledge (30% weight)
- Bonus skills: Nice-to-have or adjacent skills (20% weight)
- Skill recency: Recently used vs outdated (10% weight)

**Scale:**
- 10 = Perfect match with all required + bonus skills
- 5 = Meets core requirements
- 1 = Minimal skill overlap

---

##### Category 2: EXPERIENCE (Work History)

**Evaluation Factors:**
- Years of experience vs JD requirement (40% weight)
- Relevance of past roles to target role (35% weight)
- Career progression and growth (15% weight)
- Industry alignment (10% weight)

**Scale:**
- 10 = Exceeds experience requirement with highly relevant background
- 5 = Meets minimum threshold or fresher with strong projects
- 1 = Significantly under-qualified or irrelevant experience

---

##### Category 3: EDUCATION & PROJECTS

**Evaluation Factors:**
- Educational foundation for the role (40% weight)
- Quality and relevance of projects (40% weight)
- Continuous learning evidence (certifications, courses) (20% weight)

**Scale:**
- 10 = Top-tier education + impressive projects
- 5 = Adequate education with some projects
- 1 = Education/projects unrelated to role

---

##### Category 4: ACHIEVEMENTS

**Evaluation Factors:**
- Relevance to target role (50% weight)
- Prestige/impact level (30% weight)
- Quantity and consistency (20% weight)

**Scale:**
- 10 = Multiple prestigious achievements directly relevant
- 5 = Some achievements showing excellence
- 1 = No notable achievements listed

---

##### Category 5: EXTRACURRICULAR & LEADERSHIP

**Evaluation Factors:**
- Leadership and ownership demonstrated (40% weight)
- Teamwork and collaboration skills (30% weight)
- Initiative and passion (20% weight)
- Cultural fit indicators (10% weight)

**Scale:**
- 10 = Strong leadership with significant impact
- 5 = Moderate involvement showing soft skills
- 1 = No extracurricular activities listed

---

### 5. Overall Score Calculation

**Formula:**
```
overall = (skills × 0.40) + (experience × 0.25) + (education_projects × 0.15) 
          + (achievements × 0.10) + (extracurricular × 0.10)
```

**Displayed in Prompt:**
```
The overall score (1-10) is calculated as a weighted average:
  - Skills: 40%
  - Experience: 25%
  - Education & Projects: 15%
  - Achievements: 10%
  - Extracurricular: 10%
```

---

### 6. Output Format (Structured JSON)

**Required Fields:**

```json
{
  "sub_scores": {
    "skills": <float 1-10>,
    "experience": <float 1-10>,
    "education_projects": <float 1-10>,
    "achievements": <float 1-10>,
    "extracurricular": <float 1-10>
  },
  "overall": <float 1-10>,
  "justifications": {
    "skills": "<1-2 sentences explaining the skills score>",
    "experience": "<1-2 sentences explaining experience score>",
    "education_projects": "<1-2 sentences explaining education/projects score>",
    "achievements": "<1-2 sentences explaining achievements score>",
    "extracurricular": "<1-2 sentences explaining extracurricular score>"
  },
  "feedback": [
    "<Suggestion 1: Specific skill/certification to acquire>",
    "<Suggestion 2: Experience area to develop>",
    "<Suggestion 3: Additional improvement or strength to leverage>"
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
}
```

**Validation Hints:**
- Use VALID JSON
- Double quotes for strings
- Proper escaping

---

## Testing Results

**Total: 9/10 tests passed** ✅

### Test Summary

| Test | Status | Details |
|------|--------|---------|
| Prompt Structure | ✅ PASS | All 21 required components present |
| Bias Avoidance | ✅ PASS | 6/6 bias keywords documented |
| Semantic Matching | ✅ PASS | 6/6 examples included |
| Experience Rules | ✅ PASS | 6/6 rules documented |
| Context Awareness | ✅ PASS | All 4 contexts (junior/senior/mid/general) |
| Creativity Instructions | ✅ PASS | 6/6 creativity elements |
| Scoring Categories | ✅ PASS | All 5 categories detailed |
| JSON Output Format | ✅ PASS | All 8 fields + validation hints |
| Weights Display | ✅ PASS | Default & custom weights work |
| Prompt Length | ⚠️ INFO | 1,065 words (compact but complete) |

---

## Prompt Metrics

- **Word Count:** ~1,065 words
- **Character Count:** ~7,700 characters
- **Lines:** ~186 lines
- **Sections:** 6 major sections
- **Categories:** 5 scoring categories
- **Context Types:** 4 role levels

**Token Estimate:** ~1,500-2,000 tokens (well within GPT-4o limits)

---

## Function Signature

```python
def build_scoring_prompt(
    resume_json: str,
    jd_text: str,
    weights: Optional[Dict[str, float]] = None,
    role_context: str = "general"
) -> str:
    """
    Build comprehensive LLM prompt for resume-JD matching
    
    Args:
        resume_json: Anonymized resume data in JSON format
        jd_text: Job description text
        weights: Scoring weights (defaults to DEFAULT_WEIGHTS)
        role_context: "junior", "senior", "mid-level", or "general"
        
    Returns:
        Formatted prompt string for GPT-4o
    """
```

---

## Usage Examples

### Basic Usage
```python
from backend.matcher import build_scoring_prompt
import json

# Prepare resume data
resume_data = {
    "name": "Anonymized Candidate",
    "skills": ["Python", "Machine Learning", "SQL"],
    "experience": {"years": 3.0, "roles": [...]},
    "education": [...],
    "projects": [...],
    "achievements": [...],
    "extracurricular": [...]
}
resume_json = json.dumps(resume_data, indent=2)

# Job description
jd_text = """
Software Engineer - Machine Learning
Requirements:
- 2+ years Python and ML experience
- SQL and data analysis skills
- Bachelor's in CS or related field
"""

# Build prompt
prompt = build_scoring_prompt(resume_json, jd_text)
```

### With Custom Weights
```python
# Tech-heavy role
tech_weights = {
    'skills': 0.50,
    'experience': 0.25,
    'education_projects': 0.15,
    'achievements': 0.05,
    'extracurricular': 0.05
}

prompt = build_scoring_prompt(
    resume_json, 
    jd_text, 
    weights=tech_weights
)
```

### With Role Context
```python
# Junior role
prompt = build_scoring_prompt(
    resume_json,
    jd_text,
    role_context="junior"
)

# Senior role
prompt = build_scoring_prompt(
    resume_json,
    jd_text,
    role_context="senior"
)
```

---

## Key Features Implemented

### ✅ Extraordinary Elements

1. **Bias Avoidance**
   - Explicit anonymization acknowledgment
   - Demographics ignored
   - Protected characteristics excluded
   - Merit-based evaluation only

2. **Semantic Intelligence**
   - Equivalent skill recognition
   - Related technology matching
   - Domain knowledge understanding
   - Transferable skills identification

3. **Context Awareness**
   - Junior: Emphasize projects over experience
   - Senior: Prioritize leadership and impact
   - Mid-level: Balance skills and track record
   - General: Holistic evaluation

4. **Creative Insights**
   - Transferable skills from extracurriculars
   - Hidden potential recognition
   - Unique strengths identification
   - Fresh perspective suggestions

5. **Comprehensive Scoring**
   - 5 detailed categories
   - Clear 1-10 scale guidance
   - Weighted sub-components
   - Justifications required

6. **Actionable Feedback**
   - 3 specific improvement suggestions
   - Gap identification
   - Strength highlighting
   - Hiring recommendation

---

## Prompt Quality Checklist

- ✅ Expert persona (10+ years)
- ✅ Comprehensive bias avoidance
- ✅ Semantic matching examples
- ✅ Experience calculation rules (internships, freshers)
- ✅ Context-aware evaluation (4 role types)
- ✅ Creativity & transferable skills
- ✅ 5 detailed scoring categories
- ✅ Structured JSON output format
- ✅ Configurable weights display
- ✅ Validation instructions
- ✅ Consistency guidelines

---

## Comparison with Requirements

### Original Requirements ✅

1. ✅ **Expert recruiter persona** - "10+ years in tech hiring"
2. ✅ **Anonymized resume data** - Explicitly mentioned
3. ✅ **JD analysis** - Extract key requirements
4. ✅ **5 Category scoring** - Skills, Experience, Education/Projects, Achievements, Extracurricular
5. ✅ **Semantic matching** - "data analysis" covers "SQL"
6. ✅ **Experience calculation** - Internships as 0.5-1 equiv, 0 for freshers
7. ✅ **Weighted scoring** - Formula with configurable weights
8. ✅ **JSON output** - Structured with all required fields

### Extraordinary Additions ✅

1. ✅ **Bias avoidance** - Demographics explicitly ignored
2. ✅ **Context awareness** - Junior roles emphasize projects
3. ✅ **Creativity** - Transferable skills from extracurriculars
4. ✅ **Multiple contexts** - Junior/senior/mid-level/general
5. ✅ **Detailed guidance** - Sub-weights for each category
6. ✅ **Validation hints** - JSON format instructions
7. ✅ **Hiring recommendation** - STRONG_FIT | GOOD_FIT | etc.
8. ✅ **Transferable skills** - Separate field in output

---

## Benefits

### For Hiring Managers
- Consistent, structured evaluations
- Clear justifications for decisions
- Actionable feedback to share with candidates
- Reduced unconscious bias

### For Candidates
- Fair, merit-based evaluation
- Recognition of transferable skills
- Specific improvement suggestions
- Understanding of gaps and strengths

### For System
- Structured JSON output for parsing
- Configurable weights per role type
- Context-aware evaluation
- Scalable to batch processing

---

## Next Steps

### Step 3: LLM API Integration
- Implement LLM call with prompt
- Parse JSON response
- Handle errors and edge cases
- Validate output structure

### Step 4: Response Processing
- Extract scores and justifications
- Calculate weighted overall score
- Format results for API response
- Add logging and monitoring

### Step 5: Batch Processing
- Score multiple resumes efficiently
- Rank candidates by overall score
- Generate comparison reports
- Optimize API usage

---

## File Structure

### Updated: `backend/matcher.py`

```
Lines 1-61:   Configuration (client, model, weights)
Lines 64-177:  Utility functions (validate, aggregate, get_weights)
Lines 180-398: build_scoring_prompt() - Main prompt builder
Lines 401+:    calculate_match_score() - To be updated
```

**New Function:** `build_scoring_prompt()` (~220 lines with documentation)

---

## Dependencies

- `typing.Optional` - Type hints for optional parameters
- JSON formatting for resume data
- String formatting for dynamic prompt generation

---

## Configuration Options

### Role Contexts
```python
# Junior role (0-2 years)
build_scoring_prompt(resume, jd, role_context="junior")

# Senior role (5+ years)
build_scoring_prompt(resume, jd, role_context="senior")

# Mid-level role (2-5 years)
build_scoring_prompt(resume, jd, role_context="mid-level")

# General (any level)
build_scoring_prompt(resume, jd, role_context="general")
```

### Custom Weights
```python
# Skills-heavy role
tech_weights = {'skills': 0.50, 'experience': 0.20, ...}
build_scoring_prompt(resume, jd, weights=tech_weights)

# Experience-heavy role
senior_weights = {'skills': 0.25, 'experience': 0.40, ...}
build_scoring_prompt(resume, jd, weights=senior_weights)
```

---

## Conclusion

**Step 2 Status:** ✅ COMPLETE

Successfully crafted an extraordinary LLM prompt with:
- ✅ Expert recruiter persona (10+ years)
- ✅ Comprehensive bias avoidance
- ✅ Semantic matching intelligence
- ✅ Context-aware evaluation
- ✅ Creative insight instructions
- ✅ 5 detailed scoring categories
- ✅ Structured JSON output
- ✅ Configurable weights

**Quality Metrics:**
- 9/10 tests passed
- 1,065 words (comprehensive yet efficient)
- 21 critical components validated
- 4 context types supported

**Ready for Step 3:** LLM API integration and response parsing! 🚀
