"""
MongoDB database integration for Smart Resume Screener
Handles storage and retrieval of resumes, job descriptions, and match results
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from bson import ObjectId
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB Configuration
# Try MONGODB_URI first (Atlas), fallback to MONGO_URI, then localhost
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "resume_screener"

# Collections
CANDIDATES_COLLECTION = "candidates"
JOBS_COLLECTION = "jobs"
MATCH_RESULTS_COLLECTION = "match_results"

# Global client instance
_client = None
_db = None


# ============================================================================
# CONNECTION MANAGEMENT
# ============================================================================

def get_client() -> MongoClient:
    """
    Get MongoDB client (singleton pattern)
    
    Returns:
        MongoClient instance
        
    Raises:
        ConnectionFailure: If cannot connect to MongoDB
    """
    global _client
    
    if _client is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            _client.admin.command('ping')
            logger.info(f"✓ Connected to MongoDB at {MONGO_URI}")
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise ConnectionFailure(f"Cannot connect to MongoDB at {MONGO_URI}. Make sure MongoDB is running.")
    
    return _client


def get_database():
    """
    Get database instance
    
    Returns:
        Database instance
    """
    global _db
    
    if _db is None:
        client = get_client()
        _db = client[DATABASE_NAME]
        logger.info(f"✓ Using database: {DATABASE_NAME}")
    
    return _db


def close_connection():
    """Close MongoDB connection"""
    global _client, _db
    
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("✓ MongoDB connection closed")


# ============================================================================
# CANDIDATE/RESUME OPERATIONS
# ============================================================================

def save_parsed_resume(resume_data: Dict[str, Any], file_id: Optional[str] = None) -> str:
    """
    Save parsed resume to database
    
    Args:
        resume_data: Parsed resume dictionary from parser
        file_id: Optional custom file ID (generates ObjectId if None)
        
    Returns:
        Document ID (string)
        
    Raises:
        ValueError: If resume_data is invalid
    """
    db = get_database()
    candidates = db[CANDIDATES_COLLECTION]
    
    # Validate required fields
    if not resume_data:
        raise ValueError("Resume data cannot be empty")
    
    # Prepare document
    document = {
        "resume_data": resume_data,
        "uploaded_at": datetime.now(),
        "updated_at": datetime.now(),
        "match_history": [],  # Will store match results
        "status": "parsed",
        "metadata": {
            "name": resume_data.get("name", "Unknown"),
            "email": resume_data.get("email"),
            "skills": resume_data.get("skills", []),
            "experience_years": resume_data.get("experience", {}).get("years", 0)
        }
    }
    
    # Use custom ID if provided
    if file_id:
        document["_id"] = file_id
    
    try:
        result = candidates.insert_one(document)
        doc_id = str(result.inserted_id)
        logger.info(f"✓ Saved resume to database: {doc_id} (Name: {document['metadata']['name']})")
        return doc_id
        
    except DuplicateKeyError:
        logger.warning(f"⚠️ Document with ID {file_id} already exists - updating instead")
        # Update existing document
        candidates.update_one(
            {"_id": file_id},
            {"$set": {
                "resume_data": resume_data,
                "updated_at": datetime.now(),
                "metadata": document["metadata"]
            }}
        )
        return file_id


def get_resume_by_id(resume_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve resume by ID
    
    Args:
        resume_id: Document ID (string or ObjectId)
        
    Returns:
        Resume document or None if not found
    """
    db = get_database()
    candidates = db[CANDIDATES_COLLECTION]
    
    try:
        # Try as ObjectId first, then as string
        try:
            doc_id = ObjectId(resume_id)
        except:
            doc_id = resume_id
        
        document = candidates.find_one({"_id": doc_id})
        
        if document:
            # Convert ObjectId to string for JSON serialization
            document["_id"] = str(document["_id"])
            logger.debug(f"✓ Retrieved resume: {resume_id}")
            return document
        else:
            logger.warning(f"⚠️ Resume not found: {resume_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error retrieving resume {resume_id}: {e}")
        return None


def get_all_resumes(limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
    """
    Get all resumes with pagination
    
    Args:
        limit: Maximum number of documents to return
        skip: Number of documents to skip
        
    Returns:
        List of resume documents
    """
    db = get_database()
    candidates = db[CANDIDATES_COLLECTION]
    
    documents = list(candidates.find().sort("uploaded_at", DESCENDING).skip(skip).limit(limit))
    
    # Convert ObjectIds to strings
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    
    logger.info(f"✓ Retrieved {len(documents)} resumes (skip={skip}, limit={limit})")
    return documents


def update_match_results(resume_id: str, jd_id: str, match_result: Dict[str, Any]) -> bool:
    """
    Add match result to resume's history
    
    Args:
        resume_id: Resume document ID
        jd_id: Job description ID
        match_result: Match result dictionary from matcher
        
    Returns:
        True if successful, False otherwise
    """
    db = get_database()
    candidates = db[CANDIDATES_COLLECTION]
    
    try:
        # Try as ObjectId first
        try:
            doc_id = ObjectId(resume_id)
        except:
            doc_id = resume_id
        
        # Prepare match entry
        match_entry = {
            "jd_id": jd_id,
            "timestamp": datetime.now(),
            "overall_score": match_result.get("overall", 0),
            "sub_scores": match_result.get("sub_scores", {}),
            "shortlisted": match_result.get("shortlisted", False),
            "hiring_recommendation": match_result.get("hiring_recommendation", ""),
            "feedback": match_result.get("feedback", []),
            "strengths": match_result.get("strengths", []),
            "gaps": match_result.get("gaps", [])
        }
        
        # Append to match_history array
        result = candidates.update_one(
            {"_id": doc_id},
            {
                "$push": {"match_history": match_entry},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"✓ Added match result for resume {resume_id} with JD {jd_id}")
            return True
        else:
            logger.warning(f"⚠️ Resume {resume_id} not found for match update")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error updating match results: {e}")
        return False


def delete_resume(resume_id: str) -> bool:
    """
    Delete resume by ID
    
    Args:
        resume_id: Document ID
        
    Returns:
        True if deleted, False otherwise
    """
    db = get_database()
    candidates = db[CANDIDATES_COLLECTION]
    
    try:
        try:
            doc_id = ObjectId(resume_id)
        except:
            doc_id = resume_id
        
        result = candidates.delete_one({"_id": doc_id})
        
        if result.deleted_count > 0:
            logger.info(f"✓ Deleted resume: {resume_id}")
            return True
        else:
            logger.warning(f"⚠️ Resume not found for deletion: {resume_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error deleting resume: {e}")
        return False


# ============================================================================
# JOB DESCRIPTION OPERATIONS
# ============================================================================

def save_job_description(jd_text: str, requirements: Optional[Dict[str, Any]] = None, jd_id: Optional[str] = None) -> str:
    """
    Save job description to database
    
    Args:
        jd_text: Job description text
        requirements: Optional parsed requirements (skills, exp, education)
        jd_id: Optional custom JD ID
        
    Returns:
        Document ID (string)
    """
    db = get_database()
    jobs = db[JOBS_COLLECTION]
    
    if not jd_text:
        raise ValueError("Job description text cannot be empty")
    
    # Auto-extract requirements if not provided
    if requirements is None:
        from matcher import extract_jd_requirements
        requirements = extract_jd_requirements(jd_text)
    
    document = {
        "jd_text": jd_text,
        "requirements": requirements,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "active",
        "metadata": {
            "required_skills": requirements.get("required_skills", [])[:10],
            "experience_years": requirements.get("experience_years"),
            "education": requirements.get("education")
        }
    }
    
    if jd_id:
        document["_id"] = jd_id
    
    try:
        result = jobs.insert_one(document)
        doc_id = str(result.inserted_id)
        logger.info(f"✓ Saved job description: {doc_id}")
        return doc_id
        
    except DuplicateKeyError:
        logger.warning(f"⚠️ JD with ID {jd_id} already exists - updating instead")
        jobs.update_one(
            {"_id": jd_id},
            {"$set": {
                "jd_text": jd_text,
                "requirements": requirements,
                "updated_at": datetime.now(),
                "metadata": document["metadata"]
            }}
        )
        return jd_id


def get_job_by_id(jd_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve job description by ID
    
    Args:
        jd_id: Document ID
        
    Returns:
        JD document or None if not found
    """
    db = get_database()
    jobs = db[JOBS_COLLECTION]
    
    try:
        try:
            doc_id = ObjectId(jd_id)
        except:
            doc_id = jd_id
        
        document = jobs.find_one({"_id": doc_id})
        
        if document:
            document["_id"] = str(document["_id"])
            logger.debug(f"✓ Retrieved JD: {jd_id}")
            return document
        else:
            logger.warning(f"⚠️ JD not found: {jd_id}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error retrieving JD {jd_id}: {e}")
        return None


def get_all_jobs(limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    """
    Get all job descriptions with pagination
    
    Args:
        limit: Maximum number of documents to return
        skip: Number of documents to skip
        
    Returns:
        List of JD documents
    """
    db = get_database()
    jobs = db[JOBS_COLLECTION]
    
    documents = list(jobs.find().sort("created_at", DESCENDING).skip(skip).limit(limit))
    
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    
    logger.info(f"✓ Retrieved {len(documents)} job descriptions")
    return documents


def delete_job(jd_id: str) -> bool:
    """
    Delete job description by ID
    
    Args:
        jd_id: Document ID
        
    Returns:
        True if deleted, False otherwise
    """
    db = get_database()
    jobs = db[JOBS_COLLECTION]
    
    try:
        try:
            doc_id = ObjectId(jd_id)
        except:
            doc_id = jd_id
        
        result = jobs.delete_one({"_id": doc_id})
        
        if result.deleted_count > 0:
            logger.info(f"✓ Deleted job description: {jd_id}")
            return True
        else:
            logger.warning(f"⚠️ JD not found for deletion: {jd_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error deleting JD: {e}")
        return False


# ============================================================================
# MATCH RESULTS OPERATIONS
# ============================================================================

def save_match_result(resume_id: str, jd_id: str, match_data: Dict[str, Any]) -> str:
    """
    Save standalone match result (for batch processing history)
    
    Args:
        resume_id: Resume document ID
        jd_id: Job description ID
        match_data: Full match result from matcher
        
    Returns:
        Match result document ID
    """
    db = get_database()
    match_results = db[MATCH_RESULTS_COLLECTION]
    
    document = {
        "resume_id": resume_id,
        "jd_id": jd_id,
        "timestamp": datetime.now(),
        "match_data": match_data,
        "overall_score": match_data.get("overall", 0),
        "shortlisted": match_data.get("shortlisted", False)
    }
    
    result = match_results.insert_one(document)
    doc_id = str(result.inserted_id)
    
    logger.info(f"✓ Saved match result: {doc_id} (Resume: {resume_id}, JD: {jd_id}, Score: {document['overall_score']:.1f})")
    
    return doc_id


def get_match_history(resume_id: Optional[str] = None, jd_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get match history with optional filters
    
    Args:
        resume_id: Optional filter by resume ID
        jd_id: Optional filter by JD ID
        limit: Maximum results to return
        
    Returns:
        List of match result documents
    """
    db = get_database()
    match_results = db[MATCH_RESULTS_COLLECTION]
    
    query = {}
    if resume_id:
        query["resume_id"] = resume_id
    if jd_id:
        query["jd_id"] = jd_id
    
    documents = list(match_results.find(query).sort("timestamp", DESCENDING).limit(limit))
    
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    
    logger.info(f"✓ Retrieved {len(documents)} match results")
    return documents


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_database_stats() -> Dict[str, Any]:
    """
    Get database statistics
    
    Returns:
        Dictionary with collection counts and stats
    """
    db = get_database()
    
    stats = {
        "database": DATABASE_NAME,
        "collections": {
            "candidates": db[CANDIDATES_COLLECTION].count_documents({}),
            "jobs": db[JOBS_COLLECTION].count_documents({}),
            "match_results": db[MATCH_RESULTS_COLLECTION].count_documents({})
        },
        "timestamp": datetime.now()
    }
    
    logger.info(f"📊 Database stats: {stats['collections']}")
    
    return stats


def clear_all_data():
    """
    DANGER: Clear all data from database (for testing only)
    """
    db = get_database()
    
    db[CANDIDATES_COLLECTION].delete_many({})
    db[JOBS_COLLECTION].delete_many({})
    db[MATCH_RESULTS_COLLECTION].delete_many({})
    
    logger.warning("⚠️ All database data cleared!")


# Initialize connection on module import
if __name__ != "__main__":
    try:
        get_client()
    except ConnectionFailure:
        logger.warning("⚠️ MongoDB not available - database operations will fail")
        logger.info("💡 To start MongoDB:")
        logger.info("   1. Install MongoDB Community Edition from mongodb.com")
        logger.info("   2. Run: mongod")
        logger.info("   3. Or use MongoDB Atlas (cloud): atlas.mongodb.com")
