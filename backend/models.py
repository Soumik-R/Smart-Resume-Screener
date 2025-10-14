"""
Data models and database schemas for Smart Resume Screener
Defines Pydantic models for API validation and MongoDB schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import copy


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


# ============================================================================
# Resume Parsing Models - Detailed structured extraction
# ============================================================================

class Role(BaseModel):
    """Model for a single work experience role"""
    title: str
    company: str
    duration: str  # e.g., "Jan 2020 - Dec 2021" or "6 months"
    description: str
    is_internship: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "duration": "Jan 2020 - Dec 2021",
                "description": "Developed REST APIs using Python and FastAPI",
                "is_internship": False
            }
        }


class Experience(BaseModel):
    """Model for overall work experience"""
    years: float = 0.0  # Total years of experience (0 for freshers)
    roles: List[Role] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "years": 2.5,
                "roles": [
                    {
                        "title": "Software Engineer",
                        "company": "Tech Corp",
                        "duration": "2 years",
                        "description": "Built scalable APIs",
                        "is_internship": False
                    }
                ]
            }
        }


class Education(BaseModel):
    """Model for educational qualification"""
    degree: str  # e.g., "Bachelor of Technology", "MBA"
    field: str  # e.g., "Computer Science", "Business Administration"
    institution: str
    year: Optional[int] = None  # Graduation year
    
    class Config:
        json_schema_extra = {
            "example": {
                "degree": "Bachelor of Technology",
                "field": "Computer Science",
                "institution": "MIT",
                "year": 2020
            }
        }


class Project(BaseModel):
    """Model for a project"""
    name: str
    technologies: List[str] = []  # Tech stack used
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "E-commerce Platform",
                "technologies": ["Python", "React", "MongoDB"],
                "description": "Built a full-stack e-commerce platform with payment integration"
            }
        }


class Resume(BaseModel):
    """
    Comprehensive model for parsed resume data
    Represents structured information extracted from a resume
    """
    # Basic Information
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    # Skills
    skills: List[str] = []
    
    # Experience
    experience: Experience = Field(default_factory=lambda: Experience(years=0.0, roles=[]))
    
    # Education
    education: List[Education] = []
    
    # Projects
    projects: List[Project] = []
    
    # Achievements (with metrics if available)
    achievements: List[str] = []
    
    # Extra-curricular and Leadership
    extracurricular: List[str] = []
    
    # Raw text for reference
    raw_text: str = ""
    
    def anonymize(self) -> 'Resume':
        """
        Create an anonymized copy of the resume for bias-free LLM processing
        Removes personally identifiable information (name, email, phone)
        
        Returns:
            Resume: Anonymized copy with PII removed
        """
        anonymized = self.model_copy(deep=True)
        anonymized.name = "CANDIDATE"
        anonymized.email = None
        anonymized.phone = None
        return anonymized
    
    def to_summary(self) -> str:
        """
        Generate a human-readable summary of the resume
        
        Returns:
            str: Formatted summary text
        """
        summary = f"Name: {self.name}\n"
        summary += f"Email: {self.email or 'N/A'}\n"
        summary += f"Phone: {self.phone or 'N/A'}\n"
        summary += f"Total Experience: {self.experience.years} years\n"
        summary += f"Skills: {', '.join(self.skills)}\n"
        summary += f"Education: {len(self.education)} qualification(s)\n"
        summary += f"Projects: {len(self.projects)}\n"
        summary += f"Achievements: {len(self.achievements)}\n"
        summary += f"Extra-curricular: {len(self.extracurricular)}\n"
        return summary
    
    def is_fresher(self) -> bool:
        """
        Check if the candidate is a fresher (no work experience)
        Internships are considered but don't count towards professional experience
        
        Returns:
            bool: True if fresher, False otherwise
        """
        return self.experience.years == 0.0 or (
            len(self.experience.roles) > 0 and 
            all(role.is_internship for role in self.experience.roles)
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-234-567-8900",
                "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
                "experience": {
                    "years": 2.5,
                    "roles": [
                        {
                            "title": "Software Engineer",
                            "company": "Tech Corp",
                            "duration": "Jan 2020 - Dec 2021",
                            "description": "Developed REST APIs",
                            "is_internship": False
                        }
                    ]
                },
                "education": [
                    {
                        "degree": "B.Tech",
                        "field": "Computer Science",
                        "institution": "MIT",
                        "year": 2020
                    }
                ],
                "projects": [
                    {
                        "name": "E-commerce Platform",
                        "technologies": ["Python", "React"],
                        "description": "Full-stack platform"
                    }
                ],
                "achievements": [
                    "Improved system performance by 40%",
                    "Led team of 5 developers"
                ],
                "extracurricular": [
                    "President of Computer Science Club",
                    "Volunteer at local NGO"
                ],
                "raw_text": "Full resume text..."
            }
        }


# Legacy simple model for backward compatibility
class ResumeData(BaseModel):
    """Simple model for parsed resume data (legacy)"""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: List[str] = []
    raw_text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-234-567-8900",
                "skills": ["Python", "FastAPI", "MongoDB"],
                "raw_text": "John Doe\nSoftware Engineer..."
            }
        }


class JobDescriptionData(BaseModel):
    """Model for parsed job description data"""
    title: Optional[str] = None
    required_skills: List[str] = []
    raw_text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "required_skills": ["Python", "FastAPI", "MongoDB", "AWS"],
                "raw_text": "We are looking for a Senior Python Developer..."
            }
        }


class MatchResult(BaseModel):
    """Model for resume-JD match result"""
    candidate_name: str
    candidate_email: Optional[str] = None
    candidate_skills: List[str] = []
    match_score: int = Field(..., ge=0, le=100)
    analysis: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "candidate_name": "John Doe",
                "candidate_email": "john.doe@example.com",
                "candidate_skills": ["Python", "FastAPI", "MongoDB"],
                "match_score": 85,
                "analysis": "SCORE: 85\nSTRENGTHS: Strong Python skills...\nGAPS: No AWS experience...\nRECOMMENDATION: Strong candidate..."
            }
        }


class CandidateDB(BaseModel):
    """Model for candidate stored in MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: List[str] = []
    raw_text: str
    match_score: Optional[int] = None
    analysis: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-234-567-8900",
                "skills": ["Python", "FastAPI", "MongoDB"],
                "raw_text": "John Doe\nSoftware Engineer...",
                "match_score": 85,
                "analysis": "Strong candidate...",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }


class UploadResponse(BaseModel):
    """Model for file upload response"""
    message: str
    filename: str
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Resume uploaded and processed successfully",
                "filename": "john_doe_resume.pdf",
                "status": "success"
            }
        }
