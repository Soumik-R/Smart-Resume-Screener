"""
Data models and database schemas for Smart Resume Screener
Defines Pydantic models for API validation and MongoDB schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


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


class ResumeData(BaseModel):
    """Model for parsed resume data"""
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
