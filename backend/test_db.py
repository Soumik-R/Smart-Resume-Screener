"""
Test database connection and basic operations
"""
import sys
sys.path.insert(0, '.')

from db import (
    get_database_stats,
    save_parsed_resume,
    get_resume_by_id,
    save_job_description,
    get_job_by_id,
    update_match_results,
    save_match_result,
    get_match_history
)


def test_connection():
    """Test MongoDB connection"""
    print("\n=== Test 1: Database Connection ===")
    
    try:
        stats = get_database_stats()
        print(f"✓ Connected to database: {stats['database']}")
        print(f"Collections:")
        for collection, count in stats['collections'].items():
            print(f"  - {collection}: {count} documents")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_resume_operations():
    """Test resume CRUD operations"""
    print("\n=== Test 2: Resume Operations ===")
    
    # Sample resume data
    sample_resume = {
        "name": "Test Candidate",
        "email": "test@example.com",
        "phone": "1234567890",
        "skills": ["Python", "MongoDB", "FastAPI"],
        "experience": {
            "years": 3,
            "roles": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2021-Present"
                }
            ]
        },
        "education": [
            {
                "degree": "Bachelor's",
                "field": "Computer Science",
                "institution": "Test University",
                "year": 2021
            }
        ],
        "projects": [],
        "achievements": [],
        "extracurricular": []
    }
    
    try:
        # Save resume
        print("Saving resume...")
        resume_id = save_parsed_resume(sample_resume)
        print(f"✓ Saved resume with ID: {resume_id}")
        
        # Retrieve resume
        print("Retrieving resume...")
        retrieved = get_resume_by_id(resume_id)
        if retrieved:
            print(f"✓ Retrieved resume: {retrieved['metadata']['name']}")
        else:
            print("✗ Failed to retrieve resume")
            return False
        
        return resume_id
        
    except Exception as e:
        print(f"✗ Resume operations failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_job_operations():
    """Test job description operations"""
    print("\n=== Test 3: Job Description Operations ===")
    
    sample_jd = """
    Senior Python Developer
    
    Required Skills:
    - Python, FastAPI
    - MongoDB, PostgreSQL
    - 5+ years experience
    - Bachelor's degree required
    
    Responsibilities:
    - Build REST APIs
    - Design database schemas
    - Lead development team
    """
    
    try:
        # Save JD
        print("Saving job description...")
        jd_id = save_job_description(sample_jd)
        print(f"✓ Saved JD with ID: {jd_id}")
        
        # Retrieve JD
        print("Retrieving JD...")
        retrieved = get_job_by_id(jd_id)
        if retrieved:
            print(f"✓ Retrieved JD with {len(retrieved['requirements']['required_skills'])} skills")
        else:
            print("✗ Failed to retrieve JD")
            return False
        
        return jd_id
        
    except Exception as e:
        print(f"✗ JD operations failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_match_operations(resume_id, jd_id):
    """Test match result operations"""
    print("\n=== Test 4: Match Result Operations ===")
    
    # Mock match result
    mock_match = {
        "overall": 7.5,
        "sub_scores": {
            "skills": 8.0,
            "experience": 7.0,
            "education_projects": 7.5,
            "achievements": 6.0,
            "extracurricular": 7.0
        },
        "shortlisted": True,
        "hiring_recommendation": "GOOD_FIT - Strong technical skills",
        "feedback": ["Consider AWS certification", "Build more complex projects"],
        "strengths": ["Solid Python skills", "Good experience level"],
        "gaps": ["Limited cloud experience"]
    }
    
    try:
        # Update resume with match result
        print("Updating resume with match result...")
        success = update_match_results(resume_id, jd_id, mock_match)
        if success:
            print("✓ Match result added to resume history")
        else:
            print("✗ Failed to update resume")
        
        # Save standalone match result
        print("Saving standalone match result...")
        match_id = save_match_result(resume_id, jd_id, mock_match)
        print(f"✓ Saved match result with ID: {match_id}")
        
        # Retrieve match history
        print("Retrieving match history...")
        history = get_match_history(resume_id=resume_id)
        print(f"✓ Retrieved {len(history)} match results for resume")
        
        return True
        
    except Exception as e:
        print(f"✗ Match operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*60)
    print("Testing Database Module")
    print("="*60)
    
    # Test 1: Connection
    if not test_connection():
        print("\n❌ Database connection failed!")
        print("Make sure MongoDB is running: mongod")
        sys.exit(1)
    
    # Test 2: Resume operations
    resume_id = test_resume_operations()
    if not resume_id:
        print("\n❌ Resume operations failed!")
        sys.exit(1)
    
    # Test 3: Job operations
    jd_id = test_job_operations()
    if not jd_id:
        print("\n❌ Job operations failed!")
        sys.exit(1)
    
    # Test 4: Match operations
    if not test_match_operations(resume_id, jd_id):
        print("\n❌ Match operations failed!")
        sys.exit(1)
    
    # Final stats
    print("\n" + "="*60)
    print("✅ ALL DATABASE TESTS PASSED")
    print("="*60)
    
    final_stats = get_database_stats()
    print(f"\nFinal database state:")
    for collection, count in final_stats['collections'].items():
        print(f"  {collection}: {count} documents")
    
    print("\n✓ Database module ready for API integration!")
